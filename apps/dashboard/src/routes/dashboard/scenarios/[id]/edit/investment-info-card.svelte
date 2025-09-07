<script lang="ts">
  import * as Card from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Button } from '$lib/components/ui/button';
  import { Progress } from '$lib/components/ui/progress';
  import { Edit, Trash2, Wallet, PiggyBank, Building2, Shield, ShieldOff } from '@lucide/svelte';
  import type { Investment, InvestmentType } from '$lib/server/db/schema/schema';

  interface Props {
    investments: Investment[];
    investmentTypes: InvestmentType[];
    onEdit?: (investment: Investment) => void;
    onDelete?: (id: string) => void;
    onAdd?: () => void;
    readonly?: boolean;
    showProgress?: boolean;
  }

  let {
    investments,
    investmentTypes,
    onEdit,
    onDelete,
    onAdd,
    readonly = false,
    showProgress = true
  }: Props = $props();

  // Create lookup map for investment types
  const investmentTypeMap = $derived(
    investmentTypes.reduce(
      (map, type) => {
        map[type.id] = type;
        return map;
      },
      {} as Record<string, InvestmentType>
    )
  );

  // Calculate totals
  const totalValue = $derived(investments.reduce((sum, inv) => sum + Number(inv.currentValue), 0));
  const totalsByTaxStatus = $derived(() => {
    const totals = {
      non_retirement: 0,
      pre_tax_retirement: 0,
      after_tax_retirement: 0
    };
    investments.forEach((inv) => {
      totals[inv.accountTaxStatus] += Number(inv.currentValue);
    });
    return totals;
  });

  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  function formatPercentage(value: number, total: number): string {
    if (total === 0) return '0.0%';
    return `${((value / total) * 100).toFixed(1)}%`;
  }

  function getTaxStatusIcon(taxStatus: string) {
    switch (taxStatus) {
      case 'non_retirement':
        return Wallet;
      case 'pre_tax_retirement':
        return PiggyBank;
      case 'after_tax_retirement':
        return Building2;
      default:
        return Wallet;
    }
  }

  function getTaxStatusLabel(taxStatus: string): string {
    switch (taxStatus) {
      case 'non_retirement':
        return 'Taxable';
      case 'pre_tax_retirement':
        return 'Pre-Tax Retirement';
      case 'after_tax_retirement':
        return 'After-Tax Retirement (Roth)';
      default:
        return taxStatus;
    }
  }

  function getTaxStatusColor(taxStatus: string): 'default' | 'destructive' | 'secondary' {
    switch (taxStatus) {
      case 'non_retirement':
        return 'default';
      case 'pre_tax_retirement':
        return 'destructive';
      case 'after_tax_retirement':
        return 'secondary';
      default:
        return 'default';
    }
  }

  // Group investments by tax status
  const investmentsByTaxStatus = $derived(() => {
    const grouped: Record<string, Investment[]> = {
      non_retirement: [],
      pre_tax_retirement: [],
      after_tax_retirement: []
    };

    investments.forEach((investment) => {
      grouped[investment.accountTaxStatus].push(investment);
    });

    return grouped;
  });
</script>

<Card.Root>
  <Card.Header>
    <div class="flex items-center justify-between">
      <div>
        <Card.Title class="flex items-center gap-2">
          <Wallet class="h-5 w-5" />
          Investments
        </Card.Title>
        <Card.Description>Current investment holdings across all account types</Card.Description>
      </div>
      {#if !readonly && onAdd}
        <Button onclick={onAdd} size="sm">Add Investment</Button>
      {/if}
    </div>
  </Card.Header>

  <Card.Content>
    {#if investments.length === 0}
      <div class="py-8 text-center text-muted-foreground">
        <Wallet class="mx-auto mb-4 h-12 w-12 opacity-50" />
        <p class="text-lg font-medium">No Investments</p>
        <p class="text-sm">Add investments to define your current financial position.</p>
        {#if !readonly && onAdd}
          <Button onclick={onAdd} class="mt-4" variant="outline">Add Your First Investment</Button>
        {/if}
      </div>
    {:else}
      <!-- Summary Section -->
      {#if showProgress && totalValue > 0}
        <div class="mb-6 rounded-lg bg-muted/50 p-4">
          <div class="mb-3 flex items-center justify-between">
            <h3 class="text-lg font-semibold">Portfolio Summary</h3>
            <span class="text-2xl font-bold">{formatCurrency(totalValue)}</span>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span>Taxable Accounts</span>
                <span class="font-medium">{formatCurrency(totalsByTaxStatus().non_retirement)}</span
                >
              </div>
              <Progress
                value={(totalsByTaxStatus().non_retirement / totalValue) * 100}
                class="h-2"
              />
              <span class="text-xs text-muted-foreground"
                >{formatPercentage(totalsByTaxStatus().non_retirement, totalValue)}</span
              >
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span>Pre-Tax Retirement</span>
                <span class="font-medium"
                  >{formatCurrency(totalsByTaxStatus().pre_tax_retirement)}</span
                >
              </div>
              <Progress
                value={(totalsByTaxStatus().pre_tax_retirement / totalValue) * 100}
                class="h-2"
              />
              <span class="text-xs text-muted-foreground"
                >{formatPercentage(totalsByTaxStatus().pre_tax_retirement, totalValue)}</span
              >
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span>After-Tax Retirement</span>
                <span class="font-medium"
                  >{formatCurrency(totalsByTaxStatus().after_tax_retirement)}</span
                >
              </div>
              <Progress
                value={(totalsByTaxStatus().after_tax_retirement / totalValue) * 100}
                class="h-2"
              />
              <span class="text-xs text-muted-foreground"
                >{formatPercentage(totalsByTaxStatus().after_tax_retirement, totalValue)}</span
              >
            </div>
          </div>
        </div>
      {/if}

      <!-- Investments by Tax Status -->
      <div class="space-y-6">
        {#each Object.entries(investmentsByTaxStatus) as [taxStatus, statusInvestments]}
          {#if statusInvestments.length > 0}
            <div class="space-y-3">
              <div class="flex items-center gap-2">
                {#snippet icon()}
                  {@const IconComponent = getTaxStatusIcon(taxStatus)}
                  <IconComponent class="h-4 w-4" />
                {/snippet}
                {@render icon()}
                <h3 class="text-sm font-semibold tracking-wide text-muted-foreground uppercase">
                  {getTaxStatusLabel(taxStatus)}
                </h3>
                <Badge variant={getTaxStatusColor(taxStatus)} class="text-xs">
                  {formatCurrency(totalsByTaxStatus[taxStatus as keyof typeof totalsByTaxStatus])}
                </Badge>
              </div>

              <div class="grid gap-3">
                {#each statusInvestments as investment}
                  {@const investmentType = investmentTypeMap[investment.investmentTypeId]}
                  <Card.Root
                    class="border-l-4 {taxStatus === 'non_retirement'
                      ? 'border-l-blue-500'
                      : taxStatus === 'pre_tax_retirement'
                        ? 'border-l-red-500'
                        : 'border-l-green-500'}"
                  >
                    <Card.Content class="pt-4">
                      <div class="flex items-center justify-between">
                        <div class="flex-1">
                          <div class="mb-2 flex items-center gap-2">
                            <h4 class="font-semibold">{investment.name}</h4>
                            <div class="flex gap-1">
                              {#if investmentType?.isCash}
                                <Badge
                                  variant="default"
                                  class="bg-green-100 text-xs text-green-800 hover:bg-green-100"
                                >
                                  Cash
                                </Badge>
                              {/if}
                              {#if investmentType?.taxability === 'tax_exempt'}
                                <Badge
                                  variant="secondary"
                                  class="bg-blue-100 text-xs text-blue-800 hover:bg-blue-100"
                                >
                                  <Shield class="mr-1 h-3 w-3" />
                                  Tax Exempt
                                </Badge>
                              {:else if investmentType?.taxability === 'taxable'}
                                <Badge variant="outline" class="text-xs">
                                  <ShieldOff class="mr-1 h-3 w-3" />
                                  Taxable
                                </Badge>
                              {/if}
                            </div>
                          </div>

                          <div class="flex items-center justify-between">
                            <div class="text-sm text-muted-foreground">
                              {#if investmentType}
                                Type: {investmentType.name}
                              {:else}
                                Unknown investment type
                              {/if}
                            </div>
                            <div class="flex items-center gap-4">
                              <span class="text-lg font-bold"
                                >{formatCurrency(investment.currentValue)}</span
                              >
                              <span class="text-sm text-muted-foreground">
                                {formatPercentage(investment.currentValue, totalValue)}
                              </span>
                            </div>
                          </div>
                        </div>

                        {#if !readonly}
                          <div class="ml-4 flex gap-1">
                            {#if onEdit}
                              <Button
                                variant="ghost"
                                size="sm"
                                onclick={() => onEdit?.(investment)}
                              >
                                <Edit class="h-4 w-4" />
                              </Button>
                            {/if}
                            {#if onDelete}
                              <Button
                                variant="ghost"
                                size="sm"
                                onclick={() => onDelete?.(investment.id)}
                              >
                                <Trash2 class="h-4 w-4" />
                              </Button>
                            {/if}
                          </div>
                        {/if}
                      </div>
                    </Card.Content>
                  </Card.Root>
                {/each}
              </div>
            </div>
          {/if}
        {/each}
      </div>
    {/if}
  </Card.Content>
</Card.Root>
