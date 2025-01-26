import { TRPCError } from "@trpc/server";
import { and, asc, desc, eq, sql } from "drizzle-orm";
import { z } from "zod";
import { areas, projects, tasks } from "../../db/schema";
import { createTRPCRouter, protectedProcedure } from "../trpc";

// Project status type from schema
type ProjectStatus = typeof projects.$inferSelect.status;

// Input validation schemas
const createProjectSchema = z.object({
  name: z.string().min(3).max(100),
  description: z.string().optional(),
  areaId: z.string().uuid(),
  status: z
    .enum(["active", "completed", "archived"] as const)
    .default("active"),
  targetDate: z.date().min(new Date()).optional(), // Optional but must be in future if provided
});

const updateProjectSchema = createProjectSchema.partial().extend({
  id: z.string().uuid(),
});

export const projectRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createProjectSchema)
    .mutation(async ({ ctx, input }) => {
      // Validate area exists and is active or evergreen
      const area = await ctx.db.query.areas.findFirst({
        where: eq(areas.id, input.areaId),
      });

      if (!area) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Parent area not found",
        });
      }

      if (area.status === "archived") {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot create project under archived area",
        });
      }

      // Check for name uniqueness within area
      const existing = await ctx.db.query.projects.findFirst({
        where: and(
          eq(projects.areaId, input.areaId),
          eq(projects.name, input.name),
        ),
      });

      if (existing) {
        throw new TRPCError({
          code: "CONFLICT",
          message: "A project with this name already exists under this area",
        });
      }

      return ctx.db.insert(projects).values({
        ...input,
        userId: ctx.session.user.id,
      });
    }),

  list: protectedProcedure
    .input(
      z.object({
        areaId: z.string().uuid(),
        status: z.enum(["active", "completed", "archived"] as const).optional(),
      }),
    )
    .query(async ({ ctx, input }) => {
      const conditions = [eq(projects.areaId, input.areaId)];

      if (input.status) {
        conditions.push(eq(projects.status, input.status));
      }

      return ctx.db.query.projects.findMany({
        where: and(...conditions),
        orderBy: (projects) => [
          asc(projects.status),
          asc(projects.targetDate),
          desc(projects.createdAt),
        ],
        with: {
          area: true,
        },
      });
    }),

  byId: protectedProcedure
    .input(z.string().uuid())
    .query(async ({ ctx, input }) => {
      const project = await ctx.db.query.projects.findFirst({
        where: eq(projects.id, input),
        with: {
          area: true,
        },
      });

      if (!project) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Project not found",
        });
      }

      // Get task counts
      const taskCounts = await ctx.db
        .select({
          total: sql<number>`count(*)`,
          completed: sql<number>`sum(case when status = 'completed' then 1 else 0 end)`,
        })
        .from(tasks)
        .where(eq(tasks.projectId, input));

      const total = taskCounts[0]?.total ?? 0;
      const completed = taskCounts[0]?.completed ?? 0;
      const active = total - completed;

      return {
        ...project,
        taskCounts: {
          total,
          active,
          completed,
        },
      };
    }),

  update: protectedProcedure
    .input(updateProjectSchema)
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      const existing = await ctx.db.query.projects.findFirst({
        where: eq(projects.id, id),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Project not found",
        });
      }

      // Validate status transition
      if (data.status && data.status !== existing.status) {
        const validTransitions: Record<ProjectStatus, ProjectStatus[]> = {
          active: ["completed", "archived"],
          completed: ["active", "archived"],
          archived: ["active"],
        };

        if (!validTransitions[existing.status]?.includes(data.status)) {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: `Invalid status transition from ${existing.status} to ${data.status}`,
          });
        }

        // If completing project, check all tasks are completed
        if (data.status === "completed") {
          const activeTasks = await ctx.db.query.tasks.findFirst({
            where: and(eq(tasks.projectId, id), eq(tasks.status, "active")),
          });

          if (activeTasks) {
            throw new TRPCError({
              code: "BAD_REQUEST",
              message: "Cannot complete project with active tasks",
            });
          }
        }
      }

      // If changing area, validate new area exists and is active or evergreen
      if (data.areaId) {
        const newArea = await ctx.db.query.areas.findFirst({
          where: eq(areas.id, data.areaId),
        });

        if (!newArea) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "New parent area not found",
          });
        }

        if (newArea.status === "archived") {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: "Cannot move project under archived area",
          });
        }
      }

      return ctx.db.update(projects).set(data).where(eq(projects.id, id));
    }),

  delete: protectedProcedure
    .input(z.string().uuid())
    .mutation(async ({ ctx, input }) => {
      const existing = await ctx.db.query.projects.findFirst({
        where: eq(projects.id, input),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Project not found",
        });
      }

      // Check for active tasks
      const activeTasks = await ctx.db.query.tasks.findFirst({
        where: and(eq(tasks.projectId, input), eq(tasks.status, "active")),
      });

      if (activeTasks) {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot delete project with active tasks",
        });
      }

      return ctx.db.delete(projects).where(eq(projects.id, input));
    }),
});
