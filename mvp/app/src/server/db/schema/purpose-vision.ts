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

export const createTable = pgTableCreator((name) => `app_${name}`);

export const purposes = createTable(
  "purpose",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: varchar("user_id", { length: 255 })
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
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
      table.name
    ),
  })
);

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
      table.name
    ),
  })
);

export const purposesRelations = relations(purposes, ({ many }) => ({
  visions: many(visions),
}));

export const visionsRelations = relations(visions, ({ one }) => ({
  purpose: one(purposes, {
    fields: [visions.purposeId],
    references: [purposes.id],
  }),
}));
