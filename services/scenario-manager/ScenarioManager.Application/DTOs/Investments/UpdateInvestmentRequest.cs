using System.ComponentModel.DataAnnotations;
using ScenarioManager.Domain.Enums;

namespace ScenarioManager.Application.DTOs.Investments;

public class UpdateInvestmentRequest
{
    [MaxLength(255)] public string? Name { get; set; }

    public decimal? CurrentValue { get; set; }
    public AccountTaxStatus? TaxStatus { get; set; }
    public decimal? CostBasis { get; set; }
    public int? OrderIndex { get; set; }
}