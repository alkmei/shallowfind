<script lang="ts">
  import AppSidebar from '$lib/components/sidebar/app-sidebar.svelte';
  import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
  import { Separator } from '$lib/components/ui/separator/index.js';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import {createGetUserApiUsersUserIdGet} from "$lib/api/users/users"

  let { children } = $props();

  const userQuery = createGetUserApiUsersUserIdGet(
    ""
  );
</script>

<Sidebar.Provider>
  {#if $userQuery.isLoading}
    <div class="flex h-full items-center justify-center">
      <span class="text-gray-500">Loading...</span>
    </div>
  {:else if $userQuery.isError}
    <div class="flex h-full items-center justify-center">
      <span class="text-red-500">Error loading user data</span>
    </div>
  {:else if $userQuery.isSuccess}
    <AppSidebar user={$userQuery.data?.data} />
  {/if}
  <Sidebar.Inset>
    <header
      class="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12"
    >
      <div class="flex items-center gap-2 px-4">
        <Sidebar.Trigger class="-ml-1" />
        <Separator orientation="vertical" class="mr-2 data-[orientation=vertical]:h-4" />
        <Breadcrumb.Root>
          <Breadcrumb.List>
            <Breadcrumb.Item class="hidden md:block">
              <Breadcrumb.Link href="#">Building Your Application</Breadcrumb.Link>
            </Breadcrumb.Item>
            <Breadcrumb.Separator class="hidden md:block" />
            <Breadcrumb.Item>
              <Breadcrumb.Page>Data Fetching</Breadcrumb.Page>
            </Breadcrumb.Item>
          </Breadcrumb.List>
        </Breadcrumb.Root>
      </div>
    </header>
    <div class="flex flex-1 flex-col gap-4 p-4 pt-0">
      {@render children()}
    </div>
  </Sidebar.Inset>
</Sidebar.Provider>
