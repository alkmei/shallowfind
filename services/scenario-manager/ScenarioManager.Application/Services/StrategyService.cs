using Microsoft.EntityFrameworkCore;
using ScenarioManager.Application.DTOs.Strategies;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Infrastructure.Data;

namespace ScenarioManager.Application.Services;

public class StrategyService : IStrategyService
{
    private readonly ScenarioDbContext _context;

    public StrategyService(ScenarioDbContext context)
    {
        _context = context;
    }

    public async Task<StrategyResponse> CreateStrategyAsync(CreateStrategyRequest request, string userId)
    {
        var strategy = new Strategy
        {
            Name = request.Name,
            Description = request.Description,
            StrategyType = request.StrategyType,
            IsActive = request.IsActive,
            Ordering = request.Ordering,
            ScenarioId = request.ScenarioId
        };

        _context.Strategies.Add(strategy);
        await _context.SaveChangesAsync();

        return MapToResponse(strategy);
    }

    public async Task<StrategyResponse?> GetStrategyByIdAsync(string id, string userId)
    {
        var strategy = await _context.Strategies
            .Include(s => s.Scenario)
            .FirstOrDefaultAsync(s => s.Id == id && s.Scenario.OwnerId == userId);

        return strategy == null ? null : MapToResponse(strategy);
    }

    public async Task<IEnumerable<StrategyResponse>> GetStrategiesByScenarioAsync(string scenarioId, string userId)
    {
        var strategies = await _context.Strategies
            .Include(s => s.Scenario)
            .Where(s => s.ScenarioId == scenarioId && s.Scenario.OwnerId == userId)
            .OrderBy(s => s.Name)
            .ToListAsync();

        return strategies.Select(MapToResponse);
    }

    public async Task<StrategyResponse?> UpdateStrategyAsync(string id, CreateStrategyRequest request, string userId)
    {
        var strategy = await _context.Strategies
            .Include(s => s.Scenario)
            .FirstOrDefaultAsync(s => s.Id == id && s.Scenario.OwnerId == userId);

        if (strategy == null)
            return null;

        strategy.Name = request.Name;
        strategy.Description = request.Description;
        strategy.StrategyType = request.StrategyType;
        strategy.IsActive = request.IsActive;
        strategy.Ordering = request.Ordering;

        await _context.SaveChangesAsync();
        return MapToResponse(strategy);
    }

    public async Task<bool> DeleteStrategyAsync(string id, string userId)
    {
        var strategy = await _context.Strategies
            .Include(s => s.Scenario)
            .FirstOrDefaultAsync(s => s.Id == id && s.Scenario.OwnerId == userId);

        if (strategy == null)
            return false;

        _context.Strategies.Remove(strategy);
        await _context.SaveChangesAsync();

        return true;
    }

    private static StrategyResponse MapToResponse(Strategy strategy)
    {
        return new StrategyResponse
        {
            ScenarioId = strategy.ScenarioId,
            Name = strategy.Name,
            Description = strategy.Description,
            StrategyType = strategy.StrategyType,
            IsActive = strategy.IsActive,
            Ordering = strategy.Ordering,
            Id = strategy.Id
        };
    }
}