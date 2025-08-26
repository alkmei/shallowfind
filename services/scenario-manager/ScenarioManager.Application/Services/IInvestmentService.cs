using ScenarioManager.Application.DTOs.Investments;

namespace ScenarioManager.Application.Services;

public interface IInvestmentService
{
    Task<InvestmentResponse> CreateInvestmentAsync(string investmentTypeId, CreateInvestmentRequest request,
        string userId);

    Task<InvestmentResponse?> GetInvestmentByIdAsync(string id, string userId);
    Task<IEnumerable<InvestmentResponse>> GetInvestmentsByScenarioAsync(string scenarioId, string userId);
    Task<InvestmentResponse?> UpdateInvestmentAsync(string id, CreateInvestmentRequest request, string userId);
    Task<bool> DeleteInvestmentAsync(string id, string userId);
}