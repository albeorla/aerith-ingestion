import { areas, db } from "@/server/db/schema";
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

describe("area router", () => {
  let goalId: string;

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

      goalId = goal.id;
    });
  });

  it("should create an area", async () => {
    const caller = await createCaller(mockSession);

    const input: ProcedureInput<"area", "create"> = {
      name: "Test Area",
      description: "Test Description",
      goalId,
      status: "active" as const,
    };

    await db.transaction(async (tx) => {
      const result = await caller.area.create(input);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create area");
      const created = result[0] as Area;
      expect(created).toBeDefined();
      expect(created).toMatchObject({
        ...input,
        userId: mockSession.user.id,
      });
    });
  });

  it("should list areas", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test areas
      const input1: ProcedureInput<"area", "create"> = {
        name: "Test Area 1",
        description: "Test Description 1",
        goalId,
        status: "active" as const,
      };
      const input2: ProcedureInput<"area", "create"> = {
        name: "Test Area 2",
        description: "Test Description 2",
        goalId,
        status: "active" as const,
      };

      // Create both areas
      const [area1Result, area2Result] = await Promise.all([
        caller.area.create(input1),
        caller.area.create(input2),
      ]);

      expect(area1Result).toHaveLength(1);
      expect(area2Result).toHaveLength(1);

      // List all areas for the goal
      const result = await caller.area.list({ goalId });

      expect(result).toBeDefined();
      const filteredResults = result.filter(
        (a) => a.name === input1.name || a.name === input2.name,
      );
      expect(filteredResults).toHaveLength(2);
      expect(result.find((a) => a.name === input2.name)).toBeDefined();
      expect(result.find((a) => a.name === input1.name)).toBeDefined();
    });
  });

  it("should update an area", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test area
      const createInput: ProcedureInput<"area", "create"> = {
        name: "Test Area",
        description: "Test Description",
        goalId,
        status: "active" as const,
      };

      const result = await caller.area.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create area");
      const created = result[0] as Area;

      // Verify area exists
      const existing = await caller.area.byId(created.id);
      expect(existing).toBeDefined();
      expect(existing.id).toBe(created.id);

      // Update the area
      const updateInput: ProcedureInput<"area", "update"> = {
        id: created.id,
        name: "Updated Area",
        description: "Updated Description",
        status: "evergreen" as const,
      };

      const updated = await caller.area.update(updateInput);
      const updatedFirstElement = updated[0];
      expect(updatedFirstElement).toEqual(
        expect.objectContaining({
          name: updateInput.name,
          description: updateInput.description,
          status: updateInput.status,
        }),
      );
    });
  });

  it("should delete an area", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create test area
      const createInput: ProcedureInput<"area", "create"> = {
        name: "Test Area",
        description: "Test Description",
        goalId,
        status: "active" as const,
      };

      const result = await caller.area.create(createInput);
      expect(result).toHaveLength(1);
      if (!result[0]) throw new Error("Failed to create area");
      const created = result[0] as Area;

      // Delete the area
      await caller.area.delete(created.id);

      // Verify deletion
      const deleted = await tx
        .select()
        .from(areas)
        .where(eq(areas.id, created.id));
      expect(deleted).toHaveLength(0);
    });
  });

  it("should not allow unauthorized access", async () => {
    const caller = await createCaller(null);

    await db.transaction(async (tx) => {
      const input: ProcedureInput<"area", "create"> = {
        name: "Test Area",
        description: "Test Description",
        goalId,
        status: "active" as const,
      };

      await expect(caller.area.create(input)).rejects.toThrow("UNAUTHORIZED");
    });
  });

  it("should not allow creating area under inactive goal", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Archive the goal
      await caller.goal.update({
        id: goalId,
        status: "archived",
      });

      const input: ProcedureInput<"area", "create"> = {
        name: "Test Area",
        description: "Test Description",
        goalId,
        status: "active" as const,
      };

      await expect(caller.area.create(input)).rejects.toThrow(
        "Cannot create area under inactive goal",
      );
    });
  });

  it("should not allow archiving area with active projects", async () => {
    const caller = await createCaller(mockSession);

    await db.transaction(async (tx) => {
      // Create area
      const areaResult = await caller.area.create({
        name: "Test Area",
        description: "Test Description",
        goalId,
        status: "active" as const,
      });
      if (!areaResult[0]) throw new Error("Failed to create area");
      const area = areaResult[0] as Area;

      // Create active project
      await caller.project.create({
        name: "Test Project",
        description: "Test Description",
        areaId: area.id,
        status: "active" as const,
      });

      // Try to archive area
      await expect(
        caller.area.update({
          id: area.id,
          status: "archived",
        }),
      ).rejects.toThrow("Cannot archive area with active projects");
    });
  });
});
