import NextAuth from "next-auth";
import { cache } from "react";
import { authConfig, handlers } from "./config";

const { auth: uncachedAuth, signIn, signOut } = NextAuth(authConfig);
const auth = cache(uncachedAuth);

export { auth, handlers, signIn, signOut };
