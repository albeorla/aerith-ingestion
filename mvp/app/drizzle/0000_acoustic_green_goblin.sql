CREATE TABLE IF NOT EXISTS "app_account" (
	"user_id" text NOT NULL,
	"type" text NOT NULL,
	"provider" text NOT NULL,
	"provider_account_id" text NOT NULL,
	"refresh_token" text,
	"access_token" text,
	"expires_at" integer,
	"token_type" text,
	"scope" text,
	"id_token" text,
	"session_state" text,
	CONSTRAINT "app_account_provider_provider_account_id_pk" PRIMARY KEY("provider","provider_account_id")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_area" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" varchar(255) NOT NULL,
	"goal_id" uuid NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_goal" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" varchar(255) NOT NULL,
	"vision_id" uuid NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"target_date" timestamp with time zone,
	"progress_percentage" numeric,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_project" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" varchar(255) NOT NULL,
	"area_id" uuid NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"target_date" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"due_date" timestamp with time zone,
	"is_active" boolean DEFAULT true
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_purpose" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" text NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_session" (
	"session_token" varchar(255) PRIMARY KEY NOT NULL,
	"user_id" varchar(255) NOT NULL,
	"expires" timestamp with time zone NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_task" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" varchar(255) NOT NULL,
	"project_id" uuid NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"due_date" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_user" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text,
	"email" text NOT NULL,
	"email_verified" timestamp,
	"image" text,
	CONSTRAINT "app_user_email_unique" UNIQUE("email")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_verification_token" (
	"identifier" varchar(255) NOT NULL,
	"token" varchar(255) NOT NULL,
	"expires" timestamp with time zone NOT NULL,
	CONSTRAINT "app_verification_token_identifier_token_pk" PRIMARY KEY("identifier","token")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "app_vision" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" varchar(255) NOT NULL,
	"purpose_id" uuid NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"target_date" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_account" ADD CONSTRAINT "app_account_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_area" ADD CONSTRAINT "app_area_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_area" ADD CONSTRAINT "app_area_goal_id_app_goal_id_fk" FOREIGN KEY ("goal_id") REFERENCES "public"."app_goal"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_goal" ADD CONSTRAINT "app_goal_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_goal" ADD CONSTRAINT "app_goal_vision_id_app_vision_id_fk" FOREIGN KEY ("vision_id") REFERENCES "public"."app_vision"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_project" ADD CONSTRAINT "app_project_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_project" ADD CONSTRAINT "app_project_area_id_app_area_id_fk" FOREIGN KEY ("area_id") REFERENCES "public"."app_area"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_purpose" ADD CONSTRAINT "app_purpose_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_session" ADD CONSTRAINT "app_session_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_task" ADD CONSTRAINT "app_task_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_task" ADD CONSTRAINT "app_task_project_id_app_project_id_fk" FOREIGN KEY ("project_id") REFERENCES "public"."app_project"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_vision" ADD CONSTRAINT "app_vision_user_id_app_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."app_user"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "app_vision" ADD CONSTRAINT "app_vision_purpose_id_app_purpose_id_fk" FOREIGN KEY ("purpose_id") REFERENCES "public"."app_purpose"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "area_user_id_idx" ON "app_area" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "area_goal_id_idx" ON "app_area" USING btree ("goal_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "area_status_idx" ON "app_area" USING btree ("status");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "area_unique_name_per_user_idx" ON "app_area" USING btree ("user_id","name");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "goal_user_id_idx" ON "app_goal" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "goal_vision_id_idx" ON "app_goal" USING btree ("vision_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "goal_status_idx" ON "app_goal" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "goal_target_date_idx" ON "app_goal" USING btree ("target_date");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "goal_unique_name_per_user_idx" ON "app_goal" USING btree ("user_id","name");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "project_user_id_idx" ON "app_project" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "project_area_id_idx" ON "app_project" USING btree ("area_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "project_status_idx" ON "app_project" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "project_target_date_idx" ON "app_project" USING btree ("target_date");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "project_unique_name_per_user_idx" ON "app_project" USING btree ("user_id","name");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "purpose_user_id_idx" ON "app_purpose" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "purpose_status_idx" ON "app_purpose" USING btree ("status");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "purpose_unique_name_per_user_idx" ON "app_purpose" USING btree ("user_id","name");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "session_user_id_idx" ON "app_session" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "task_user_id_idx" ON "app_task" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "task_project_id_idx" ON "app_task" USING btree ("project_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "task_status_idx" ON "app_task" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "task_due_date_idx" ON "app_task" USING btree ("due_date");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "task_unique_name_per_user_idx" ON "app_task" USING btree ("user_id","name");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "vision_user_id_idx" ON "app_vision" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "vision_purpose_id_idx" ON "app_vision" USING btree ("purpose_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "vision_status_idx" ON "app_vision" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "vision_target_date_idx" ON "app_vision" USING btree ("target_date");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "vision_unique_name_per_user_idx" ON "app_vision" USING btree ("user_id","name");