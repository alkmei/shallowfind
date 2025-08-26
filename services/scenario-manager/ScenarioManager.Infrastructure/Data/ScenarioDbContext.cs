using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using ScenarioManager.Domain.Entities;

namespace ScenarioManager.Infrastructure.Data;

public class ScenarioDbContext : DbContext
{
    public ScenarioDbContext(DbContextOptions<ScenarioDbContext> options) : base(options)
    {
    }

    public DbSet<Scenario> Scenarios { get; set; }
    public DbSet<InvestmentType> InvestmentTypes { get; set; }
    public DbSet<Investment> Investments { get; set; }
    public DbSet<EventSeries> EventSeries { get; set; }
    public DbSet<Strategy> Strategies { get; set; }
    public DbSet<ScenarioShare> ScenarioShares { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure enum conversions to strings for PostgreSQL
        modelBuilder.Entity<Scenario>()
            .Property(e => e.ScenarioType)
            .HasConversion<string>();

        modelBuilder.Entity<Scenario>()
            .Property(e => e.Status)
            .HasConversion<string>();

        modelBuilder.Entity<InvestmentType>()
            .Property(e => e.Taxability)
            .HasConversion<string>();

        modelBuilder.Entity<Investment>()
            .Property(e => e.TaxStatus)
            .HasConversion<string>();

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.EventType)
            .HasConversion<string>();

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.TargetTaxStatus)
            .HasConversion<string>();

        modelBuilder.Entity<Strategy>()
            .Property(e => e.StrategyType)
            .HasConversion<string>();

        modelBuilder.Entity<ScenarioShare>()
            .Property(e => e.Permission)
            .HasConversion<string>();

        // Configure JSON columns for PostgreSQL
        var jsonSerializerOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        // Scenario JSON fields
        modelBuilder.Entity<Scenario>()
            .Property(e => e.UserLifeExpectancy)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions));

        modelBuilder.Entity<Scenario>()
            .Property(e => e.SpouseLifeExpectancy)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions));

        modelBuilder.Entity<Scenario>()
            .Property(e => e.InflationAssumption)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions));

        // InvestmentType JSON fields
        modelBuilder.Entity<InvestmentType>()
            .Property(e => e.ExpectedAnnualReturn)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions)!);

        modelBuilder.Entity<InvestmentType>()
            .Property(e => e.ExpectedAnnualIncome)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions)!);

        // EventSeries JSON fields
        modelBuilder.Entity<EventSeries>()
            .Property(e => e.StartYear)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions));

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.Duration)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions));

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.AnnualChange)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Distribution>(v, jsonSerializerOptions));

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.AssetAllocation)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Dictionary<string, decimal>>(v, jsonSerializerOptions));

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.InitialAllocation)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Dictionary<string, decimal>>(v, jsonSerializerOptions));

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.FinalAllocation)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Dictionary<string, decimal>>(v, jsonSerializerOptions));

        // Strategy JSON fields
        modelBuilder.Entity<Strategy>()
            .Property(e => e.Ordering)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<List<string>>(v, jsonSerializerOptions));

        modelBuilder.Entity<Strategy>()
            .Property(e => e.Settings)
            .HasColumnType("jsonb")
            .HasConversion(
                v => JsonSerializer.Serialize(v, jsonSerializerOptions),
                v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, jsonSerializerOptions));

        // Configure relationships
        modelBuilder.Entity<InvestmentType>()
            .HasOne(it => it.Scenario)
            .WithMany(s => s.InvestmentTypes)
            .HasForeignKey(it => it.ScenarioId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Investment>()
            .HasOne(i => i.Scenario)
            .WithMany(s => s.Investments)
            .HasForeignKey(i => i.ScenarioId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Investment>()
            .HasOne(i => i.InvestmentType)
            .WithMany(it => it.Investments)
            .HasForeignKey(i => i.InvestmentTypeId)
            .OnDelete(DeleteBehavior.Restrict);

        modelBuilder.Entity<EventSeries>()
            .HasOne(es => es.Scenario)
            .WithMany(s => s.EventSeries)
            .HasForeignKey(es => es.ScenarioId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<EventSeries>()
            .HasOne(es => es.ReferenceEventSeries)
            .WithMany(es => es.ReferencingEventSeries)
            .HasForeignKey(es => es.ReferenceEventSeriesId)
            .OnDelete(DeleteBehavior.SetNull);

        modelBuilder.Entity<Strategy>()
            .HasOne(st => st.Scenario)
            .WithMany(s => s.Strategies)
            .HasForeignKey(st => st.ScenarioId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<ScenarioShare>()
            .HasOne(ss => ss.Scenario)
            .WithMany(s => s.ScenarioShares)
            .HasForeignKey(ss => ss.ScenarioId)
            .OnDelete(DeleteBehavior.Cascade);

        // Configure decimal precision for PostgreSQL
        ConfigureDecimalPrecision(modelBuilder);

        // Configure indexes
        ConfigureIndexes(modelBuilder);
    }

    private static void ConfigureDecimalPrecision(ModelBuilder modelBuilder)
    {
        // Configure decimal properties with appropriate precision for financial data
        modelBuilder.Entity<Scenario>()
            .Property(e => e.FinancialGoal)
            .HasPrecision(18, 2);

        modelBuilder.Entity<Scenario>()
            .Property(e => e.AnnualRetirementContributionLimit)
            .HasPrecision(18, 2);

        modelBuilder.Entity<InvestmentType>()
            .Property(e => e.ExpenseRatio)
            .HasPrecision(18, 6);

        modelBuilder.Entity<Investment>()
            .Property(e => e.CurrentValue)
            .HasPrecision(18, 2);

        modelBuilder.Entity<Investment>()
            .Property(e => e.CostBasis)
            .HasPrecision(18, 2);

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.InitialAmount)
            .HasPrecision(18, 2);

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.UserPercentage)
            .HasPrecision(5, 4);

        modelBuilder.Entity<EventSeries>()
            .Property(e => e.MaximumCash)
            .HasPrecision(18, 2);
    }

    private static void ConfigureIndexes(ModelBuilder modelBuilder)
    {
        // Add indexes for common query patterns
        modelBuilder.Entity<Scenario>()
            .HasIndex(s => s.OwnerId);

        modelBuilder.Entity<InvestmentType>()
            .HasIndex(it => it.ScenarioId);

        modelBuilder.Entity<Investment>()
            .HasIndex(i => i.ScenarioId);

        modelBuilder.Entity<Investment>()
            .HasIndex(i => i.InvestmentTypeId);

        modelBuilder.Entity<EventSeries>()
            .HasIndex(es => es.ScenarioId);

        modelBuilder.Entity<EventSeries>()
            .HasIndex(es => es.ReferenceEventSeriesId);

        modelBuilder.Entity<Strategy>()
            .HasIndex(st => st.ScenarioId);

        modelBuilder.Entity<ScenarioShare>()
            .HasIndex(ss => ss.ScenarioId);

        modelBuilder.Entity<ScenarioShare>()
            .HasIndex(ss => ss.SharedWithUserId);
    }
}