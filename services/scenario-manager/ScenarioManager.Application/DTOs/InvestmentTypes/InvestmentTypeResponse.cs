using ScenarioManager.Domain.Entities;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.InvestmentTypes;

public class InvestmentTypeResponse
{
    public required string Id { get; set; }
    public required string ScenarioId { get; set; }
    public required string Name { get; set; }
    public string? Description { get; set; }
    public required Distribution ExpectedAnnualReturn { get; set; }
    public decimal ExpenseRatio { get; set; }
    public required Distribution ExpectedAnnualIncome { get; set; }
    public InvestmentTaxability Taxability { get; set; }
    public bool IsCash { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}