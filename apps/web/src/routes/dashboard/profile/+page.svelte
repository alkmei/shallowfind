<script lang="ts">
  import type { AdminUser } from '$lib/api/shallowfind.schemas';
  import { createUsersMeRetrieve, usersMeRetrieve } from '$lib/api/users/users';
  import { onMount } from 'svelte';

  const userQuery = createUsersMeRetrieve();
</script>

{#if $userQuery.isLoading}
  <span>Loading...</span>
{:else if $userQuery.isError}
  <span>Error occured loading user data</span>
{:else if $userQuery.isSuccess}
  {@const currentUser: AdminUser = $userQuery.data.data}

  <div class="grid grid-cols-[auto_1fr] gap-4">
    <div class="p-4">
      <img src={`https://api.dicebear.com/9.x/lorelei/svg?seed=${currentUser.email}`} alt="" />
      hello
    </div>
    <div class="p-4"></div>
  </div>
{/if}
