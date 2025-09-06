ALTER TYPE "public"."start_timing_type" ADD VALUE 'event_series' BEFORE 'distribution';--> statement-breakpoint
CREATE TABLE "investment" (
	"id" uuid PRIMARY KEY NOT NULL,
	"scenario_id" uuid NOT NULL,
	"investment_type_id" uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	"current_value" numeric DEFAULT '0' NOT NULL,
	"account_tax_status" "account_tax_status" NOT NULL,
	"order_index" integer NOT NULL
);
--> statement-breakpoint
ALTER TABLE "investment" ADD CONSTRAINT "investment_scenario_id_scenario_id_fk" FOREIGN KEY ("scenario_id") REFERENCES "public"."scenario"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "investment" ADD CONSTRAINT "investment_investment_type_id_investment_type_id_fk" FOREIGN KEY ("investment_type_id") REFERENCES "public"."investment_type"("id") ON DELETE no action ON UPDATE no action;