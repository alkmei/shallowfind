<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import Avatar from '$lib/components/ui/avatar/avatar.svelte';
	import { DropdownMenu } from '$lib/components/ui/dropdown-menu';
	import Collapsible from '$lib/components/ui/collapsible/collapsible.svelte';
	import { ChevronsUpDown } from '@lucide/svelte';
	import CollapsibleTrigger from '$lib/components/ui/collapsible/collapsible-trigger.svelte';
	import CollapsibleContent from '$lib/components/ui/collapsible/collapsible-content.svelte';

	let { children } = $props();
</script>

<div class="mx-8 grid grid-cols-[auto_1fr] grid-rows-[auto_1fr] gap-6 py-6">
	<a href="/dashboard">
		<h1 class="text-4xl">
			<span class="font-bold">Shallow</span>Find
		</h1>
	</a>

	<header class="flex items-center justify-between">
		<div>Breadcrumb</div>
		<!-- {#if user}
			<DropdownMenu>
				<DropdownMenu.Trigger asChild>
					<Avatar class="cursor-pointer hover:brightness-75">
						<Avatar.Image
							src={`https://api.dicebear.com/9.x/lorelei/svg?seed=${user.name}`}
							alt={user.name}
							referrerpolicy="no-referrer"
						/>
						<Avatar.Fallback>{user.name}</Avatar.Fallback>
					</Avatar>
				</DropdownMenu.Trigger>
				<DropdownMenu.Content>
					<DropdownMenu.Label>{user.name}</DropdownMenu.Label>
					<DropdownMenu.Separator />
					<DropdownMenu.Item>
						<Link to={`/dashboard/users/${user.id}`}>Profile</Link>
					</DropdownMenu.Item>
					<DropdownMenu.Item>Settings</DropdownMenu.Item>
					<DropdownMenu.Item on:click={logout}>Logout</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu>
		{:else}
			<LoginButton class="w-52" />
		{/if} -->
	</header>

	<aside class="flex h-full w-3xs flex-col justify-between">
		<div>
			<Button class="mb-4 w-full cursor-pointer">New Scenario</Button>
			<Collapsible class="mb-2 w-full">
				<CollapsibleTrigger asChild>
					<Button variant="ghost" size="sm" class="mb-2 w-full">
						<span class="w-full text-left">Scenarios</span>
						<ChevronsUpDown class="h-4 w-4" />
					</Button>
				</CollapsibleTrigger>
				<CollapsibleContent class="CollapsibleContent flex flex-col gap-2">
					<!-- {#each scenarios as scenario}
						<Link to={`/dashboard/scenario/${scenario.id}`}>
							<Button class="w-full justify-normal" variant="outline">
								{scenario.name}
							</Button>
						</Link>
					{/each} -->
				</CollapsibleContent>
			</Collapsible>
			<Collapsible class="w-full">
				<CollapsibleTrigger asChild>
					<Button variant="ghost" size="sm" class="mb-2 w-full">
						<span class="w-full text-left">Shared Scenarios</span>
						<ChevronsUpDown class="h-4 w-4" />
					</Button>
				</CollapsibleTrigger>
				<CollapsibleContent class="CollapsibleContent flex flex-col gap-2">
					<!-- {#each sharedScenarios as scenario}
						<Link to={`/dashboard/scenario/${scenario.id}`}>
							<Button class="w-full justify-normal" variant="outline">
								{scenario.name}
							</Button>
						</Link>
					{/each} -->
				</CollapsibleContent>
			</Collapsible>
		</div>
		<div class="flex flex-col gap-2">
			<Button class="w-full" variant="outline">Import Scenario</Button>
			<Button class="w-full" variant="outline">Support</Button>
			<Button class="w-full" variant="outline">About</Button>
		</div>
	</aside>
	<main class="h-full w-full overflow-auto rounded-2xl border p-2">
		{@render children()}
	</main>
</div>
