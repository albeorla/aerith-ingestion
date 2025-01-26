import { env } from "@/env";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { schema } from "../schema";

// Pool configuration
const poolConfig = {
  connectionString: env.DATABASE_URL,
  max: 3, // Allow a small pool for parallel operations
  idleTimeoutMillis: 60000, // 1 minute
  connectionTimeoutMillis: 20000, // 20 seconds
  statement_timeout: 30000, // 30 seconds
  application_name: "test_client",
};

// Single pool instance
let pool: Pool | null = null;
let db: ReturnType<typeof drizzle> | null = null;

// Get or create pool
function getPool(): Pool {
  if (!pool) {
    pool = new Pool(poolConfig);
    pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
    });
  }
  return pool;
}

// Get or create DB instance
export function getDb() {
  if (!db) {
    db = drizzle(getPool(), { 
      schema,
      logger: process.env.NODE_ENV === "development",
    });
  }
  return db;
}

// Export for compatibility
export const testDb = getDb();

// Export a function to verify database connection
export async function verifyConnection(retries = 5, delay = 1000): Promise<boolean> {
  const currentPool = getPool();
  while (retries > 0) {
    try {
      const client = await currentPool.connect();
      try {
        await client.query('SELECT 1');
        return true;
      } finally {
        client.release();
      }
    } catch (error) {
      console.error(`Database connection attempt failed. Retries left: ${retries-1}`, error);
      retries--;
      if (retries === 0) throw error;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  return false;
}

// Export a function to ensure clean connection state
export async function ensureConnection(): Promise<void> {
  try {
    // End existing pool if it exists
    if (pool) {
      await pool.end();
      pool = null;
      db = null;
    }
    
    // Wait a moment for connections to fully close
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create new pool and verify connection
    const newPool = getPool();
    const client = await newPool.connect();
    try {
      await client.query('SELECT 1');
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Failed to ensure clean connection state:", error);
    throw error;
  }
}

// Export pool for direct access when needed
export { pool };
