import { TRPCError } from "@trpc/server";
import { and, asc, desc, eq } from "drizzle-orm";
import { z } from "zod";
import { projects, tasks } from "../../db/schema";
import { createTRPCRouter, protectedProcedure } from "../trpc";

// Task status type from schema
type TaskStatus = typeof tasks.$inferSelect.status;

// Input validation schemas
const createTaskSchema = z.object({
  name: z.string().min(3).max(100),
  description: z.string().optional(),
  projectId: z.string().uuid(),
  status: z.enum(["active", "completed"] as const).default("active"),
  dueDate: z.date().min(new Date()).optional(), // Optional but must be in future if provided
});

const updateTaskSchema = createTaskSchema.partial().extend({
  id: z.string().uuid(),
});

export const taskRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createTaskSchema)
    .mutation(async ({ ctx, input }) => {
      // Validate project exists and is active
      const project = await ctx.db.query.projects.findFirst({
        where: eq(projects.id, input.projectId),
      });

      if (!project) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Parent project not found",
        });
      }

      if (project.status !== "active") {
        throw new TRPCError({
          code: "BAD_REQUEST",
          message: "Cannot create task under inactive project",
        });
      }

      // Check for name uniqueness within project
      const existing = await ctx.db.query.tasks.findFirst({
        where: and(
          eq(tasks.projectId, input.projectId),
          eq(tasks.name, input.name),
        ),
      });

      if (existing) {
        throw new TRPCError({
          code: "CONFLICT",
          message: "A task with this name already exists under this project",
        });
      }

      return ctx.db.insert(tasks).values({
        ...input,
        userId: ctx.session.user.id,
      });
    }),

  list: protectedProcedure
    .input(
      z.object({
        projectId: z.string().uuid(),
        status: z.enum(["active", "completed"] as const).optional(),
      }),
    )
    .query(async ({ ctx, input }) => {
      const conditions = [eq(tasks.projectId, input.projectId)];

      if (input.status) {
        conditions.push(eq(tasks.status, input.status));
      }

      return ctx.db.query.tasks.findMany({
        where: and(...conditions),
        orderBy: (tasks) => [
          asc(tasks.status),
          asc(tasks.dueDate),
          desc(tasks.createdAt),
        ],
        with: {
          project: true,
        },
      });
    }),

  byId: protectedProcedure
    .input(z.string().uuid())
    .query(async ({ ctx, input }) => {
      const task = await ctx.db.query.tasks.findFirst({
        where: eq(tasks.id, input),
        with: {
          project: {
            with: {
              area: true,
            },
          },
        },
      });

      if (!task) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Task not found",
        });
      }

      return task;
    }),

  update: protectedProcedure
    .input(updateTaskSchema)
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      const existing = await ctx.db.query.tasks.findFirst({
        where: eq(tasks.id, id),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Task not found",
        });
      }

      // Validate status transition
      if (data.status && data.status !== existing.status) {
        const validTransitions: Record<TaskStatus, TaskStatus[]> = {
          active: ["completed"],
          completed: ["active"],
        };

        if (!validTransitions[existing.status]?.includes(data.status)) {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: `Invalid status transition from ${existing.status} to ${data.status}`,
          });
        }
      }

      // If changing project, validate new project exists and is active
      if (data.projectId) {
        const newProject = await ctx.db.query.projects.findFirst({
          where: eq(projects.id, data.projectId),
        });

        if (!newProject) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "New parent project not found",
          });
        }

        if (newProject.status !== "active") {
          throw new TRPCError({
            code: "BAD_REQUEST",
            message: "Cannot move task under inactive project",
          });
        }
      }

      return ctx.db.update(tasks).set(data).where(eq(tasks.id, id));
    }),

  delete: protectedProcedure
    .input(z.string().uuid())
    .mutation(async ({ ctx, input }) => {
      const existing = await ctx.db.query.tasks.findFirst({
        where: eq(tasks.id, input),
      });

      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Task not found",
        });
      }

      return ctx.db.delete(tasks).where(eq(tasks.id, input));
    }),
});
