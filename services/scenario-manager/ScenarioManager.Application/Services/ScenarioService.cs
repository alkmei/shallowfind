using Microsoft.EntityFrameworkCore;
using ScenarioManager.Application.DTOs;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Domain.Enums;
using ScenarioManager.Infrastructure.Data;

namespace ScenarioManager.Application.Services;

public class ScenarioService : IScenarioService
{
    private readonly ScenarioDbContext _context;

    public ScenarioService(ScenarioDbContext context)
    {
        _context = context;
    }

    public async Task<ScenarioResponse> CreateDraftScenarioAsync(CreateScenarioRequest request, string ownerId)
    {
        var scenario = new Scenario
        {
            Name = request.Name,
            OwnerId = ownerId,
            ScenarioType = request.ScenarioType,
            Status = ScenarioStatus.Draft,
            FinancialGoal = 0m,
            AnnualRetirementContributionLimit = 0m,
            RothOptimizerEnabled = false,
            ExportCount = 0
        };

        _context.Scenarios.Add(scenario);
        await _context.SaveChangesAsync();

        return MapToResponse(scenario);
    }

    public async Task<ScenarioResponse?> GetScenarioByIdAsync(string id, string userId)
    {
        var scenario = await _context.Scenarios
            .FirstOrDefaultAsync(s => s.Id == id && s.OwnerId == userId);

        return scenario != null ? MapToResponse(scenario) : null;
    }

    public async Task<IEnumerable<ScenarioResponse>> GetUserScenariosAsync(string userId)
    {
        var scenarios = await _context.Scenarios
            .Where(s => s.OwnerId == userId)
            .OrderByDescending(s => s.UpdatedAt)
            .ToListAsync();

        return scenarios.Select(MapToResponse);
    }

    public async Task<ScenarioResponse?> UpdateScenarioAsync(string id, CreateScenarioRequest request, string userId)
    {
        var scenario = await _context.Scenarios
            .FirstOrDefaultAsync(s => s.Id == id && s.OwnerId == userId);

        if (scenario == null)
            return null;

        scenario.Name = request.Name;
        scenario.ScenarioType = request.ScenarioType;
        scenario.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        return MapToResponse(scenario);
    }

    public async Task<bool> DeleteScenarioAsync(string id, string userId)
    {
        var scenario = await _context.Scenarios
            .FirstOrDefaultAsync(s => s.Id == id && s.OwnerId == userId);

        if (scenario == null)
            return false;

        _context.Scenarios.Remove(scenario);
        await _context.SaveChangesAsync();

        return true;
    }

    private static ScenarioResponse MapToResponse(Scenario scenario)
    {
        return new ScenarioResponse
        {
            Id = scenario.Id,
            Name = scenario.Name,
            OwnerId = scenario.OwnerId,
            ScenarioType = scenario.ScenarioType,
            Status = scenario.Status,
            CreatedAt = scenario.CreatedAt,
            UpdatedAt = scenario.UpdatedAt,
            UserBirthYear = scenario.UserBirthYear,
            SpouseBirthYear = scenario.SpouseBirthYear,
            FinancialGoal = scenario.FinancialGoal,
            StateOfResidence = scenario.StateOfResidence,
            AnnualRetirementContributionLimit = scenario.AnnualRetirementContributionLimit,
            RothOptimizerEnabled = scenario.RothOptimizerEnabled,
            RothOptimizerStartYear = scenario.RothOptimizerStartYear,
            RothOptimizerEndYear = scenario.RothOptimizerEndYear,
            ImportSource = scenario.ImportSource,
            ExportCount = scenario.ExportCount,
            LastSimulationRun = scenario.LastSimulationRun
        };
    }
}