using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Domain.Entities;

public class InvestmentType : BaseEntity
{
    [Required] public required string ScenarioId { get; set; }

    [Required] [MaxLength(255)] public required string Name { get; set; }

    [MaxLength(1000)] public string? Description { get; set; }

    public required Distribution ExpectedAnnualReturn { get; set; }
    public decimal ExpenseRatio { get; set; } = 0m;
    public required Distribution ExpectedAnnualIncome { get; set; }
    public InvestmentTaxability Taxability { get; set; } = InvestmentTaxability.Taxable;
    public bool IsCash { get; set; } = false;

    // Navigation properties
    public virtual Scenario Scenario { get; set; } = null!;
    public virtual ICollection<Investment> Investments { get; set; } = new List<Investment>();
}