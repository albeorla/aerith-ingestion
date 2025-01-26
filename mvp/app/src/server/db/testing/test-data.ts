import { sql } from "drizzle-orm";
import { mockSession, testDb } from "../../api/__tests__/test-utils";
import * as schema from "../schema";

export async function cleanupTestData() {
  await testDb.execute(sql`
    TRUNCATE TABLE 
      app_purpose,
      app_vision,
      app_goal,
      app_area,
      app_project,
      app_task,
      app_user,
      app_account,
      app_session,
      app_verification_token
    RESTART IDENTITY CASCADE
  `);
}

export async function setupTestData() {
  await testDb.insert(schema.users).values({
    id: mockSession.user.id,
    name: mockSession.user.name,
    email: mockSession.user.email!,
    emailVerified: new Date(),
    image: mockSession.user.image!,
  });
}
