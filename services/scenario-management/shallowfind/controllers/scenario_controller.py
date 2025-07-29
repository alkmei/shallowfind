# controllers/scenario_controller.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from http import HTTPStatus
from sqlalchemy.orm import Session
import uuid

from ..config.database import get_db
from ..services.scenario_service import ScenarioService
from ..schemas.scenario import (
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioListResponse,
    ScenarioValidationResponse,
    ScenarioSharingCreate
)
from ..models.base import StatusEnum
from ..exceptions import (
    ScenarioNotFoundError,
    PermissionDeniedError,
    InvalidScenarioStateError,
    ValidationError
)
from ..responses import (
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse
)


def get_current_user():
    # Placeholder for user authentication logic
    # In a real application, this would extract the user from the request context
    return "current_user_id"

router = APIRouter(prefix="/scenarios")


@router.post("/draft", response_model=SuccessResponse[ScenarioResponse])
async def create_draft_scenario(
    name: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new draft scenario with default values."""
    try:
        service = ScenarioService(db)
        scenario = service.create_draft_scenario(current_user, name)
        
        return SuccessResponse(
            data=scenario,
            message="Draft scenario created successfully"
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to create draft scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.get("/{scenario_id}", response_model=SuccessResponse[ScenarioResponse])
async def get_scenario(
    scenario_id: uuid.UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a scenario by ID."""
    try:
        service = ScenarioService(db)
        scenario = service.get_scenario(scenario_id, current_user)
        
        return SuccessResponse(
            data=scenario,
            message="Scenario retrieved successfully"
        )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except PermissionDeniedError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.FORBIDDEN
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to retrieve scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.get("/", response_model=SuccessResponse[List[ScenarioListResponse]])
async def get_user_scenarios(
    status: Optional[StatusEnum] = Query(None, description="Filter by scenario status"),
    include_shared: bool = Query(False, description="Include scenarios shared with user"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scenarios for the current user."""
    try:
        service = ScenarioService(db)
        
        # Get user's own scenarios
        scenarios = service.get_user_scenarios(current_user, status)
        
        # Optionally include shared scenarios
        if include_shared:
            shared_scenarios = service.get_shared_scenarios(current_user)
            scenarios.extend(shared_scenarios)
        
        return SuccessResponse(
            data=scenarios,
            message=f"Retrieved {len(scenarios)} scenarios"
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to retrieve scenarios",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.put("/{scenario_id}", response_model=SuccessResponse[ScenarioResponse])
async def update_scenario(
    scenario_id: uuid.UUID,
    scenario_data: ScenarioUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a draft scenario."""
    try:
        service = ScenarioService(db)
        scenario = service.update_scenario(scenario_id, scenario_data, current_user)
        
        return SuccessResponse(
            data=scenario,
            message="Scenario updated successfully"
        )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except PermissionDeniedError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.FORBIDDEN
        )
    except InvalidScenarioStateError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to update scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.post("/{scenario_id}/validate", response_model=SuccessResponse[ScenarioValidationResponse])
async def validate_scenario(
    scenario_id: uuid.UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate a scenario for completion."""
    try:
        service = ScenarioService(db)
        validation_result = service.validate_scenario(scenario_id, current_user)
        
        return SuccessResponse(
            data=validation_result,
            message="Scenario validation completed"
        )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to validate scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.post("/{scenario_id}/complete", response_model=SuccessResponse[ScenarioResponse])
async def complete_scenario(
    scenario_id: uuid.UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a scenario as complete after validation."""
    try:
        service = ScenarioService(db)
        scenario = service.complete_scenario(scenario_id, current_user)
        
        return SuccessResponse(
            data=scenario,
            message="Scenario marked as complete successfully"
        )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except PermissionDeniedError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.FORBIDDEN
        )
    except InvalidScenarioStateError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.BAD_REQUEST
        )
    except ValidationError as e:
        return ValidationErrorResponse(
            message=e.args[0],
            validation_errors=e.validation_errors,
            status_code=HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to complete scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.post("/{scenario_id}/publish", response_model=SuccessResponse[ScenarioResponse])
async def publish_scenario(
    scenario_id: uuid.UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a completed scenario to enable sharing."""
    try:
        service = ScenarioService(db)
        scenario = service.publish_scenario(scenario_id, current_user)
        
        return SuccessResponse(
            data=scenario,
            message="Scenario published successfully and is now shareable"
        )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except InvalidScenarioStateError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to publish scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.delete("/{scenario_id}", response_model=SuccessResponse[dict])
async def delete_scenario(
    scenario_id: uuid.UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scenario."""
    try:
        service = ScenarioService(db)
        success = service.delete_scenario(scenario_id, current_user)
        
        if success:
            return SuccessResponse(
                data={"deleted": True},
                message="Scenario deleted successfully"
            )
        else:
            return ErrorResponse(
                message="Failed to delete scenario",
                status_code=HTTPStatus.BAD_REQUEST
            )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to delete scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.post("/{scenario_id}/share", response_model=SuccessResponse[dict])
async def share_scenario(
    scenario_id: uuid.UUID,
    sharing_data: ScenarioSharingCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share a scenario with another user."""
    try:
        service = ScenarioService(db)
        success = service.share_scenario(scenario_id, sharing_data, current_user)
        
        if success:
            return SuccessResponse(
                data={"shared": True},
                message="Scenario shared successfully"
            )
        else:
            return ErrorResponse(
                message="Failed to share scenario",
                status_code=HTTPStatus.BAD_REQUEST
            )
    except ScenarioNotFoundError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.NOT_FOUND
        )
    except InvalidScenarioStateError as e:
        return ErrorResponse(
            message=str(e),
            status_code=HTTPStatus.BAD_REQUEST
        )
    except Exception as e:
        return ErrorResponse(
            message="Failed to share scenario",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@router.delete("/{scenario_id}/share/{shared_with_user_id}", response_model=SuccessResponse[dict])
async def unshare_scenario(
    scenario_id: uuid.UUID,
    shared_with_user_id: uuid.UUID,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove sharing for a scenario."""
    try:
        service = ScenarioService(db)
        success = service.unshare_scenario(scenario_id, shared_with_user_id, current_user)
        
        if success:
            return SuccessResponse(
                data={"unshared": True},
                message="Scenario sharing removed successfully"
            )
        else:
            return ErrorResponse(
                message="Failed to remove scenario sharing",
                status_code=HTTPStatus.BAD_REQUEST
            )
    except Exception as e:
        return ErrorResponse(
            message="Failed to remove scenario sharing",
            error=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )