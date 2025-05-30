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
    <div class="grid grid-cols-2 gap-x-4 px-2 py-1.5 text-sm">
      <div class="font-medium text-gray-500">Last Logged In:</div>
      <div>
        {currentUser.last_login ? new Date(currentUser.last_login).toLocaleString() : 'Never'}
      </div>
      <div class="font-medium text-gray-500">Date Joined:</div>
      <div>{currentUser.date_joined ? new Date(currentUser.date_joined).toLocaleString() : ''}</div>
      <div class="font-medium text-gray-500">Active:</div>
      <div>{currentUser.is_active ? 'Yes' : 'No'}</div>
    </div>
    <DropdownMenu.Separator />
    <DropdownMenu.Item>Settings</DropdownMenu.Item>
    <DropdownMenu.Item>Logout</DropdownMenu.Item>
  </DropdownMenu.Content>
</DropdownMenu.Root>
