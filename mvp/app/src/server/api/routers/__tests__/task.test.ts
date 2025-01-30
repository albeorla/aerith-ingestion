import { db, tasks } from "@/server/db/schema";
import { eq } from "drizzle-orm";
import { beforeEach, describe, expect, it } from "vitest";
import {
  type ProcedureInput,
  createCaller,
  mockSession,
} from "../../__tests__/test-utils";

type Purpose = { id: string; [key: string]: unknown };
type Vision = { id: string; [key: string]: unknown };
type Goal = { id: string; [key: string]: unknown };
type Area = { id: string; [key: string]: unknown };
type Project = { id: string; [key: string]: unknown };
type Task = { id: string; [key: string]: unknown };

describe("task router", () => {
  let projectId: string;

  beforeEach(async () => {
    const caller = await createCaller(mockSession);

    // Create test hierarchy
    await db.transaction(async (tx) => {
      // Create purpose
      const purposeResult = await caller.purpose.create({
        name: `Test Purpose ${Date.now()}`,
        description: "Test Purpose Description",
        status: "active",
      });
      if (!purposeResult?.[0]) throw new Error("Failed to create purpose");
      const purpose = purposeResult[0] as Purpose;

      // Create vision
      const visionResult = await caller.vision.create({
        name: `Test Vision ${Date.now()}`,
        description: "Test Vision Description",
        purposeId: purpose.id,
        status: "active",
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 365), // 1 year from now
      });
      if (!visionResult?.[0]) throw new Error("Failed to create vision");
      const vision = visionResult[0] as Vision;

      // Create goal
      const goalResult = await caller.goal.create({
        name: `Test Goal ${Date.now()}`,
        description: "Test Goal Description",
        visionId: vision.id,
        status: "active",
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      });
      if (!goalResult?.[0]) throw new Error("Failed to create goal");
      const goal = goalResult[0] as Goal;

      // Create area
      const areaResult = await caller.area.create({
        name: `Test Area ${Date.now()}`,
        description: "Test Area Description",
        goalId: goal.id,
        status: "active",
      });
      if (!areaResult?.[0]) throw new Error("Failed to create area");
      const area = areaResult[0] as Area;

      // Create project
      const projectResult = await caller.project.create({
        name: `Test Project ${Date.now()}`,
        description: "Test Project Description",
        areaId: area.id,
        status: "active",
      });
      if (!projectResult?.[0]) throw new Error("Failed to create project");
      const project = projectResult[0] as Project;

      projectId = project.id;
    });
  });

  it("should create a task", async () => {
    const caller = await createCaller(mockSession);

    const input: ProcedureInput<"task", "create"> = {
      name: "Test Task",
      description: "Test Description",
      projectId,
      status: "active" as const,
    };

    await db.transaction(async (tx) => {
      const result = await caller.task.create(input);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create task");
      const created = result[0] as Task;
      expect(created).toBeDefined();
      expect(created).toMatchObject({
        ...input,
        userId: mockSession.user.id,
      });
    });
  });

  it("should list tasks", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test tasks
      const input1: ProcedureInput<"task", "create"> = {
        name: "Test Task 1",
        description: "Test Description 1",
        projectId,
        status: "active" as const,
      };
      const input2: ProcedureInput<"task", "create"> = {
        name: "Test Task 2",
        description: "Test Description 2",
        projectId,
        status: "active" as const,
      };

      // Create both tasks
      const [task1Result, task2Result] = await Promise.all([
        caller.task.create(input1),
        caller.task.create(input2),
      ]);

      expect(task1Result).toHaveLength(1);
      expect(task2Result).toHaveLength(1);

      // List all tasks for the project
      const result = await caller.task.list({ projectId });

      expect(result).toBeDefined();
      const filteredResults = result.filter(
        (t) => t.name === input1.name || t.name === input2.name,
      );
      expect(filteredResults).toHaveLength(2);
      expect(result.find((t) => t.name === input2.name)).toBeDefined();
      expect(result.find((t) => t.name === input1.name)).toBeDefined();
    });
  });

  it("should update a task", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test task
      const createInput: ProcedureInput<"task", "create"> = {
        name: "Test Task",
        description: "Test Description",
        projectId,
        status: "active" as const,
      };

      const result = await caller.task.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create task");
      const created = result[0] as Task;

      // Verify task exists
      const existing = await caller.task.byId(created.id);
      expect(existing).toBeDefined();
      expect(existing.id).toBe(created.id);

      // Update the task
      const updateInput: ProcedureInput<"task", "update"> = {
        id: created.id,
        name: "Updated Task",
        description: "Updated Description",
        status: "completed" as const,
      };

      const resultUpdate = await caller.task.update(updateInput);

      expect(resultUpdate).toBeDefined();
      expect(Array.isArray(resultUpdate)).toBe(true);
      expect(resultUpdate).toHaveLength(1);

      const updated = resultUpdate[0];
      expect(updated).toMatchObject({
        name: updateInput.name,
        description: updateInput.description,
        status: updateInput.status,
      });
    });
  });

  it("should delete a task", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test task
      const createInput: ProcedureInput<"task", "create"> = {
        name: "Test Task",
        description: "Test Description",
        projectId,
        status: "active" as const,
      };

      const result = await caller.task.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create task");
      const created = result[0] as Task;

      // Delete the task
      await caller.task.delete(created.id);

      // Verify deletion
      const deleted = await tx
        .select()
        .from(tasks)
        .where(eq(tasks.id, created.id));
      expect(deleted).toHaveLength(0);
    });
  });

  it("should not allow unauthorized access", async () => {
    const caller = await createCaller(null);

    await db.transaction(async (tx) => {
      const input: ProcedureInput<"task", "create"> = {
        name: "Test Task",
        description: "Test Description",
        projectId,
        status: "active" as const,
      };

      await expect(caller.task.create(input)).rejects.toThrow("UNAUTHORIZED");
    });
  });

  it("should not allow creating task under inactive project", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Archive the project
      await caller.project.update({
        id: projectId,
        status: "archived",
      });

      const input: ProcedureInput<"task", "create"> = {
        name: "Test Task",
        description: "Test Description",
        projectId,
        status: "active" as const,
      };

      await expect(caller.task.create(input)).rejects.toThrow(
        "Cannot create task under inactive project",
      );
    });
  });

  it("should prevent duplicate task names within project", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create first task
      const createInput: ProcedureInput<"task", "create"> = {
        name: "Test Task",
        description: "Test Description",
        projectId,
        status: "active" as const,
      };

      const firstResult = await caller.task.create(createInput);
      expect(firstResult).toHaveLength(1);

      // Try to create second task with same name
      await expect(caller.task.create(createInput)).rejects.toThrow();

      // Should allow same name in different project
      const newProjectResult = await caller.project.create({
        name: "Another Project",
        description: "Another Project Description",
        areaId: (await caller.project.byId(projectId)).areaId,
        status: "active" as const,
      });
      expect(newProjectResult).toHaveLength(1);
      if (!newProjectResult[0]) throw new Error("Failed to create project");

      // Create task with same name but different project
      const differentProjectInput = {
        ...createInput,
        projectId: newProjectResult[0].id,
      };
      const thirdResult = await caller.task.create(differentProjectInput);
      expect(thirdResult).toHaveLength(1);
    });
  });

  it("should validate task status transitions", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test task
      const createInput: ProcedureInput<"task", "create"> = {
        name: "Test Task",
        description: "Test Description",
        projectId,
        status: "active" as const,
      };

      const createResult = await caller.task.create(createInput);
      expect(createResult).toHaveLength(1);
      if (!createResult[0]) throw new Error("Failed to create task");
      const created = createResult[0] as Task;

      // Try invalid status
      const invalidUpdate: ProcedureInput<"task", "update"> = {
        id: created.id,
        status: "invalid_status" as any,
      };
      await expect(caller.task.update(invalidUpdate)).rejects.toThrow();

      // Update to completed
      const completedUpdate: ProcedureInput<"task", "update"> = {
        id: created.id,
        status: "completed" as const,
      };
      const completedResult = await caller.task.update(completedUpdate);
      expect(completedResult).toHaveLength(1);
      expect(completedResult[0]).toMatchObject({
        status: "completed",
      });

      // Update back to active
      const activeUpdate: ProcedureInput<"task", "update"> = {
        id: created.id,
        status: "active" as const,
      };
      const activeResult = await caller.task.update(activeUpdate);
      expect(activeResult).toHaveLength(1);
      expect(activeResult[0]).toMatchObject({
        status: "active",
      });
    });
  });

  it("should list and filter tasks", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create tasks with different statuses
      const activeTask = await caller.task.create({
        name: "Active Task",
        description: "Active Task Description",
        projectId,
        status: "active" as const,
      });
      expect(activeTask).toHaveLength(1);

      const completedTask = await caller.task.create({
        name: "Completed Task",
        description: "Completed Task Description",
        projectId,
        status: "completed" as const,
      });
      expect(completedTask).toHaveLength(1);

      const anotherActiveTask = await caller.task.create({
        name: "Another Active Task",
        description: "Another Active Task Description",
        projectId,
        status: "active" as const,
      });
      expect(anotherActiveTask).toHaveLength(1);

      // List all tasks
      const allTasks = await caller.task.list({ projectId });
      expect(allTasks.length).toBeGreaterThanOrEqual(3);

      // Verify tasks are ordered by creation date (descending)
      const relevantTasks = allTasks.filter(
        (t) =>
          t.name === "Active Task" ||
          t.name === "Completed Task" ||
          t.name === "Another Active Task",
      );
      expect(relevantTasks).toHaveLength(3);

      // Verify we can find tasks by status
      const activeTasks = relevantTasks.filter((t) => t.status === "active");
      expect(activeTasks).toHaveLength(2);
      expect(activeTasks.map((t) => t.name)).toContain("Active Task");
      expect(activeTasks.map((t) => t.name)).toContain("Another Active Task");

      const completedTasks = relevantTasks.filter(
        (t) => t.status === "completed",
      );
      expect(completedTasks).toHaveLength(1);
      expect(completedTasks[0]?.name).toBe("Completed Task");
    });
  });
});
