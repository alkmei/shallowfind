using Microsoft.EntityFrameworkCore;
using ScenarioManager.Application.DTOs.EventSeries;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Domain.Enums;
using ScenarioManager.Infrastructure.Data;

namespace ScenarioManager.Application.Services;

public class EventSeriesService : IEventSeriesService
{
    private readonly ScenarioDbContext _context;

    public EventSeriesService(ScenarioDbContext context)
    {
        _context = context;
    }

    public async Task<EventSeriesResponse> CreateIncomeEventAsync(string scenarioId, CreateIncomeEventRequest request,
        string userId)
    {
        await ValidateScenarioOwnership(scenarioId, userId);
        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, scenarioId, userId);
        ValidateUserPercentage(request.UserPercentage);

        var eventSeries = new EventSeries
        {
            ScenarioId = scenarioId,
            Name = request.Name,
            Description = request.Description,
            EventType = EventSeriesType.Income,
            StartYear = request.StartYear,
            Duration = request.Duration,
            ReferenceEventSeriesId = request.ReferenceEventSeriesId,
            StartTimingType = request.StartTimingType,
            IsActive = request.IsActive,
            OrderIndex = request.OrderIndex,
            InitialAmount = request.InitialAmount,
            AnnualChange = request.AnnualChange,
            InflationAdjusted = request.InflationAdjusted,
            UserPercentage = request.UserPercentage,
            IsSocialSecurity = request.IsSocialSecurity
        };

        _context.EventSeries.Add(eventSeries);
        await _context.SaveChangesAsync();

        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse> CreateExpenseEventAsync(string scenarioId, CreateExpenseEventRequest request,
        string userId)
    {
        await ValidateScenarioOwnership(scenarioId, userId);
        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, scenarioId, userId);
        ValidateUserPercentage(request.UserPercentage);

        var eventSeries = new EventSeries
        {
            ScenarioId = scenarioId,
            Name = request.Name,
            Description = request.Description,
            EventType = EventSeriesType.Expense,
            StartYear = request.StartYear,
            Duration = request.Duration,
            ReferenceEventSeriesId = request.ReferenceEventSeriesId,
            StartTimingType = request.StartTimingType,
            IsActive = request.IsActive,
            OrderIndex = request.OrderIndex,
            InitialAmount = request.InitialAmount,
            AnnualChange = request.AnnualChange,
            InflationAdjusted = request.InflationAdjusted,
            UserPercentage = request.UserPercentage,
            IsDiscretionary = request.IsDiscretionary
        };

        _context.EventSeries.Add(eventSeries);
        await _context.SaveChangesAsync();

        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse> CreateInvestEventAsync(string scenarioId, CreateInvestEventRequest request,
        string userId)
    {
        await ValidateScenarioOwnership(scenarioId, userId);
        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, scenarioId, userId);
        await ValidateAssetAllocation(request.AssetAllocation, scenarioId, userId);
        await ValidateNoOverlappingInvestEvents(scenarioId, request.StartYear, request.Duration);

        if (request.IsGlidePath)
        {
            ValidateGlidePath(request.InitialAllocation, request.FinalAllocation);
            await ValidateAssetAllocation(request.InitialAllocation!, scenarioId, userId);
            await ValidateAssetAllocation(request.FinalAllocation!, scenarioId, userId);
        }

        var eventSeries = new EventSeries
        {
            ScenarioId = scenarioId,
            Name = request.Name,
            Description = request.Description,
            EventType = EventSeriesType.Invest,
            StartYear = request.StartYear,
            Duration = request.Duration,
            ReferenceEventSeriesId = request.ReferenceEventSeriesId,
            StartTimingType = request.StartTimingType,
            IsActive = request.IsActive,
            OrderIndex = request.OrderIndex,
            AssetAllocation = request.AssetAllocation,
            IsGlidePath = request.IsGlidePath,
            InitialAllocation = request.InitialAllocation,
            FinalAllocation = request.FinalAllocation,
            MaximumCash = request.MaximumCash
        };

        _context.EventSeries.Add(eventSeries);
        await _context.SaveChangesAsync();

        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse> CreateRebalanceEventAsync(string scenarioId,
        CreateRebalanceEventRequest request, string userId)
    {
        await ValidateScenarioOwnership(scenarioId, userId);
        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, scenarioId, userId);
        await ValidateAssetAllocationForTaxStatus(request.AssetAllocation, scenarioId, userId, request.TargetTaxStatus);
        await ValidateNoOverlappingRebalanceEvents(scenarioId, request.TargetTaxStatus, request.StartYear,
            request.Duration);

        if (request.IsGlidePath)
        {
            ValidateGlidePath(request.InitialAllocation, request.FinalAllocation);
            await ValidateAssetAllocationForTaxStatus(request.InitialAllocation!, scenarioId, userId,
                request.TargetTaxStatus);
            await ValidateAssetAllocationForTaxStatus(request.FinalAllocation!, scenarioId, userId,
                request.TargetTaxStatus);
        }

        var eventSeries = new EventSeries
        {
            ScenarioId = scenarioId,
            Name = request.Name,
            Description = request.Description,
            EventType = EventSeriesType.Rebalance,
            StartYear = request.StartYear,
            Duration = request.Duration,
            ReferenceEventSeriesId = request.ReferenceEventSeriesId,
            StartTimingType = request.StartTimingType,
            IsActive = request.IsActive,
            OrderIndex = request.OrderIndex,
            AssetAllocation = request.AssetAllocation,
            IsGlidePath = request.IsGlidePath,
            InitialAllocation = request.InitialAllocation,
            FinalAllocation = request.FinalAllocation,
            TargetTaxStatus = request.TargetTaxStatus
        };

        _context.EventSeries.Add(eventSeries);
        await _context.SaveChangesAsync();

        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse?> UpdateIncomeEventAsync(string id, CreateIncomeEventRequest request,
        string userId)
    {
        var eventSeries = await GetEventSeriesForUpdate(id, userId, EventSeriesType.Income);
        if (eventSeries == null) return null;

        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, eventSeries.ScenarioId, userId);
        ValidateUserPercentage(request.UserPercentage);

        UpdateCommonFields(eventSeries, request.Name, request.Description, request.StartYear,
            request.Duration, request.ReferenceEventSeriesId, request.StartTimingType,
            request.IsActive, request.OrderIndex);

        eventSeries.InitialAmount = request.InitialAmount;
        eventSeries.AnnualChange = request.AnnualChange;
        eventSeries.InflationAdjusted = request.InflationAdjusted;
        eventSeries.UserPercentage = request.UserPercentage;
        eventSeries.IsSocialSecurity = request.IsSocialSecurity;
        eventSeries.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse?> UpdateExpenseEventAsync(string id, CreateExpenseEventRequest request,
        string userId)
    {
        var eventSeries = await GetEventSeriesForUpdate(id, userId, EventSeriesType.Expense);
        if (eventSeries == null) return null;

        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, eventSeries.ScenarioId, userId);
        ValidateUserPercentage(request.UserPercentage);

        UpdateCommonFields(eventSeries, request.Name, request.Description, request.StartYear,
            request.Duration, request.ReferenceEventSeriesId, request.StartTimingType,
            request.IsActive, request.OrderIndex);

        eventSeries.InitialAmount = request.InitialAmount;
        eventSeries.AnnualChange = request.AnnualChange;
        eventSeries.InflationAdjusted = request.InflationAdjusted;
        eventSeries.UserPercentage = request.UserPercentage;
        eventSeries.IsDiscretionary = request.IsDiscretionary;
        eventSeries.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse?> UpdateInvestEventAsync(string id, CreateInvestEventRequest request,
        string userId)
    {
        var eventSeries = await GetEventSeriesForUpdate(id, userId, EventSeriesType.Invest);
        if (eventSeries == null) return null;

        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, eventSeries.ScenarioId, userId);
        await ValidateAssetAllocation(request.AssetAllocation, eventSeries.ScenarioId, userId);

        if (request.IsGlidePath)
        {
            ValidateGlidePath(request.InitialAllocation, request.FinalAllocation);
            await ValidateAssetAllocation(request.InitialAllocation!, eventSeries.ScenarioId, userId);
            await ValidateAssetAllocation(request.FinalAllocation!, eventSeries.ScenarioId, userId);
        }

        UpdateCommonFields(eventSeries, request.Name, request.Description, request.StartYear,
            request.Duration, request.ReferenceEventSeriesId, request.StartTimingType,
            request.IsActive, request.OrderIndex);

        eventSeries.AssetAllocation = request.AssetAllocation;
        eventSeries.IsGlidePath = request.IsGlidePath;
        eventSeries.InitialAllocation = request.InitialAllocation;
        eventSeries.FinalAllocation = request.FinalAllocation;
        eventSeries.MaximumCash = request.MaximumCash;
        eventSeries.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse?> UpdateRebalanceEventAsync(string id, CreateRebalanceEventRequest request,
        string userId)
    {
        var eventSeries = await GetEventSeriesForUpdate(id, userId, EventSeriesType.Rebalance);
        if (eventSeries == null) return null;

        await ValidateReferenceEventSeries(request.ReferenceEventSeriesId, eventSeries.ScenarioId, userId);
        await ValidateAssetAllocationForTaxStatus(request.AssetAllocation, eventSeries.ScenarioId, userId,
            request.TargetTaxStatus);

        if (request.IsGlidePath)
        {
            ValidateGlidePath(request.InitialAllocation, request.FinalAllocation);
            await ValidateAssetAllocationForTaxStatus(request.InitialAllocation!, eventSeries.ScenarioId, userId,
                request.TargetTaxStatus);
            await ValidateAssetAllocationForTaxStatus(request.FinalAllocation!, eventSeries.ScenarioId, userId,
                request.TargetTaxStatus);
        }

        UpdateCommonFields(eventSeries, request.Name, request.Description, request.StartYear,
            request.Duration, request.ReferenceEventSeriesId, request.StartTimingType,
            request.IsActive, request.OrderIndex);

        eventSeries.AssetAllocation = request.AssetAllocation;
        eventSeries.IsGlidePath = request.IsGlidePath;
        eventSeries.InitialAllocation = request.InitialAllocation;
        eventSeries.FinalAllocation = request.FinalAllocation;
        eventSeries.TargetTaxStatus = request.TargetTaxStatus;
        eventSeries.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        return MapToResponse(eventSeries);
    }

    public async Task<EventSeriesResponse?> GetEventSeriesByIdAsync(string id, string userId)
    {
        var eventSeries = await _context.EventSeries
            .Include(es => es.Scenario)
            .FirstOrDefaultAsync(es => es.Id == id && es.Scenario.OwnerId == userId);

        return eventSeries != null ? MapToResponse(eventSeries) : null;
    }

    public async Task<IEnumerable<EventSeriesResponse>> GetEventSeriesByScenarioAsync(string scenarioId, string userId)
    {
        var eventSeries = await _context.EventSeries
            .Include(es => es.Scenario)
            .Where(es => es.ScenarioId == scenarioId && es.Scenario.OwnerId == userId)
            .OrderBy(es => es.OrderIndex)
            .ThenBy(es => es.Name)
            .ToListAsync();

        return eventSeries.Select(MapToResponse);
    }

    public async Task<IEnumerable<EventSeriesResponse>> GetEventSeriesByTypeAsync(string scenarioId,
        EventSeriesType eventType, string userId)
    {
        var eventSeries = await _context.EventSeries
            .Include(es => es.Scenario)
            .Where(es => es.ScenarioId == scenarioId && es.EventType == eventType && es.Scenario.OwnerId == userId)
            .OrderBy(es => es.OrderIndex)
            .ThenBy(es => es.Name)
            .ToListAsync();

        return eventSeries.Select(MapToResponse);
    }

    public async Task<bool> DeleteEventSeriesAsync(string id, string userId)
    {
        var eventSeries = await _context.EventSeries
            .Include(es => es.Scenario)
            .Include(es => es.ReferencingEventSeries)
            .FirstOrDefaultAsync(es => es.Id == id && es.Scenario.OwnerId == userId);

        if (eventSeries == null)
            return false;

        // Check if other event series reference this one
        if (eventSeries.ReferencingEventSeries.Any())
            throw new InvalidOperationException("Cannot delete event series that is referenced by other event series");

        _context.EventSeries.Remove(eventSeries);
        await _context.SaveChangesAsync();

        return true;
    }

    // Private helper methods
    private async Task ValidateScenarioOwnership(string scenarioId, string userId)
    {
        var scenario = await _context.Scenarios
            .FirstOrDefaultAsync(s => s.Id == scenarioId && s.OwnerId == userId);

        if (scenario == null)
            throw new UnauthorizedAccessException("Scenario not found or access denied");
    }

    private async Task ValidateReferenceEventSeries(string? referenceId, string scenarioId, string userId)
    {
        if (string.IsNullOrEmpty(referenceId)) return;

        var referenceExists = await _context.EventSeries
            .Include(es => es.Scenario)
            .AnyAsync(es => es.Id == referenceId && es.ScenarioId == scenarioId && es.Scenario.OwnerId == userId);

        if (!referenceExists)
            throw new ArgumentException("Referenced event series not found in this scenario");
    }

    private static void ValidateUserPercentage(decimal? userPercentage)
    {
        if (userPercentage.HasValue && (userPercentage < 0 || userPercentage > 100))
            throw new ArgumentException("User percentage must be between 0 and 100");
    }

    private async Task ValidateAssetAllocation(Dictionary<string, decimal> allocation, string scenarioId, string userId)
    {
        if (allocation == null || !allocation.Any())
            throw new ArgumentException("Asset allocation cannot be empty");

        var totalPercentage = allocation.Values.Sum();
        if (Math.Abs(totalPercentage - 100) > 0.01m)
            throw new ArgumentException("Asset allocation percentages must sum to 100");

        // Validate that all investment IDs exist and belong to the scenario
        var investmentIds = allocation.Keys.ToList();
        var validInvestments = await _context.Investments
            .Include(i => i.Scenario)
            .Where(i => investmentIds.Contains(i.Id) && i.ScenarioId == scenarioId && i.Scenario.OwnerId == userId)
            .CountAsync();

        if (validInvestments != investmentIds.Count)
            throw new ArgumentException("One or more investments in allocation do not exist in this scenario");
    }

    private async Task ValidateAssetAllocationForTaxStatus(Dictionary<string, decimal> allocation, string scenarioId,
        string userId, AccountTaxStatus taxStatus)
    {
        if (allocation == null || !allocation.Any())
            throw new ArgumentException("Asset allocation cannot be empty");

        var totalPercentage = allocation.Values.Sum();
        if (Math.Abs(totalPercentage - 100) > 0.01m)
            throw new ArgumentException("Asset allocation percentages must sum to 100");

        // Validate that all investment IDs exist, belong to the scenario, and have the correct tax status
        var investmentIds = allocation.Keys.ToList();
        var validInvestments = await _context.Investments
            .Include(i => i.Scenario)
            .Where(i => investmentIds.Contains(i.Id) &&
                        i.ScenarioId == scenarioId &&
                        i.TaxStatus == taxStatus &&
                        i.Scenario.OwnerId == userId)
            .CountAsync();

        if (validInvestments != investmentIds.Count)
            throw new ArgumentException(
                $"One or more investments in allocation do not exist in this scenario or do not have tax status {taxStatus}");
    }

    private static void ValidateGlidePath(Dictionary<string, decimal>? initial, Dictionary<string, decimal>? final)
    {
        if (initial == null || final == null)
            throw new ArgumentException("Both initial and final allocations are required for glide paths");

        if (!initial.Keys.SequenceEqual(final.Keys))
            throw new ArgumentException("Initial and final allocations must contain the same investments");
    }

    private async Task ValidateNoOverlappingInvestEvents(string scenarioId, Distribution? startYear,
        Distribution? duration)
    {
        // For simplicity, we'll just check if there are any other active invest events
        // A more sophisticated implementation would check for actual temporal overlap
        var existingInvestEvents = await _context.EventSeries
            .CountAsync(es => es.ScenarioId == scenarioId &&
                              es.EventType == EventSeriesType.Invest &&
                              es.IsActive);

        if (existingInvestEvents > 0)
            throw new InvalidOperationException("Scenario may not contain temporally overlapping invest event series");
    }

    private async Task ValidateNoOverlappingRebalanceEvents(string scenarioId, AccountTaxStatus taxStatus,
        Distribution? startYear, Distribution? duration)
    {
        // For simplicity, we'll just check if there are any other active rebalance events for the same tax status
        var existingRebalanceEvents = await _context.EventSeries
            .CountAsync(es => es.ScenarioId == scenarioId &&
                              es.EventType == EventSeriesType.Rebalance &&
                              es.TargetTaxStatus == taxStatus &&
                              es.IsActive);

        if (existingRebalanceEvents > 0)
            throw new InvalidOperationException(
                $"Scenario may not contain overlapping rebalance event series for tax status {taxStatus}");
    }

    private async Task<EventSeries?> GetEventSeriesForUpdate(string id, string userId, EventSeriesType expectedType)
    {
        var eventSeries = await _context.EventSeries
            .Include(es => es.Scenario)
            .FirstOrDefaultAsync(es => es.Id == id && es.Scenario.OwnerId == userId);

        if (eventSeries == null || eventSeries.EventType != expectedType)
            return null;

        return eventSeries;
    }

    private static void UpdateCommonFields(EventSeries eventSeries, string name, string? description,
        Distribution? startYear, Distribution? duration, string? referenceId, string? startTimingType,
        bool isActive, int orderIndex)
    {
        eventSeries.Name = name;
        eventSeries.Description = description;
        eventSeries.StartYear = startYear;
        eventSeries.Duration = duration;
        eventSeries.ReferenceEventSeriesId = referenceId;
        eventSeries.StartTimingType = startTimingType;
        eventSeries.IsActive = isActive;
        eventSeries.OrderIndex = orderIndex;
    }

    private static EventSeriesResponse MapToResponse(EventSeries eventSeries)
    {
        return new EventSeriesResponse
        {
            Id = eventSeries.Id,
            ScenarioId = eventSeries.ScenarioId,
            Name = eventSeries.Name,
            Description = eventSeries.Description,
            EventType = eventSeries.EventType,
            StartYear = eventSeries.StartYear,
            Duration = eventSeries.Duration,
            ReferenceEventSeriesId = eventSeries.ReferenceEventSeriesId,
            StartTimingType = eventSeries.StartTimingType,
            IsActive = eventSeries.IsActive,
            OrderIndex = eventSeries.OrderIndex,
            InitialAmount = eventSeries.InitialAmount,
            AnnualChange = eventSeries.AnnualChange,
            InflationAdjusted = eventSeries.InflationAdjusted,
            UserPercentage = eventSeries.UserPercentage,
            IsSocialSecurity = eventSeries.IsSocialSecurity,
            IsDiscretionary = eventSeries.IsDiscretionary,
            AssetAllocation = eventSeries.AssetAllocation,
            IsGlidePath = eventSeries.IsGlidePath,
            InitialAllocation = eventSeries.InitialAllocation,
            FinalAllocation = eventSeries.FinalAllocation,
            MaximumCash = eventSeries.MaximumCash,
            TargetTaxStatus = eventSeries.TargetTaxStatus,
            CreatedAt = eventSeries.CreatedAt,
            UpdatedAt = eventSeries.UpdatedAt
        };
    }
}