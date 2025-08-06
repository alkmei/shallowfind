using Microsoft.EntityFrameworkCore;
using ScenarioManager.Application.DTOs.Investments;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Infrastructure.Data;

namespace ScenarioManager.Application.Services;

public class InvestmentService : IInvestmentService
{
    private readonly ScenarioDbContext _context;

    public InvestmentService(ScenarioDbContext context)
    {
        _context = context;
    }

    public async Task<InvestmentResponse> CreateInvestmentAsync(string investmentTypeId,
        CreateInvestmentRequest request,
        string userId)
    {
        var investmentType =
            await _context.InvestmentTypes.FirstOrDefaultAsync(it =>
                it.Id == investmentTypeId && it.Scenario.OwnerId == userId);

        if (investmentType == null)
            throw new UnauthorizedAccessException("Investment type not found or access denied");

        var investment = new Investment
        {
            ScenarioId = investmentType.ScenarioId,
            InvestmentTypeId = investmentTypeId,
            Name = request.Name,
            CurrentValue = request.CurrentValue,
            TaxStatus = request.TaxStatus,
            CostBasis = request.CostBasis,
            OrderIndex = request.OrderIndex
        };

        return MapToResponse(investment);
    }

    public async Task<InvestmentResponse?> GetInvestmentByIdAsync(string id, string userId)
    {
        var investment = await _context.Investments
            .Include(i => i.Scenario)
            .FirstOrDefaultAsync(i => i.Id == id && i.Scenario.OwnerId == userId);

        return investment != null ? MapToResponse(investment) : null;
    }

    public async Task<IEnumerable<InvestmentResponse>> GetInvestmentsByScenarioAsync(string scenarioId, string userId)
    {
        var investments = await _context.Investments
            .Include(i => i.Scenario)
            .Where(i => i.ScenarioId == scenarioId && i.Scenario.OwnerId == userId)
            .OrderBy(i => i.OrderIndex)
            .ToListAsync();

        return investments.Select(MapToResponse);
    }

    public async Task<InvestmentResponse?> UpdateInvestmentAsync(string id, CreateInvestmentRequest request,
        string userId)
    {
        var investment = await _context.Investments
            .Include(i => i.Scenario)
            .FirstOrDefaultAsync(i => i.Id == id && i.Scenario.OwnerId == userId);

        if (investment == null)
            return null;

        investment.Name = request.Name;
        investment.CurrentValue = request.CurrentValue;
        investment.TaxStatus = request.TaxStatus;
        investment.CostBasis = request.CostBasis;
        investment.OrderIndex = request.OrderIndex;
        investment.InvestmentTypeId = request.InvestmentTypeId;
        investment.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        return MapToResponse(investment);
    }

    public async Task<bool> DeleteInvestmentAsync(string id, string userId)
    {
        var investment = await _context.Investments
            .Include(i => i.Scenario)
            .FirstOrDefaultAsync(i => i.Id == id && i.Scenario.OwnerId == userId);

        if (investment == null)
            return false;

        _context.Investments.Remove(investment);
        await _context.SaveChangesAsync();

        return true;
    }


    private static InvestmentResponse MapToResponse(Investment investment)
    {
        return new InvestmentResponse
        {
            ScenarioId = investment.ScenarioId,
            InvestmentTypeId = investment.InvestmentTypeId,
            Name = investment.Name,
            CurrentValue = investment.CurrentValue,
            TaxStatus = investment.TaxStatus,
            CostBasis = investment.CostBasis,
            OrderIndex = investment.OrderIndex
        };
    }
}