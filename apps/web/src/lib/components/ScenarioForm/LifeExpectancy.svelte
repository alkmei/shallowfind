<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Switch } from '$lib/components/ui/switch';

  const { form } = $props();
  const { form: formData } = form;

  let isNormalDistribution = $state($formData.userLifeExpectancy?.type === 'normal');

  // Update form data when switch changes
  $effect(() => {
    if (isNormalDistribution) {
      $formData.userLifeExpectancy.type = 'normal';
      // Clear fixed value when switching to normal
      $formData.userLifeExpectancy.value = null;
    } else {
      $formData.userLifeExpectancy.type = 'fixed';
      // Clear normal distribution values when switching to fixed
      $formData.userLifeExpectancy.mean = null;
      $formData.userLifeExpectancy.stdev = null;
    }
  });
</script>

<div class="space-y-4">
  <!-- Distribution Type Switch -->
  <div class="flex items-center space-x-2">
    <Label for="distribution-switch">Use Normal Distribution</Label>
    <Switch id="distribution-switch" bind:checked={isNormalDistribution} />
    <span class="text-muted-foreground text-sm">
      {isNormalDistribution ? 'Normal (mean ± std dev)' : 'Fixed value'}
    </span>
  </div>

  <!-- Life Expectancy Fields -->
  <div class="space-y-3">
    <h4 class="text-sm font-medium">
      Life Expectancy <span class="text-red-500">*</span>
    </h4>

    {#if isNormalDistribution}
      <!-- Normal Distribution Fields -->
      <div class="grid grid-cols-2 gap-3">
        <Form.Field {form} name="userLifeExpectancy.mean">
          <Form.Control>
            <Form.Label>Mean Age</Form.Label>
            <Input
              type="number"
              bind:value={$formData.userLifeExpectancy.mean}
              min="1"
              max="120"
              placeholder="e.g., 78"
            />
          </Form.Control>
          <Form.FieldErrors />
          <Form.Description>
            Normal distribution allows for uncertainty in life expectancy. Most values will fall
            within 2 standard deviations of the mean.
          </Form.Description>
        </Form.Field>

        <Form.Field {form} name="userLifeExpectancy.stdev">
          <Form.Control>
            <Form.Label>Standard Deviation</Form.Label>
            <Input
              type="number"
              bind:value={$formData.userLifeExpectancy.stdev}
              min="0.1"
              max="20"
              step="0.1"
              placeholder="e.g., 5"
            />
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
      </div>
    {:else}
      <!-- Fixed Distribution Field -->
      <Form.Field {form} name="userLifeExpectancy.value">
        <Form.Control>
          <Form.Label>Life Expectancy (Years)</Form.Label>
          <Input
            type="number"
            bind:value={$formData.userLifeExpectancy.value}
            min="1"
            max="120"
            placeholder="e.g., 78"
          />
        </Form.Control>
        <Form.Description>Enter a fixed life expectancy value in years.</Form.Description>
        <Form.FieldErrors />
      </Form.Field>
    {/if}
  </div>
</div>
