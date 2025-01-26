import {
  areas,
  db,
  goals,
  projects,
  purposes,
  tasks,
  users,
  visions,
} from "@/server/db/schema";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { env } from "../../env";

async function main() {
  console.log("🌱 Seeding database...");

  const pool = new Pool({ connectionString: env.DATABASE_URL });
  const db = drizzle(pool);

  // Create test user
  const [user] = await db
    .insert(users)
    .values({
      id: "seed-user-id",
      name: "Test User",
      email: "test@example.com",
      emailVerified: new Date(),
    })
    .returning();

  console.log("Created test user:", user!.id);

  // Create purpose
  const [purpose] = await db
    .insert(purposes)
    .values({
      userId: user!.id,
      name: "Live a balanced and fulfilling life",
      description:
        "Achieve harmony across personal, professional, and spiritual aspects of life",
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
      description:
        "Become a recognized expert in software development while maintaining work-life balance",
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
      description:
        "Develop expertise in full-stack development and system design",
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
      description: "Core skills and projects in full-stack development",
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
      description:
        "Create showcase projects demonstrating full-stack capabilities",
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
      description:
        "Configure local development environment with necessary tools",
      status: "completed" as const,
      dueDate: new Date("2024-01-15"),
    },
    {
      userId: user!.id,
      projectId: project!.id,
      name: "Learn Next.js and Drizzle",
      description: "Complete tutorials and build sample applications",
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

  await pool.end();
  console.log("✅ Seeding complete!");
  process.exit(0);
}

if (require.main === module) {
  main()
    .catch((e) => {
      console.error("Error seeding database:", e);
      process.exit(1);
    });
}
