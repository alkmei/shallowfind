using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Entities;

namespace ScenarioManager.Application.DTOs.EventSeries;

public class CreateInvestEventRequest
{
    [Required] [MaxLength(255)] public required string Name { get; set; }

    [MaxLength(1000)] public string? Description { get; set; }

    public Distribution? StartYear { get; set; }
    public Distribution? Duration { get; set; }
    public string? ReferenceEventSeriesId { get; set; }

    [MaxLength(50)] public string? StartTimingType { get; set; }

    public bool IsActive { get; set; } = true;
    public int OrderIndex { get; set; } = 0;

    // Invest-specific fields
    [Required] public required Dictionary<string, decimal> AssetAllocation { get; set; } // InvestmentId -> Percentage

    public bool IsGlidePath { get; set; } = false;
    public Dictionary<string, decimal>? InitialAllocation { get; set; } // For glide paths
    public Dictionary<string, decimal>? FinalAllocation { get; set; } // For glide paths
    public decimal? MaximumCash { get; set; }
}