<script lang="ts">
  import { buttonVariants, Button } from '$lib/components/ui/button';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Input } from '$lib/components/ui/input';
</script>

<Dialog.Root>
  <Dialog.Trigger class={'w-48' + buttonVariants({ variant: 'secondary' })} type="button">
    Import Scenario
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Header>
      <Dialog.Title>Import Scenario</Dialog.Title>
      <Dialog.Description>
        Import a scenario from a YAML file. The file should be in the correct format.
      </Dialog.Description>
    </Dialog.Header>
    <form method="POST" action="?/file" enctype="multipart/form-data" class="flex flex-col gap-4">
      <Input type="file" name="scenarioFile" accept=".yaml" required />
      <div class="mt-4 flex justify-end">
        <Button type="submit">Import</Button>
      </div>
    </form>
  </Dialog.Content>
</Dialog.Root>
