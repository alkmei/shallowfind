# services/scenario_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from ..repositories.scenario_repository import ScenarioRepository
from ..models.base import StatusEnum, PermissionLevelEnum, ScenarioTypeEnum
from ..schemas.scenario import (
    ScenarioCreate, 
    ScenarioUpdate, 
    ScenarioResponse, 
    ScenarioListResponse,
    ScenarioValidationError,
    ScenarioValidationResponse,
    ScenarioSharingCreate
)
from ..exceptions import (
    ScenarioNotFoundError,
    PermissionDeniedError,
    InvalidScenarioStateError,
    ValidationError
)


class ScenarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ScenarioRepository(db)

    def create_draft_scenario(self, user_id: str, name: str) -> ScenarioResponse:
        """Create a default draft scenario with minimal required data."""
        default_scenario = ScenarioCreate(
            name=name,
            description="Draft scenario",
            scenario_type=ScenarioTypeEnum.individual,
            financial_goal=0.0,
            inflation_assumption={"type": "fixed", "value": 0.03}  # Default 3% inflation
        )
        
        scenario = self.repository.create(default_scenario, user_id)
        return ScenarioResponse.from_orm(scenario)

    def get_scenario(self, scenario_id: uuid.UUID, user_id: str) -> ScenarioResponse:
        """Get a scenario by ID with permission check."""
        if not self.repository.has_permission(scenario_id, user_id):
            raise PermissionDeniedError("You don't have permission to access this scenario")
        
        scenario = self.repository.get_by_id(scenario_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        return ScenarioResponse.from_orm(scenario)

    def get_user_scenarios(self, user_id: str, status: Optional[StatusEnum] = None) -> List[ScenarioListResponse]:
        """Get all scenarios for a user."""
        scenarios = self.repository.get_user_scenarios(user_id, status)
        return [ScenarioListResponse.from_orm(scenario) for scenario in scenarios]

    def get_shared_scenarios(self, user_id: str) -> List[ScenarioListResponse]:
        """Get scenarios shared with a user."""
        scenarios = self.repository.get_shared_scenarios(user_id)
        return [ScenarioListResponse.from_orm(scenario) for scenario in scenarios]

    def update_scenario(
        self, 
        scenario_id: uuid.UUID, 
        scenario_data: ScenarioUpdate, 
        user_id: str
    ) -> ScenarioResponse:
        """Update a scenario draft."""
        if not self.repository.has_permission(scenario_id, user_id, PermissionLevelEnum.write):
            raise PermissionDeniedError("You don't have permission to modify this scenario")
        
        scenario = self.repository.get_by_id(scenario_id, user_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        if scenario.status != StatusEnum.draft:
            raise InvalidScenarioStateError("Only draft scenarios can be updated")
        
        updated_scenario = self.repository.update(scenario_id, scenario_data, user_id)
        if not updated_scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        return ScenarioResponse.from_orm(updated_scenario)

    def validate_scenario(self, scenario_id: uuid.UUID, user_id: str) -> ScenarioValidationResponse:
        """Validate a scenario for completion."""
        scenario = self.repository.get_by_id(scenario_id, user_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        errors = []
        
        # Basic required fields validation
        if not scenario.name or len(scenario.name.strip()) == 0:
            errors.append(ScenarioValidationError(field="name", message="Name is required"))
        
        if not scenario.user_birth_year:
            errors.append(ScenarioValidationError(field="user_birth_year", message="User birth year is required"))
        
        if not scenario.user_life_expectancy:
            errors.append(ScenarioValidationError(field="user_life_expectancy", message="User life expectancy is required"))
        
        # Married couple specific validations
        if scenario.scenario_type == ScenarioTypeEnum.married_couple:
            if not scenario.spouse_birth_year:
                errors.append(ScenarioValidationError(field="spouse_birth_year", message="Spouse birth year is required for married couples"))
            
            if not scenario.spouse_life_expectancy:
                errors.append(ScenarioValidationError(field="spouse_life_expectancy", message="Spouse life expectancy is required for married couples"))
        
        # Financial goal validation
        if scenario.financial_goal < 0:
            errors.append(ScenarioValidationError(field="financial_goal", message="Financial goal cannot be negative"))
        
        # Inflation assumption validation
        if not scenario.inflation_assumption:
            errors.append(ScenarioValidationError(field="inflation_assumption", message="Inflation assumption is required"))
        else:
            inflation_errors = self._validate_distribution(scenario.inflation_assumption, "inflation_assumption")
            errors.extend(inflation_errors)
        
        # Life expectancy distribution validation
        if scenario.user_life_expectancy:
            life_exp_errors = self._validate_distribution(scenario.user_life_expectancy, "user_life_expectancy")
            errors.extend(life_exp_errors)
        
        if scenario.spouse_life_expectancy:
            spouse_life_exp_errors = self._validate_distribution(scenario.spouse_life_expectancy, "spouse_life_expectancy")
            errors.extend(spouse_life_exp_errors)
        
        # Check if scenario has at least one investment
        if not scenario.investments:
            errors.append(ScenarioValidationError(field="investments", message="At least one investment is required"))
        
        # Check if scenario has at least one event series
        if not scenario.event_series:
            errors.append(ScenarioValidationError(field="event_series", message="At least one event series is required"))
        
        return ScenarioValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors
        )

    def complete_scenario(self, scenario_id: uuid.UUID, user_id: str) -> ScenarioResponse:
        """Mark a scenario as complete after validation."""
        if not self.repository.has_permission(scenario_id, user_id, PermissionLevelEnum.write):
            raise PermissionDeniedError("You don't have permission to modify this scenario")
        
        scenario = self.repository.get_by_id(scenario_id, user_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        if scenario.status != StatusEnum.draft:
            raise InvalidScenarioStateError("Only draft scenarios can be completed")
        
        # Validate scenario before completion
        validation_result = self.validate_scenario(scenario_id, user_id)
        if not validation_result.is_valid:
            raise ValidationError("Scenario validation failed", validation_result.errors)
        
        completed_scenario = self.repository.mark_complete(scenario_id, user_id)
        if not completed_scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        return ScenarioResponse.from_orm(completed_scenario)

    def publish_scenario(self, scenario_id: uuid.UUID, user_id: str) -> ScenarioResponse:
        """Publish a completed scenario to enable sharing."""
        scenario = self.repository.get_by_id(scenario_id, user_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        if scenario.status != StatusEnum.complete:
            raise InvalidScenarioStateError("Only completed scenarios can be published")
        
        published_scenario = self.repository.publish(scenario_id, user_id)
        if not published_scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        return ScenarioResponse.from_orm(published_scenario)

    def delete_scenario(self, scenario_id: uuid.UUID, user_id: str) -> bool:
        """Delete a scenario."""
        scenario = self.repository.get_by_id(scenario_id, user_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        return self.repository.delete(scenario_id, user_id)

    def share_scenario(
        self, 
        scenario_id: uuid.UUID, 
        sharing_data: ScenarioSharingCreate, 
        owner_user_id: str
    ) -> bool:
        """Share a scenario with another user."""
        scenario = self.repository.get_by_id(scenario_id, owner_user_id)
        if not scenario:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        
        if scenario.status != StatusEnum.published:
            raise InvalidScenarioStateError("Only published scenarios can be shared")
        
        sharing = self.repository.share_scenario(
            scenario_id, 
            owner_user_id, 
            sharing_data.shared_with_user_id, 
            sharing_data.permission_level
        )
        
        return sharing is not None

    def unshare_scenario(
        self, 
        scenario_id: uuid.UUID, 
        shared_with_user_id: uuid.UUID, 
        owner_user_id: str
    ) -> bool:
        """Remove sharing for a scenario."""
        return self.repository.unshare_scenario(scenario_id, owner_user_id, shared_with_user_id)

    def _validate_distribution(self, distribution: Dict[str, Any], field_name: str) -> List[ScenarioValidationError]:
        """Validate a distribution dictionary."""
        errors = []
        
        if not isinstance(distribution, dict):
            errors.append(ScenarioValidationError(field=field_name, message="Distribution must be a dictionary"))
            return errors
        
        dist_type = distribution.get("type")
        if not dist_type:
            errors.append(ScenarioValidationError(field=f"{field_name}.type", message="Distribution type is required"))
            return errors
        
        if dist_type == "fixed":
            if "value" not in distribution:
                errors.append(ScenarioValidationError(field=f"{field_name}.value", message="Fixed distribution requires a value"))
            elif not isinstance(distribution["value"], (int, float)):
                errors.append(ScenarioValidationError(field=f"{field_name}.value", message="Fixed distribution value must be a number"))
        
        elif dist_type == "normal":
            if "mean" not in distribution:
                errors.append(ScenarioValidationError(field=f"{field_name}.mean", message="Normal distribution requires a mean"))
            elif not isinstance(distribution["mean"], (int, float)):
                errors.append(ScenarioValidationError(field=f"{field_name}.mean", message="Normal distribution mean must be a number"))
            
            if "stdev" not in distribution:
                errors.append(ScenarioValidationError(field=f"{field_name}.stdev", message="Normal distribution requires a standard deviation"))
            elif not isinstance(distribution["stdev"], (int, float)) or distribution["stdev"] <= 0:
                errors.append(ScenarioValidationError(field=f"{field_name}.stdev", message="Normal distribution standard deviation must be a positive number"))
        
        elif dist_type == "uniform":
            if "lower" not in distribution:
                errors.append(ScenarioValidationError(field=f"{field_name}.lower", message="Uniform distribution requires a lower bound"))
            elif not isinstance(distribution["lower"], (int, float)):
                errors.append(ScenarioValidationError(field=f"{field_name}.lower", message="Uniform distribution lower bound must be a number"))
            
            if "upper" not in distribution:
                errors.append(ScenarioValidationError(field=f"{field_name}.upper", message="Uniform distribution requires an upper bound"))
            elif not isinstance(distribution["upper"], (int, float)):
                errors.append(ScenarioValidationError(field=f"{field_name}.upper", message="Uniform distribution upper bound must be a number"))
            
            if "lower" in distribution and "upper" in distribution and distribution["lower"] >= distribution["upper"]:
                errors.append(ScenarioValidationError(field=f"{field_name}.upper", message="Upper bound must be greater than lower bound"))
        
        else:
            errors.append(ScenarioValidationError(field=f"{field_name}.type", message="Invalid distribution type. Must be 'fixed', 'normal', or 'uniform'"))
        
        return errors