<script lang="ts" module>
  import AudioWaveformIcon from '@lucide/svelte/icons/audio-waveform';
  import CommandIcon from '@lucide/svelte/icons/command';
  import GalleryVerticalEndIcon from '@lucide/svelte/icons/gallery-vertical-end';

  const data = {
    teams: [
      {
        name: 'Acme Inc',
        logo: GalleryVerticalEndIcon,
        plan: 'Enterprise'
      },
      {
        name: 'Acme Corp.',
        logo: AudioWaveformIcon,
        plan: 'Startup'
      },
      {
        name: 'Evil Corp.',
        logo: CommandIcon,
        plan: 'Free'
      }
    ],
    navMain: [
      {
        title: 'Scenarios',
        url: '#',
        icon: Layers,
        isActive: true,
        items: [
          {
            title: 'My Scenarios',
            url: '#'
          },
          {
            title: 'Create New Scenario',
            url: '#'
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
            url: '#'
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
            title: 'Investments',
            url: '#'
          },
          {
            title: 'Event Series',
            url: '#'
          },
          {
            title: 'Tax Settings',
            url: '#'
          },
          {
            title: 'Strategies',
            url: '#'
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
            url: '#'
          },
          {
            title: 'Sharing',
            url: '#'
          },
          {
            title: 'Optimization Tools',
            url: '#'
          },
          {
            title: 'Logs & Reports',
            url: '#'
          }
        ]
      }
    ]
  };
</script>

<script lang="ts">
  import NavMain from './NavMain.svelte';
  import NavUser from './NavUser.svelte';
  import TeamSwitcher from './TeamSwitcher.svelte';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';
  import type { ComponentProps } from 'svelte';
  import type { AdminUser } from '$lib/api/shallowfind.schemas';
  import { BadgeDollarSign, Layers, TrendingUp, Wrench } from '@lucide/svelte';

  let {
    ref = $bindable(null),
    collapsible = 'icon',
    user,
    ...restProps
  }: ComponentProps<typeof Sidebar.Root> & { user: AdminUser } = $props();
</script>

<Sidebar.Root {collapsible} {...restProps}>
  <Sidebar.Header>
    <TeamSwitcher teams={data.teams} />
  </Sidebar.Header>
  <Sidebar.Content>
    <NavMain items={data.navMain} />
  </Sidebar.Content>
  <Sidebar.Footer>
    <NavUser {user} />
  </Sidebar.Footer>
  <Sidebar.Rail />
</Sidebar.Root>
