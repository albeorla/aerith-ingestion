import { DrizzleAdapter } from "@auth/drizzle-adapter";
import type { DefaultSession, Session } from "next-auth";
import NextAuth from "next-auth";

import {
  accounts,
  db,
  sessions,
  users,
  verificationTokens,
} from "@/server/db/schema";

/**
 * Module augmentation for `next-auth` types. Allows us to add custom properties to the `session`
 * object and keep type safety.
 *
 * @see https://next-auth.js.org/getting-started/typescript#module-augmentation
 */
declare module "next-auth" {
  interface Session extends DefaultSession {
    user: {
      id: string;
      // ...other properties
      // role: UserRole;
    } & DefaultSession["user"];
  }

  // interface User {
  //   // ...other properties
  //   // role: UserRole;
  // }
}

/**
 * Options for NextAuth.js used to configure adapters, providers, callbacks, etc.
 *
 * @see https://next-auth.js.org/configuration/options
 */
export const authConfig = {
  adapter: DrizzleAdapter(db, {
    usersTable: users,
    accountsTable: accounts,
    sessionsTable: sessions,
    verificationTokensTable: verificationTokens,
  }),
  providers: [],
  session: {
    strategy: "database" as const,
  },
  callbacks: {
    session({ session, user }: { session: Session; user: { id: string } }) {
      if (session.user) {
        session.user.id = user.id;
      }
      return session;
    },
  },
};

export const { auth, handlers } = NextAuth(authConfig);
