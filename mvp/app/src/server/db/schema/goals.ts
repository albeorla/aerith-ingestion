import { relations, sql } from "drizzle-orm";
import {
  decimal,
  index,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import { areas } from "./areas";
import { users } from "./users";
import { createTable } from "./utils";
import { visions } from "./visions";

export const goals = createTable(
  "goal",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    visionId: uuid("vision_id")
      .notNull()
      .references(() => visions.id, { onDelete: "cascade" }),
    name: varchar("name", { length: 100 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 })
      .notNull()
      .default("active")
      .$type<"active" | "achieved" | "archived">(),
    targetDate: timestamp("target_date", { withTimezone: true }),
    progressPercentage: decimal("progress_percentage"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("goal_user_id_idx").on(table.userId),
    visionIdIdx: index("goal_vision_id_idx").on(table.visionId),
    statusIdx: index("goal_status_idx").on(table.status),
    targetDateIdx: index("goal_target_date_idx").on(table.targetDate),
    uniqueNamePerUser: uniqueIndex("goal_unique_name_per_vision_idx").on(
      table.visionId,
      table.name,
    ),
  }),
);

export const goalsRelations = relations(goals, ({ one, many }) => ({
  vision: one(visions, {
    fields: [goals.visionId],
    references: [visions.id],
  }),
  areas: many(areas),
}));
