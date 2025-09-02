ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "start_year" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "duration" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "reference_event_series_id" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "start_timing_type" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "initial_amount" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "annual_change" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "inflation_adjusted" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "user_percentage" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "is_social_security" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "is_discretionary" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "asset_allocation" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "is_glide_path" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "maximum_cash" DROP NOT NULL;--> statement-breakpoint
ALTER TABLE "shallowfind"."event_series" ALTER COLUMN "target_tax_status" DROP NOT NULL;