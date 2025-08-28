// @ts-check
import { defineConfig } from "astro/config";

// https://astro.build/config
export default defineConfig({
  site: "https://alkmei.github.io",
  base: "/shallowfind",
  outDir: "dist",
  build: {
    assets: "_astro",
  },
});
