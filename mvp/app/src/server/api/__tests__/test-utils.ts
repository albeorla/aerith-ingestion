import { type inferRouterInputs, type inferRouterOutputs } from "@trpc/server";
import { type CreateNextContextOptions } from "@trpc/server/adapters/next";
import { config } from "dotenv";
import { type InferModel, type Table, sql } from "drizzle-orm";
import { type Session } from "next-auth";
import { afterAll, afterEach, beforeEach, vi } from "vitest";
import * as schema from "../../db/schema";
import { db } from "@/server/db/schema";
import { getDb } from "../../db/testing/test-db";
import { appRouter } from "../root";
import { createTRPCContext } from "../trpc";

export type AppRouter = typeof appRouter;

// Infer router input/output types
export type RouterInput = inferRouterInputs<AppRouter>;
export type RouterOutput = inferRouterOutputs<AppRouter>;

/**
 * Mock session data for testing
 */
export const mockSession: Session = {
  user: {
    id: "test-user-id",
    name: "Test User",
    email: "test@example.com",
  },
  expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
};

// Load test environment variables
config({ path: ".env.test" });

// Get the database instance
export const testDb = getDb();

// Mock NextAuth
vi.mock("next-auth", () => {
  const mod = vi.fn(() => ({
    auth: vi.fn(() => {
      const handler = async () =>
        new Response(JSON.stringify({ session: null }));
      return handler;
    }),
  }));
  return { default: mod };
});

// Mock the auth module
vi.mock("@/server/auth", () => {
  const mod = {
    auth: vi.fn(() => {
      const handler = async () =>
        new Response(JSON.stringify({ session: null }));
      return handler;
    }),
    handlers: {},
    signIn: vi.fn(),
    signOut: vi.fn(),
  };
  return mod;
});

/**
 * Creates a test context with optional session
 */
export async function createTestContext(session: Session | null = null) {
  // Create minimal context options
  const opts = {
    req: {},
    res: {},
  } as CreateNextContextOptions;

  // Create the context with session
  const ctx = await createTRPCContext(opts);
  return {
    ...ctx,
    setup: async () => {
      await db.execute(sql`BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;`);
    },
    teardown: async () => {
      await db.execute(sql`ROLLBACK;`);
      await db.execute(sql`COMMIT;`);
    },
    session,
    db,
  };
}

/**
 * Creates a caller for testing procedures
 */
export async function createCaller(session: Session | null = null) {
  const ctx = await createTestContext(session);
  return appRouter.createCaller(ctx);
}

/**
 * Helper to get input type of a procedure
 */
export type ProcedureInput<
  TRouter extends keyof RouterInput,
  TProcedure extends keyof RouterInput[TRouter],
> = RouterInput[TRouter][TProcedure];

/**
 * Helper to get output type of a procedure
 */
export type ProcedureOutput<
  TRouter extends keyof RouterOutput,
  TProcedure extends keyof RouterOutput[TRouter],
> = RouterOutput[TRouter][TProcedure];

/**
 * Helper to get return type of a drizzle query
 */
export type DrizzleReturn<T extends Table> = InferModel<T>;

/**
 * Clean up test data
 */
export async function cleanupTestData() {
  const db = getDb();
  try {
    await db.transaction(async (tx) => {
      await tx.execute(sql`
        DO $$ 
        BEGIN
          EXECUTE (
            SELECT 'TRUNCATE TABLE ' || string_agg(format('%I.%I', schemaname, tablename), ', ') || ' RESTART IDENTITY CASCADE'
            FROM pg_tables
            WHERE schemaname = 'public'
          );
        END $$;
      `);
    });
  } catch (error) {
    console.error("Error cleaning up test data:", error);
    throw error;
  }
}

/**
 * Setup test data
 */
export async function setupTestData() {
  const db = getDb();
  try {
    await cleanupTestData();

    // Create test user
    const [user] = await db.transaction(async (tx) => {
      return tx
        .insert(schema.users)
        .values({
          id: mockSession.user.id,
          name: mockSession.user.name ?? null,
          email: mockSession.user.email ?? "",
          emailVerified: new Date(),
        })
        .returning();
    });

    if (!user) throw new Error("Failed to create test user");

    return user;
  } catch (error) {
    console.error("Test setup error:", error);
    throw error;
  }
}

// Reset database before each test
beforeEach(async () => {
  await db.transaction(async (tx) => {
    await setupTestData();
  });
});

afterEach(async () => {
  await db.transaction(async (tx) => {
    await cleanupTestData();
  });
  vi.resetAllMocks();
});

// Close database connection after all tests
afterAll(async () => {
  try {
    const db = getDb();
    // Ensure all connections are terminated
    await db.execute(sql`
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = current_database()
      AND pid <> pg_backend_pid()
    `);

    // Final cleanup
    await cleanupTestData();
  } catch (error) {
    console.error("Error in test cleanup:", error);
  }
});
