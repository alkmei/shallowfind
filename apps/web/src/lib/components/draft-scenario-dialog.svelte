<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Form from '$lib/components/ui/form';
  import Button from './ui/button/button.svelte';
</script>

<Dialog.Root>
  <Dialog.Trigger>
    <Button>New Scenario</Button>
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Header>
      <Dialog.Title>Create a New Scenario</Dialog.Title>
      <Dialog.Description>
        Start building your scenario by providing the necessary details.
      </Dialog.Description>
    </Dialog.Header>

    <form method="POST"></form>
    <Dialog.Footer>
      <Dialog.Close>
        <Button variant="secondary">Cancel</Button>
      </Dialog.Close>
      <Button>Create Scenario</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
