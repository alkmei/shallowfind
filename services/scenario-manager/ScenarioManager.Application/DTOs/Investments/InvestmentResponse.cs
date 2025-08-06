using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Entities;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.Investments;

public class InvestmentResponse
{
    [Required] public required string ScenarioId { get; set; }

    [Required] public required string InvestmentTypeId { get; set; }

    [Required] [MaxLength(255)] public required string Name { get; set; }

    public decimal CurrentValue { get; set; }
    public AccountTaxStatus TaxStatus { get; set; }
    public decimal CostBasis { get; set; } = 0m;
    public int OrderIndex { get; set; } = 0;

    // Navigation properties
    public virtual Scenario Scenario { get; set; } = null!;
    public virtual InvestmentType InvestmentType { get; set; } = null!;
}