from rest_framework import serializers
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


class DistributionSerializer(serializers.ModelSerializer):
    """Serializer for probability distributions"""

    class Meta:
        model = Distribution
        fields = ["type", "value", "mean", "stdev", "lower", "upper"]

    def to_representation(self, instance):
        """Custom representation to match YAML format"""
        data = {"type": instance.type}

        if instance.type == "fixed":
            data["value"] = instance.value
        elif instance.type == "normal":
            data["mean"] = instance.mean
            data["stdev"] = instance.stdev
        elif instance.type == "uniform":
            data["lower"] = instance.lower
            data["upper"] = instance.upper

        return data

    def create(self, validated_data):
        """Create distribution with proper field validation"""
        return Distribution.objects.create(**validated_data)


class InvestmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for investment types"""

    returnDistribution = DistributionSerializer()
    incomeDistribution = DistributionSerializer()

    # Map YAML field names to model field names
    returnAmtOrPct = serializers.CharField(source="return_amt_or_pct")
    incomeAmtOrPct = serializers.CharField(source="income_amt_or_pct")
    expenseRatio = serializers.FloatField(source="expense_ratio")

    class Meta:
        model = InvestmentType
        fields = [
            "name",
            "description",
            "returnAmtOrPct",
            "returnDistribution",
            "expenseRatio",
            "incomeAmtOrPct",
            "incomeDistribution",
            "taxability",
        ]

    def create(self, validated_data):
        return_dist_data = validated_data.pop("returnDistribution")
        income_dist_data = validated_data.pop("incomeDistribution")

        return_dist = Distribution.objects.create(**return_dist_data)
        income_dist = Distribution.objects.create(**income_dist_data)

        return InvestmentType.objects.create(
            return_distribution=return_dist,
            income_distribution=income_dist,
            **validated_data
        )


class InvestmentSerializer(serializers.ModelSerializer):
    """Serializer for individual investments"""

    investmentType = serializers.CharField(source="investment_type.name")
    taxStatus = serializers.CharField(source="tax_status")
    id = serializers.CharField(source="investment_id")

    class Meta:
        model = Investment
        fields = ["investmentType", "value", "taxStatus", "id"]

    def create(self, validated_data):
        investment_type_name = validated_data.pop("investment_type")["name"]
        investment_type = InvestmentType.objects.get(name=investment_type_name)

        return Investment.objects.create(
            investment_type=investment_type,
            investment_id=validated_data.pop("investment_id"),
            **validated_data
        )


class AssetAllocationSerializer(serializers.ModelSerializer):
    """Serializer for asset allocations within event series"""

    class Meta:
        model = AssetAllocation
        fields = ["investment", "percentage", "is_final_allocation"]

    def to_representation(self, instance):
        """Return as investment_id: percentage format"""
        return {instance.investment.investment_id: instance.percentage}


class EventSeriesSerializer(serializers.ModelSerializer):
    """Serializer for event series with complex nested data"""

    # Distribution fields
    start = DistributionSerializer(source="start_distribution", required=False)
    duration = DistributionSerializer(source="duration_distribution")
    changeDistribution = DistributionSerializer(
        source="change_distribution", required=False
    )

    # Asset allocation handling
    assetAllocation = serializers.SerializerMethodField()
    assetAllocation2 = serializers.SerializerMethodField()
    glidePath = serializers.BooleanField(source="glide_path", required=False)

    # Field mappings for YAML compatibility
    initialAmount = serializers.FloatField(source="initial_amount", required=False)
    changeAmtOrPct = serializers.CharField(source="change_amt_or_pct", required=False)
    inflationAdjusted = serializers.BooleanField(
        source="inflation_adjusted", required=False
    )
    userFraction = serializers.FloatField(source="user_fraction", required=False)
    socialSecurity = serializers.BooleanField(source="social_security", required=False)
    maxCash = serializers.FloatField(source="max_cash", required=False)

    class Meta:
        model = EventSeries
        fields = [
            "name",
            "start",
            "duration",
            "type",
            "initialAmount",
            "changeAmtOrPct",
            "changeDistribution",
            "inflationAdjusted",
            "userFraction",
            "socialSecurity",
            "discretionary",
            "assetAllocation",
            "glidePath",
            "assetAllocation2",
            "maxCash",
        ]

    def get_assetAllocation(self, obj):
        """Get initial asset allocation as dict"""
        if obj.type in ["invest", "rebalance"]:
            allocations = obj.asset_allocations.filter(is_final_allocation=False)
            return {
                alloc.investment.investment_id: alloc.percentage
                for alloc in allocations
            }
        return None

    def get_assetAllocation2(self, obj):
        """Get final asset allocation for glide path"""
        if obj.type in ["invest", "rebalance"] and obj.glide_path:
            allocations = obj.asset_allocations.filter(is_final_allocation=True)
            return {
                alloc.investment.investment_id: alloc.percentage
                for alloc in allocations
            }
        return None

    def to_representation(self, instance):
        """Custom representation to handle start field variants"""
        data = super().to_representation(instance)

        # Handle different start types
        if instance.start_type == "distribution":
            data["start"] = DistributionSerializer(instance.start_distribution).data
        elif instance.start_type == "start_with":
            data["start"] = {
                "type": "startWith",
                "eventSeries": instance.start_with_event.name,
            }
        elif instance.start_type == "start_after":
            data["start"] = {
                "type": "startAfter",
                "eventSeries": instance.start_after_event.name,
            }

        # Remove None values to match YAML format
        return {k: v for k, v in data.items() if v is not None}

    def create(self, validated_data):
        # Handle nested distributions
        start_dist_data = validated_data.pop("start_distribution", None)
        duration_dist_data = validated_data.pop("duration_distribution")
        change_dist_data = validated_data.pop("change_distribution", None)

        # Create distributions
        if start_dist_data:
            start_dist = Distribution.objects.create(**start_dist_data)
            validated_data["start_distribution"] = start_dist
            validated_data["start_type"] = "distribution"

        duration_dist = Distribution.objects.create(**duration_dist_data)
        validated_data["duration_distribution"] = duration_dist

        if change_dist_data:
            change_dist = Distribution.objects.create(**change_dist_data)
            validated_data["change_distribution"] = change_dist

        return EventSeries.objects.create(**validated_data)


class SpendingStrategyItemSerializer(serializers.ModelSerializer):
    """Serializer for spending strategy items"""

    class Meta:
        model = SpendingStrategyItem
        fields = ["event_series", "order"]

    def to_representation(self, instance):
        """Return just the event series name for YAML format"""
        return instance.event_series.name


class ExpenseWithdrawalStrategyItemSerializer(serializers.ModelSerializer):
    """Serializer for expense withdrawal strategy items"""

    class Meta:
        model = ExpenseWithdrawalStrategyItem
        fields = ["investment", "order"]

    def to_representation(self, instance):
        """Return just the investment ID for YAML format"""
        return instance.investment.investment_id


class RMDStrategyItemSerializer(serializers.ModelSerializer):
    """Serializer for RMD strategy items"""

    class Meta:
        model = RMDStrategyItem
        fields = ["investment", "order"]

    def to_representation(self, instance):
        """Return just the investment ID for YAML format"""
        return instance.investment.investment_id


class RothConversionStrategyItemSerializer(serializers.ModelSerializer):
    """Serializer for Roth conversion strategy items"""

    class Meta:
        model = RothConversionStrategyItem
        fields = ["investment", "order"]

    def to_representation(self, instance):
        """Return just the investment ID for YAML format"""
        return instance.investment.investment_id


class ScenarioSerializer(serializers.ModelSerializer):
    """Main serializer for complete scenarios matching YAML format"""

    # Nested serializers
    investmentTypes = InvestmentTypeSerializer(many=True, source="investmenttype_set")
    investments = InvestmentSerializer(many=True)
    eventSeries = EventSeriesSerializer(many=True, source="event_series")

    # Distribution fields
    lifeExpectancy = serializers.SerializerMethodField()
    inflationAssumption = DistributionSerializer(source="inflation_assumption")

    # Strategy fields as ordered lists
    spendingStrategy = serializers.SerializerMethodField()
    expenseWithdrawalStrategy = serializers.SerializerMethodField()
    RMDStrategy = serializers.SerializerMethodField()
    RothConversionStrategy = serializers.SerializerMethodField()

    # Field mappings
    maritalStatus = serializers.CharField(source="marital_status")
    birthYears = serializers.SerializerMethodField()
    afterTaxContributionLimit = serializers.FloatField(
        source="after_tax_contribution_limit"
    )
    financialGoal = serializers.FloatField(source="financial_goal")
    residenceState = serializers.CharField(source="residence_state")

    # Roth conversion fields
    RothConversionOpt = serializers.BooleanField(source="roth_conversion_opt")
    RothConversionStart = serializers.IntegerField(
        source="roth_conversion_start", required=False
    )
    RothConversionEnd = serializers.IntegerField(
        source="roth_conversion_end", required=False
    )

    class Meta:
        model = Scenario
        fields = [
            "name",
            "maritalStatus",
            "birthYears",
            "lifeExpectancy",
            "investmentTypes",
            "investments",
            "eventSeries",
            "inflationAssumption",
            "afterTaxContributionLimit",
            "spendingStrategy",
            "expenseWithdrawalStrategy",
            "RMDStrategy",
            "RothConversionOpt",
            "RothConversionStart",
            "RothConversionEnd",
            "RothConversionStrategy",
            "financialGoal",
            "residenceState",
        ]

    def get_birthYears(self, obj):
        """Return birth years as list"""
        if obj.marital_status == "couple":
            return [obj.user_birth_year, obj.spouse_birth_year]
        return [obj.user_birth_year]

    def get_lifeExpectancy(self, obj):
        """Return life expectancy distributions as list"""
        result = [DistributionSerializer(obj.user_life_expectancy).data]
        if obj.marital_status == "couple" and obj.spouse_life_expectancy:
            result.append(DistributionSerializer(obj.spouse_life_expectancy).data)
        return result

    def get_spendingStrategy(self, obj):
        """Return ordered list of discretionary expense names"""
        items = obj.spending_strategy_items.all().order_by("order")
        return [item.event_series.name for item in items]

    def get_expenseWithdrawalStrategy(self, obj):
        """Return ordered list of investment IDs"""
        items = obj.expense_withdrawal_strategy_items.all().order_by("order")
        return [item.investment.investment_id for item in items]

    def get_RMDStrategy(self, obj):
        """Return ordered list of pre-tax investment IDs"""
        items = obj.rmd_strategy_items.all().order_by("order")
        return [item.investment.investment_id for item in items]

    def get_RothConversionStrategy(self, obj):
        """Return ordered list of pre-tax investment IDs"""
        items = obj.roth_conversion_strategy_items.all().order_by("order")
        return [item.investment.investment_id for item in items]
