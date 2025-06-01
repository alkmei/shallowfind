<script lang="ts">
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
</script>

<Sidebar.Menu>
  <Sidebar.MenuItem>
    <Sidebar.MenuButton size="lg">
      {#snippet child({ props })}
        <a href="/dashboard" {...props}>
          <div class="flex text-3xl leading-none group-data-[collapsible=icon]:hidden">
            <span>Shallow<span class="font-bold">Find</span></span>
          </div>
          <div class="hidden text-3xl leading-none group-data-[collapsible=icon]:flex">
            <span>S<span class="font-bold">F</span></span>
          </div>
        </a>
      {/snippet}
    </Sidebar.MenuButton>
  </Sidebar.MenuItem>
</Sidebar.Menu>
