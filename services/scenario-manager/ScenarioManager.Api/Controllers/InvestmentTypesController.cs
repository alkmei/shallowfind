using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/[controller]")]
public class InvestmentTypesController : ControllerBase
{
    private readonly IInvestmentTypeService _investmentTypeService;

    public InvestmentTypesController(IInvestmentTypeService investmentTypeService)
    {
        _investmentTypeService = investmentTypeService;
    }

    /// <summary>
    ///     Create a new investment type for a scenario
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<InvestmentTypeResponse>> CreateInvestmentType(
        string scenarioId,
        [FromBody] CreateInvestmentTypeRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var investmentType = await _investmentTypeService.CreateInvestmentTypeAsync(scenarioId, request, userId);
            return CreatedAtAction(nameof(GetInvestmentType),
                new { scenarioId, id = investmentType.Id }, investmentType);
        }
        catch (UnauthorizedAccessException)
        {
            return NotFound($"Scenario with ID {scenarioId} not found");
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while creating the investment type: {ex.Message}");
        }
    }

    /// <summary>
    ///     Get a specific investment type by ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<InvestmentTypeResponse>> GetInvestmentType(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investmentType = await _investmentTypeService.GetInvestmentTypeByIdAsync(id, userId);

        if (investmentType == null || investmentType.ScenarioId != scenarioId)
            return NotFound($"Investment type with ID {id} not found in scenario {scenarioId}");

        return Ok(investmentType);
    }

    /// <summary>
    ///     Get all investment types for a specific scenario
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<InvestmentTypeResponse>>> GetInvestmentTypes(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investmentTypes = await _investmentTypeService.GetInvestmentTypesByScenarioAsync(scenarioId, userId);
        return Ok(investmentTypes);
    }

    /// <summary>
    ///     Update an investment type
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<InvestmentTypeResponse>> UpdateInvestmentType(
        string scenarioId,
        string id,
        [FromBody] CreateInvestmentTypeRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investmentType = await _investmentTypeService.UpdateInvestmentTypeAsync(id, request, userId);

        if (investmentType == null || investmentType.ScenarioId != scenarioId)
            return NotFound($"Investment type with ID {id} not found in scenario {scenarioId}");

        return Ok(investmentType);
    }

    /// <summary>
    ///     Delete an investment type
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteInvestmentType(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var success = await _investmentTypeService.DeleteInvestmentTypeAsync(id, userId);

            if (!success)
                return NotFound($"Investment type with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the investment type: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}