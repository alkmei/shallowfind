using Microsoft.EntityFrameworkCore;
using ScenarioManager.Application.DTOs.InvestmentTypes;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Infrastructure.Data;

namespace ScenarioManager.Application.Services;

public class InvestmentTypeService : IInvestmentTypeService
{
    private readonly ScenarioDbContext _context;

    public InvestmentTypeService(ScenarioDbContext context)
    {
        _context = context;
    }

    public async Task<InvestmentTypeResponse> CreateInvestmentTypeAsync(string scenarioId,
        CreateInvestmentTypeRequest request, string userId)
    {
        // Verify the scenario exists and belongs to the user
        var scenario = await _context.Scenarios
            .FirstOrDefaultAsync(s => s.Id == scenarioId && s.OwnerId == userId);

        if (scenario == null)
            throw new UnauthorizedAccessException("Scenario not found or access denied");

        var investmentType = new InvestmentType
        {
            ScenarioId = scenarioId,
            Name = request.Name,
            Description = request.Description,
            ExpectedAnnualReturn = request.ExpectedAnnualReturn,
            ExpenseRatio = request.ExpenseRatio,
            ExpectedAnnualIncome = request.ExpectedAnnualIncome,
            Taxability = request.Taxability,
            IsCash = request.IsCash
        };

        _context.InvestmentTypes.Add(investmentType);
        await _context.SaveChangesAsync();

        return MapToResponse(investmentType);
    }

    public async Task<InvestmentTypeResponse?> GetInvestmentTypeByIdAsync(string id, string userId)
    {
        var investmentType = await _context.InvestmentTypes
            .Include(it => it.Scenario)
            .FirstOrDefaultAsync(it => it.Id == id && it.Scenario.OwnerId == userId);

        return investmentType != null ? MapToResponse(investmentType) : null;
    }

    public async Task<IEnumerable<InvestmentTypeResponse>> GetInvestmentTypesByScenarioAsync(string scenarioId,
        string userId)
    {
        var investmentTypes = await _context.InvestmentTypes
            .Include(it => it.Scenario)
            .Where(it => it.ScenarioId == scenarioId && it.Scenario.OwnerId == userId)
            .OrderBy(it => it.Name)
            .ToListAsync();

        return investmentTypes.Select(MapToResponse);
    }

    public async Task<InvestmentTypeResponse?> UpdateInvestmentTypeAsync(string id, CreateInvestmentTypeRequest request,
        string userId)
    {
        var investmentType = await _context.InvestmentTypes
            .Include(it => it.Scenario)
            .FirstOrDefaultAsync(it => it.Id == id && it.Scenario.OwnerId == userId);

        if (investmentType == null)
            return null;

        investmentType.Name = request.Name;
        investmentType.Description = request.Description;
        investmentType.ExpectedAnnualReturn = request.ExpectedAnnualReturn;
        investmentType.ExpenseRatio = request.ExpenseRatio;
        investmentType.ExpectedAnnualIncome = request.ExpectedAnnualIncome;
        investmentType.Taxability = request.Taxability;
        investmentType.IsCash = request.IsCash;
        investmentType.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        return MapToResponse(investmentType);
    }

    public async Task<bool> DeleteInvestmentTypeAsync(string id, string userId)
    {
        var investmentType = await _context.InvestmentTypes
            .Include(it => it.Scenario)
            .Include(it => it.Investments)
            .FirstOrDefaultAsync(it => it.Id == id && it.Scenario.OwnerId == userId);

        if (investmentType == null)
            return false;

        // Check if there are any investments using this investment type
        if (investmentType.Investments.Count != 0)
            throw new InvalidOperationException("Cannot delete investment type that is being used by investments");

        _context.InvestmentTypes.Remove(investmentType);
        await _context.SaveChangesAsync();

        return true;
    }

    private static InvestmentTypeResponse MapToResponse(InvestmentType investmentType)
    {
        return new InvestmentTypeResponse
        {
            Id = investmentType.Id,
            ScenarioId = investmentType.ScenarioId,
            Name = investmentType.Name,
            Description = investmentType.Description,
            ExpectedAnnualReturn = investmentType.ExpectedAnnualReturn,
            ExpenseRatio = investmentType.ExpenseRatio,
            ExpectedAnnualIncome = investmentType.ExpectedAnnualIncome,
            Taxability = investmentType.Taxability,
            IsCash = investmentType.IsCash,
            CreatedAt = investmentType.CreatedAt,
            UpdatedAt = investmentType.UpdatedAt
        };
    }
}