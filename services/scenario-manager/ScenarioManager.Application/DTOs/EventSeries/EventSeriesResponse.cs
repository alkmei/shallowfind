using ScenarioManager.Domain.Entities;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.EventSeries;

public class EventSeriesResponse
{
    public required string Id { get; set; }
    public required string ScenarioId { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public EventSeriesType EventType { get; set; }

    // Timing
    public Distribution? StartYear { get; set; }
    public Distribution? Duration { get; set; }
    public string? ReferenceEventSeriesId { get; set; }
    public string? StartTimingType { get; set; }

    // Common fields
    public bool IsActive { get; set; }
    public int OrderIndex { get; set; }

    // Income/Expense specific fields
    public decimal? InitialAmount { get; set; }
    public Distribution? AnnualChange { get; set; }
    public bool InflationAdjusted { get; set; }
    public decimal? UserPercentage { get; set; }
    public bool IsSocialSecurity { get; set; }
    public bool IsDiscretionary { get; set; }

    // Invest/Rebalance specific fields
    public Dictionary<string, decimal>? AssetAllocation { get; set; }
    public bool IsGlidePath { get; set; }
    public Dictionary<string, decimal>? InitialAllocation { get; set; }
    public Dictionary<string, decimal>? FinalAllocation { get; set; }
    public decimal? MaximumCash { get; set; }
    public AccountTaxStatus? TargetTaxStatus { get; set; }

    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}