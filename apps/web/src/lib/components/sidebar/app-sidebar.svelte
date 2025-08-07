<script lang="ts" module>
  import AudioWaveformIcon from '@lucide/svelte/icons/audio-waveform';
  import CommandIcon from '@lucide/svelte/icons/command';
  import GalleryVerticalEndIcon from '@lucide/svelte/icons/gallery-vertical-end';

  const data = {
    navMain: [
      {
        title: 'Scenarios',
        url: '#',
        icon: Layers,
        isActive: true,
        items: [
          {
            title: 'My Scenarios',
            url: '/dashboard/scenarios'
          },
          {
            title: 'Create New Scenario',
            url: '/dashboard/scenarios/create'
          },
          {
            title: 'Scenario Explorer',
            url: '#'
          },
          {
            title: 'Financial Goals',
            url: '#'
          }
        ]
      },
      {
        title: 'Simulations',
        url: '#',
        icon: TrendingUp,
        items: [
          {
            title: 'Run Simulations',
            url: '/dashboard/simulations/run'
          },
          {
            title: 'Results Dashboard',
            url: '#'
          },
          {
            title: 'Charts & Visualizations',
            url: '#'
          },
          {
            title: 'Comparison Tools',
            url: '#'
          }
        ]
      },
      {
        title: 'Financial Data',
        url: '#',
        icon: BadgeDollarSign,
        items: [
          {
            title: 'Investment Types',
            url: '/dashboard/investment-types'
          },
          {
            title: 'Event Series',
            url: '/dashboard/event-series'
          },
          {
            title: 'Tax Settings',
            url: '/dashboard/tax-settings'
          },
          {
            title: 'Strategies',
            url: '/dashboard/strategies'
          }
        ]
      },
      {
        title: 'Tools & Utilities',
        url: '#',
        icon: Wrench,
        items: [
          {
            title: 'Import/Export',
            url: '/dashboard/import-export'
          },
          {
            title: 'Sharing',
            url: '/dashboard/sharing'
          },
          {
            title: 'Optimization Tools',
            url: '#'
          },
          {
            title: 'Logs & Reports',
            url: '/dashboard/scenarios/logs'
          }
        ]
      }
    ]
  };
</script>

<script lang="ts">
  import NavMain from './nav-main.svelte';
  import NavUser from './nav-user.svelte';
  import SidebarLogo from './sidebar-logo.svelte';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import type { ComponentProps } from 'svelte';
  import { BadgeDollarSign, Layers, TrendingUp, Wrench } from '@lucide/svelte';

  let {
    ref = $bindable(null),
    collapsible = 'icon',
    ...restProps
  }: ComponentProps<typeof Sidebar.Root> = $props();

  let { user }: { user: { firstName: string; email: string } } = {
    user: {
      firstName: 'Charlie',
      email: 'charlie@example.com'
    }
  };
</script>

<Sidebar.Root {collapsible} {...restProps}>
  <Sidebar.Header>
    <SidebarLogo />
  </Sidebar.Header>
  <Sidebar.Content>
    <NavMain items={data.navMain} />
  </Sidebar.Content>
  <Sidebar.Footer>
    <NavUser {user} />
  </Sidebar.Footer>
  <Sidebar.Rail />
</Sidebar.Root>
