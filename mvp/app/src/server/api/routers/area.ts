import { TRPCError } from "@trpc/server";
import { and, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { areas, goals, projects } from "../../db/schema";
import { createTRPCRouter, protectedProcedure } from "../trpc";

// Area status type from schema
type AreaStatus = typeof areas.$inferSelect.status;

// Input validation schemas
const createAreaSchema = z.object({
  name: z.string().min(3).max(100),
  description: z.string().optional(),
  goalId: z.string().uuid(),
  status: z
    .enum(["active", "archived", "evergreen"] as const)
    .default("active"),
});

const updateAreaSchema = createAreaSchema.partial().extend({
  id: z.string().uuid(),
});

export const areaRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createAreaSchema)
    .mutation(async ({ ctx, input }) => {
      // Validate goal exists and is active
      const goal = await ctx.db.query.goals.findFirst({
        where: eq(goals.id, input.goalId),
      });

      if (!goal) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Parent goal not found",
        });
      }

      if (goal.status !== "active") {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot create area under inactive goal",
        });
      }

      // Check for name uniqueness within goal
      const existing = await ctx.db.query.areas.findFirst({
        where: and(eq(areas.goalId, input.goalId), eq(areas.name, input.name)),
      });

      if (existing) {
        throw new TRPCError({
          code: "CONFLICT",
          message: "An area with this name already exists under this goal",
        });
      }

      return ctx.db
        .insert(areas)
        .values({
          ...input,
          userId: ctx.session.user.id,
        })
        .returning();
    }),

  list: protectedProcedure
    .input(
      z.object({
        goalId: z.string().uuid(),
        status: z.enum(["active", "archived", "evergreen"] as const).optional(),
      }),
    )
    .query(async ({ ctx, input }) => {
      const conditions = [eq(areas.goalId, input.goalId)];

      if (input.status) {
        conditions.push(eq(areas.status, input.status));
      }

      return ctx.db.query.areas.findMany({
        where: and(...conditions),
        orderBy: (areas, { desc }) => [desc(areas.createdAt)],
        with: {
          goal: true,
        },
      });
    }),

  byId: protectedProcedure
    .input(z.string().uuid())
    .query(async ({ ctx, input }) => {
      const area = await ctx.db.query.areas.findFirst({
        where: eq(areas.id, input),
        with: {
          goal: true,
        },
      });

      if (!area) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Area not found",
        });
      }

      // Get project count
      const projectCount = await ctx.db
        .select({ count: sql<number>`count(*)` })
        .from(projects)
        .where(eq(projects.areaId, input));

      // Get active project count
      const activeProjectCount = await ctx.db
        .select({ count: sql<number>`count(*)` })
        .from(projects)
        .where(and(eq(projects.areaId, input), eq(projects.status, "active")));

      return {
        ...area,
        projectCount: projectCount[0]?.count ?? 0,
        activeProjectCount: activeProjectCount[0]?.count ?? 0,
      };
    }),

  update: protectedProcedure
    .input(updateAreaSchema)
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      const existing = await ctx.db.query.areas.findFirst({
        where: eq(areas.id, id),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Area not found",
        });
      }

      // Validate status transition
      if (data.status && data.status !== existing.status) {
        const validTransitions: Record<AreaStatus, AreaStatus[]> = {
          active: ["archived", "evergreen"],
          archived: ["active"],
          evergreen: ["archived"],
        };

        if (!validTransitions[existing.status]?.includes(data.status)) {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: `Invalid status transition from ${existing.status} to ${data.status}`,
          });
        }

        // If transitioning to archived, check for active projects
        if (data.status === "archived") {
          const activeProjects = await ctx.db.query.projects.findFirst({
            where: and(eq(projects.areaId, id), eq(projects.status, "active")),
          });

          if (activeProjects) {
            throw new TRPCError({
              code: "BAD_REQUEST",
              message: "Cannot archive area with active projects",
            });
          }
        }
      }

      // If changing goal, validate new goal exists and is active
      if (data.goalId) {
        const newGoal = await ctx.db.query.goals.findFirst({
          where: eq(goals.id, data.goalId),
        });

        if (!newGoal) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "New parent goal not found",
          });
        }

        if (newGoal.status !== "active") {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: "Cannot move area under inactive goal",
          });
        }
      }

      return ctx.db.update(areas).set(data).where(eq(areas.id, id)).returning();
    }),

  delete: protectedProcedure
    .input(z.string().uuid())
    .mutation(async ({ ctx, input }) => {
      const existing = await ctx.db.query.areas.findFirst({
        where: eq(areas.id, input),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Area not found",
        });
      }

      // Check for active projects
      const activeProjects = await ctx.db.query.projects.findFirst({
        where: and(eq(projects.areaId, input), eq(projects.status, "active")),
      });

      if (activeProjects) {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot delete area with active projects",
        });
      }

      return ctx.db.delete(areas).where(eq(areas.id, input));
    }),
});
