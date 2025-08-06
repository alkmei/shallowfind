using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.Strategies;

public class CreateStrategyRequest
{
    [Required] public required string ScenarioId { get; set; }

    public StrategyType StrategyType { get; set; }

    [Required] [MaxLength(255)] public required string Name { get; set; }

    [MaxLength(1000)] public string? Description { get; set; }

    public bool IsActive { get; set; } = true;
    public List<string>? Ordering { get; set; }
}