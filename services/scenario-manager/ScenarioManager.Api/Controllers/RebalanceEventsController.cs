using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs.EventSeries;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/rebalance-events")]
public class RebalanceEventsController : ControllerBase
{
    private readonly IEventSeriesService _eventSeriesService;

    public RebalanceEventsController(IEventSeriesService eventSeriesService)
    {
        _eventSeriesService = eventSeriesService;
    }

    [HttpPost]
    public async Task<ActionResult<EventSeriesResponse>> CreateRebalanceEvent(
        string scenarioId,
        [FromBody] CreateRebalanceEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var rebalanceEvent = await _eventSeriesService.CreateRebalanceEventAsync(scenarioId, request, userId);
            return CreatedAtAction(nameof(GetRebalanceEvent),
                new { scenarioId, id = rebalanceEvent.Id }, rebalanceEvent);
        }
        catch (UnauthorizedAccessException)
        {
            return NotFound($"Scenario with ID {scenarioId} not found");
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while creating the rebalance event: {ex.Message}");
        }
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> GetRebalanceEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var rebalanceEvent = await _eventSeriesService.GetEventSeriesByIdAsync(id, userId);

        if (rebalanceEvent == null || rebalanceEvent.ScenarioId != scenarioId ||
            rebalanceEvent.EventType != EventSeriesType.Rebalance)
            return NotFound($"Rebalance event with ID {id} not found in scenario {scenarioId}");

        return Ok(rebalanceEvent);
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<EventSeriesResponse>>> GetRebalanceEvents(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var rebalanceEvents =
            await _eventSeriesService.GetEventSeriesByTypeAsync(scenarioId, EventSeriesType.Rebalance, userId);
        return Ok(rebalanceEvents);
    }

    [HttpPut("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> UpdateRebalanceEvent(
        string scenarioId,
        string id,
        [FromBody] CreateRebalanceEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var rebalanceEvent = await _eventSeriesService.UpdateRebalanceEventAsync(id, request, userId);

            if (rebalanceEvent == null || rebalanceEvent.ScenarioId != scenarioId)
                return NotFound($"Rebalance event with ID {id} not found in scenario {scenarioId}");

            return Ok(rebalanceEvent);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while updating the rebalance event: {ex.Message}");
        }
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteRebalanceEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var success = await _eventSeriesService.DeleteEventSeriesAsync(id, userId);

            if (!success)
                return NotFound($"Rebalance event with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the rebalance event: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}