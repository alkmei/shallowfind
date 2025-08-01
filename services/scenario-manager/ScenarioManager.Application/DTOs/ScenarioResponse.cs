using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs;

public class ScenarioResponse
{
    public required string Id { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public required string OwnerId { get; set; }
    public ScenarioType ScenarioType { get; set; }
    public ScenarioStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }

    // Personal Information (optional fields for draft)
    public int? UserBirthYear { get; set; }
    public int? SpouseBirthYear { get; set; }

    // Financial Settings
    public decimal FinancialGoal { get; set; }
    public string? StateOfResidence { get; set; }
    public decimal AnnualRetirementContributionLimit { get; set; }

    // Roth Conversion Optimizer
    public bool RothOptimizerEnabled { get; set; }
    public int? RothOptimizerStartYear { get; set; }
    public int? RothOptimizerEndYear { get; set; }

    // Metadata
    public string? ImportSource { get; set; }
    public int ExportCount { get; set; }
    public DateTime? LastSimulationRun { get; set; }
}