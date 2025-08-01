using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs;

public class CreateScenarioRequest
{
    [Required] [MaxLength(255)] public required string Name { get; set; }
    public string? Description { get; set; }
    [Required] public ScenarioType ScenarioType { get; set; }
}