import { db, goals } from "@/server/db/schema";
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

describe("goal router", () => {
  let visionId: string;

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

      visionId = vision.id;
    });
  });

  it("should create a goal", async () => {
    const caller = await createCaller(mockSession);

    const input: ProcedureInput<"goal", "create"> = {
      name: "Test Goal",
      description: "Test Description",
      visionId,
      status: "active" as const,
      targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
    };

    await db.transaction(async (tx) => {
      const result = await caller.goal.create(input);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create goal");
      const created = result[0] as Goal;
      expect(created).toBeDefined();
      expect(created).toMatchObject({
        ...input,
        userId: mockSession.user.id,
      });
    });
  });

  it("should list goals", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test goals
      const input1: ProcedureInput<"goal", "create"> = {
        name: "Test Goal 1",
        description: "Test Description 1",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      };
      const input2: ProcedureInput<"goal", "create"> = {
        name: "Test Goal 2",
        description: "Test Description 2",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 60), // 60 days from now
      };

      // Create both goals
      const [goal1Result, goal2Result] = await Promise.all([
        caller.goal.create(input1),
        caller.goal.create(input2),
      ]);

      expect(goal1Result).toHaveLength(1);
      expect(goal2Result).toHaveLength(1);

      // List all goals for the vision
      const result = await caller.goal.list({ visionId });

      expect(result).toBeDefined();
      const filteredResults = result.filter(
        (g) => g.name === input1.name || g.name === input2.name,
      );
      expect(filteredResults).toHaveLength(2);
      expect(result.find((g) => g.name === input2.name)).toBeDefined();
      expect(result.find((g) => g.name === input1.name)).toBeDefined();
    });
  });

  it("should update a goal", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test goal
      const createInput: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      };

      const createResult = await caller.goal.create(createInput);
      expect(createResult).toHaveLength(1);
      if (!createResult[0]) throw new Error("Failed to create goal");
      const created = createResult[0] as Goal;

      // Verify goal exists
      const existing = await caller.goal.byId(created.id);
      expect(existing).toBeDefined();
      expect(existing.id).toBe(created.id);

      // Update the goal
      const updateInput: ProcedureInput<"goal", "update"> = {
        id: created.id,
        name: "Updated Goal",
        description: "Updated Description",
        status: "achieved" as const,
      };

      const resultUpdate = await caller.goal.update(updateInput);

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

  it("should delete a goal", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test goal
      const createInput: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      };

      const result = await caller.goal.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create goal");
      const created = result[0] as Goal;

      // Delete the goal
      await caller.goal.delete(created.id);

      // Verify deletion
      const deleted = await tx
        .select()
        .from(goals)
        .where(eq(goals.id, created.id));
      expect(deleted).toHaveLength(0);
    });
  });

  it("should not allow unauthorized access", async () => {
    const caller = await createCaller(null);

    await db.transaction(async (tx) => {
      const input: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      };

      await expect(caller.goal.create(input)).rejects.toThrow("UNAUTHORIZED");
    });
  });

  it("should not allow creating goal under inactive vision", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Archive the vision
      await caller.vision.update({
        id: visionId,
        status: "archived",
      });

      const input: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      };

      await expect(caller.goal.create(input)).rejects.toThrow(
        "Cannot create goal under inactive vision",
      );
    });
  });

  it("should not allow deleting goal with active areas", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create goal
      const goalResult = await caller.goal.create({
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30), // 30 days from now
      });
      if (!goalResult[0]) throw new Error("Failed to create goal");
      const goal = goalResult[0] as Goal;

      // Create active area
      await caller.area.create({
        name: "Test Area",
        description: "Test Description",
        goalId: goal.id,
        status: "active" as const,
      });

      // Try to delete goal
      await expect(caller.goal.delete(goal.id)).rejects.toThrow(
        "Cannot delete goal with active areas",
      );
    });
  });

  it("should not allow invalid status transitions", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test goal
      const createInput: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
      };

      const createResult = await caller.goal.create(createInput);
      expect(createResult).toHaveLength(1);
      if (!createResult[0]) throw new Error("Failed to create goal");
      const created = createResult[0] as Goal;

      // Try to update with invalid status transition
      const updateInput: ProcedureInput<"goal", "update"> = {
        id: created.id,
        status: "invalid_status" as any,
      };

      await expect(caller.goal.update(updateInput)).rejects.toThrow();
    });
  });

  it("should not allow updating non-existent goal", async () => {
    const caller = await createCaller(mockSession);

    const updateInput: ProcedureInput<"goal", "update"> = {
      id: "00000000-0000-0000-0000-000000000000", // Valid UUID that won't exist
      name: "Updated Goal",
      description: "Updated Description",
      status: "achieved" as const,
    };

    await expect(caller.goal.update(updateInput)).rejects.toThrow("NOT_FOUND");
  });

  it("should validate goal target date", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Try to create goal with past target date
      const pastDate = new Date(Date.now() - 1000 * 60 * 60 * 24); // Yesterday
      const createInput: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: pastDate,
      };

      await expect(caller.goal.create(createInput)).rejects.toThrow();
    });
  });

  it("should validate status transitions", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test goal
      const createInput: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
      };

      const createResult = await caller.goal.create(createInput);
      expect(createResult).toHaveLength(1);
      if (!createResult[0]) throw new Error("Failed to create goal");
      const created = createResult[0] as Goal;

      // Update to achieved
      const achievedUpdate: ProcedureInput<"goal", "update"> = {
        id: created.id,
        status: "achieved" as const,
      };

      const achievedResult = await caller.goal.update(achievedUpdate);
      expect(achievedResult).toHaveLength(1);
      expect(achievedResult[0]).toMatchObject({
        status: "achieved",
      });

      // Update to archived
      const archivedUpdate: ProcedureInput<"goal", "update"> = {
        id: created.id,
        status: "archived" as const,
      };

      const archivedResult = await caller.goal.update(archivedUpdate);
      expect(archivedResult).toHaveLength(1);
      expect(archivedResult[0]).toMatchObject({
        status: "archived",
      });
    });
  });

  it("should prevent duplicate goal names within vision", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create first goal
      const createInput: ProcedureInput<"goal", "create"> = {
        name: "Test Goal",
        description: "Test Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
      };

      const firstResult = await caller.goal.create(createInput);
      expect(firstResult).toHaveLength(1);

      // Try to create second goal with same name
      await expect(caller.goal.create(createInput)).rejects.toThrow();

      // Should allow same name in different vision
      const newVisionResult = await caller.vision.create({
        name: "Another Vision",
        description: "Another Vision Description",
        purposeId: (await caller.vision.byId(visionId)).purposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 365),
      });
      expect(newVisionResult).toHaveLength(1);
      if (!newVisionResult[0]) throw new Error("Failed to create vision");

      // Create goal with same name but different vision
      const differentVisionInput = {
        ...createInput,
        visionId: newVisionResult[0].id,
      };
      const thirdResult = await caller.goal.create(differentVisionInput);
      expect(thirdResult).toHaveLength(1);
    });
  });

  it("should list and filter goals", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create goals with different statuses
      const activeGoal = await caller.goal.create({
        name: "Active Goal",
        description: "Active Goal Description",
        visionId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
      });
      expect(activeGoal).toHaveLength(1);

      const achievedGoal = await caller.goal.create({
        name: "Achieved Goal",
        description: "Achieved Goal Description",
        visionId,
        status: "achieved" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
      });
      expect(achievedGoal).toHaveLength(1);

      const archivedGoal = await caller.goal.create({
        name: "Archived Goal",
        description: "Archived Goal Description",
        visionId,
        status: "archived" as const,
        targetDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30),
      });
      expect(archivedGoal).toHaveLength(1);

      // List all goals
      const allGoals = await caller.goal.list({ visionId });
      expect(allGoals.length).toBeGreaterThanOrEqual(3);

      // Verify goals are ordered by creation date (descending)
      const relevantGoals = allGoals.filter(
        (g) =>
          g.name === "Active Goal" ||
          g.name === "Achieved Goal" ||
          g.name === "Archived Goal",
      );
      expect(relevantGoals).toHaveLength(3);

      // Verify we can find goals by status
      const activeGoals = relevantGoals.filter((g) => g.status === "active");
      expect(activeGoals).toHaveLength(1);
      expect(activeGoals[0]?.name).toBe("Active Goal");

      const achievedGoals = relevantGoals.filter(
        (g) => g.status === "achieved",
      );
      expect(achievedGoals).toHaveLength(1);
      expect(achievedGoals[0]?.name).toBe("Achieved Goal");

      const archivedGoals = relevantGoals.filter(
        (g) => g.status === "archived",
      );
      expect(archivedGoals).toHaveLength(1);
      expect(archivedGoals[0]?.name).toBe("Archived Goal");
    });
  });
});
