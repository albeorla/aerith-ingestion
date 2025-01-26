import { purposes } from "@/server/db/schema";
import { cleanupTestData, setupTestData } from "@/server/db/testing/test-data";
import { getDb, verifyConnection, ensureConnection } from "@/server/db/testing/test-db";
import "@testing-library/jest-dom/vitest";
import { sql } from "drizzle-orm";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { afterAll, afterEach, beforeAll, beforeEach, vi } from "vitest";
import path from "path";
import { config } from "dotenv";

// Load test environment variables
config({ path: ".env.test" });

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
    // Ensure clean connection state
    await ensureConnection();

    // Run migrations with absolute path
    const migrationsPath = path.join(process.cwd(), "drizzle");
    await migrate(getDb(), { migrationsFolder: migrationsPath });

    // Clean any existing data after migrations
    await cleanupTestData();
  } catch (error) {
    console.error("Failed to initialize test database:", error);
    throw error;
  }
});

// Reset all mocks between tests
beforeEach(async () => {
  vi.resetAllMocks();

  try {
    // Ensure clean connection state before each test
    await ensureConnection();
    
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
  try {
    await cleanupTestData();
  } catch (error) {
    console.error("Error cleaning up test data:", error);
  }
});

// Clean up after all tests
afterAll(async () => {
  try {
    // Ensure connection is available for cleanup
    if (await verifyConnection(3, 1000)) {
      const db = getDb();
      // Terminate other connections
      await db.execute(sql`
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = current_database()
        AND pid <> pg_backend_pid()
      `);

      // Final cleanup
      await cleanupTestData();
    }
  } catch (error) {
    console.error("Error during test cleanup:", error);
  } finally {
    // Add final validation only if connection is available
    if (process.env.CI) {
      try {
        if (await verifyConnection(2, 500)) {
          const remaining = await getDb().select().from(purposes);
          if (remaining.length > 0) {
            console.warn("Test data cleanup incomplete - some records remain");
          }
        }
      } catch (error) {
        console.error("Error during final validation:", error);
      }
    }
  }
});

// Test configuration based on environment
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
