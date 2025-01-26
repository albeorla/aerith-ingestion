import { purposes } from "@/server/db/schema";
import { cleanupTestData, setupTestData } from "@/server/db/testing/test-data";
import { client, testDb } from "@/server/db/testing/test-db";
import "@testing-library/jest-dom/vitest";
import { sql } from "drizzle-orm";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import { afterAll, afterEach, beforeAll, beforeEach, vi } from "vitest";

// Mock environment variables
vi.mock("@/env.js", () => ({
  env: {
    DATABASE_URL:
      "postgresql://postgres:4ZzZoAvAe7qkNJ8q@localhost:5432/test_db?sslmode=disable",
    NEXTAUTH_SECRET: "test-secret",
    NEXTAUTH_URL: "http://localhost:3000",
    DISCORD_CLIENT_ID: "test-client-id",
    DISCORD_CLIENT_SECRET: "test-client-secret",
    NODE_ENV: "test",
  },
}));

// Mock auth by default
vi.mock("@/server/auth", () => ({
  auth: vi.fn(() => {
    const handler = async () => new Response(JSON.stringify({ session: null }));
    return handler;
  }),
  handlers: {},
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

// Initialize database schema before all tests
beforeAll(async () => {
  try {
    // Verify database connection
    await testDb.execute(sql`SELECT 1`);

    // Run migrations
    await migrate(testDb, { migrationsFolder: "./drizzle" });
  } catch (error) {
    console.error("Failed to initialize test database:", error);
    throw error;
  }
});

// Reset all mocks between tests
beforeEach(async () => {
  vi.resetAllMocks();

  try {
    // Clean and setup test data
    await cleanupTestData();
    await setupTestData();
  } catch (error) {
    console.error("Failed to setup test data:", error);
    throw error;
  }
});

// Clean up after each test
afterEach(async () => {
  vi.clearAllMocks();
});

// Clean up after all tests
afterAll(async () => {
  let error: Error | undefined;

  try {
    // Add connection termination for lingering connections
    await testDb.execute(sql`
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = current_database()
      AND pid <> pg_backend_pid()
    `);

    // Close connection with timeout
    await client.end({ timeout: 5000 });
  } catch (e) {
    error = e as Error;
  } finally {
    // Add final validation
    if (process.env.CI) {
      const remaining = await testDb.select().from(purposes);
      if (remaining.length > 0) {
        throw new Error("Test data cleanup failed!");
      }
    }
  }
});

// Add this to your setup file
const isCI = process.env.CI === "true";

if (isCI) {
  // CI-specific configurations
  process.env.TEST_RETRIES = "3";
  process.env.TEST_TIMEOUT = "30000";
} else {
  // Local development configurations
  process.env.TEST_RETRIES = "1";
  process.env.TEST_TIMEOUT = "10000";
}
