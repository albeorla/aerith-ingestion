import { env } from "@/env";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import { schema } from "../schema";

// Configure postgres with a connection pool for tests
export const client = postgres(env.DATABASE_URL, {
  max: 5,
  idle_timeout: 60,
  max_lifetime: 60 * 60,
  connect_timeout: 10,
  connection: {
    application_name: "test_client",
    idle_in_transaction_session_timeout: 30,
  },
});

export const testDb = drizzle(client, { schema });
