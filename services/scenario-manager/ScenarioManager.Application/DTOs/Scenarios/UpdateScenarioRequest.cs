using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.Scenarios;

public class UpdateScenarioRequest
{
    [MaxLength(255)] public string? Name { get; set; }

    public string? Description { get; set; }

    public ScenarioType? ScenarioType { get; set; }

    // Personal Information
    public int? UserBirthYear { get; set; }
    public int? SpouseBirthYear { get; set; }
    public Distribution? UserLifeExpectancy { get; set; }
    public Distribution? SpouseLifeExpectancy { get; set; }

    // Financial Settings
    public decimal? FinancialGoal { get; set; } = 0m;

    [MaxLength(100)] public string? StateOfResidence { get; set; }

    public Distribution? InflationAssumption { get; set; }
    public decimal? AnnualRetirementContributionLimit { get; set; } = 0m;

    // Roth Conversion Optimizer
    public bool? RothOptimizerEnabled { get; set; }
    public int? RothOptimizerStartYear { get; set; }
    public int? RothOptimizerEndYear { get; set; }
}