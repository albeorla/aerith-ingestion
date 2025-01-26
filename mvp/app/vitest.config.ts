import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["node_modules/", "src/test/"],
      reportsDirectory: "./coverage",
      all: true,
      include: ["src/server/api/**/*.ts"],
    },
    retry: 2,
    testTimeout: 30000,
    hookTimeout: 15000,
    teardownTimeout: 10000,
    poolOptions: {
      threads: {
        singleThread: true,
      },
      forks: {
        isolate: false,
      },
    },
  },
});
