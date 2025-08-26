using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs.Strategies;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/[controller]")]
public class StrategiesController : ControllerBase
{
    private readonly IStrategyService _strategyService;

    public StrategiesController(IStrategyService strategyService)
    {
        _strategyService = strategyService;
    }

    /// <summary>
    ///     Create a new strategy for a scenario
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<StrategyResponse>> CreateStrategy(
        string scenarioId,
        [FromBody] CreateStrategyRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        // Ensure the scenarioId in the route matches the one in the request body
        if (request.ScenarioId != scenarioId)
            return BadRequest("Scenario ID in request body must match the scenario ID in the route");

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var strategy = await _strategyService.CreateStrategyAsync(request, userId);
            return CreatedAtAction(nameof(GetStrategy),
                new { scenarioId, id = strategy.Id }, strategy);
        }
        catch (UnauthorizedAccessException)
        {
            return NotFound($"Scenario with ID {scenarioId} not found");
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while creating the strategy: {ex.Message}");
        }
    }

    /// <summary>
    ///     Get a specific strategy by ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<StrategyResponse>> GetStrategy(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var strategy = await _strategyService.GetStrategyByIdAsync(id, userId);

        if (strategy == null || strategy.ScenarioId != scenarioId)
            return NotFound($"Strategy with ID {id} not found in scenario {scenarioId}");

        return Ok(strategy);
    }

    /// <summary>
    ///     Get all strategies for a specific scenario
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<StrategyResponse>>> GetStrategies(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var strategies = await _strategyService.GetStrategiesByScenarioAsync(scenarioId, userId);
        return Ok(strategies);
    }

    /// <summary>
    ///     Update a strategy
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<StrategyResponse>> UpdateStrategy(
        string scenarioId,
        string id,
        [FromBody] CreateStrategyRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        // Ensure the scenarioId in the route matches the one in the request body
        if (request.ScenarioId != scenarioId)
            return BadRequest("Scenario ID in request body must match the scenario ID in the route");

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var strategy = await _strategyService.UpdateStrategyAsync(id, request, userId);

        if (strategy == null || strategy.ScenarioId != scenarioId)
            return NotFound($"Strategy with ID {id} not found in scenario {scenarioId}");

        return Ok(strategy);
    }

    /// <summary>
    ///     Delete a strategy
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteStrategy(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var success = await _strategyService.DeleteStrategyAsync(id, userId);

            if (!success)
                return NotFound($"Strategy with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the strategy: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}