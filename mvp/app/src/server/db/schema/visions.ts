import { relations, sql } from "drizzle-orm";
import {
  index,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import { goals } from "./goals";
import { purposes } from "./purposes";
import { users } from "./users";
import { createTable } from "./utils";

export const visions = createTable(
  "vision",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    purposeId: uuid("purpose_id")
      .notNull()
      .references(() => purposes.id, { onDelete: "cascade" }),
    name: varchar("name", { length: 100 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 })
      .notNull()
      .default("active")
      .$type<"active" | "achieved" | "archived">(),
    targetDate: timestamp("target_date", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("vision_user_id_idx").on(table.userId),
    purposeIdIdx: index("vision_purpose_id_idx").on(table.purposeId),
    statusIdx: index("vision_status_idx").on(table.status),
    targetDateIdx: index("vision_target_date_idx").on(table.targetDate),
    uniqueNamePerUser: uniqueIndex("vision_unique_name_per_user_idx").on(
      table.userId,
      table.name,
    ),
  }),
);

export const visionsRelations = relations(visions, ({ one, many }) => ({
  purpose: one(purposes, {
    fields: [visions.purposeId],
    references: [purposes.id],
  }),
  goals: many(goals),
}));
