import "server-only";

import { appRouter, type AppRouter } from "@/server/api/root";
import { auth } from "@/server/auth";
import { db } from "@/server/db/schema";
import { createHydrationHelpers } from "@trpc/react-query/rsc";
import { cache } from "react";
import { createQueryClient } from "./query-client";

const getQueryClient = cache(createQueryClient);

const createCaller = cache(async () => {
  const session = await auth();
  return appRouter.createCaller({
    session,
    db,
  });
});

const { trpc, HydrateClient } = createHydrationHelpers<AppRouter>(
  await createCaller(),
  getQueryClient,
);

export { trpc as api, HydrateClient };
