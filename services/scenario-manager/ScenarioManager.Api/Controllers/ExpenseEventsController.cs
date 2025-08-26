using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs.EventSeries;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/expense-events")]
public class ExpenseEventsController : ControllerBase
{
    private readonly IEventSeriesService _eventSeriesService;

    public ExpenseEventsController(IEventSeriesService eventSeriesService)
    {
        _eventSeriesService = eventSeriesService;
    }

    /// <summary>
    ///     Create a new expense event for a scenario
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<EventSeriesResponse>> CreateExpenseEvent(
        string scenarioId,
        [FromBody] CreateExpenseEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var expenseEvent = await _eventSeriesService.CreateExpenseEventAsync(scenarioId, request, userId);
            return CreatedAtAction(nameof(GetExpenseEvent),
                new { scenarioId, id = expenseEvent.Id }, expenseEvent);
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
            return StatusCode(500, $"An error occurred while creating the expense event: {ex.Message}");
        }
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> GetExpenseEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var expenseEvent = await _eventSeriesService.GetEventSeriesByIdAsync(id, userId);

        if (expenseEvent == null || expenseEvent.ScenarioId != scenarioId ||
            expenseEvent.EventType != EventSeriesType.Expense)
            return NotFound($"Expense event with ID {id} not found in scenario {scenarioId}");

        return Ok(expenseEvent);
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<EventSeriesResponse>>> GetExpenseEvents(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var expenseEvents =
            await _eventSeriesService.GetEventSeriesByTypeAsync(scenarioId, EventSeriesType.Expense, userId);
        return Ok(expenseEvents);
    }

    [HttpPut("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> UpdateExpenseEvent(
        string scenarioId,
        string id,
        [FromBody] CreateExpenseEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var expenseEvent = await _eventSeriesService.UpdateExpenseEventAsync(id, request, userId);

            if (expenseEvent == null || expenseEvent.ScenarioId != scenarioId)
                return NotFound($"Expense event with ID {id} not found in scenario {scenarioId}");

            return Ok(expenseEvent);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while updating the expense event: {ex.Message}");
        }
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteExpenseEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var success = await _eventSeriesService.DeleteEventSeriesAsync(id, userId);

            if (!success)
                return NotFound($"Expense event with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the expense event: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}