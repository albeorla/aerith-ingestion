import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  // Force test environment detection
  process.env.VITEST = "true";

  return {
    plugins: [react(), tsconfigPaths()],
    test: {
      // Prevent parallel test execution
      threads: false,
      singleThread: true,
      // Increase timeouts
      testTimeout: 30_000,
      hookTimeout: 30_000,
      
      // Watch mode configuration
      watch: false,
      
      // Cache configuration
      cache: {
        dir: "node_modules/.vitest_cache",
      },

      // Coverage configuration
      coverage: {
        provider: "v8",
        reporter: ["text", "html", "lcov"],
        all: true,
        exclude: [
          "**/index.ts",
          "**/*.config.*",
          "**/.next/**",
        ],
        include: ["src/**/*.{ts,tsx}"],
        thresholds: {
          lines: 80,
          functions: 80,
          branches: 80,
          statements: 80,
        },
      },

      // Exclude patterns
      exclude: [
        ...configDefaults.exclude,
        "node_modules",
        ".turbo",
        ".vscode",
      ],

      // Keep existing other config
      environment: "jsdom",
      setupFiles: ["./src/test/setup.ts"]
    },
  };
});
