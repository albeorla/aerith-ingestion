DROP INDEX IF EXISTS "goal_unique_name_per_user_idx";--> statement-breakpoint
DROP INDEX IF EXISTS "project_unique_name_per_user_idx";--> statement-breakpoint
DROP INDEX IF EXISTS "task_unique_name_per_user_idx";--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "goal_unique_name_per_vision_idx" ON "app_goal" USING btree ("vision_id","name");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "project_unique_name_per_area_idx" ON "app_project" USING btree ("area_id","name");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "task_unique_name_per_project_idx" ON "app_task" USING btree ("project_id","name");