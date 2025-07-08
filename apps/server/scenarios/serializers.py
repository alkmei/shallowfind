from rest_framework import serializers
from .models import (
    Scenario,
    InvestmentType,
    Investment,
    EventSeries,
    AssetAllocation,
    SpendingStrategyItem,
    ExpenseWithdrawalStrategyItem,
    RMDStrategyItem,
    RothConversionStrategyItem,
)


class DistributionSerializer(serializers.Serializer):
    """Serializer for distribution JSON field"""

    type = serializers.ChoiceField(choices=["fixed", "normal", "uniform"])
    value = serializers.FloatField(required=False, allow_null=True)
    mean = serializers.FloatField(required=False, allow_null=True)
    stdev = serializers.FloatField(required=False, allow_null=True)
    lower = serializers.FloatField(required=False, allow_null=True)
    upper = serializers.FloatField(required=False, allow_null=True)

    def validate(self, attrs):
        dist_type = attrs.get("type")

        if dist_type == "fixed":
            if attrs.get("value") is None:
                raise serializers.ValidationError("Fixed distribution requires 'value'")
        elif dist_type == "normal":
            if attrs.get("mean") is None or attrs.get("stdev") is None:
                raise serializers.ValidationError(
                    "Normal distribution requires 'mean' and 'stdev'"
                )
            if attrs.get("stdev", 0) <= 0:
                raise serializers.ValidationError("Standard deviation must be positive")
        elif dist_type == "uniform":
            if attrs.get("lower") is None or attrs.get("upper") is None:
                raise serializers.ValidationError(
                    "Uniform distribution requires 'lower' and 'upper'"
                )
            if attrs.get("lower", 0) >= attrs.get("upper", 1):
                raise serializers.ValidationError(
                    "Upper bound must be greater than lower bound"
                )

        return attrs


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
            "description",
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

        # Create scenario
        scenario = Scenario.objects.create(
            **validated_data,
        )

        # Create investment types and investments
        for investment_data in investments_data:
            investment_type_data = investment_data.pop("investment_type")

            investment_type, created = InvestmentType.objects.get_or_create(
                scenario=scenario,
                name=investment_type_data["name"],
                defaults=investment_type_data,
            )

            Investment.objects.create(
                scenario=scenario, investment_type=investment_type, **investment_data
            )

        # Create event series
        for event_data in event_series_data:
            event_data.pop("start_with_event_name_input", None)
            event_data.pop("start_after_event_name_input", None)
            asset_allocation_input = event_data.pop("asset_allocation_input", {})
            asset_allocation2_input = event_data.pop("asset_allocation2_input", {})

            event_series = EventSeries.objects.create(scenario=scenario, **event_data)
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
