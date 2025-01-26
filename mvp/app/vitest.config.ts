import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  // Load env file based on mode
  process.env.VITEST = "true";
  const env = loadEnv(mode, process.cwd(), "");
  const testEnv = {
    ...env,
    NODE_ENV: "test" as const,
  };

  return {
    plugins: [react(), tsconfigPaths()],
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: ["./src/test/setup.ts"],
      include: ["**/__tests__/**/*.test.{ts,tsx}"],
      environmentOptions: {
        jsdom: {
          resources: "usable",
        },
      },
      env: testEnv,
      testTimeout: 30000,
    },
  };
});
