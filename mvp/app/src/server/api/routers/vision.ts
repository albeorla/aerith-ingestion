import { TRPCError } from "@trpc/server";
import { and, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { goals, purposes, visions } from "../../db/schema";
import { createTRPCRouter, protectedProcedure } from "../trpc";

// Vision status type from schema
type VisionStatus = typeof visions.$inferSelect.status;

// Input validation schemas
const createVisionSchema = z.object({
  name: z.string().min(3).max(100),
  description: z.string().optional(),
  purposeId: z.string().uuid(),
  status: z.enum(["active", "achieved", "archived"] as const).default("active"),
  targetDate: z.date().min(new Date()), // Must be in the future
});

const updateVisionSchema = createVisionSchema.partial().extend({
  id: z.string().uuid(),
});

export const visionRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createVisionSchema)
    .mutation(async ({ ctx, input }) => {
      // Validate purpose exists and is active
      const purpose = await ctx.db.query.purposes.findFirst({
        where: and(
          eq(purposes.id, input.purposeId),
          eq(purposes.userId, ctx.session.user.id),
        ),
      });

      if (!purpose) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Parent purpose not found",
        });
      }

      if (purpose.status !== "active") {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot create vision under inactive purpose",
        });
      }

      // Check for name uniqueness within purpose
      const existing = await ctx.db.query.visions.findFirst({
        where: and(
          eq(visions.purposeId, input.purposeId),
          eq(visions.name, input.name),
          eq(visions.userId, ctx.session.user.id),
        ),
      });

      if (existing) {
        throw new TRPCError({
          code: "CONFLICT",
          message: "A vision with this name already exists under this purpose",
        });
      }

      const result = await ctx.db
        .insert(visions)
        .values({
          ...input,
          userId: ctx.session.user.id,
        })
        .returning();

      return result;
    }),

  list: protectedProcedure
    .input(
      z.object({
        purposeId: z.string().uuid(),
        status: z.enum(["active", "achieved", "archived"] as const).optional(),
      }),
    )
    .query(async ({ ctx, input }) => {
      const conditions = [
        eq(visions.purposeId, input.purposeId),
        eq(visions.userId, ctx.session.user.id),
      ];

      if (input.status) {
        conditions.push(eq(visions.status, input.status));
      }

      return ctx.db.query.visions.findMany({
        where: and(...conditions),
        orderBy: (visions, { desc }) => [desc(visions.createdAt)],
        with: {
          purpose: true,
        },
      });
    }),

  byId: protectedProcedure
    .input(z.string().uuid())
    .query(async ({ ctx, input }) => {
      const vision = await ctx.db.query.visions.findFirst({
        where: and(
          eq(visions.id, input),
          eq(visions.userId, ctx.session.user.id),
        ),
        with: {
          purpose: true,
        },
      });

      if (!vision) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Vision not found",
        });
      }

      // Get goal count
      const goalCount = await ctx.db
        .select({ count: sql<number>`count(*)` })
        .from(goals)
        .where(eq(goals.visionId, input));

      return {
        ...vision,
        goalCount: goalCount[0]?.count ?? 0,
      };
    }),

  update: protectedProcedure
    .input(updateVisionSchema)
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      const existing = await ctx.db.query.visions.findFirst({
        where: and(eq(visions.id, id), eq(visions.userId, ctx.session.user.id)),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Vision not found",
        });
      }

      // Validate status transition
      if (data.status && data.status !== existing.status) {
        const validTransitions: Record<VisionStatus, VisionStatus[]> = {
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

      // If changing purpose, validate new purpose exists and is active
      if (data.purposeId) {
        const newPurpose = await ctx.db.query.purposes.findFirst({
          where: and(
            eq(purposes.id, data.purposeId),
            eq(purposes.userId, ctx.session.user.id),
          ),
        });

        if (!newPurpose) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "New parent purpose not found",
          });
        }

        if (newPurpose.status !== "active") {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: "Cannot move vision under inactive purpose",
          });
        }
      }

      const result = await ctx.db
        .update(visions)
        .set(data)
        .where(and(eq(visions.id, id), eq(visions.userId, ctx.session.user.id)))
        .returning();

      return result[0];
    }),

  delete: protectedProcedure
    .input(z.string().uuid())
    .mutation(async ({ ctx, input }) => {
      const existing = await ctx.db.query.visions.findFirst({
        where: and(
          eq(visions.id, input),
          eq(visions.userId, ctx.session.user.id),
        ),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Vision not found",
        });
      }

      // Check for active goals
      const activeGoals = await ctx.db.query.goals.findFirst({
        where: and(
          eq(goals.visionId, input),
          eq(goals.status, "active" as const),
        ),
      });

      if (activeGoals) {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot delete vision with active goals",
        });
      }

      const result = await ctx.db
        .delete(visions)
        .where(
          and(eq(visions.id, input), eq(visions.userId, ctx.session.user.id)),
        )
        .returning();

      return result[0];
    }),
});
