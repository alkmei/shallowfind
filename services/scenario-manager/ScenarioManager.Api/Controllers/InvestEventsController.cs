using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs.EventSeries;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/invest-events")]
public class InvestEventsController : ControllerBase
{
    private readonly IEventSeriesService _eventSeriesService;

    public InvestEventsController(IEventSeriesService eventSeriesService)
    {
        _eventSeriesService = eventSeriesService;
    }

    [HttpPost]
    public async Task<ActionResult<EventSeriesResponse>> CreateInvestEvent(
        string scenarioId,
        [FromBody] CreateInvestEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var investEvent = await _eventSeriesService.CreateInvestEventAsync(scenarioId, request, userId);
            return CreatedAtAction(nameof(GetInvestEvent),
                new { scenarioId, id = investEvent.Id }, investEvent);
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
            return StatusCode(500, $"An error occurred while creating the invest event: {ex.Message}");
        }
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> GetInvestEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investEvent = await _eventSeriesService.GetEventSeriesByIdAsync(id, userId);

        if (investEvent == null || investEvent.ScenarioId != scenarioId ||
            investEvent.EventType != EventSeriesType.Invest)
            return NotFound($"Invest event with ID {id} not found in scenario {scenarioId}");

        return Ok(investEvent);
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<EventSeriesResponse>>> GetInvestEvents(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investEvents =
            await _eventSeriesService.GetEventSeriesByTypeAsync(scenarioId, EventSeriesType.Invest, userId);
        return Ok(investEvents);
    }

    [HttpPut("{id}")]
    public async Task<ActionResult<EventSeriesResponse>> UpdateInvestEvent(
        string scenarioId,
        string id,
        [FromBody] CreateInvestEventRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var investEvent = await _eventSeriesService.UpdateInvestEventAsync(id, request, userId);

            if (investEvent == null || investEvent.ScenarioId != scenarioId)
                return NotFound($"Invest event with ID {id} not found in scenario {scenarioId}");

            return Ok(investEvent);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while updating the invest event: {ex.Message}");
        }
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteInvestEvent(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var success = await _eventSeriesService.DeleteEventSeriesAsync(id, userId);

            if (!success)
                return NotFound($"Invest event with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the invest event: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}