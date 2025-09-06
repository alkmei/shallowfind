CREATE TYPE "public"."account_tax_status" AS ENUM('non_retirement', 'pre_tax_retirement', 'after_tax_retirement');--> statement-breakpoint
CREATE TYPE "public"."event_series_type" AS ENUM('income', 'expense', 'invest', 'rebalance');--> statement-breakpoint
CREATE TYPE "public"."investment_taxability" AS ENUM('taxable', 'tax_exempt');--> statement-breakpoint
CREATE TYPE "public"."scenario_status" AS ENUM('draft', 'active', 'archived');--> statement-breakpoint
CREATE TYPE "public"."scenario_type" AS ENUM('individual', 'married_couple');--> statement-breakpoint
CREATE TYPE "public"."share_permission" AS ENUM('ro', 'rw');--> statement-breakpoint
CREATE TYPE "public"."start_timing_type" AS ENUM('same_year', 'year_after', 'distribution');--> statement-breakpoint
CREATE TYPE "public"."state" AS ENUM('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY');--> statement-breakpoint
CREATE TYPE "public"."strategy_type" AS ENUM('spending', 'expense_withdrawal', 'rmd', 'roth_conversion');--> statement-breakpoint
CREATE TABLE "account" (
	"id" text PRIMARY KEY NOT NULL,
	"account_id" text NOT NULL,
	"provider_id" text NOT NULL,
	"user_id" text NOT NULL,
	"access_token" text,
	"refresh_token" text,
	"id_token" text,
	"access_token_expires_at" timestamp,
	"refresh_token_expires_at" timestamp,
	"scope" text,
	"password" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL
);
--> statement-breakpoint
CREATE TABLE "session" (
	"id" text PRIMARY KEY NOT NULL,
	"expires_at" timestamp NOT NULL,
	"token" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp NOT NULL,
	"ip_address" text,
	"user_agent" text,
	"user_id" text NOT NULL,
	CONSTRAINT "session_token_unique" UNIQUE("token")
);
--> statement-breakpoint
CREATE TABLE "user" (
	"id" text PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"email" text NOT NULL,
	"email_verified" boolean DEFAULT false NOT NULL,
	"image" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "user_email_unique" UNIQUE("email")
);
--> statement-breakpoint
CREATE TABLE "verification" (
	"id" text PRIMARY KEY NOT NULL,
	"identifier" text NOT NULL,
	"value" text NOT NULL,
	"expires_at" timestamp NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "event_series" (
	"id" uuid PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	"description" text NOT NULL,
	"type" "event_series_type" NOT NULL,
	"start_year" jsonb,
	"duration" jsonb,
	"reference_event_series_id" uuid,
	"start_timing_type" "start_timing_type",
	"is_active" boolean DEFAULT true NOT NULL,
	"order_index" integer NOT NULL,
	"initial_amount" numeric,
	"annual_change" jsonb,
	"inflation_adjusted" boolean DEFAULT false,
	"user_percentage" numeric,
	"is_social_security" boolean DEFAULT false,
	"is_discretionary" boolean DEFAULT false,
	"asset_allocation" jsonb,
	"is_glide_path" boolean DEFAULT false,
	"initial_allocation" jsonb,
	"final_allocation" jsonb,
	"maximum_cash" numeric,
	"target_tax_status" "account_tax_status"
);
--> statement-breakpoint
CREATE TABLE "investment_type" (
	"id" uuid PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	"description" text NOT NULL,
	"expected_annual_return" jsonb NOT NULL,
	"expense_ratio" numeric NOT NULL,
	"expected_annual_income" jsonb NOT NULL,
	"taxability" "investment_taxability" NOT NULL,
	"is_cash" boolean DEFAULT false NOT NULL
);
--> statement-breakpoint
CREATE TABLE "scenario" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" text NOT NULL,
	"title" varchar(255) NOT NULL,
	"description" text NOT NULL,
	"scenario_type" "scenario_type" NOT NULL,
	"scenario_status" "scenario_status" DEFAULT 'draft' NOT NULL,
	"user_birth_year" integer,
	"spouse_birth_year" integer,
	"user_life_expectancy" jsonb,
	"spouse_life_expectancy" jsonb,
	"financial_goal" numeric,
	"state_of_residence" "state" NOT NULL,
	"inflation_assumption" jsonb,
	"annual_retirement_contribution_limit" numeric,
	"roth_optimizer_enabled" boolean DEFAULT false NOT NULL,
	"roth_optimizer_start_year" integer,
	"roth_optimizer_end_year" integer,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "scenario_sharing" (
	"id" uuid PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"shared_with_user_id" text NOT NULL,
	"permission" "share_permission" NOT NULL
);
--> statement-breakpoint
CREATE TABLE "strategy" (
	"id" uuid PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"type" "strategy_type" NOT NULL,
	"name" varchar(255) NOT NULL,
	"description" text NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"ordering" jsonb
);
--> statement-breakpoint
ALTER TABLE "account" ADD CONSTRAINT "account_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "session" ADD CONSTRAINT "session_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "event_series" ADD CONSTRAINT "event_series_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "event_series" ADD CONSTRAINT "event_series_reference_event_series_id_event_series_id_fk" FOREIGN KEY ("reference_event_series_id") REFERENCES "public"."event_series"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "investment_type" ADD CONSTRAINT "investment_type_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "scenario" ADD CONSTRAINT "scenario_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "scenario_sharing" ADD CONSTRAINT "scenario_sharing_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "strategy" ADD CONSTRAINT "strategy_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;