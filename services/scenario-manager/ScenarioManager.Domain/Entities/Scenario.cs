using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Domain.Entities;

public class Scenario : BaseEntity
{
    [Required] [MaxLength(255)] public required string Name { get; set; }

    public string? Description { get; set; }

    [Required] public required string OwnerId { get; set; }

    public ScenarioType ScenarioType { get; set; }

    public ScenarioStatus Status { get; set; } = ScenarioStatus.Draft;

    // Personal Information
    public int? UserBirthYear { get; set; }
    public int? SpouseBirthYear { get; set; }
    public Distribution? UserLifeExpectancy { get; set; }
    public Distribution? SpouseLifeExpectancy { get; set; }

    // Financial Settings
    public decimal FinancialGoal { get; set; } = 0m;

    [MaxLength(100)] public string? StateOfResidence { get; set; }

    public Distribution? InflationAssumption { get; set; }
    public decimal AnnualRetirementContributionLimit { get; set; } = 0m;

    // Roth Conversion Optimizer
    public bool RothOptimizerEnabled { get; set; } = false;
    public int? RothOptimizerStartYear { get; set; }
    public int? RothOptimizerEndYear { get; set; }

    // Import/Export metadata
    [MaxLength(255)] public string? ImportSource { get; set; }

    public int ExportCount { get; set; } = 0;
    public DateTime? LastSimulationRun { get; set; }

    // Navigation properties
    public virtual ICollection<InvestmentType> InvestmentTypes { get; set; } = new List<InvestmentType>();
    public virtual ICollection<Investment> Investments { get; set; } = new List<Investment>();
    public virtual ICollection<EventSeries> EventSeries { get; set; } = new List<EventSeries>();
    public virtual ICollection<Strategy> Strategies { get; set; } = new List<Strategy>();
    public virtual ICollection<ScenarioShare> ScenarioShares { get; set; } = new List<ScenarioShare>();
}