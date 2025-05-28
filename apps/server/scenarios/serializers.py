from rest_framework import serializers
from .models import (
    Distribution,
    Scenario,
    Person,
    InvestmentType,
    Investment,
    AssetAllocation,
    InvestmentAllocation,
    EventSeries,
    SpendingStrategy,
    ExpenseWithdrawalStrategy,
    RMDStrategy,
    RothConversionOptimizer,
)


class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = [
            "type",
            "value",
            "mean",
            "stdev",
            "lower",
            "upper",
        ]  # fixed/normal/uniform params [1]


class PersonSerializer(serializers.ModelSerializer):
    lifeExpectancy = DistributionSerializer(source="life_expectancy")

    class Meta:
        model = Person
        fields = [
            "birth_year",
            "role",
            "lifeExpectancy",
        ]  # maps birthYears & lifeExpectancy in YAML [2]


class InvestmentTypeSerializer(serializers.ModelSerializer):
    returnDistribution = DistributionSerializer(source="return_distribution")
    incomeDistribution = DistributionSerializer(source="income_distribution")

    class Meta:
        model = InvestmentType
        fields = [
            "name",
            "description",
            "returnDistribution",
            "expense_ratio",
            "incomeDistribution",
            "taxability",
        ]


class InvestmentSerializer(serializers.ModelSerializer):
    investmentType = serializers.SlugRelatedField(
        slug_field="name",
        queryset=InvestmentType.objects.all(),
        source="investment_type",
    )
    taxStatus = serializers.ChoiceField(
        choices=Investment.TAX_STATUS_CHOICES, source="tax_status"
    )
    id = serializers.CharField()  # allows YAML id field

    class Meta:
        model = Investment
        fields = ["investmentType", "value", "taxStatus", "id"]


class InvestmentAllocationSerializer(serializers.ModelSerializer):
    investment = serializers.SlugRelatedField(
        slug_field="id", queryset=Investment.objects.all()
    )
    percentage = serializers.FloatField()
    role = serializers.CharField()

    class Meta:
        model = InvestmentAllocation
        fields = ["investment", "percentage", "role"]


class AssetAllocationSerializer(serializers.ModelSerializer):
    investment_allocations = InvestmentAllocationSerializer(
        many=True, source="investment_allocations"
    )

    class Meta:
        model = AssetAllocation
        fields = ["type", "investment_allocations"]


class EventSeriesSerializer(serializers.ModelSerializer):
    start = DistributionSerializer(source="start_distribution")
    duration = DistributionSerializer(source="duration")
    changeDistribution = DistributionSerializer(source="expected_annual_change")
    assetAllocation = AssetAllocationSerializer(
        source="asset_allocation", required=False
    )
    assetAllocation2 = AssetAllocationSerializer(
        source="asset_allocation__glide", required=False
    )

    class Meta:
        model = EventSeries
        fields = [
            "name",
            "start",
            "duration",
            "type",
            "initial_amount",
            "changeDistribution",
            "inflation_adjusted",
            "user_fraction",
            "socialSecurity",
            "discretionary",
            "assetAllocation",
            "assetAllocation2",
            "max_cash",
        ]


class SpendingStrategySerializer(serializers.ModelSerializer):
    spendingStrategy = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field="name",
            queryset=EventSeries.objects.filter(type=EventSeries.EXPENSE),
        ),
        source="expense_order",
    )

    class Meta:
        model = SpendingStrategy
        fields = ["spendingStrategy"]


class ExpenseWithdrawalStrategySerializer(serializers.ModelSerializer):
    expenseWithdrawalStrategy = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field="id", queryset=Investment.objects.all()
        ),
        source="withdrawal_order",
    )

    class Meta:
        model = ExpenseWithdrawalStrategy
        fields = ["expenseWithdrawalStrategy"]


class RMDStrategySerializer(serializers.ModelSerializer):
    RMDStrategy = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field="id",
            queryset=Investment.objects.filter(account_type=Investment.PRE_TAX),
        ),
        source="withdrawal_order",
    )

    class Meta:
        model = RMDStrategy
        fields = ["RMDStrategy"]


class RothConversionSerializer(serializers.ModelSerializer):
    RothConversionOpt = serializers.BooleanField(source="enabled")
    RothConversionStart = serializers.IntegerField(source="start_year")
    RothConversionEnd = serializers.IntegerField(source="end_year")
    RothConversionStrategy = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field="id",
            queryset=Investment.objects.filter(account_type=Investment.PRE_TAX),
        ),
        source="conversion_order",
    )

    class Meta:
        model = RothConversionOptimizer
        fields = [
            "RothConversionOpt",
            "RothConversionStart",
            "RothConversionEnd",
            "RothConversionStrategy",
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    maritalStatus = serializers.CharField(source="marital_status")
    birthYears = serializers.ListField(
        child=serializers.IntegerField(), source="persons.birth_year", write_only=True
    )
    persons = PersonSerializer(many=True, read_only=True)
    lifeExpectancy = DistributionSerializer(
        source="persons.life_expectancy", many=True, write_only=True
    )
    investmentTypes = InvestmentTypeSerializer(many=True, source="investment_types")
    investments = InvestmentSerializer(many=True, source="investments")
    eventSeries = EventSeriesSerializer(many=True, source="event_series")
    spendingStrategy = SpendingStrategySerializer(
        source="spendingstrategy", read_only=True
    )
    expenseWithdrawalStrategy = ExpenseWithdrawalStrategySerializer(
        source="expensewithdrawalstrategy", read_only=True
    )
    RMDStrategy = RMDStrategySerializer(source="rmdstrategy", read_only=True)
    RothConversion = RothConversionSerializer(
        source="rothconversionoptimizer", read_only=True
    )
    financialGoal = serializers.DecimalField(
        max_digits=19, decimal_places=4, source="financial_goal.amount"
    )
    residenceState = serializers.CharField(source="residence_state")

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
            "spendingStrategy",
            "expenseWithdrawalStrategy",
            "RMDStrategy",
            "RothConversion",
            "financialGoal",
            "residenceState",
        ]

    def create(self, validated_data):
        # Pop nested blocks
        persons_data = validated_data.pop("persons", [])
        types_data = validated_data.pop("investment_types", [])
        inv_data = validated_data.pop("investments", [])
        events_data = validated_data.pop("event_series", [])

        scenario = Scenario.objects.create(**validated_data)

        # Persons & distributions
        for person_attrs, life_dist in zip(
            persons_data, validated_data.get("lifeExpectancy", [])
        ):
            dist = Distribution.objects.create(**life_dist)
            Person.objects.create(
                scenario=scenario, **person_attrs, life_expectancy=dist
            )

        # Investment types
        for it in types_data:
            dist_r = Distribution.objects.create(**it.pop("return_distribution"))
            dist_i = Distribution.objects.create(**it.pop("income_distribution"))
            InvestmentType.objects.create(
                scenario=scenario,
                return_distribution=dist_r,
                income_distribution=dist_i,
                **it,
            )

        # Investments
        for inv in inv_data:
            Investment.objects.create(scenario=scenario, **inv)

        # Event series
        for ev in events_data:
            # create distributions
            sd = Distribution.objects.create(**ev.pop("start_distribution"))
            du = Distribution.objects.create(**ev.pop("duration"))
            ch = Distribution.objects.create(**ev.pop("expected_annual_change"))
            allocation = ev.pop("asset_allocation", None)
            evs = EventSeries.objects.create(
                scenario=scenario,
                start_distribution=sd,
                duration=du,
                expected_annual_change=ch,
                **ev,
            )
            if allocation:
                # assetAllocation and optional glide path
                aa = AssetAllocation.objects.create(type=allocation.pop("type"))
                for ia in allocation.pop("investment_allocations"):
                    inv = Investment.objects.get(id=ia["investment"])
                    InvestmentAllocation.objects.create(
                        asset_allocation=aa,
                        investment=inv,
                        percentage=ia["percentage"],
                        role=ia["role"],
                    )
                evs.asset_allocation = aa
                evs.save()

        return scenario
