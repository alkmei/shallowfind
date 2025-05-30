<script lang="ts">
  import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
  import * as Avatar from '$lib/components/ui/avatar';
  import type { AdminUser } from '$lib/api/shallowfind.schemas';

  let { currentUser }: { currentUser: AdminUser } = $props();

  const isFullNameAvailable = currentUser.first_name && currentUser.last_name;
</script>

<DropdownMenu.Root>
  <DropdownMenu.Trigger>
    <Avatar.Root class="cursor-pointer hover:brightness-75">
      <Avatar.Image
        src={`https://api.dicebear.com/9.x/lorelei/svg?seed=${currentUser.email}`}
        alt={currentUser.email}
        referrerpolicy="no-referrer"
      />
      <Avatar.Fallback>
        {isFullNameAvailable
          ? `${currentUser.first_name} ${currentUser.last_name}`
          : currentUser.email}
      </Avatar.Fallback>
    </Avatar.Root>
  </DropdownMenu.Trigger>
  <DropdownMenu.Content>
    <DropdownMenu.Label>
      {currentUser.email}
    </DropdownMenu.Label>
    <DropdownMenu.Separator />
    <DropdownMenu.Item>Profile</DropdownMenu.Item>
    <DropdownMenu.Item>Settings</DropdownMenu.Item>
    <DropdownMenu.Item>Logout</DropdownMenu.Item>
  </DropdownMenu.Content>
</DropdownMenu.Root>
