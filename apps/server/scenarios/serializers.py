from rest_framework import serializers
from .models import (
    Scenario,
    Distribution,
    InvestmentType,
    Investment,
    EventSeries,
    AssetAllocation,
    SpendingStrategyItem,
    ExpenseWithdrawalStrategyItem,
    RMDStrategyItem,
    RothConversionStrategyItem,
)


class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = ["type", "value", "mean", "stdev", "lower", "upper"]


class InvestmentTypeSerializer(serializers.ModelSerializer):
    return_distribution = DistributionSerializer()
    income_distribution = DistributionSerializer()

    class Meta:
        model = InvestmentType
        fields = [
            "name",
            "description",
            "return_amt_or_pct",
            "return_distribution",
            "expense_ratio",
            "income_amt_or_pct",
            "income_distribution",
            "taxability",
        ]


class InvestmentSerializer(serializers.ModelSerializer):
    investment_type = InvestmentTypeSerializer()

    class Meta:
        model = Investment
        fields = ["investment_type", "value", "tax_status", "investment_id"]


class AssetAllocationSerializer(serializers.ModelSerializer):
    investment_id = serializers.CharField(
        source="investment.investment_id", read_only=True
    )

    class Meta:
        model = AssetAllocation
        fields = ["investment_id", "percentage", "is_final_allocation"]


class EventSeriesSerializer(serializers.ModelSerializer):
    start_distribution = DistributionSerializer(required=False, allow_null=True)
    duration_distribution = DistributionSerializer()
    change_distribution = DistributionSerializer(required=False, allow_null=True)
    start_with_event_name = serializers.CharField(
        source="start_with_event.name", read_only=True, required=False
    )
    start_after_event_name = serializers.CharField(
        source="start_after_event.name", read_only=True, required=False
    )
    asset_allocations = AssetAllocationSerializer(many=True, read_only=True)

    # Input fields for creating relationships
    start_with_event_name_input = serializers.CharField(
        write_only=True, required=False, allow_null=True
    )
    start_after_event_name_input = serializers.CharField(
        write_only=True, required=False, allow_null=True
    )
    asset_allocation_input = serializers.DictField(write_only=True, required=False)
    asset_allocation2_input = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = EventSeries
        fields = [
            "name",
            "description",
            "start_type",
            "start_distribution",
            "start_with_event_name",
            "start_after_event_name",
            "duration_distribution",
            "type",
            "initial_amount",
            "change_amt_or_pct",
            "change_distribution",
            "inflation_adjusted",
            "user_fraction",
            "social_security",
            "discretionary",
            "max_cash",
            "glide_path",
            "asset_allocations",
            "start_with_event_name_input",
            "start_after_event_name_input",
            "asset_allocation_input",
            "asset_allocation2_input",
        ]


class SpendingStrategyItemSerializer(serializers.ModelSerializer):
    event_series_name = serializers.CharField(
        source="event_series.name", read_only=True
    )

    class Meta:
        model = SpendingStrategyItem
        fields = ["event_series_name", "order"]


class ExpenseWithdrawalStrategyItemSerializer(serializers.ModelSerializer):
    investment_id = serializers.CharField(
        source="investment.investment_id", read_only=True
    )

    class Meta:
        model = ExpenseWithdrawalStrategyItem
        fields = ["investment_id", "order"]


class RMDStrategyItemSerializer(serializers.ModelSerializer):
    investment_id = serializers.CharField(
        source="investment.investment_id", read_only=True
    )

    class Meta:
        model = RMDStrategyItem
        fields = ["investment_id", "order"]


class RothConversionStrategyItemSerializer(serializers.ModelSerializer):
    investment_id = serializers.CharField(
        source="investment.investment_id", read_only=True
    )

    class Meta:
        model = RothConversionStrategyItem
        fields = ["investment_id", "order"]


class ScenarioSerializer(serializers.ModelSerializer):
    # Nested distributions
    user_life_expectancy = DistributionSerializer()
    spouse_life_expectancy = DistributionSerializer(required=False, allow_null=True)
    inflation_assumption = DistributionSerializer()

    # Related objects with full nesting
    investments = InvestmentSerializer(many=True)
    event_series = EventSeriesSerializer(many=True)
    spending_strategy_items = SpendingStrategyItemSerializer(many=True, read_only=True)
    expense_withdrawal_strategy_items = ExpenseWithdrawalStrategyItemSerializer(
        many=True, read_only=True
    )
    rmd_strategy_items = RMDStrategyItemSerializer(many=True, read_only=True)
    roth_conversion_strategy_items = RothConversionStrategyItemSerializer(
        many=True, read_only=True
    )

    # Input fields for strategies (write-only)
    spending_strategy_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    expense_withdrawal_strategy_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    rmd_strategy_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    roth_conversion_strategy_input = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Scenario
        fields = [
            "id",
            "name",
            "marital_status",
            "user_birth_year",
            "spouse_birth_year",
            "user_life_expectancy",
            "spouse_life_expectancy",
            "inflation_assumption",
            "after_tax_contribution_limit",
            "financial_goal",
            "residence_state",
            "roth_conversion_opt",
            "roth_conversion_start",
            "roth_conversion_end",
            "investments",
            "event_series",
            "spending_strategy_items",
            "expense_withdrawal_strategy_items",
            "rmd_strategy_items",
            "roth_conversion_strategy_items",
            "created_at",
            "updated_at",
            "spending_strategy_input",
            "expense_withdrawal_strategy_input",
            "rmd_strategy_input",
            "roth_conversion_strategy_input",
        ]

    def create(self, validated_data):
        # Extract nested data
        user_life_expectancy_data = validated_data.pop("user_life_expectancy")
        spouse_life_expectancy_data = validated_data.pop("spouse_life_expectancy", None)
        inflation_assumption_data = validated_data.pop("inflation_assumption")
        investments_data = validated_data.pop("investments")
        event_series_data = validated_data.pop("event_series")

        # Extract strategy inputs
        spending_strategy_input = validated_data.pop("spending_strategy_input", [])
        expense_withdrawal_strategy_input = validated_data.pop(
            "expense_withdrawal_strategy_input", []
        )
        rmd_strategy_input = validated_data.pop("rmd_strategy_input", [])
        roth_conversion_strategy_input = validated_data.pop(
            "roth_conversion_strategy_input", []
        )

        # Create distributions
        user_life_expectancy = Distribution.objects.create(**user_life_expectancy_data)
        spouse_life_expectancy = None
        if spouse_life_expectancy_data:
            spouse_life_expectancy = Distribution.objects.create(
                **spouse_life_expectancy_data
            )
        inflation_assumption = Distribution.objects.create(**inflation_assumption_data)

        # Create scenario
        scenario = Scenario.objects.create(
            user_life_expectancy=user_life_expectancy,
            spouse_life_expectancy=spouse_life_expectancy,
            inflation_assumption=inflation_assumption,
            **validated_data,
        )

        # Create investment types and investments
        for investment_data in investments_data:
            investment_type_data = investment_data.pop("investment_type")
            return_dist_data = investment_type_data.pop("return_distribution")
            income_dist_data = investment_type_data.pop("income_distribution")

            return_dist = Distribution.objects.create(**return_dist_data)
            income_dist = Distribution.objects.create(**income_dist_data)

            investment_type, created = InvestmentType.objects.get_or_create(
                name=investment_type_data["name"],
                defaults={
                    **investment_type_data,
                    "return_distribution": return_dist,
                    "income_distribution": income_dist,
                },
            )

            Investment.objects.create(
                scenario=scenario, investment_type=investment_type, **investment_data
            )

        # Create event series
        for event_data in event_series_data:
            start_dist_data = event_data.pop("start_distribution", None)
            duration_dist_data = event_data.pop("duration_distribution")
            change_dist_data = event_data.pop("change_distribution", None)

            # Remove input fields and asset allocation data
            event_data.pop("start_with_event_name_input", None)
            event_data.pop("start_after_event_name_input", None)
            asset_allocation_input = event_data.pop("asset_allocation_input", {})
            asset_allocation2_input = event_data.pop("asset_allocation2_input", {})

            start_dist = None
            if start_dist_data:
                start_dist = Distribution.objects.create(**start_dist_data)

            duration_dist = Distribution.objects.create(**duration_dist_data)

            change_dist = None
            if change_dist_data:
                change_dist = Distribution.objects.create(**change_dist_data)

            event_series = EventSeries.objects.create(
                scenario=scenario,
                start_distribution=start_dist,
                duration_distribution=duration_dist,
                change_distribution=change_dist,
                **event_data,
            )

            # Create asset allocations if provided
            if asset_allocation_input:
                for investment_id, percentage in asset_allocation_input.items():
                    investment = scenario.investments.get(investment_id=investment_id)
                    AssetAllocation.objects.create(
                        event_series=event_series,
                        investment=investment,
                        percentage=percentage,
                        is_final_allocation=False,
                    )

            if asset_allocation2_input:
                for investment_id, percentage in asset_allocation2_input.items():
                    investment = scenario.investments.get(investment_id=investment_id)
                    AssetAllocation.objects.create(
                        event_series=event_series,
                        investment=investment,
                        percentage=percentage,
                        is_final_allocation=True,
                    )

        # Create strategy items
        for order, event_name in enumerate(spending_strategy_input, 1):
            event_series = scenario.event_series.get(name=event_name)
            SpendingStrategyItem.objects.create(
                scenario=scenario, event_series=event_series, order=order
            )

        for order, investment_id in enumerate(expense_withdrawal_strategy_input, 1):
            investment = scenario.investments.get(investment_id=investment_id)
            ExpenseWithdrawalStrategyItem.objects.create(
                scenario=scenario, investment=investment, order=order
            )

        for order, investment_id in enumerate(rmd_strategy_input, 1):
            investment = scenario.investments.get(investment_id=investment_id)
            RMDStrategyItem.objects.create(
                scenario=scenario, investment=investment, order=order
            )

        for order, investment_id in enumerate(roth_conversion_strategy_input, 1):
            investment = scenario.investments.get(investment_id=investment_id)
            RothConversionStrategyItem.objects.create(
                scenario=scenario, investment=investment, order=order
            )

        return scenario

    def update(self, instance, validated_data):
        # Handle updates - similar structure but updating existing objects
        # This would require careful handling of nested objects and relationships
        # For brevity, implementing basic field updates

        for attr, value in validated_data.items():
            if attr not in [
                "user_life_expectancy",
                "spouse_life_expectancy",
                "inflation_assumption",
                "investments",
                "event_series",
            ]:
                setattr(instance, attr, value)

        instance.save()
        return instance
