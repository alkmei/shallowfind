using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using ScenarioManager.Application.DTOs.Investments;
using ScenarioManager.Application.Services;

namespace ScenarioManager.Api.Controllers;

[ApiController]
[Route("api/scenarios/{scenarioId}/[controller]")]
public class InvestmentsController : ControllerBase
{
    private readonly IInvestmentService _investmentService;

    public InvestmentsController(IInvestmentService investmentService)
    {
        _investmentService = investmentService;
    }

    /// <summary>
    ///     Create a new investment for a scenario
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<InvestmentResponse>> CreateInvestment(
        string scenarioId,
        [FromBody] CreateInvestmentRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var investment = await _investmentService.CreateInvestmentAsync(request.InvestmentTypeId, request, userId);

            // Verify the investment belongs to the correct scenario
            if (investment.ScenarioId != scenarioId)
                return BadRequest("Investment type does not belong to the specified scenario");

            return CreatedAtAction(nameof(GetInvestment),
                new { scenarioId, id = investment.Id }, investment);
        }
        catch (UnauthorizedAccessException)
        {
            return NotFound($"Investment type with ID {request.InvestmentTypeId} not found or access denied");
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while creating the investment: {ex.Message}");
        }
    }

    /// <summary>
    ///     Get a specific investment by ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<InvestmentResponse>> GetInvestment(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investment = await _investmentService.GetInvestmentByIdAsync(id, userId);

        if (investment == null || investment.ScenarioId != scenarioId)
            return NotFound($"Investment with ID {id} not found in scenario {scenarioId}");

        return Ok(investment);
    }

    /// <summary>
    ///     Get all investments for a specific scenario
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<InvestmentResponse>>> GetInvestments(string scenarioId)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        var investments = await _investmentService.GetInvestmentsByScenarioAsync(scenarioId, userId);
        return Ok(investments);
    }

    /// <summary>
    ///     Update an investment
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<InvestmentResponse>> UpdateInvestment(
        string scenarioId,
        string id,
        [FromBody] CreateInvestmentRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            var investment = await _investmentService.UpdateInvestmentAsync(id, request, userId);

            if (investment == null || investment.ScenarioId != scenarioId)
                return NotFound($"Investment with ID {id} not found in scenario {scenarioId}");

            return Ok(investment);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while updating the investment: {ex.Message}");
        }
    }

    /// <summary>
    ///     Partially update an investment
    /// </summary>
    [HttpPatch("{id}")]
    public async Task<ActionResult<InvestmentResponse>> PatchInvestment(
        string scenarioId,
        string id,
        [FromBody] UpdateInvestmentRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            // First get the current investment to merge with partial update
            var currentInvestment = await _investmentService.GetInvestmentByIdAsync(id, userId);

            if (currentInvestment == null || currentInvestment.ScenarioId != scenarioId)
                return NotFound($"Investment with ID {id} not found in scenario {scenarioId}");

            // Create a full update request by merging current values with patch values
            var fullUpdateRequest = new CreateInvestmentRequest
            {
                InvestmentTypeId = currentInvestment.InvestmentTypeId,
                Name = request.Name ?? currentInvestment.Name,
                CurrentValue = request.CurrentValue ?? currentInvestment.CurrentValue,
                TaxStatus = request.TaxStatus ?? currentInvestment.TaxStatus,
                CostBasis = request.CostBasis ?? currentInvestment.CostBasis,
                OrderIndex = request.OrderIndex ?? currentInvestment.OrderIndex
            };

            var updatedInvestment = await _investmentService.UpdateInvestmentAsync(id, fullUpdateRequest, userId);

            if (updatedInvestment == null)
                return NotFound($"Investment with ID {id} not found");

            return Ok(updatedInvestment);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while updating the investment: {ex.Message}");
        }
    }

    /// <summary>
    ///     Delete an investment
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteInvestment(string scenarioId, string id)
    {
        var userId = GetCurrentUserId();
        if (string.IsNullOrEmpty(userId))
            return Unauthorized("User ID not found in token");

        try
        {
            // First verify the investment belongs to the correct scenario
            var investment = await _investmentService.GetInvestmentByIdAsync(id, userId);

            if (investment == null || investment.ScenarioId != scenarioId)
                return NotFound($"Investment with ID {id} not found in scenario {scenarioId}");

            var success = await _investmentService.DeleteInvestmentAsync(id, userId);

            if (!success)
                return NotFound($"Investment with ID {id} not found");

            return NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"An error occurred while deleting the investment: {ex.Message}");
        }
    }

    private string? GetCurrentUserId()
    {
        return User.FindFirst(ClaimTypes.NameIdentifier)?.Value
               ?? User.FindFirst("sub")?.Value
               ?? User.FindFirst("user_id")?.Value;
    }
}