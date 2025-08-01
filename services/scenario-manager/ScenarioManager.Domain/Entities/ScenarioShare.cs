using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Domain.Entities;

public class ScenarioShare : BaseEntity
{
    [Required] public required string ScenarioId { get; set; }

    [Required] public required string SharedWithUserId { get; set; }

    public SharePermission Permission { get; set; }

    [Required] public required string SharedByUserId { get; set; }

    public bool IsActive { get; set; } = true;

    // Navigation properties
    public virtual Scenario Scenario { get; set; } = null!;
}