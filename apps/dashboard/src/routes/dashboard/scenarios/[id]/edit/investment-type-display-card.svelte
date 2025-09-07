<script lang="ts">
  import * as Card from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Button } from '$lib/components/ui/button';
  import { Separator } from '$lib/components/ui/separator';
  import { Edit, Trash2, TrendingUp, DollarSign, Percent, Shield, ShieldOff } from '@lucide/svelte';
  import type { InvestmentType, Distribution } from '$lib/server/db/schema/schema';

  interface Props {
    investmentType: InvestmentType;
    onEdit?: (investmentType: InvestmentType) => void;
    onDelete?: (id: string) => void;
    onAdd?: () => void;
    readonly?: boolean;
  }

  let { investmentType, onEdit, onDelete, onAdd, readonly = false }: Props = $props();

  function formatDistribution(dist: Distribution): string {
    switch (dist.type) {
      case 'fixed':
        return `${(dist.value! * 100).toFixed(2)}%`;
      case 'normal':
        return `μ=${(dist.mean! * 100).toFixed(1)}%, σ=${(dist.stdev! * 100).toFixed(1)}%`;
      case 'uniform':
        return `${(dist.min! * 100).toFixed(1)}% - ${(dist.max! * 100).toFixed(1)}%`;
      default:
        return 'Unknown';
    }
  }

  function formatDistributionDollars(dist: Distribution): string {
    switch (dist.type) {
      case 'fixed':
        return `$${dist.value!.toFixed(2)}`;
      case 'normal':
        return `μ=$${dist.mean!.toFixed(2)}, σ=$${dist.stdev!.toFixed(2)}`;
      case 'uniform':
        return `$${dist.min!.toFixed(2)} - $${dist.max!.toFixed(2)}`;
      default:
        return 'Unknown';
    }
  }

  function getDistributionColor(type: string): 'default' | 'secondary' | 'outline' {
    switch (type) {
      case 'fixed':
        return 'default';
      case 'normal':
        return 'secondary';
      case 'uniform':
        return 'outline';
      default:
        return 'default';
    }
  }

  function formatExpenseRatio(ratio: string): string {
    return `${parseFloat(ratio).toFixed(2)}%`;
  }
</script>

<Card.Root>
  <Card.Header class="pb-3">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="mb-2 flex items-center gap-2">
          <Card.Title class="text-lg">{investmentType.name}</Card.Title>
          <div class="flex gap-1">
            {#if investmentType.isCash}
              <Badge variant="default" class="bg-green-100 text-green-800 hover:bg-green-100">
                <DollarSign class="mr-1 h-3 w-3" />
                Cash
              </Badge>
            {/if}
            {#if investmentType.taxability === 'tax_exempt'}
              <Badge variant="secondary" class="bg-blue-100 text-blue-800 hover:bg-blue-100">
                <Shield class="mr-1 h-3 w-3" />
                Tax Exempt
              </Badge>
            {:else}
              <Badge variant="outline">
                <ShieldOff class="mr-1 h-3 w-3" />
                Taxable
              </Badge>
            {/if}
          </div>
        </div>
        {#if investmentType.description}
          <Card.Description class="text-sm">
            {investmentType.description}
          </Card.Description>
        {/if}
      </div>
      {#if !readonly}
        <div class="flex gap-1">
          {#if onEdit}
            <Button variant="ghost" size="sm" onclick={() => onEdit?.(investmentType)}>
              <Edit class="h-4 w-4" />
            </Button>
          {/if}
          {#if onDelete}
            <Button variant="ghost" size="sm" onclick={() => onDelete?.(investmentType.id)}>
              <Trash2 class="h-4 w-4" />
            </Button>
          {/if}
        </div>
      {/if}
    </div>
  </Card.Header>

  <Card.Content class="pt-0">
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <!-- Expected Annual Return -->
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <TrendingUp class="h-4 w-4 text-green-600" />
          <span class="text-sm font-medium">Expected Annual Return</span>
        </div>
        <div class="flex items-center gap-2">
          <Badge
            variant={getDistributionColor(investmentType.expectedAnnualReturn.type)}
            class="text-xs"
          >
            {investmentType.expectedAnnualReturn.type.toUpperCase()}
          </Badge>
          <span class="font-mono text-sm">
            {formatDistribution(investmentType.expectedAnnualReturn)}
          </span>
        </div>
      </div>

      <!-- Expected Annual Income -->
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <DollarSign class="h-4 w-4 text-blue-600" />
          <span class="text-sm font-medium">Expected Annual Income</span>
        </div>
        <div class="flex items-center gap-2">
          <Badge
            variant={getDistributionColor(investmentType.expectedAnnualIncome.type)}
            class="text-xs"
          >
            {investmentType.expectedAnnualIncome.type.toUpperCase()}
          </Badge>
          <span class="font-mono text-sm">
            {formatDistribution(investmentType.expectedAnnualIncome)}
          </span>
        </div>
      </div>

      <!-- Expense Ratio -->
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <Percent class="h-4 w-4 text-orange-600" />
          <span class="text-sm font-medium">Expense Ratio</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="font-mono text-sm">
            {formatExpenseRatio(investmentType.expenseRatio)}
          </span>
        </div>
      </div>
    </div>

    <!-- Distribution Details Expandable Section -->
    <Separator class="my-4" />

    <div class="grid grid-cols-1 gap-4 text-xs text-muted-foreground md:grid-cols-2">
      <div>
        <span class="font-medium">Return Distribution:</span>
        {#if investmentType.expectedAnnualReturn.type === 'fixed'}
          Fixed at {formatDistribution(investmentType.expectedAnnualReturn)}
        {:else if investmentType.expectedAnnualReturn.type === 'normal'}
          Normal distribution with mean {(investmentType.expectedAnnualReturn.mean! * 100).toFixed(
            1
          )}% and standard deviation {(investmentType.expectedAnnualReturn.stdev! * 100).toFixed(
            1
          )}%
        {:else if investmentType.expectedAnnualReturn.type === 'uniform'}
          Uniform distribution between {(investmentType.expectedAnnualReturn.min! * 100).toFixed(
            1
          )}% and {(investmentType.expectedAnnualReturn.max! * 100).toFixed(1)}%
        {/if}
      </div>

      <div>
        <span class="font-medium">Income Distribution:</span>
        {#if investmentType.expectedAnnualIncome.type === 'fixed'}
          Fixed at {formatDistribution(investmentType.expectedAnnualIncome)}
        {:else if investmentType.expectedAnnualIncome.type === 'normal'}
          Normal distribution with mean {(investmentType.expectedAnnualIncome.mean! * 100).toFixed(
            1
          )}% and standard deviation {(investmentType.expectedAnnualIncome.stdev! * 100).toFixed(
            1
          )}%
        {:else if investmentType.expectedAnnualIncome.type === 'uniform'}
          Uniform distribution between {(investmentType.expectedAnnualIncome.min! * 100).toFixed(
            1
          )}% and {(investmentType.expectedAnnualIncome.max! * 100).toFixed(1)}%
        {/if}
      </div>
    </div>
  </Card.Content>
</Card.Root>
