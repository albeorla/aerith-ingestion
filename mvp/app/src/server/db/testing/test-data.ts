import { sql } from "drizzle-orm";
import { mockSession } from "../../api/__tests__/test-utils";
import * as schema from "../schema";
import { getDb } from "./test-db";

type TableResult = Record<string, unknown> & {
  tablename: string;
};

export async function cleanupTestData() {
  const db = getDb();
  await db.transaction(async (tx) => {
    // Check if there are any tables to clean
    const result = await tx.execute<TableResult>(sql`
      SELECT tablename 
      FROM pg_tables 
      WHERE schemaname = 'public'
    `);

    const tables = result.rows;
    if (tables.length > 0) {
      const tableList = tables
        .map((t: TableResult) => `public.${t.tablename}`)
        .join(", ");

      await tx.execute(sql`
        TRUNCATE TABLE ${sql.raw(tableList)} RESTART IDENTITY CASCADE
      `);
    }
  });
}

export async function setupTestData() {
  const db = getDb();
  await db.transaction(async (tx) => {
    await tx.insert(schema.users).values({
      id: mockSession.user.id,
      name: mockSession.user.name,
      email: mockSession.user.email!,
      emailVerified: new Date(),
      image: mockSession.user.image!,
    });
  });
}
