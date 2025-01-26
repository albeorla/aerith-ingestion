import { areaRouter } from "./routers/area";
import { goalRouter } from "./routers/goal";
import { projectRouter } from "./routers/project";
import { purposeRouter } from "./routers/purpose";
import { taskRouter } from "./routers/task";
import { visionRouter } from "./routers/vision";
import { createTRPCRouter } from "./trpc";

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
  purpose: purposeRouter,
  vision: visionRouter,
  goal: goalRouter,
  area: areaRouter,
  project: projectRouter,
  task: taskRouter,
});

// Export type router type signature,
// NOT the router itself.
export type AppRouter = typeof appRouter;
