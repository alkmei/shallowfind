using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.EventSeries;

public interface IEventSeriesService
{
    // Income Events
    Task<EventSeriesResponse>
        CreateIncomeEventAsync(string scenarioId, CreateIncomeEventRequest request, string userId);

    Task<EventSeriesResponse?> UpdateIncomeEventAsync(string id, CreateIncomeEventRequest request, string userId);

    // Expense Events
    Task<EventSeriesResponse> CreateExpenseEventAsync(string scenarioId, CreateExpenseEventRequest request,
        string userId);

    Task<EventSeriesResponse?> UpdateExpenseEventAsync(string id, CreateExpenseEventRequest request, string userId);

    // Invest Events
    Task<EventSeriesResponse>
        CreateInvestEventAsync(string scenarioId, CreateInvestEventRequest request, string userId);

    Task<EventSeriesResponse?> UpdateInvestEventAsync(string id, CreateInvestEventRequest request, string userId);

    // Rebalance Events
    Task<EventSeriesResponse> CreateRebalanceEventAsync(string scenarioId, CreateRebalanceEventRequest request,
        string userId);

    Task<EventSeriesResponse?> UpdateRebalanceEventAsync(string id, CreateRebalanceEventRequest request, string userId);

    // Common operations
    Task<EventSeriesResponse?> GetEventSeriesByIdAsync(string id, string userId);
    Task<IEnumerable<EventSeriesResponse>> GetEventSeriesByScenarioAsync(string scenarioId, string userId);

    Task<IEnumerable<EventSeriesResponse>> GetEventSeriesByTypeAsync(string scenarioId, EventSeriesType eventType,
        string userId);

    Task<bool> DeleteEventSeriesAsync(string id, string userId);
}