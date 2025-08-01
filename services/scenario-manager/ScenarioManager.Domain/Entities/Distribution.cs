namespace ScenarioManager.Domain.Entities;

public class Distribution
{
    public required string Type { get; set; } // "normal", "fixed", "uniform"
    public decimal? Value { get; set; }
    public decimal? Mean { get; set; }
    public decimal? Stdev { get; set; }
    public decimal? Lower { get; set; }
    public decimal? Upper { get; set; }
}