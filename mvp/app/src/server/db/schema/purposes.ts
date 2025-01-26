import { relations, sql } from "drizzle-orm";
import {
  index,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import { users } from "./users";
import { createTable } from "./utils";
import { visions } from "./visions";

export const purposes = createTable(
  "purpose",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id")
      .notNull()
      .references(() => users.id),
    name: varchar("name", { length: 100 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 })
      .notNull()
      .default("active")
      .$type<"active" | "archived">(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("purpose_user_id_idx").on(table.userId),
    statusIdx: index("purpose_status_idx").on(table.status),
    uniqueNamePerUser: uniqueIndex("purpose_unique_name_per_user_idx").on(
      table.userId,
      table.name,
    ),
  }),
);

export const purposesRelations = relations(purposes, ({ many }) => ({
  visions: many(visions),
}));
