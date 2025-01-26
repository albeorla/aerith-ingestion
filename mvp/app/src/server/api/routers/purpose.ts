import { TRPCError } from "@trpc/server";
import { and, eq, ne } from "drizzle-orm";
import { z } from "zod";
import { purposes } from "../../db/schema";
import { createTRPCRouter, protectedProcedure } from "../trpc";

// Input validation schemas
const createPurposeSchema = z.object({
  name: z.string().min(3).max(100),
  description: z.string().optional(),
  status: z.enum(["active", "archived"]).default("active"),
});

const updatePurposeSchema = createPurposeSchema.partial().extend({
  id: z.string().uuid(),
});

export const purposeRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createPurposeSchema)
    .mutation(async ({ ctx, input }) => {
      // Check for name uniqueness within user's purposes
      const existing = await ctx.db.query.purposes.findFirst({
        where: and(
          eq(purposes.name, input.name),
          eq(purposes.userId, ctx.session.user.id),
        ),
      });

      if (existing) {
        throw new TRPCError({
          code: "CONFLICT",
          message: "A purpose with this name already exists",
        });
      }

      // Create the purpose
      const result = await ctx.db
        .insert(purposes)
        .values({
          ...input,
          userId: ctx.session.user.id,
        })
        .returning();

      return result;
    }),

  list: protectedProcedure
    .input(
      z
        .object({
          status: z.enum(["active", "archived"]).optional(),
        })
        .optional(),
    )
    .query(async ({ ctx, input }) => {
      const conditions = [eq(purposes.userId, ctx.session.user.id)];
      if (input?.status) {
        conditions.push(eq(purposes.status, input.status));
      }

      return ctx.db.query.purposes.findMany({
        where: and(...conditions),
        orderBy: (purposes, { desc }) => [desc(purposes.createdAt)],
      });
    }),

  byId: protectedProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ ctx, input }) => {
      const purpose = await ctx.db
        .select()
        .from(purposes)
        .where(
          and(
            eq(purposes.id, input.id),
            eq(purposes.userId, ctx.session.user.id),
            eq(purposes.status, "active"),
          ),
        );

      if (!purpose[0]) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Purpose not found",
        });
      }

      return purpose[0];
    }),

  update: protectedProcedure
    .input(updatePurposeSchema)
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      const existing = await ctx.db.query.purposes.findFirst({
        where: and(
          eq(purposes.id, id),
          eq(purposes.userId, ctx.session.user.id),
        ),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Purpose not found",
        });
      }

      // Check name uniqueness if name is being updated
      if (data.name && data.name !== existing.name) {
        const nameExists = await ctx.db.query.purposes.findFirst({
          where: and(
            eq(purposes.name, data.name),
            eq(purposes.userId, ctx.session.user.id),
            ne(purposes.id, id),
          ),
        });

        if (nameExists) {
          throw new TRPCError({
            code: "CONFLICT",
            message: "A purpose with this name already exists",
          });
        }
      }

      // Validate status transition
      if (data.status && data.status !== existing.status) {
        if (existing.status === "archived" && data.status === "active") {
          // Allow reactivation
        } else if (existing.status === "active" && data.status === "archived") {
          // Allow archiving
        } else {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: "Invalid status transition",
          });
        }
      }

      const result = await ctx.db
        .update(purposes)
        .set(data)
        .where(
          and(eq(purposes.id, id), eq(purposes.userId, ctx.session.user.id)),
        )
        .returning();

      return result[0];
    }),

  delete: protectedProcedure
    .input(z.string().uuid())
    .mutation(async ({ ctx, input }) => {
      const existing = await ctx.db.query.purposes.findFirst({
        where: and(
          eq(purposes.id, input),
          eq(purposes.userId, ctx.session.user.id),
        ),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Purpose not found",
        });
      }

      const result = await ctx.db
        .delete(purposes)
        .where(
          and(eq(purposes.id, input), eq(purposes.userId, ctx.session.user.id)),
        )
        .returning();

      return result[0];
    }),
});
