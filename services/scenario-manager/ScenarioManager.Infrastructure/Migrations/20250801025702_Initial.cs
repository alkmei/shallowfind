using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ScenarioManager.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class Initial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Scenarios",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    Name = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    OwnerId = table.Column<string>(type: "text", nullable: false),
                    ScenarioType = table.Column<string>(type: "text", nullable: false),
                    Status = table.Column<string>(type: "text", nullable: false),
                    UserBirthYear = table.Column<int>(type: "integer", nullable: true),
                    SpouseBirthYear = table.Column<int>(type: "integer", nullable: true),
                    UserLifeExpectancy = table.Column<string>(type: "jsonb", nullable: true),
                    SpouseLifeExpectancy = table.Column<string>(type: "jsonb", nullable: true),
                    FinancialGoal = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    StateOfResidence = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    InflationAssumption = table.Column<string>(type: "jsonb", nullable: true),
                    AnnualRetirementContributionLimit = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    RothOptimizerEnabled = table.Column<bool>(type: "boolean", nullable: false),
                    RothOptimizerStartYear = table.Column<int>(type: "integer", nullable: true),
                    RothOptimizerEndYear = table.Column<int>(type: "integer", nullable: true),
                    ImportSource = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: true),
                    ExportCount = table.Column<int>(type: "integer", nullable: false),
                    LastSimulationRun = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Scenarios", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "EventSeries",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ScenarioId = table.Column<string>(type: "text", nullable: false),
                    Name = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    Description = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: true),
                    EventType = table.Column<string>(type: "text", nullable: false),
                    StartYear = table.Column<string>(type: "jsonb", nullable: true),
                    Duration = table.Column<string>(type: "jsonb", nullable: true),
                    ReferenceEventSeriesId = table.Column<string>(type: "text", nullable: true),
                    StartTimingType = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    IsActive = table.Column<bool>(type: "boolean", nullable: false),
                    OrderIndex = table.Column<int>(type: "integer", nullable: false),
                    InitialAmount = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: true),
                    AnnualChange = table.Column<string>(type: "jsonb", nullable: true),
                    InflationAdjusted = table.Column<bool>(type: "boolean", nullable: false),
                    UserPercentage = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: true),
                    IsSocialSecurity = table.Column<bool>(type: "boolean", nullable: false),
                    IsDiscretionary = table.Column<bool>(type: "boolean", nullable: false),
                    AssetAllocation = table.Column<string>(type: "jsonb", nullable: true),
                    IsGlidePath = table.Column<bool>(type: "boolean", nullable: false),
                    InitialAllocation = table.Column<string>(type: "jsonb", nullable: true),
                    FinalAllocation = table.Column<string>(type: "jsonb", nullable: true),
                    MaximumCash = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: true),
                    TargetTaxStatus = table.Column<string>(type: "text", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EventSeries", x => x.Id);
                    table.ForeignKey(
                        name: "FK_EventSeries_EventSeries_ReferenceEventSeriesId",
                        column: x => x.ReferenceEventSeriesId,
                        principalTable: "EventSeries",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_EventSeries_Scenarios_ScenarioId",
                        column: x => x.ScenarioId,
                        principalTable: "Scenarios",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "InvestmentTypes",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ScenarioId = table.Column<string>(type: "text", nullable: false),
                    Name = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    Description = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: true),
                    ExpectedAnnualReturn = table.Column<string>(type: "jsonb", nullable: false),
                    ExpenseRatio = table.Column<decimal>(type: "numeric(18,6)", precision: 18, scale: 6, nullable: false),
                    ExpectedAnnualIncome = table.Column<string>(type: "jsonb", nullable: false),
                    Taxability = table.Column<string>(type: "text", nullable: false),
                    IsCash = table.Column<bool>(type: "boolean", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_InvestmentTypes", x => x.Id);
                    table.ForeignKey(
                        name: "FK_InvestmentTypes_Scenarios_ScenarioId",
                        column: x => x.ScenarioId,
                        principalTable: "Scenarios",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ScenarioShares",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ScenarioId = table.Column<string>(type: "text", nullable: false),
                    SharedWithUserId = table.Column<string>(type: "text", nullable: false),
                    Permission = table.Column<string>(type: "text", nullable: false),
                    SharedByUserId = table.Column<string>(type: "text", nullable: false),
                    IsActive = table.Column<bool>(type: "boolean", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ScenarioShares", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ScenarioShares_Scenarios_ScenarioId",
                        column: x => x.ScenarioId,
                        principalTable: "Scenarios",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Strategies",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ScenarioId = table.Column<string>(type: "text", nullable: false),
                    StrategyType = table.Column<string>(type: "text", nullable: false),
                    Name = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    Description = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: true),
                    IsActive = table.Column<bool>(type: "boolean", nullable: false),
                    Ordering = table.Column<string>(type: "jsonb", nullable: true),
                    Settings = table.Column<string>(type: "jsonb", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Strategies", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Strategies_Scenarios_ScenarioId",
                        column: x => x.ScenarioId,
                        principalTable: "Scenarios",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Investments",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ScenarioId = table.Column<string>(type: "text", nullable: false),
                    InvestmentTypeId = table.Column<string>(type: "text", nullable: false),
                    Name = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    CurrentValue = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    TaxStatus = table.Column<string>(type: "text", nullable: false),
                    CostBasis = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    OrderIndex = table.Column<int>(type: "integer", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Investments", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Investments_InvestmentTypes_InvestmentTypeId",
                        column: x => x.InvestmentTypeId,
                        principalTable: "InvestmentTypes",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Investments_Scenarios_ScenarioId",
                        column: x => x.ScenarioId,
                        principalTable: "Scenarios",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_EventSeries_ReferenceEventSeriesId",
                table: "EventSeries",
                column: "ReferenceEventSeriesId");

            migrationBuilder.CreateIndex(
                name: "IX_EventSeries_ScenarioId",
                table: "EventSeries",
                column: "ScenarioId");

            migrationBuilder.CreateIndex(
                name: "IX_Investments_InvestmentTypeId",
                table: "Investments",
                column: "InvestmentTypeId");

            migrationBuilder.CreateIndex(
                name: "IX_Investments_ScenarioId",
                table: "Investments",
                column: "ScenarioId");

            migrationBuilder.CreateIndex(
                name: "IX_InvestmentTypes_ScenarioId",
                table: "InvestmentTypes",
                column: "ScenarioId");

            migrationBuilder.CreateIndex(
                name: "IX_Scenarios_OwnerId",
                table: "Scenarios",
                column: "OwnerId");

            migrationBuilder.CreateIndex(
                name: "IX_ScenarioShares_ScenarioId",
                table: "ScenarioShares",
                column: "ScenarioId");

            migrationBuilder.CreateIndex(
                name: "IX_ScenarioShares_SharedWithUserId",
                table: "ScenarioShares",
                column: "SharedWithUserId");

            migrationBuilder.CreateIndex(
                name: "IX_Strategies_ScenarioId",
                table: "Strategies",
                column: "ScenarioId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "EventSeries");

            migrationBuilder.DropTable(
                name: "Investments");

            migrationBuilder.DropTable(
                name: "ScenarioShares");

            migrationBuilder.DropTable(
                name: "Strategies");

            migrationBuilder.DropTable(
                name: "InvestmentTypes");

            migrationBuilder.DropTable(
                name: "Scenarios");
        }
    }
}
