using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Domain.Entities;

public class EventSeries : BaseEntity
{
    [Required] public required string ScenarioId { get; set; }

    [Required] [MaxLength(255)] public required string Name { get; set; }

    [MaxLength(1000)] public string? Description { get; set; }

    public EventSeriesType EventType { get; set; }

    // Timing
    public Distribution? StartYear { get; set; }
    public Distribution? Duration { get; set; }
    public string? ReferenceEventSeriesId { get; set; }

    [MaxLength(50)] public string? StartTimingType { get; set; }

    // Common fields
    public bool IsActive { get; set; } = true;
    public int OrderIndex { get; set; } = 0;

    // Income/Expense specific fields
    public decimal? InitialAmount { get; set; }
    public Distribution? AnnualChange { get; set; }
    public bool InflationAdjusted { get; set; } = false;
    public decimal? UserPercentage { get; set; }
    public bool IsSocialSecurity { get; set; } = false;
    public bool IsDiscretionary { get; set; } = false;

    // Invest/Rebalance specific fields
    public Dictionary<string, decimal>? AssetAllocation { get; set; }
    public bool IsGlidePath { get; set; } = false;
    public Dictionary<string, decimal>? InitialAllocation { get; set; }
    public Dictionary<string, decimal>? FinalAllocation { get; set; }
    public decimal? MaximumCash { get; set; }
    public AccountTaxStatus? TargetTaxStatus { get; set; }

    // Navigation properties
    public virtual Scenario Scenario { get; set; } = null!;
    public virtual EventSeries? ReferenceEventSeries { get; set; }
    public virtual ICollection<EventSeries> ReferencingEventSeries { get; set; } = new List<EventSeries>();
}