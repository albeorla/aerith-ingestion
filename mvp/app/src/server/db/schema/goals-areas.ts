import { relations, sql } from "drizzle-orm";
import {
  index,
  pgTableCreator,
  text,
  timestamp,
  uuid,
  varchar,
  uniqueIndex,
} from "drizzle-orm/pg-core";
import { users } from "../schema";
import { visions } from "./purpose-vision";

export const createTable = pgTableCreator((name) => `app_${name}`);

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
    uniqueNamePerUser: uniqueIndex("goal_unique_name_per_user_idx").on(
      table.userId,
      table.name
    ),
  })
);

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
      table.name
    ),
  })
);

export const goalsRelations = relations(goals, ({ one, many }) => ({
  vision: one(visions, {
    fields: [goals.visionId],
    references: [visions.id],
  }),
  areas: many(areas),
}));

export const areasRelations = relations(areas, ({ one }) => ({
  goal: one(goals, {
    fields: [areas.goalId],
    references: [goals.id],
  }),
})); 