import { TRPCError } from "@trpc/server";
import { and, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { areas, goals, visions } from "../../db/schema";
import { createTRPCRouter, protectedProcedure } from "../trpc";

// Goal status type from schema
type GoalStatus = typeof goals.$inferSelect.status;

// Input validation schemas
const createGoalSchema = z.object({
  name: z.string().min(3).max(100),
  description: z.string().optional(),
  visionId: z.string().uuid(),
  status: z.enum(["active", "achieved", "archived"] as const).default("active"),
  targetDate: z.date().min(new Date()), // Must be in the future
});

const updateGoalSchema = createGoalSchema.partial().extend({
  id: z.string().uuid(),
});

export const goalRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createGoalSchema)
    .mutation(async ({ ctx, input }) => {
      // Validate vision exists and is active
      const vision = await ctx.db.query.visions.findFirst({
        where: eq(visions.id, input.visionId),
      });

      if (!vision) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Parent vision not found",
        });
      }

      if (vision.status !== "active") {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot create goal under inactive vision",
        });
      }

      // Check for name uniqueness within vision
      const existing = await ctx.db.query.goals.findFirst({
        where: and(
          eq(goals.visionId, input.visionId),
          eq(goals.name, input.name),
        ),
      });

      if (existing) {
        throw new TRPCError({
          code: "CONFLICT",
          message: "A goal with this name already exists under this vision",
        });
      }

      return ctx.db.insert(goals).values({
        ...input,
        userId: ctx.session.user.id,
      });
    }),

  list: protectedProcedure
    .input(
      z.object({
        visionId: z.string().uuid(),
        status: z.enum(["active", "achieved", "archived"] as const).optional(),
      }),
    )
    .query(async ({ ctx, input }) => {
      const conditions = [eq(goals.visionId, input.visionId)];

      if (input.status) {
        conditions.push(eq(goals.status, input.status));
      }

      return ctx.db.query.goals.findMany({
        where: and(...conditions),
        orderBy: (goals, { desc }) => [desc(goals.createdAt)],
        with: {
          vision: true,
        },
      });
    }),

  byId: protectedProcedure
    .input(z.string().uuid())
    .query(async ({ ctx, input }) => {
      const goal = await ctx.db.query.goals.findFirst({
        where: eq(goals.id, input),
        with: {
          vision: true,
        },
      });

      if (!goal) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Goal not found",
        });
      }

      // Get area count
      const areaCount = await ctx.db
        .select({ count: sql<number>`count(*)` })
        .from(areas)
        .where(eq(areas.goalId, input));

      return {
        ...goal,
        areaCount: areaCount[0]?.count ?? 0,
      };
    }),

  update: protectedProcedure
    .input(updateGoalSchema)
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      const existing = await ctx.db.query.goals.findFirst({
        where: eq(goals.id, id),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Goal not found",
        });
      }

      // Validate status transition
      if (data.status && data.status !== existing.status) {
        const validTransitions: Record<GoalStatus, GoalStatus[]> = {
          active: ["achieved", "archived"],
          achieved: ["archived"],
          archived: [],
        };

        if (!validTransitions[existing.status]?.includes(data.status)) {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: `Invalid status transition from ${existing.status} to ${data.status}`,
          });
        }
      }

      // If changing vision, validate new vision exists and is active
      if (data.visionId) {
        const newVision = await ctx.db.query.visions.findFirst({
          where: eq(visions.id, data.visionId),
        });

        if (!newVision) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "New parent vision not found",
          });
        }

        if (newVision.status !== "active") {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: "Cannot move goal under inactive vision",
          });
        }
      }

      return ctx.db.update(goals).set(data).where(eq(goals.id, id));
    }),

  delete: protectedProcedure
    .input(z.string().uuid())
    .mutation(async ({ ctx, input }) => {
      const existing = await ctx.db.query.goals.findFirst({
        where: eq(goals.id, input),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Goal not found",
        });
      }

      // Check for active areas
      const activeAreas = await ctx.db.query.areas.findFirst({
        where: and(
          eq(areas.goalId, input),
          eq(areas.status, "active" as const),
        ),
      });

      if (activeAreas) {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot delete goal with active areas",
        });
      }

      return ctx.db.delete(goals).where(eq(goals.id, input));
    }),
});
