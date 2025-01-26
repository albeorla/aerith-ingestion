-- Create Purposes table (50,000 ft)
CREATE TABLE IF NOT EXISTS "app_purpose" (
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "user_id" varchar(255) NOT NULL,
    "name" varchar(100) NOT NULL,
    "description" text,
    "status" varchar(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    "created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT "app_purpose_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "app_user"("id") ON DELETE CASCADE,
    CONSTRAINT "app_purpose_name_length" CHECK (length(name) >= 3),
    CONSTRAINT "app_purpose_description_length" CHECK (description IS NULL OR length(description) <= 500),
    CONSTRAINT "app_purpose_unique_name_per_user" UNIQUE ("user_id", "name")
);

-- Create Visions table (40,000 ft)
CREATE TABLE IF NOT EXISTS "app_vision" (
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "user_id" varchar(255) NOT NULL,
    "purpose_id" uuid NOT NULL,
    "name" varchar(100) NOT NULL,
    "description" text,
    "status" varchar(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'achieved', 'archived')),
    "target_date" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT "app_vision_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "app_user"("id") ON DELETE CASCADE,
    CONSTRAINT "app_vision_purpose_id_fk" FOREIGN KEY ("purpose_id") REFERENCES "app_purpose"("id") ON DELETE CASCADE,
    CONSTRAINT "app_vision_name_length" CHECK (length(name) >= 3),
    CONSTRAINT "app_vision_description_length" CHECK (description IS NULL OR length(description) <= 500),
    CONSTRAINT "app_vision_unique_name_per_user" UNIQUE ("user_id", "name")
);

-- Create indexes
CREATE INDEX IF NOT EXISTS "purpose_user_id_idx" ON "app_purpose" ("user_id");
CREATE INDEX IF NOT EXISTS "purpose_status_idx" ON "app_purpose" ("status");
CREATE INDEX IF NOT EXISTS "vision_user_id_idx" ON "app_vision" ("user_id");
CREATE INDEX IF NOT EXISTS "vision_purpose_id_idx" ON "app_vision" ("purpose_id");
CREATE INDEX IF NOT EXISTS "vision_status_idx" ON "app_vision" ("status");
CREATE INDEX IF NOT EXISTS "vision_target_date_idx" ON "app_vision" ("target_date");

-- Add updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_app_purpose_updated_at
    BEFORE UPDATE ON app_purpose
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_app_vision_updated_at
    BEFORE UPDATE ON app_vision
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 