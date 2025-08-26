using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ScenarioManager.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class Adddescriptiontoscenario : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Description",
                table: "Scenarios",
                type: "text",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Description",
                table: "Scenarios");
        }
    }
}
