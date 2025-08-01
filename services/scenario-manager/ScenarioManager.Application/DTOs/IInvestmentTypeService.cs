namespace ScenarioManager.Application.DTOs;

public interface IInvestmentTypeService
{
    Task<InvestmentTypeResponse> CreateInvestmentTypeAsync(string scenarioId, CreateInvestmentTypeRequest request,
        string userId);

    Task<InvestmentTypeResponse?> GetInvestmentTypeByIdAsync(string id, string userId);
    Task<IEnumerable<InvestmentTypeResponse>> GetInvestmentTypesByScenarioAsync(string scenarioId, string userId);

    Task<InvestmentTypeResponse?> UpdateInvestmentTypeAsync(string id, CreateInvestmentTypeRequest request,
        string userId);

    Task<bool> DeleteInvestmentTypeAsync(string id, string userId);
}