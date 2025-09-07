<script lang="ts">
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import * as Card from '$lib/components/ui/card';
  import { Label } from '$lib/components/ui/label';
  import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Select from '$lib/components/ui/select';
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Form from '$lib/components/ui/form';
  import * as Tabs from '$lib/components/ui/tabs';
  import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
  import { Switch } from '$lib/components/ui/switch';
  import Separator from '$lib/components/ui/separator/separator.svelte';
  import { PlusCircle, Trash2, Plus } from '@lucide/svelte';
  import type { EventSeries } from '$lib/server/db/schema/schema';
  import type { PageProps } from './$types';
  import { superForm } from 'sveltekit-superforms';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import { eventSeriesCreateSchema } from './schema';

  const { data, onSubmit, form }: PageProps & { onSubmit: (es: EventSeries) => void } = $props();

  let open = $state(false);

  const eventSeriesForm = superForm(data.eventSeriesForm, {
    validators: zod4Client(eventSeriesCreateSchema),
    dataType: 'json',
    onUpdated: (event) => {
      open = false;
      const es = { ...event.form.data.eventSeries, id: form?.uuid } as EventSeries;
      onSubmit(es);
    }
  });

  let { form: formData, enhance } = eventSeriesForm;

  // Helper for start timing type options
  const startTimingOptions = [
    { value: 'distribution', label: 'Distribution' },
    { value: 'same_as_start', label: 'Same as another event start' },
    { value: 'after_end', label: 'After another event ends' }
  ];

  // Helper for event type options
  const eventTypeOptions = [
    { value: 'income', label: 'Income' },
    { value: 'expense', label: 'Expense' },
    { value: 'invest', label: 'Invest' },
    { value: 'rebalance', label: 'Rebalance' }
  ];
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger class={'w-48' + buttonVariants({ variant: 'default' })} type="button">
    <Plus /> New Event Series
  </Dialog.Trigger>
  <Dialog.Content class="max-h-screen min-w-4xl overflow-hidden">
    <Dialog.Header>
      <Dialog.Title class="text-xl font-bold">Event Series</Dialog.Title>
      <Dialog.Description>Configure the event series details below.</Dialog.Description>
    </Dialog.Header>
    <form action="?/eventSeries" method="POST" use:enhance class="max-h-fit">
      <ScrollArea class="h-[70vh] pr-2">
        <div class="flex flex-col gap-4 p-1">
          <!-- Basic Information -->
          <Card.Root>
            <Card.Header>
              <Card.Title>Basic Information</Card.Title>
            </Card.Header>
            <Card.Content class="flex flex-col gap-4">
              <Form.Field
                form={eventSeriesForm}
                name="eventSeries.name"
                class="flex flex-col gap-2"
              >
                <Form.Control>
                  <Form.Label>Name</Form.Label>
                  <Input bind:value={$formData.eventSeries.name} maxlength={255} />
                </Form.Control>
              </Form.Field>

              <Form.Field
                form={eventSeriesForm}
                name="eventSeries.description"
                class="flex flex-col gap-2"
              >
                <Form.Control>
                  <Form.Label>Description</Form.Label>
                  <Textarea bind:value={$formData.eventSeries.description} maxlength={1000} />
                </Form.Control>
              </Form.Field>

              <Form.Field
                form={eventSeriesForm}
                name="eventSeries.type"
                class="flex flex-col gap-2"
              >
                <Form.Control>
                  <Form.Label>Event Type</Form.Label>
                  <RadioGroup bind:value={$formData.eventSeries.type}>
                    {#each eventTypeOptions as option}
                      <div class="flex items-center space-x-2">
                        <RadioGroupItem value={option.value} />
                        <Label>{option.label}</Label>
                      </div>
                    {/each}
                  </RadioGroup>
                </Form.Control>
              </Form.Field>

              <div class="flex gap-4">
                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.isActive"
                  class="flex items-center gap-2"
                >
                  <Form.Control>
                    <Checkbox bind:checked={$formData.eventSeries.isActive} />
                    <Form.Label>Active</Form.Label>
                  </Form.Control>
                </Form.Field>

                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.orderIndex"
                  class="flex flex-col gap-2"
                >
                  <Form.Control>
                    <Form.Label>Order Index</Form.Label>
                    <Input type="number" bind:value={$formData.eventSeries.orderIndex} min="0" />
                  </Form.Control>
                </Form.Field>
              </div>
            </Card.Content>
          </Card.Root>

          <!-- Timing Configuration -->
          <Card.Root>
            <Card.Header>
              <Card.Title>Timing</Card.Title>
            </Card.Header>
            <Card.Content class="flex flex-col gap-4">
              <Form.Field
                form={eventSeriesForm}
                name="eventSeries.startTimingType"
                class="flex flex-col gap-2"
              >
                <Form.Control>
                  <Form.Label>Start Timing Type</Form.Label>
                  <Select.Root bind:value={$formData.eventSeries.startTimingType} type="single">
                    <Select.Trigger>Select timing type</Select.Trigger>
                    <Select.Content>
                      {#each startTimingOptions as option}
                        <Select.Item value={option.value}>{option.label}</Select.Item>
                      {/each}
                    </Select.Content>
                  </Select.Root>
                </Form.Control>
              </Form.Field>

              {#if $formData.eventSeries.startTimingType === 'distribution' && $formData.eventSeries.startYear}
                <div class="flex flex-col gap-2">
                  <Label>Start Year Distribution</Label>
                  <Tabs.Root bind:value={$formData.eventSeries.startYear.type}>
                    <Tabs.List class="w-full">
                      <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
                      <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
                      <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
                    </Tabs.List>

                    {#if $formData.eventSeries.startYear.type === 'fixed'}
                      <Tabs.Content value="fixed">
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.startYear.value"
                          class="flex flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Start Year</Form.Label>
                            <Input
                              type="number"
                              bind:value={$formData.eventSeries.startYear.value}
                            />
                          </Form.Control>
                        </Form.Field>
                      </Tabs.Content>
                    {/if}

                    {#if $formData.eventSeries.startYear.type === 'normal'}
                      <Tabs.Content value="normal" class="flex gap-3">
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.startYear.mean"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Mean Year</Form.Label>
                            <Input
                              type="number"
                              bind:value={$formData.eventSeries.startYear.mean}
                            />
                          </Form.Control>
                        </Form.Field>
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.startYear.stdev"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Standard Deviation</Form.Label>
                            <Input
                              type="number"
                              step="0.1"
                              min="0"
                              bind:value={$formData.eventSeries.startYear.stdev}
                            />
                          </Form.Control>
                        </Form.Field>
                      </Tabs.Content>
                    {/if}

                    {#if $formData.eventSeries.startYear.type === 'uniform'}
                      <Tabs.Content value="uniform" class="flex gap-3">
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.startYear.min"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Min Year</Form.Label>
                            <Input type="number" bind:value={$formData.eventSeries.startYear.min} />
                          </Form.Control>
                        </Form.Field>
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.startYear.max"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Max Year</Form.Label>
                            <Input type="number" bind:value={$formData.eventSeries.startYear.max} />
                          </Form.Control>
                        </Form.Field>
                      </Tabs.Content>
                    {/if}
                  </Tabs.Root>
                </div>
              {:else}
                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.referenceEventSeriesId"
                  class="flex flex-col gap-2"
                >
                  <Form.Control>
                    <Form.Label>Reference Event Series</Form.Label>
                    <Select.Root type="single">
                      <Select.Trigger>Select reference event</Select.Trigger>
                      <Select.Content>
                        <!-- TODO: Populate with existing event series -->
                      </Select.Content>
                    </Select.Root>
                  </Form.Control>
                </Form.Field>
              {/if}

              <div class="flex flex-col gap-2">
                <Label>Duration (Years)</Label>
                <Tabs.Root bind:value={$formData.eventSeries.duration.type}>
                  <Tabs.List class="w-full">
                    <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
                    <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
                    <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
                  </Tabs.List>

                  {#if $formData.eventSeries.duration.type === 'fixed'}
                    <Tabs.Content value="fixed">
                      <Form.Field
                        form={eventSeriesForm}
                        name="eventSeries.duration.value"
                        class="flex flex-col gap-2"
                      >
                        <Form.Control>
                          <Form.Label>Duration (Years)</Form.Label>
                          <Input
                            type="number"
                            min="1"
                            bind:value={$formData.eventSeries.duration.value}
                          />
                        </Form.Control>
                      </Form.Field>
                    </Tabs.Content>
                  {/if}

                  {#if $formData.eventSeries.duration.type === 'normal'}
                    <Tabs.Content value="normal" class="flex gap-3">
                      <Form.Field
                        form={eventSeriesForm}
                        name="eventSeries.duration.mean"
                        class="flex flex-grow flex-col gap-2"
                      >
                        <Form.Control>
                          <Form.Label>Mean Duration</Form.Label>
                          <Input
                            type="number"
                            min="1"
                            bind:value={$formData.eventSeries.duration.mean}
                          />
                        </Form.Control>
                      </Form.Field>
                      <Form.Field
                        form={eventSeriesForm}
                        name="eventSeries.duration.stdev"
                        class="flex flex-grow flex-col gap-2"
                      >
                        <Form.Control>
                          <Form.Label>Standard Deviation</Form.Label>
                          <Input
                            type="number"
                            step="0.1"
                            min="0"
                            bind:value={$formData.eventSeries.duration.stdev}
                          />
                        </Form.Control>
                      </Form.Field>
                    </Tabs.Content>
                  {/if}

                  {#if $formData.eventSeries.duration.type === 'uniform'}
                    <Tabs.Content value="uniform" class="flex gap-3">
                      <Form.Field
                        form={eventSeriesForm}
                        name="eventSeries.duration.min"
                        class="flex flex-grow flex-col gap-2"
                      >
                        <Form.Control>
                          <Form.Label>Min Duration</Form.Label>
                          <Input
                            type="number"
                            min="1"
                            bind:value={$formData.eventSeries.duration.min}
                          />
                        </Form.Control>
                      </Form.Field>
                      <Form.Field
                        form={eventSeriesForm}
                        name="eventSeries.duration.max"
                        class="flex flex-grow flex-col gap-2"
                      >
                        <Form.Control>
                          <Form.Label>Max Duration</Form.Label>
                          <Input
                            type="number"
                            min="1"
                            bind:value={$formData.eventSeries.duration.max}
                          />
                        </Form.Control>
                      </Form.Field>
                    </Tabs.Content>
                  {/if}
                </Tabs.Root>
              </div>
            </Card.Content>
          </Card.Root>

          <!-- Type-specific Configuration -->
          {#if $formData.eventSeries.type === 'income' || $formData.eventSeries.type === 'expense'}
            <Card.Root>
              <Card.Header>
                <Card.Title
                  >{$formData.eventSeries.type === 'income' ? 'Income' : 'Expense'} Configuration</Card.Title
                >
              </Card.Header>
              <Card.Content class="flex flex-col gap-4">
                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.initialAmount"
                  class="flex flex-col gap-2"
                >
                  <Form.Control>
                    <Form.Label>Initial Amount ($)</Form.Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      bind:value={$formData.eventSeries.initialAmount}
                    />
                  </Form.Control>
                </Form.Field>

                <div class="flex flex-col gap-2">
                  <Label>Annual Change</Label>
                  <Tabs.Root bind:value={$formData.eventSeries.annualChange.type}>
                    <Tabs.List class="w-full">
                      <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
                      <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
                      <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
                    </Tabs.List>

                    {#if $formData.eventSeries.annualChange.type === 'fixed'}
                      <Tabs.Content value="fixed">
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.annualChange.value"
                          class="flex flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Annual Change (%)</Form.Label>
                            <Input
                              type="number"
                              step="0.01"
                              bind:value={$formData.eventSeries.annualChange.value}
                            />
                          </Form.Control>
                        </Form.Field>
                      </Tabs.Content>
                    {/if}

                    {#if $formData.eventSeries.annualChange.type === 'normal'}
                      <Tabs.Content value="normal" class="flex gap-3">
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.annualChange.mean"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Mean Change (%)</Form.Label>
                            <Input
                              type="number"
                              step="0.01"
                              bind:value={$formData.eventSeries.annualChange.mean}
                            />
                          </Form.Control>
                        </Form.Field>
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.annualChange.stdev"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Standard Deviation</Form.Label>
                            <Input
                              type="number"
                              step="0.01"
                              min="0"
                              bind:value={$formData.eventSeries.annualChange.stdev}
                            />
                          </Form.Control>
                        </Form.Field>
                      </Tabs.Content>
                    {/if}

                    {#if $formData.eventSeries.annualChange.type === 'uniform'}
                      <Tabs.Content value="uniform" class="flex gap-3">
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.annualChange.min"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Min Change (%)</Form.Label>
                            <Input
                              type="number"
                              step="0.01"
                              bind:value={$formData.eventSeries.annualChange.min}
                            />
                          </Form.Control>
                        </Form.Field>
                        <Form.Field
                          form={eventSeriesForm}
                          name="eventSeries.annualChange.max"
                          class="flex flex-grow flex-col gap-2"
                        >
                          <Form.Control>
                            <Form.Label>Max Change (%)</Form.Label>
                            <Input
                              type="number"
                              step="0.01"
                              bind:value={$formData.eventSeries.annualChange.max}
                            />
                          </Form.Control>
                        </Form.Field>
                      </Tabs.Content>
                    {/if}
                  </Tabs.Root>
                </div>

                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.inflationAdjusted"
                  class="flex items-center gap-2"
                >
                  <Form.Control>
                    <Checkbox bind:checked={$formData.eventSeries.inflationAdjusted} />
                    <Form.Label>Inflation Adjusted</Form.Label>
                  </Form.Control>
                </Form.Field>

                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.userPercentage"
                  class="flex flex-col gap-2"
                >
                  <Form.Control>
                    <Form.Label>User Percentage (for married couples)</Form.Label>
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      bind:value={$formData.eventSeries.userPercentage}
                    />
                  </Form.Control>
                </Form.Field>

                {#if $formData.eventSeries.type === 'income'}
                  <Form.Field
                    form={eventSeriesForm}
                    name="eventSeries.isSocialSecurity"
                    class="flex items-center gap-2"
                  >
                    <Form.Control>
                      <Checkbox bind:checked={$formData.eventSeries.isSocialSecurity} />
                      <Form.Label>Social Security Income</Form.Label>
                    </Form.Control>
                  </Form.Field>
                {/if}

                {#if $formData.eventSeries.type === 'expense'}
                  <Form.Field
                    form={eventSeriesForm}
                    name="eventSeries.isDiscretionary"
                    class="flex items-center gap-2"
                  >
                    <Form.Control>
                      <Checkbox bind:checked={$formData.eventSeries.isDiscretionary} />
                      <Form.Label>Discretionary Expense</Form.Label>
                    </Form.Control>
                  </Form.Field>
                {/if}
              </Card.Content>
            </Card.Root>
          {/if}

          {#if $formData.eventSeries.type === 'invest' || $formData.eventSeries.type === 'rebalance'}
            <Card.Root>
              <Card.Header>
                <Card.Title
                  >{$formData.eventSeries.type === 'invest' ? 'Investment' : 'Rebalance'} Configuration</Card.Title
                >
              </Card.Header>
              <Card.Content class="flex flex-col gap-4">
                <Form.Field
                  form={eventSeriesForm}
                  name="eventSeries.isGlidePath"
                  class="flex items-center gap-2"
                >
                  <Form.Control>
                    <Checkbox bind:checked={$formData.eventSeries.isGlidePath} />
                    <Form.Label>Use Glide Path (Linear allocation change over time)</Form.Label>
                  </Form.Control>
                </Form.Field>

                <!-- Asset Allocation section would need to be populated with available investments -->
                <div class="flex flex-col gap-2">
                  <Label>Asset Allocation</Label>
                  <p class="text-sm text-muted-foreground">
                    Configure investment allocations here (requires integration with investment
                    data)
                  </p>
                </div>

                {#if $formData.eventSeries.type === 'invest'}
                  <Form.Field
                    form={eventSeriesForm}
                    name="eventSeries.maximumCash"
                    class="flex flex-col gap-2"
                  >
                    <Form.Control>
                      <Form.Label>Maximum Cash ($)</Form.Label>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        bind:value={$formData.eventSeries.maximumCash}
                      />
                    </Form.Control>
                  </Form.Field>
                {/if}

                {#if $formData.eventSeries.type === 'rebalance'}
                  <Form.Field
                    form={eventSeriesForm}
                    name="eventSeries.targetTaxStatus"
                    class="flex flex-col gap-2"
                  >
                    <Form.Control>
                      <Form.Label>Target Tax Status</Form.Label>
                      <Select.Root bind:value={$formData.eventSeries.targetTaxStatus} type="single">
                        <Select.Trigger>
                          {$formData.eventSeries.targetTaxStatus || 'Select tax status'}
                        </Select.Trigger>
                        <Select.Content>
                          <Select.Item value="non_retirement">Non-Retirement</Select.Item>
                          <Select.Item value="pre_tax_retirement">Pre-Tax Retirement</Select.Item>
                          <Select.Item value="after_tax_retirement"
                            >After-Tax Retirement</Select.Item
                          >
                        </Select.Content>
                      </Select.Root>
                    </Form.Control>
                  </Form.Field>
                {/if}
              </Card.Content>
            </Card.Root>
          {/if}
        </div>
      </ScrollArea>
      <Dialog.Footer class="mt-6 flex justify-end gap-2">
        <Dialog.Close>
          <Button variant="outline">Close</Button>
        </Dialog.Close>
        <Button type="submit">Add Event Series</Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>
