<script lang="ts">
  import Benjamin from '$lib/images/benjamin.jpg';
  let { children } = $props();
</script>

<div class="flex h-screen w-full">
  <div
    class="relative h-full w-1/2 border-r-4 border-white bg-cover bg-center"
    style={`background-image: url(${Benjamin})`}
  >
    <div class="absolute inset-0 flex -translate-y-32 flex-col items-end justify-center pr-8">
      <h1 class="text-right text-3xl leading-tight text-white drop-shadow">
        <span class="font-bold">Shallow</span>Find
      </h1>
      <p class="text-right text-5xl text-white drop-shadow">Financial Planner For All</p>
    </div>
    <div class="absolute bottom-4 left-4 text-sm text-gray-300">
      Photo by <a
        href="https://unsplash.com/@adamnir?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash"
        target="_blank"
        rel="noopener noreferrer"
        class="hover:text-gray-50">Jason Leung</a
      >
      on
      <a
        href="https://unsplash.com/photos/a-close-up-of-a-one-dollar-bill-wTO6MWpMrJk?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash"
        target="_blank"
        rel="noopener noreferrer"
        class="hover:text-gray-50">Unsplash</a
      >
    </div>
  </div>

  <div class="relative flex w-1/2 flex-col items-center justify-center">
    {@render children()}
  </div>
</div>
