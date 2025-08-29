CREATE TYPE "public"."account_tax_status" AS ENUM('non_retirement', 'pre_tax_retirement', 'after_tax_retirement');--> statement-breakpoint
CREATE TYPE "public"."event_series_type" AS ENUM('income', 'expense', 'invest', 'rebalance');--> statement-breakpoint
CREATE TYPE "public"."investment_taxability" AS ENUM('taxable', 'tax_exempt');--> statement-breakpoint
CREATE TYPE "public"."scenario_status" AS ENUM('draft', 'active', 'archived');--> statement-breakpoint
CREATE TYPE "public"."scenario_type" AS ENUM('individual', 'married_couple');--> statement-breakpoint
CREATE TYPE "public"."share_permission" AS ENUM('ro', 'rw');--> statement-breakpoint
CREATE TYPE "public"."start_timing_type" AS ENUM('same_year', 'year_after', 'distribution');--> statement-breakpoint
CREATE TYPE "public"."state" AS ENUM('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY');--> statement-breakpoint
CREATE TYPE "public"."strategy_type" AS ENUM('spending', 'expense_withdrawal', 'rmd', 'roth_conversion');--> statement-breakpoint
CREATE TABLE "event_series" (
	"id" serial PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	"description" text NOT NULL,
	"type" "event_series_type" NOT NULL,
	"start_year" jsonb NOT NULL,
	"duration" jsonb NOT NULL,
	"reference_event_series_id" integer NOT NULL,
	"start_timing_type" "start_timing_type" NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"order_index" integer NOT NULL,
	"initial_amount" numeric NOT NULL,
	"annual_change" jsonb NOT NULL,
	"inflation_adjusted" boolean DEFAULT false NOT NULL,
	"user_percentage" numeric NOT NULL,
	"is_social_security" boolean DEFAULT false NOT NULL,
	"is_discretionary" boolean DEFAULT false NOT NULL,
	"asset_allocation" jsonb NOT NULL,
	"is_glide_path" boolean DEFAULT false NOT NULL,
	"initial_allocation" jsonb,
	"final_allocation" jsonb,
	"maximum_cash" numeric NOT NULL,
	"target_tax_status" "account_tax_status" NOT NULL
);
--> statement-breakpoint
CREATE TABLE "investment_type" (
	"id" serial PRIMARY KEY NOT NULL,
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
	"id" uuid PRIMARY KEY NOT NULL,
	"user_id" varchar NOT NULL,
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
	"id" serial PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"shared_with_user_id" varchar NOT NULL,
	"permission" "share_permission" NOT NULL
);
--> statement-breakpoint
CREATE TABLE "strategy" (
	"id" serial PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"type" "strategy_type" NOT NULL,
	"name" varchar(255) NOT NULL,
	"description" text NOT NULL,
	"is_active" boolean DEFAULT true NOT NULL,
	"ordering" jsonb
);
--> statement-breakpoint
ALTER TABLE "event_series" ADD CONSTRAINT "event_series_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "event_series" ADD CONSTRAINT "event_series_reference_event_series_id_event_series_id_fk" FOREIGN KEY ("reference_event_series_id") REFERENCES "public"."event_series"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "investment_type" ADD CONSTRAINT "investment_type_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "scenario_sharing" ADD CONSTRAINT "scenario_sharing_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "strategy" ADD CONSTRAINT "strategy_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;