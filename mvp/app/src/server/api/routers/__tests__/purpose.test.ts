import { purposes } from "@/server/db/schema/purposes";
import { eq } from "drizzle-orm";
import { beforeEach, describe, expect, it } from "vitest";
import {
  type ProcedureInput,
  createCaller,
  mockSession,
  testDb,
} from "../../__tests__/test-utils";

describe("purpose router", () => {
  beforeEach(async () => {
    const caller = await createCaller(mockSession);

    // Create test purpose with unique name
    const purposeName = `Test Purpose ${Date.now()}`;
    await caller.purpose.create({
      name: purposeName,
      description: "Test Description",
      status: "active",
    });
  });

  it("should create a purpose", async () => {
    const caller = await createCaller(mockSession);

    const input: ProcedureInput<"purpose", "create"> = {
      name: "Test Purpose",
      description: "Test Description",
      status: "active" as const,
    };

    const result = await caller.purpose.create(input);
    expect(result).toHaveLength(1);
    const created = result[0];
    expect(created).toBeDefined();
    expect(created).toMatchObject({
      ...input,
      userId: mockSession.user.id,
    });
  });

  it("should list purposes", async () => {
    const caller = await createCaller(mockSession);

    // Create test purposes
    const input1: ProcedureInput<"purpose", "create"> = {
      name: "Test Purpose 1",
      description: "Test Description 1",
      status: "active" as const,
    };
    const input2: ProcedureInput<"purpose", "create"> = {
      name: "Test Purpose 2",
      description: "Test Description 2",
      status: "active" as const,
    };

    // Create both purposes and verify they were created
    const [purpose1, purpose2] = await Promise.all([
      caller.purpose.create(input1),
      caller.purpose.create(input2),
    ]);

    expect(purpose1).toHaveLength(1);
    expect(purpose2).toHaveLength(1);

    // List all purposes
    const result = await caller.purpose.list();

    expect(result).toBeDefined();
    const filteredResults = result.filter(
      (p) => p.name === input1.name || p.name === input2.name,
    );
    expect(filteredResults).toHaveLength(2);
    expect(result.find((p) => p.name === input2.name)).toBeDefined();
    expect(result.find((p) => p.name === input1.name)).toBeDefined();
  });

  it("should update a purpose", async () => {
    const caller = await createCaller(mockSession);

    // Create test purpose
    const createInput: ProcedureInput<"purpose", "create"> = {
      name: "Test Purpose",
      description: "Test Description",
      status: "active" as const,
    };

    const result = await caller.purpose.create(createInput);
    expect(result).toHaveLength(1);
    const created = result[0];
    if (!created) throw new Error("Failed to create purpose");

    // Verify purpose exists
    const existing = await caller.purpose.byId({ id: created.id });
    expect(existing).toBeDefined();
    expect(existing.id).toBe(created.id);

    // Update the purpose
    const updateInput: ProcedureInput<"purpose", "update"> = {
      id: created.id,
      name: "Updated Purpose",
      description: "Updated Description",
      status: "archived" as const,
    };

    const updated = await caller.purpose.update(updateInput);

    expect(updated).toBeDefined();
    expect(updated).toEqual(
      expect.objectContaining({
        name: updateInput.name,
        description: updateInput.description,
        status: updateInput.status,
      }),
    );
  });

  it("should delete a purpose", async () => {
    const caller = await createCaller(mockSession);

    // Create test purpose
    const createInput: ProcedureInput<"purpose", "create"> = {
      name: "Test Purpose",
      description: "Test Description",
      status: "active" as const,
    };

    const result = await caller.purpose.create(createInput);
    expect(result).toHaveLength(1);
    const created = result[0];
    if (!created) throw new Error("Failed to create purpose");

    // Delete the purpose
    await caller.purpose.delete(created.id);

    // Verify deletion
    const deleted = await testDb
      .select()
      .from(purposes)
      .where(eq(purposes.id, created.id));
    expect(deleted).toHaveLength(0);
  });

  it("should not allow unauthorized access", async () => {
    const caller = await createCaller(null);

    const input: ProcedureInput<"purpose", "create"> = {
      name: "Test Purpose",
      description: "Test Description",
      status: "active" as const,
    };

    await expect(caller.purpose.create(input)).rejects.toThrow("UNAUTHORIZED");
  });
});
