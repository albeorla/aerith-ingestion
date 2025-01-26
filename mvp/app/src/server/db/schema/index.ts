import { env } from "@/env";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

// Import all schemas
import * as accounts from "./accounts";
import * as areas from "./areas";
import * as goals from "./goals";
import * as projects from "./projects";
import * as purposes from "./purposes";
import * as sessions from "./sessions";
import * as tasks from "./tasks";
import * as users from "./users";
import * as utils from "./utils";
import * as verificationTokens from "./verification-tokens";
import * as visions from "./visions";

// Re-export all schemas
export * from "./accounts";
export * from "./areas";
export * from "./goals";
export * from "./projects";
export * from "./purposes";
export * from "./sessions";
export * from "./tasks";
export * from "./users";
export * from "./utils";
export * from "./verification-tokens";
export * from "./visions";

// Collect all schemas in one object
export const schema = {
  ...accounts,
  ...areas,
  ...goals,
  ...projects,
  ...purposes,
  ...sessions,
  ...tasks,
  ...users,
  ...verificationTokens,
  ...visions,
  ...utils,
};

/**
 * Cache the database connection in development. This avoids creating a new connection on every HMR
 * update.
 */
const globalForDb = globalThis as unknown as {
  conn: postgres.Sql | undefined;
};

const conn = globalForDb.conn ?? postgres(env.DATABASE_URL);
if (env.NODE_ENV !== "production") globalForDb.conn = conn;

export const db = drizzle(conn, {
  schema,
  logger: true,
});
