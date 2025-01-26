import { type inferRouterInputs, type inferRouterOutputs } from "@trpc/server";
import { type CreateNextContextOptions } from "@trpc/server/adapters/next";
import { config } from "dotenv";
import { type InferModel, type Table, sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/postgres-js";
import { type Session } from "next-auth";
import postgres from "postgres";
import { afterAll, afterEach, beforeEach, vi } from "vitest";
import * as schema from "../../db/schema";
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

// Create a test database connection
const client = postgres(
  process.env.DATABASE_URL ??
    "postgresql://postgres:postgres@localhost:5433/test_db?sslmode=disable",
  {
    max: 5,
    idle_timeout: 30,
    connection: {
      application_name: "test-runner",
    },
  },
);
export const testDb = drizzle(client, { schema });

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
    session,
    db: testDb,
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
  await testDb.execute(sql`
    DO $$ 
    BEGIN
      EXECUTE (
        SELECT 'TRUNCATE TABLE ' || string_agg(format('%I.%I', schemaname, tablename), ', ') || ' RESTART IDENTITY CASCADE'
        FROM pg_tables
        WHERE schemaname = 'public'
      );
    END $$;
  `);
}

/**
 * Setup test data
 */
export async function setupTestData() {
  try {
    await cleanupTestData();

    // Create test user
    const [user] = await testDb
      .insert(schema.users)
      .values({
        id: mockSession.user.id,
        name: mockSession.user.name ?? null,
        email: mockSession.user.email ?? "",
        emailVerified: new Date(),
      })
      .returning();

    if (!user) throw new Error("Failed to create test user");

    return user;
  } catch (error) {
    console.error("Test setup error:", error);
    throw error;
  }
}

// Reset database before each test
beforeEach(async () => {
  // Add connection check
  await testDb.execute(sql`SELECT 1`);

  // Use transactions for test isolation
  await testDb.execute(sql`BEGIN`);
  await setupTestData();
});

afterEach(async () => {
  await testDb.execute(sql`ROLLBACK`);
  vi.resetAllMocks();
});

// Close database connection after all tests
afterAll(async () => {
  try {
    await cleanupTestData();
    await client.end();

    // New validation
    const remaining = await testDb
      .select({ count: sql`count(*)` })
      .from(schema.purposes);
    if (remaining[0]?.count !== 0) {
      throw new Error("Test data cleanup failed!");
    }
  } catch (error) {
    console.error("Error in test cleanup:", error);
    throw error;
  }
});
