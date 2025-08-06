namespace ScenarioManager.Application.DTOs.Strategies;

public interface IStrategyService
{
    Task<StrategyResponse> CreateStrategyAsync(CreateStrategyRequest request, string userId);
    Task<StrategyResponse?> GetStrategyByIdAsync(string id, string userId);
    Task<IEnumerable<StrategyResponse>> GetStrategiesByScenarioAsync(string scenarioId, string userId);
    Task<StrategyResponse?> UpdateStrategyAsync(string id, CreateStrategyRequest request, string userId);
    Task<bool> DeleteStrategyAsync(string id, string userId);
}