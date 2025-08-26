using System.ComponentModel.DataAnnotations;

namespace ScenarioManager.Domain.Entities;

public abstract class BaseEntity
{
    [Key] public string Id { get; set; } = Guid.NewGuid().ToString();

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}