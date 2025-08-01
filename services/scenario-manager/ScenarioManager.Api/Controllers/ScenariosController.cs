using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ScenariosController : ControllerBase
{
    private readonly IScenarioService _scenarioService;

    public ScenariosController(IScenarioService scenarioService)
    {
        _scenarioService = scenarioService;
    }

    /// <summary>
    ///     Create a new draft scenario with minimal information
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<ScenarioResponse>> CreateScenario([FromBody] CreateScenarioRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var scenario = await _scenarioService.CreateDraftScenarioAsync(request, userId);
            return CreatedAtAction(nameof(GetScenario), new { id = scenario.Id }, scenario);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while creating the scenario: {ex.Message}");
        }
    }

    /// <summary>
    ///     Get a specific scenario by ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<ScenarioResponse>> GetScenario(string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var scenario = await _scenarioService.GetScenarioByIdAsync(id, userId);

        if (scenario == null)
            return NotFound($"Scenario with ID {id} not found");

        return Ok(scenario);
    }

    /// <summary>
    ///     Get all scenarios for the current user
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<ScenarioResponse>>> GetUserScenarios()
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var scenarios = await _scenarioService.GetUserScenariosAsync(userId);
        return Ok(scenarios);
    }

    /// <summary>
    ///     Update a scenario's basic information
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<ScenarioResponse>> UpdateScenario(string id,
        [FromBody] CreateScenarioRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var scenario = await _scenarioService.UpdateScenarioAsync(id, request, userId);

        if (scenario == null)
            return NotFound($"Scenario with ID {id} not found");

        return Ok(scenario);
    }

    /// <summary>
    ///     Delete a scenario
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteScenario(string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var success = await _scenarioService.DeleteScenarioAsync(id, userId);

        if (!success)
            return NotFound($"Scenario with ID {id} not found");

        return NoContent();
    }

    private string? GetCurrentUserId()
    {
        // This assumes you're using JWT tokens with a "sub" or "nameid" claim
        // Adjust based on your authentication implementation
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}