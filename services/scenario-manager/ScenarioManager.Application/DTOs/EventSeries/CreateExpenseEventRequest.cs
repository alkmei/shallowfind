using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Entities;

namespace ScenarioManager.Application.DTOs.EventSeries;

public class CreateExpenseEventRequest
{
    [Required] [MaxLength(255)] public required string Name { get; set; }

    [MaxLength(1000)] public string? Description { get; set; }

    public Distribution? StartYear { get; set; }
    public Distribution? Duration { get; set; }
    public string? ReferenceEventSeriesId { get; set; }

    [MaxLength(50)] public string? StartTimingType { get; set; }

    public bool IsActive { get; set; } = true;
    public int OrderIndex { get; set; } = 0;

    // Expense-specific fields
    [Required] public decimal InitialAmount { get; set; }

    public Distribution? AnnualChange { get; set; }
    public bool InflationAdjusted { get; set; } = false;
    public decimal? UserPercentage { get; set; } // For married couples (0-100)
    public bool IsDiscretionary { get; set; } = false;
}