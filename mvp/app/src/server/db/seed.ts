import { db } from "./index";
import { users, purposes, visions, goals, areas, projects, tasks } from "./schema";
import { sql } from "drizzle-orm";

async function main() {
  console.log("🌱 Seeding database...");

  // Create test user
  const [user] = await db
    .insert(users)
    .values({
      name: "Test User",
      email: "test@example.com",
    })
    .returning();

  console.log("Created test user:", user!.id);

  // Create purpose
  const [purpose] = await db
    .insert(purposes)
    .values({
      userId: user!.id,
      name: "Live a balanced and fulfilling life",
      description: "Create a life that balances personal growth, relationships, and impact",
      status: "active",
    })
    .returning();

  console.log("Created purpose:", purpose!.id);

  // Create vision
  const [vision] = await db
    .insert(visions)
    .values({
      userId: user!.id,
      purposeId: purpose!.id,
      name: "5-Year Vision 2029",
      description: "By 2029, establish a sustainable work-life balance while making meaningful contributions",
      status: "active",
      targetDate: new Date("2029-12-31"),
    })
    .returning();

  console.log("Created vision:", vision!.id);

  // Create goal
  const [goal] = await db
    .insert(goals)
    .values({
      userId: user!.id,
      visionId: vision!.id,
      name: "Master Software Development",
      description: "Become proficient in modern software development practices and technologies",
      status: "active",
      targetDate: new Date("2024-12-31"),
    })
    .returning();

  console.log("Created goal:", goal!.id);

  // Create area
  const [area] = await db
    .insert(areas)
    .values({
      userId: user!.id,
      goalId: goal!.id,
      name: "Full-Stack Development",
      description: "Focus on both frontend and backend development skills",
      status: "active",
    })
    .returning();

  console.log("Created area:", area!.id);

  // Create project
  const [project] = await db
    .insert(projects)
    .values({
      userId: user!.id,
      areaId: area!.id,
      name: "Build Personal Project Portfolio",
      description: "Create meaningful projects to demonstrate skills",
      status: "active",
      targetDate: new Date("2024-06-30"),
    })
    .returning();

  console.log("Created project:", project!.id);

  // Create tasks
  const taskData = [
    {
      userId: user!.id,
      projectId: project!.id,
      name: "Setup Development Environment",
      description: "Configure local development environment with necessary tools",
      status: "completed" as const,
      dueDate: new Date("2024-01-15"),
    },
    {
      userId: user!.id,
      projectId: project!.id,
      name: "Learn Next.js and Drizzle",
      description: "Study and implement features using Next.js and Drizzle ORM",
      status: "active" as const,
      dueDate: new Date("2024-02-15"),
    },
    {
      userId: user!.id,
      projectId: project!.id,
      name: "Implement Authentication",
      description: "Add user authentication and authorization",
      status: "active" as const,
      dueDate: new Date("2024-02-28"),
    },
  ];

  const [task1, task2, task3] = await db
    .insert(tasks)
    .values(taskData)
    .returning();

  console.log("Created tasks:", [task1!.id, task2!.id, task3!.id]);

  console.log("✅ Seeding complete!");
  process.exit(0);
}

main().catch((e) => {
  console.error("Error seeding database:", e);
  process.exit(1);
}); 