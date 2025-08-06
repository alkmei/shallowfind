using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc.ApplicationModels;
using Microsoft.EntityFrameworkCore;
using ScenarioManager.Application.DTOs.EventSeries;
using ScenarioManager.Application.DTOs.InvestmentTypes;
using ScenarioManager.Application.DTOs.Scenarios;
using ScenarioManager.Application.DTOs.Strategies;
using ScenarioManager.Application.Services;
using ScenarioManager.Infrastructure.Data;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers(options =>
{
    options.Conventions.Add(new RouteTokenTransformerConvention(new SlugifyParameterTransformer()));
}).AddJsonOptions(options =>
{
    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
});

// Add Entity Framework
builder.Services.AddDbContext<ScenarioDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Add application services
builder.Services.AddScoped<IScenarioService, ScenarioService>();
builder.Services.AddScoped<IInvestmentTypeService, InvestmentTypeService>();
builder.Services.AddScoped<IEventSeriesService, EventSeriesService>();
builder.Services.AddScoped<IStrategyService, StrategyService>();

// Add API documentation
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add CORS if needed
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", options =>
    {
        options.Authority =
            "https://securetoken.google.com/shallowfind-df121"; // URL of your Identity Provider or Auth server.
        options.Audience = "shallowfind-df121"; // Must match the "aud" claim in the JWT.
        options.ClaimsIssuer = "https://identitytoolkit.google.com/"; // Must match the "iss" claim in the JWT.
        options.RequireHttpsMetadata = false; // Only set to false for development
    });

builder.Services.AddAuthorization();

var app = builder.Build();

// Add authentication/authorization middleware here if needed
app.UseAuthentication();
app.UseAuthorization();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors();

app.MapControllers();

app.Run();