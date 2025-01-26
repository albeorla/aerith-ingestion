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
import { projects } from "./projects";
import { users } from "./users";
import { createTable } from "./utils";

export const areas = createTable(
  "area",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    goalId: uuid("goal_id")
      .notNull()
      .references(() => goals.id, { onDelete: "cascade" }),
    name: varchar("name", { length: 100 }).notNull(),
    description: text("description"),
    status: varchar("status", { length: 20 })
      .notNull()
      .default("active")
      .$type<"active" | "archived" | "evergreen">(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .default(sql`CURRENT_TIMESTAMP`)
      .notNull(),
  },
  (table) => ({
    userIdIdx: index("area_user_id_idx").on(table.userId),
    goalIdIdx: index("area_goal_id_idx").on(table.goalId),
    statusIdx: index("area_status_idx").on(table.status),
    uniqueNamePerUser: uniqueIndex("area_unique_name_per_user_idx").on(
      table.userId,
      table.name,
    ),
  }),
);

export const areasRelations = relations(areas, ({ one, many }) => ({
  goal: one(goals, {
    fields: [areas.goalId],
    references: [goals.id],
  }),
  projects: many(projects),
}));
