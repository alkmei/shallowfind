from django.contrib import admin
from django.utils.html import format_html
import json
from .models import (
    InvestmentType,
    Investment,
    EventSeries,
    AssetAllocation,
    SpendingStrategyItem,
    ExpenseWithdrawalStrategyItem,
    RMDStrategyItem,
    RothConversionStrategyItem,
    Scenario,
)


def format_distribution_display(distribution_data):
    """Helper function to format distribution JSON for display"""
    if not distribution_data:
        return "Not set"

    dist_type = distribution_data.get("type", "Unknown")

    if dist_type == "fixed":
        return f"Fixed: {distribution_data.get('value', 'N/A')}"
    elif dist_type == "normal":
        mean = distribution_data.get("mean", "N/A")
        stdev = distribution_data.get("stdev", "N/A")
        return f"Normal: μ={mean}, σ={stdev}"
    elif dist_type == "uniform":
        lower = distribution_data.get("lower", "N/A")
        upper = distribution_data.get("upper", "N/A")
        return f"Uniform: [{lower}, {upper}]"
    else:
        return f"Unknown type: {dist_type}"


@admin.register(InvestmentType)
class InvestmentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "scenario",
        "return_amt_or_pct",
        "return_distribution_display",
        "expense_ratio",
        "income_amt_or_pct",
        "income_distribution_display",
        "taxability",
    )
    list_filter = ("return_amt_or_pct", "income_amt_or_pct", "taxability")
    search_fields = ("name", "description", "scenario__name")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "description", "taxability")}),
        (
            "Return Configuration",
            {"fields": ("return_amt_or_pct", "return_distribution", "expense_ratio")},
        ),
        (
            "Income Configuration",
            {"fields": ("income_amt_or_pct", "income_distribution")},
        ),
    )

    def return_distribution_display(self, obj):
        """Display return distribution in a readable format"""
        return format_distribution_display(obj.return_distribution)

    return_distribution_display.short_description = "Return Distribution"

    def income_distribution_display(self, obj):
        """Display income distribution in a readable format"""
        return format_distribution_display(obj.income_distribution)

    income_distribution_display.short_description = "Income Distribution"


class InvestmentInline(admin.TabularInline):
    model = Investment
    extra = 0
    fields = ("investment_type", "value", "tax_status", "investment_id")


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = (
        "investment_id",
        "scenario",
        "investment_type",
        "value",
        "tax_status",
    )
    list_filter = ("tax_status", "investment_type")
    search_fields = ("investment_id", "scenario__name", "investment_type__name")
    fieldsets = (
        (
            "Investment Details",
            {"fields": ("scenario", "investment_type", "investment_id")},
        ),
        ("Financial Information", {"fields": ("value", "tax_status")}),
    )


class AssetAllocationInline(admin.TabularInline):
    model = AssetAllocation
    extra = 0
    fields = ("investment", "percentage", "is_final_allocation")


@admin.register(EventSeries)
class EventSeriesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "scenario",
        "type",
        "start_type",
        "start_distribution_display",
        "duration_distribution_display",
        "inflation_adjusted",
        "discretionary",
        "social_security",
    )
    list_filter = (
        "type",
        "start_type",
        "inflation_adjusted",
        "discretionary",
        "social_security",
    )
    search_fields = ("name", "description", "scenario__name")
    inlines = [AssetAllocationInline]
    fieldsets = (
        ("Basic Information", {"fields": ("scenario", "name", "description", "type")}),
        (
            "Start Configuration",
            {
                "fields": (
                    "start_type",
                    "start_distribution",
                    "start_with_event",
                    "start_after_event",
                )
            },
        ),
        ("Duration", {"fields": ("duration_distribution",)}),
        (
            "Income/Expense Details",
            {
                "fields": (
                    "initial_amount",
                    "change_amt_or_pct",
                    "change_distribution",
                    "inflation_adjusted",
                    "user_fraction",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Income Specific", {"fields": ("social_security",), "classes": ("collapse",)}),
        ("Expense Specific", {"fields": ("discretionary",), "classes": ("collapse",)}),
        (
            "Invest/Rebalance Specific",
            {"fields": ("max_cash", "glide_path"), "classes": ("collapse",)},
        ),
    )

    def start_distribution_display(self, obj):
        """Display start distribution in a readable format"""
        return format_distribution_display(obj.start_distribution)

    start_distribution_display.short_description = "Start Distribution"

    def duration_distribution_display(self, obj):
        """Display duration distribution in a readable format"""
        return format_distribution_display(obj.duration_distribution)

    duration_distribution_display.short_description = "Duration Distribution"

    def change_distribution_display(self, obj):
        """Display change distribution in a readable format"""
        return format_distribution_display(obj.change_distribution)

    change_distribution_display.short_description = "Change Distribution"


@admin.register(AssetAllocation)
class AssetAllocationAdmin(admin.ModelAdmin):
    list_display = ("event_series", "investment", "percentage", "is_final_allocation")
    list_filter = ("is_final_allocation", "event_series__type")
    search_fields = ("event_series__name", "investment__investment_id")


# Strategy Item Inlines
class SpendingStrategyItemInline(admin.TabularInline):
    model = SpendingStrategyItem
    extra = 0
    fields = ("event_series", "order")
    ordering = ("order",)


class ExpenseWithdrawalStrategyItemInline(admin.TabularInline):
    model = ExpenseWithdrawalStrategyItem
    extra = 0
    fields = ("investment", "order")
    ordering = ("order",)


class RMDStrategyItemInline(admin.TabularInline):
    model = RMDStrategyItem
    extra = 0
    fields = ("investment", "order")
    ordering = ("order",)


class RothConversionStrategyItemInline(admin.TabularInline):
    model = RothConversionStrategyItem
    extra = 0
    fields = ("investment", "order")
    ordering = ("order",)


@admin.register(SpendingStrategyItem)
class SpendingStrategyItemAdmin(admin.ModelAdmin):
    list_display = ("scenario", "event_series", "order")
    list_filter = ("scenario",)
    search_fields = ("scenario__name", "event_series__name")
    ordering = ("scenario", "order")


@admin.register(ExpenseWithdrawalStrategyItem)
class ExpenseWithdrawalStrategyItemAdmin(admin.ModelAdmin):
    list_display = ("scenario", "investment", "order")
    list_filter = ("scenario", "investment__tax_status")
    search_fields = ("scenario__name", "investment__investment_id")
    ordering = ("scenario", "order")


@admin.register(RMDStrategyItem)
class RMDStrategyItemAdmin(admin.ModelAdmin):
    list_display = ("scenario", "investment", "order")
    list_filter = ("scenario",)
    search_fields = ("scenario__name", "investment__investment_id")
    ordering = ("scenario", "order")


@admin.register(RothConversionStrategyItem)
class RothConversionStrategyItemAdmin(admin.ModelAdmin):
    list_display = ("scenario", "investment", "order")
    list_filter = ("scenario",)
    search_fields = ("scenario__name", "investment__investment_id")
    ordering = ("scenario", "order")


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "marital_status",
        "user_birth_year",
        "user_life_expectancy_display",
        "residence_state",
        "financial_goal",
        "roth_conversion_opt",
        "created_at",
    )
    list_filter = (
        "marital_status",
        "residence_state",
        "roth_conversion_opt",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "user_life_expectancy_formatted",
        "spouse_life_expectancy_formatted",
        "inflation_assumption_formatted",
    )
    inlines = [
        InvestmentInline,
        SpendingStrategyItemInline,
        ExpenseWithdrawalStrategyItemInline,
        RMDStrategyItemInline,
        RothConversionStrategyItemInline,
    ]
    fieldsets = (
        ("Basic Information", {"fields": ("name", "user", "marital_status")}),
        (
            "Demographics",
            {
                "fields": (
                    "user_birth_year",
                    "spouse_birth_year",
                    "user_life_expectancy",
                    "user_life_expectancy_formatted",
                    "spouse_life_expectancy",
                    "spouse_life_expectancy_formatted",
                )
            },
        ),
        (
            "Financial Settings",
            {
                "fields": (
                    "financial_goal",
                    "after_tax_contribution_limit",
                    "inflation_assumption",
                    "inflation_assumption_formatted",
                    "residence_state",
                )
            },
        ),
        (
            "Roth Conversion",
            {
                "fields": (
                    "roth_conversion_opt",
                    "roth_conversion_start",
                    "roth_conversion_end",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_life_expectancy_display(self, obj):
        """Display user life expectancy in list view"""
        return format_distribution_display(obj.user_life_expectancy)

    user_life_expectancy_display.short_description = "Life Expectancy"

    def user_life_expectancy_formatted(self, obj):
        """Display formatted user life expectancy in detail view"""
        return format_html(
            "<pre>{}</pre>", json.dumps(obj.user_life_expectancy, indent=2)
        )

    user_life_expectancy_formatted.short_description = "User Life Expectancy (JSON)"

    def spouse_life_expectancy_formatted(self, obj):
        """Display formatted spouse life expectancy in detail view"""
        if obj.spouse_life_expectancy:
            return format_html(
                "<pre>{}</pre>", json.dumps(obj.spouse_life_expectancy, indent=2)
            )
        return "N/A"

    spouse_life_expectancy_formatted.short_description = "Spouse Life Expectancy (JSON)"

    def inflation_assumption_formatted(self, obj):
        """Display formatted inflation assumption in detail view"""
        return format_html(
            "<pre>{}</pre>", json.dumps(obj.inflation_assumption, indent=2)
        )

    inflation_assumption_formatted.short_description = "Inflation Assumption (JSON)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
