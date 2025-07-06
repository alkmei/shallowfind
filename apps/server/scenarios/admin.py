from django.contrib import admin
from .models import (
    Distribution,
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


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "value", "mean", "stdev", "lower", "upper")
    list_filter = ("type",)
    search_fields = ("type",)
    fieldsets = (
        ("Distribution Type", {"fields": ("type",)}),
        ("Fixed Distribution", {"fields": ("value",), "classes": ("collapse",)}),
        (
            "Normal Distribution",
            {"fields": ("mean", "stdev"), "classes": ("collapse",)},
        ),
        (
            "Uniform Distribution",
            {"fields": ("lower", "upper"), "classes": ("collapse",)},
        ),
    )


@admin.register(InvestmentType)
class InvestmentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "return_amt_or_pct",
        "expense_ratio",
        "income_amt_or_pct",
        "taxability",
    )
    list_filter = ("return_amt_or_pct", "income_amt_or_pct", "taxability")
    search_fields = ("name", "description")
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
    readonly_fields = ("created_at", "updated_at")
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
                    "spouse_life_expectancy",
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
