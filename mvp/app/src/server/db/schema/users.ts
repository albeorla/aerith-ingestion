import { relations } from "drizzle-orm";
import { text, timestamp } from "drizzle-orm/pg-core";
import { accounts } from "./accounts";
import { createTable } from "./utils";

export const users = createTable("user", {
  id: text("id").primaryKey().notNull(),
  name: text("name"),
  email: text("email").notNull().unique(),
  emailVerified: timestamp("email_verified", { mode: "date" }),
  image: text("image"),
});

export const usersRelations = relations(users, ({ many }) => ({
  accounts: many(accounts),
}));
