namespace ScenarioManager.Application.DTOs.Scenarios;

public interface IScenarioService
{
    Task<ScenarioResponse> CreateDraftScenarioAsync(CreateScenarioRequest request, string ownerId);
    Task<ScenarioResponse?> GetScenarioByIdAsync(string id, string userId);
    Task<IEnumerable<ScenarioResponse>> GetUserScenariosAsync(string userId);
    Task<ScenarioResponse?> UpdateScenarioAsync(string id, CreateScenarioRequest request, string userId);
    Task<bool> DeleteScenarioAsync(string id, string userId);
}