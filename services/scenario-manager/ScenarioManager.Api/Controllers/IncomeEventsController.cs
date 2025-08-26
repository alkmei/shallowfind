using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs.EventSeries;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/income-events")]
public class IncomeEventsController : ControllerBase
{
    private readonly IEventSeriesService _eventSeriesService;

    public IncomeEventsController(IEventSeriesService eventSeriesService)
    {
        _eventSeriesService = eventSeriesService;
    }

    /// <summary>
    ///     Create a new income event for a scenario
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<EventSeriesResponse>> CreateIncomeEvent(
        string scenarioId,
        [FromBody] CreateIncomeEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var incomeEvent = await _eventSeriesService.CreateIncomeEventAsync(scenarioId, request, userId);
            return CreatedAtAction(nameof(GetIncomeEvent),
                new { scenarioId, id = incomeEvent.Id }, incomeEvent);
        }
        catch (UnauthorizedAccessException)
        {
            return NotFound($"Scenario with ID {scenarioId} not found");
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while creating the income event: {ex.Message}");
        }
    }

    /// <summary>
    ///     Get a specific income event by ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> GetIncomeEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var incomeEvent = await _eventSeriesService.GetEventSeriesByIdAsync(id, userId);

        if (incomeEvent == null || incomeEvent.ScenarioId != scenarioId ||
            incomeEvent.EventType != EventSeriesType.Income)
            return NotFound($"Income event with ID {id} not found in scenario {scenarioId}");

        return Ok(incomeEvent);
    }

    /// <summary>
    ///     Get all income events for a specific scenario
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<EventSeriesResponse>>> GetIncomeEvents(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var incomeEvents =
            await _eventSeriesService.GetEventSeriesByTypeAsync(scenarioId, EventSeriesType.Income, userId);
        return Ok(incomeEvents);
    }

    /// <summary>
    ///     Update an income event
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> UpdateIncomeEvent(
        string scenarioId,
        string id,
        [FromBody] CreateIncomeEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var incomeEvent = await _eventSeriesService.UpdateIncomeEventAsync(id, request, userId);

            if (incomeEvent == null || incomeEvent.ScenarioId != scenarioId)
                return NotFound($"Income event with ID {id} not found in scenario {scenarioId}");

            return Ok(incomeEvent);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while updating the income event: {ex.Message}");
        }
    }

    /// <summary>
    ///     Delete an income event
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteIncomeEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var success = await _eventSeriesService.DeleteEventSeriesAsync(id, userId);

            if (!success)
                return NotFound($"Income event with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the income event: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}