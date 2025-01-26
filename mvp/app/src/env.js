import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  /**
   * Server-side environment variables schema.
   * These variables are only available on the server and are validated at runtime.
   */
  server: {
    // Authentication
    AUTH_SECRET:
      process.env.NODE_ENV === "production"
        ? z.string()
        : z.string().optional(),
    AUTH_DISCORD_ID: z.string(),
    AUTH_DISCORD_SECRET: z.string(),
    NEXTAUTH_URL: z.string().url(),
    NEXTAUTH_SECRET: z.string(),

    // Database Configuration
    DATABASE_URL: z.string().url(),
    TEST_DATABASE_URL: z.string().url().optional(),

    // Environment
    NODE_ENV: z
      .enum(["development", "test", "production"])
      .default("development"),
  },

  /**
   * Client-side environment variables schema.
   * These variables are exposed to the client and should be prefixed with `NEXT_PUBLIC_`.
   * Currently no client-side environment variables are defined.
   */
  client: {
    // NEXT_PUBLIC_CLIENTVAR: z.string(),
  },

  /**
   * Runtime environment variable processing.
   * Special handling for test environment to use TEST_DATABASE_URL when available.
   */
  runtimeEnv: {
    // Auth configuration
    AUTH_SECRET: process.env.AUTH_SECRET,
    AUTH_DISCORD_ID: process.env.AUTH_DISCORD_ID,
    AUTH_DISCORD_SECRET: process.env.AUTH_DISCORD_SECRET,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,

    // Database configuration with test environment support
    DATABASE_URL: process.env.NODE_ENV === "test" && process.env.TEST_DATABASE_URL
      ? process.env.TEST_DATABASE_URL
      : process.env.DATABASE_URL,
    TEST_DATABASE_URL: process.env.TEST_DATABASE_URL,

    // Environment configuration
    NODE_ENV: process.env.NODE_ENV,
  },

  /**
   * Configuration Options
   */
  skipValidation: !!process.env.SKIP_ENV_VALIDATION || process.env.NODE_ENV === "test",
  emptyStringAsUndefined: true,
});
