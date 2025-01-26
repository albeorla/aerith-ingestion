import { TRPCError } from "@trpc/server";
import { beforeEach, describe, expect, it } from "vitest";
import type { visions } from "../../../db/schema";
import {
  createCaller,
  mockSession,
  type ProcedureInput,
} from "../../__tests__/test-utils";

type Vision = typeof visions.$inferSelect;

describe("Vision Router", () => {
  // Setup: Create a test purpose for vision tests
  let testPurposeId: string;

  beforeEach(async () => {
    const caller = await createCaller(mockSession);

    // Create test purpose
    const purposeResult = await caller.purpose.create({
      name: `Test Purpose ${Date.now()}`,
      description: "Test Description",
      status: "active",
    });

    if (!purposeResult?.[0]?.id) {
      throw new Error("Test purpose setup failed");
    }
    testPurposeId = purposeResult[0].id;

    // Verify purpose exists
    const existing = await caller.purpose.byId({ id: testPurposeId });
    expect(existing).toBeDefined();
    expect(existing.id).toBe(testPurposeId);
  });

  describe("create", () => {
    it("should create a vision with valid input", async () => {
      const caller = await createCaller(mockSession);

      const input: ProcedureInput<"vision", "create"> = {
        name: "Test Vision",
        description: "Test Description",
        purposeId: testPurposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 86400000 * 365), // 1 year from now
      };

      const result = await caller.vision.create(input);

      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(1);

      const vision = (result as unknown as Vision[])[0];
      expect(vision).toBeDefined();
      if (!vision) throw new Error("Vision not created");

      expect(vision.name).toBe(input.name);
      expect(vision.description).toBe(input.description);
      expect(vision.status).toBe(input.status);
      expect(vision.purposeId).toBe(input.purposeId);
      expect(vision.userId).toBe(mockSession.user.id);
      if (vision.targetDate && input.targetDate) {
        expect(new Date(vision.targetDate).getTime()).toBe(
          input.targetDate.getTime(),
        );
      } else {
        throw new Error("Target date not set");
      }
    });

    it("should fail with invalid purpose ID", async () => {
      const caller = await createCaller(mockSession);

      const input: ProcedureInput<"vision", "create"> = {
        name: "Test Vision",
        description: "Test Description",
        purposeId: "invalid-uuid",
        status: "active" as const,
        targetDate: new Date(Date.now() + 86400000 * 365),
      };

      await expect(caller.vision.create(input)).rejects.toThrow(TRPCError);
    });

    it("should fail with duplicate name under same purpose", async () => {
      const caller = await createCaller(mockSession);

      // Create a unique purpose for this test
      const purpose = await caller.purpose.create({
        name: `Test Purpose ${Date.now()}`,
        description: "Test Description",
        status: "active" as const,
      });

      expect(purpose).toHaveLength(1);
      const purposeId = purpose[0]!.id;

      // Verify purpose exists
      const existing = await caller.purpose.byId({ id: purposeId });
      expect(existing).toBeDefined();
      expect(existing.id).toBe(purposeId);

      const input: ProcedureInput<"vision", "create"> = {
        name: "Test Vision",
        description: "Test Description",
        purposeId: purposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 86400000 * 365),
      };

      // Create first vision
      await caller.vision.create(input);

      // Try to create second vision with same name
      await expect(caller.vision.create(input)).rejects.toThrow(TRPCError);
    });

    it("should fail with past target date", async () => {
      const caller = await createCaller(mockSession);

      const input: ProcedureInput<"vision", "create"> = {
        name: "Test Vision",
        description: "Test Description",
        purposeId: testPurposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() - 86400000), // Yesterday
      };

      await expect(caller.vision.create(input)).rejects.toThrow();
    });
  });

  describe("list", () => {
    beforeEach(async () => {
      const caller = await createCaller(mockSession);

      // Create some test visions
      await caller.vision.create({
        name: "Vision 1",
        description: "Description 1",
        purposeId: testPurposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 86400000 * 365),
      });

      await caller.vision.create({
        name: "Vision 2",
        description: "Description 2",
        purposeId: testPurposeId,
        status: "achieved" as const,
        targetDate: new Date(Date.now() + 86400000 * 730), // 2 years
      });
    });

    it("should list all visions for a purpose", async () => {
      const caller = await createCaller(mockSession);

      const results = await caller.vision.list({
        purposeId: testPurposeId,
      });

      expect(results).toHaveLength(2);

      const visions = results as unknown as Vision[];
      expect(visions.length).toBe(2);
      const [first, second] = visions;
      expect(first).toBeDefined();
      expect(second).toBeDefined();
      if (!first || !second) throw new Error("Missing test visions");

      // Results are ordered by createdAt desc
      expect(first.name).toBe("Vision 2");
      expect(second.name).toBe("Vision 1");
    });

    it("should filter by status", async () => {
      const caller = await createCaller(mockSession);

      const results = await caller.vision.list({
        purposeId: testPurposeId,
        status: "active",
      });

      expect(results).toHaveLength(1);

      const visions = results as unknown as Vision[];
      expect(visions.length).toBe(1);
      const [vision] = visions;
      expect(vision).toBeDefined();
      if (!vision) throw new Error("Missing active vision");

      expect(vision.name).toBe("Vision 1");
      expect(vision.status).toBe("active");
    });
  });

  describe("update", () => {
    let visionId: string;

    beforeEach(async () => {
      const caller = await createCaller(mockSession);

      // Create a test vision
      const result = await caller.vision.create({
        name: "Test Vision",
        description: "Test Description",
        purposeId: testPurposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 86400000 * 365),
      });

      const vision = (result as unknown as Vision[])[0];
      if (!vision?.id) throw new Error("Failed to create test vision");
      visionId = vision.id;
    });

    it("should update vision fields", async () => {
      const caller = await createCaller(mockSession);

      const input: ProcedureInput<"vision", "update"> = {
        id: visionId,
        name: "Updated Vision",
        description: "Updated Description",
      };

      const result = await caller.vision.update(input);
      expect(result).toBeDefined();

      // Verify update
      const updated = await caller.vision.byId(visionId);
      expect(updated.name).toBe(input.name);
      expect(updated.description).toBe(input.description);
    });

    it("should validate status transitions", async () => {
      const caller = await createCaller(mockSession);

      // Valid transition: active -> achieved
      await caller.vision.update({
        id: visionId,
        status: "achieved" as const,
      });

      // Invalid transition: achieved -> active
      await expect(
        caller.vision.update({
          id: visionId,
          status: "active" as const,
        }),
      ).rejects.toThrow(TRPCError);
    });
  });

  describe("delete", () => {
    let visionId: string;

    beforeEach(async () => {
      const caller = await createCaller(mockSession);

      // Create a test vision
      const result = await caller.vision.create({
        name: "Test Vision",
        description: "Test Description",
        purposeId: testPurposeId,
        status: "active" as const,
        targetDate: new Date(Date.now() + 86400000 * 365),
      });

      const vision = (result as unknown as Vision[])[0];
      if (!vision?.id) throw new Error("Failed to create test vision");
      visionId = vision.id;
    });

    it("should delete vision", async () => {
      const caller = await createCaller(mockSession);

      await caller.vision.delete(visionId);

      // Verify deletion
      await expect(caller.vision.byId(visionId)).rejects.toThrow(TRPCError);
    });

    it("should fail with invalid ID", async () => {
      const caller = await createCaller(mockSession);

      await expect(caller.vision.delete("invalid-uuid")).rejects.toThrow(
        TRPCError,
      );
    });
  });
});
