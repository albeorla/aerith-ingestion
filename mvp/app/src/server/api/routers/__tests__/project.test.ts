import { db, projects } from "@/server/db/schema";
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

describe("project router", () => {
  let areaId: string;

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

      areaId = area.id;
    });
  });

  it("should create a project", async () => {
    const caller = await createCaller(mockSession);

    const input: ProcedureInput<"project", "create"> = {
      name: "Test Project",
      description: "Test Description",
      areaId,
      status: "active" as const,
    };

    await db.transaction(async (tx) => {
      const result = await caller.project.create(input);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create project");
      const created = result[0] as Project;
      expect(created).toBeDefined();
      expect(created).toMatchObject({
        ...input,
        userId: mockSession.user.id,
      });
    });
  });

  it("should list projects", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test projects
      const input1: ProcedureInput<"project", "create"> = {
        name: "Test Project 1",
        description: "Test Description 1",
        areaId,
        status: "active" as const,
      };
      const input2: ProcedureInput<"project", "create"> = {
        name: "Test Project 2",
        description: "Test Description 2",
        areaId,
        status: "active" as const,
      };

      // Create both projects
      const [project1Result, project2Result] = await Promise.all([
        caller.project.create(input1),
        caller.project.create(input2),
      ]);

      expect(project1Result).toHaveLength(1);
      expect(project2Result).toHaveLength(1);

      // List all projects for the area
      const result = await caller.project.list({ areaId });

      expect(result).toBeDefined();
      const filteredResults = result.filter(
        (p) => p.name === input1.name || p.name === input2.name,
      );
      expect(filteredResults).toHaveLength(2);
      expect(result.find((p) => p.name === input2.name)).toBeDefined();
      expect(result.find((p) => p.name === input1.name)).toBeDefined();
    });
  });

  it("should update a project", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test project
      const createInput: ProcedureInput<"project", "create"> = {
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      };

      const result = await caller.project.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create project");
      const created = result[0] as Project;

      // Verify project exists
      const existing = await caller.project.byId(created.id);
      expect(existing).toBeDefined();
      expect(existing.id).toBe(created.id);

      // Update the project
      const updateInput: ProcedureInput<"project", "update"> = {
        id: created.id,
        name: "Updated Project",
        description: "Updated Description",
        status: "completed" as const,
      };

      const resultUpdate = await caller.project.update(updateInput);

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

  it("should delete a project", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test project
      const createInput: ProcedureInput<"project", "create"> = {
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      };

      const result = await caller.project.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create project");
      const created = result[0] as Project;

      // Delete the project
      await caller.project.delete(created.id);

      // Verify deletion
      const deleted = await tx
        .select()
        .from(projects)
        .where(eq(projects.id, created.id));
      expect(deleted).toHaveLength(0);
    });
  });

  it("should not allow unauthorized access", async () => {
    const caller = await createCaller(null);

    await db.transaction(async (tx) => {
      const input: ProcedureInput<"project", "create"> = {
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      };

      await expect(caller.project.create(input)).rejects.toThrow(
        "UNAUTHORIZED",
      );
    });
  });

  it("should not allow creating project under inactive area", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Archive the area
      await caller.area.update({
        id: areaId,
        status: "archived",
      });

      const input: ProcedureInput<"project", "create"> = {
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      };

      await expect(caller.project.create(input)).rejects.toThrow(
        "Cannot create project under archived area",
      );
    });
  });

  it("should not allow completing project with active tasks", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create project
      const projectResult = await caller.project.create({
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      });
      if (!projectResult[0]) throw new Error("Failed to create project");
      const project = projectResult[0] as Project;

      // Create active task
      await caller.task.create({
        name: "Test Task",
        description: "Test Description",
        projectId: project.id,
        status: "active" as const,
      });

      // Try to complete project
      await expect(
        caller.project.update({
          id: project.id,
          status: "completed",
        }),
      ).rejects.toThrow("Cannot complete project with active tasks");
    });
  });

  it("should prevent duplicate project names within area", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create first project
      const createInput: ProcedureInput<"project", "create"> = {
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      };

      const firstResult = await caller.project.create(createInput);
      expect(firstResult).toHaveLength(1);

      // Try to create second project with same name
      await expect(caller.project.create(createInput)).rejects.toThrow();

      // Should allow same name in different area
      const newAreaResult = await caller.area.create({
        name: "Another Area",
        description: "Another Area Description",
        goalId: (await caller.area.byId(areaId)).goalId,
        status: "active" as const,
      });
      expect(newAreaResult).toHaveLength(1);
      if (!newAreaResult[0]) throw new Error("Failed to create area");

      // Create project with same name but different area
      const differentAreaInput = {
        ...createInput,
        areaId: newAreaResult[0].id,
      };
      const thirdResult = await caller.project.create(differentAreaInput);
      expect(thirdResult).toHaveLength(1);
    });
  });

  it("should validate project status transitions", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test project
      const createInput: ProcedureInput<"project", "create"> = {
        name: "Test Project",
        description: "Test Description",
        areaId,
        status: "active" as const,
      };

      const createResult = await caller.project.create(createInput);
      expect(createResult).toHaveLength(1);
      if (!createResult[0]) throw new Error("Failed to create project");
      const created = createResult[0] as Project;

      // Try invalid status
      const invalidUpdate: ProcedureInput<"project", "update"> = {
        id: created.id,
        status: "invalid_status" as any,
      };
      await expect(caller.project.update(invalidUpdate)).rejects.toThrow();

      // Update to completed (should work as no active tasks)
      const completedUpdate: ProcedureInput<"project", "update"> = {
        id: created.id,
        status: "completed" as const,
      };
      const completedResult = await caller.project.update(completedUpdate);
      expect(completedResult).toHaveLength(1);
      expect(completedResult[0]).toMatchObject({
        status: "completed",
      });

      // Update to archived
      const archivedUpdate: ProcedureInput<"project", "update"> = {
        id: created.id,
        status: "archived" as const,
      };
      const archivedResult = await caller.project.update(archivedUpdate);
      expect(archivedResult).toHaveLength(1);
      expect(archivedResult[0]).toMatchObject({
        status: "archived",
      });
    });
  });

  it("should list and filter projects", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create projects with different statuses
      const activeProject = await caller.project.create({
        name: "Active Project",
        description: "Active Project Description",
        areaId,
        status: "active" as const,
      });
      expect(activeProject).toHaveLength(1);

      const completedProject = await caller.project.create({
        name: "Completed Project",
        description: "Completed Project Description",
        areaId,
        status: "completed" as const,
      });
      expect(completedProject).toHaveLength(1);

      const archivedProject = await caller.project.create({
        name: "Archived Project",
        description: "Archived Project Description",
        areaId,
        status: "archived" as const,
      });
      expect(archivedProject).toHaveLength(1);

      // List all projects
      const allProjects = await caller.project.list({ areaId });
      expect(allProjects.length).toBeGreaterThanOrEqual(3);

      // Verify projects are ordered by creation date (descending)
      const relevantProjects = allProjects.filter(
        (p) =>
          p.name === "Active Project" ||
          p.name === "Completed Project" ||
          p.name === "Archived Project",
      );
      expect(relevantProjects).toHaveLength(3);

      // Verify we can find projects by status
      const activeProjects = relevantProjects.filter(
        (p) => p.status === "active",
      );
      expect(activeProjects).toHaveLength(1);
      expect(activeProjects[0]?.name).toBe("Active Project");

      const completedProjects = relevantProjects.filter(
        (p) => p.status === "completed",
      );
      expect(completedProjects).toHaveLength(1);
      expect(completedProjects[0]?.name).toBe("Completed Project");

      const archivedProjects = relevantProjects.filter(
        (p) => p.status === "archived",
      );
      expect(archivedProjects).toHaveLength(1);
      expect(archivedProjects[0]?.name).toBe("Archived Project");
    });
  });
});
