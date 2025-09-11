ALTER TABLE "event_series" DROP CONSTRAINT "event_series_scenario_id_scenario_id_fk";
--> statement-breakpoint
ALTER TABLE "investment" DROP CONSTRAINT "investment_scenario_id_scenario_id_fk";
--> statement-breakpoint
ALTER TABLE "investment_type" DROP CONSTRAINT "investment_type_scenario_id_scenario_id_fk";
--> statement-breakpoint
ALTER TABLE "scenario_sharing" DROP CONSTRAINT "scenario_sharing_scenario_id_scenario_id_fk";
--> statement-breakpoint
ALTER TABLE "strategy" DROP CONSTRAINT "strategy_scenario_id_scenario_id_fk";
--> statement-breakpoint
ALTER TABLE "event_series" ADD CONSTRAINT "event_series_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "investment" ADD CONSTRAINT "investment_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "investment_type" ADD CONSTRAINT "investment_type_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "scenario_sharing" ADD CONSTRAINT "scenario_sharing_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "strategy" ADD CONSTRAINT "strategy_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "public"."event_series" ALTER COLUMN "start_timing_type" SET DATA TYPE text;--> statement-breakpoint
DROP TYPE "public"."start_timing_type";--> statement-breakpoint
CREATE TYPE "public"."start_timing_type" AS ENUM('same_year', 'year_after', 'distribution');--> statement-breakpoint
ALTER TABLE "public"."event_series" ALTER COLUMN "start_timing_type" SET DATA TYPE "public"."start_timing_type" USING "start_timing_type"::"public"."start_timing_type";