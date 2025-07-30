# repositories/scenario_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, func
import uuid
from datetime import datetime

from ..models.scenario import Scenario, ScenarioSharing
from ..models.base import StatusEnum, PermissionLevelEnum
from ..schemas.scenario import ScenarioCreate, ScenarioUpdate


class ScenarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, scenario_data: ScenarioCreate, user_id: str) -> Scenario:
        """Create a new scenario."""
        db_scenario = Scenario(
            user_id=user_id,
            name=scenario_data.name,
            description=scenario_data.description,
            scenario_type=scenario_data.scenario_type,
            user_birth_year=scenario_data.user_birth_year,
            spouse_birth_year=scenario_data.spouse_birth_year,
            user_life_expectancy=scenario_data.user_life_expectancy,
            spouse_life_expectancy=scenario_data.spouse_life_expectancy,
            financial_goal=scenario_data.financial_goal,
            state_of_residence=scenario_data.state_of_residence,
            inflation_assumption=scenario_data.inflation_assumption,
            annual_contribution_limit=scenario_data.annual_contribution_limit,
            status=StatusEnum.draft,
            sharing_enabled=False
        )
        
        self.db.add(db_scenario)
        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario

    def get_by_id(self, scenario_id: uuid.UUID, user_id: Optional[str] = None) -> Optional[Scenario]:
        """Get scenario by ID, optionally filtered by user."""
        query = self.db.query(Scenario).options(
            selectinload(Scenario.investments),
            selectinload(Scenario.event_series),
            selectinload(Scenario.spending_strategies),
            selectinload(Scenario.expense_withdrawal_strategies),
            selectinload(Scenario.rmd_strategies),
            selectinload(Scenario.roth_conversion_strategies),
            selectinload(Scenario.roth_optimizer_settings)
        ).filter(Scenario.id == scenario_id)
        
        if user_id:
            query = query.filter(Scenario.user_id == user_id)
            
        return query.first()

    def get_user_scenarios(self, user_id: str, status: Optional[StatusEnum] = None) -> List[Scenario]:
        """Get all scenarios for a user, optionally filtered by status."""
        query = self.db.query(Scenario).filter(Scenario.user_id == user_id)
        
        if status:
            query = query.filter(Scenario.status == status)
            
        return query.order_by(Scenario.updated_at.desc()).all()

    def get_shared_scenarios(self, user_id: str) -> List[Scenario]:
        """Get scenarios shared with a user."""
        return (
            self.db.query(Scenario)
            .join(ScenarioSharing)
            .filter(ScenarioSharing.shared_with_user_id == user_id)
            .options(
                selectinload(Scenario.sharing)
            )
            .order_by(Scenario.updated_at.desc())
            .all()
        )

    def update(self, scenario_id: uuid.UUID, scenario_data: ScenarioUpdate, user_id: str) -> Optional[Scenario]:
        """Update a scenario."""
        scenario = self.get_by_id(scenario_id, user_id)
        if not scenario:
            return None

        # Update fields that are provided
        update_data = scenario_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scenario, field, value)

        scenario.updated_at = func.now()
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def mark_complete(self, scenario_id: uuid.UUID, user_id: str) -> Optional[Scenario]:
        """Mark a scenario as complete."""
        scenario = self.get_by_id(scenario_id, user_id)
        if not scenario:
            return None

        scenario.status = StatusEnum.complete
        scenario.completed_at = func.now()
        scenario.updated_at = func.now()

        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def publish(self, scenario_id: uuid.UUID, user_id: str) -> Optional[Scenario]:
        """Publish a scenario (make it shareable)."""
        scenario = self.get_by_id(scenario_id, user_id)
        if not scenario or scenario.status != StatusEnum.complete:
            return None

        scenario.status = StatusEnum.published
        scenario.sharing_enabled = True
        scenario.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def delete(self, scenario_id: uuid.UUID, user_id: str) -> bool:
        """Delete a scenario."""
        scenario = self.get_by_id(scenario_id, user_id)
        if not scenario:
            return False

        self.db.delete(scenario)
        self.db.commit()
        return True

    def share_scenario(
        self, 
        scenario_id: uuid.UUID, 
        owner_user_id: str, 
        shared_with_user_id: str, 
        permission_level: PermissionLevelEnum
    ) -> Optional[ScenarioSharing]:
        """Share a scenario with another user."""
        scenario = self.get_by_id(scenario_id, owner_user_id)
        if not scenario or not scenario.sharing_enabled:
            return None

        # Check if sharing already exists
        existing_share = (
            self.db.query(ScenarioSharing)
            .filter(
                and_(
                    ScenarioSharing.scenario_id == scenario_id,
                    ScenarioSharing.shared_with_user_id == shared_with_user_id
                )
            )
            .first()
        )

        if existing_share:
            existing_share.permission_level = permission_level
            self.db.commit()
            return existing_share

        sharing = ScenarioSharing(
            scenario_id=scenario_id,
            shared_with_user_id=shared_with_user_id,
            permission_level=permission_level
        )
        
        self.db.add(sharing)
        self.db.commit()
        self.db.refresh(sharing)
        return sharing

    def unshare_scenario(
        self, 
        scenario_id: uuid.UUID, 
        owner_user_id: str, 
        shared_with_user_id: str
    ) -> bool:
        """Remove sharing for a scenario."""
        scenario = self.get_by_id(scenario_id, owner_user_id)
        if not scenario:
            return False

        sharing = (
            self.db.query(ScenarioSharing)
            .filter(
                and_(
                    ScenarioSharing.scenario_id == scenario_id,
                    ScenarioSharing.shared_with_user_id == shared_with_user_id
                )
            )
            .first()
        )

        if sharing:
            self.db.delete(sharing)
            self.db.commit()
            return True
        
        return False

    def has_permission(
        self, 
        scenario_id: uuid.UUID, 
        user_id: str, 
        required_permission: PermissionLevelEnum = PermissionLevelEnum.read
    ) -> bool:
        """Check if user has permission to access scenario."""
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return False

        # Owner has full permissions
        if scenario.user_id == user_id:
            return True

        # Check shared permissions
        sharing = (
            self.db.query(ScenarioSharing)
            .filter(
                and_(
                    ScenarioSharing.scenario_id == scenario_id,
                    ScenarioSharing.shared_with_user_id == user_id
                )
            )
            .first()
        )

        if not sharing:
            return False

        # If write permission is required, check if user has write access
        if required_permission == PermissionLevelEnum.write:
            return sharing.permission_level == PermissionLevelEnum.write

        # Read permission is sufficient
        return True