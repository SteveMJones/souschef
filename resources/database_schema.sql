PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "tags" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT,
	`description`	TEXT
);
CREATE TABLE `utensils` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT,
	`description`	TEXT
);
CREATE TABLE "recipes_ingredients" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`recipe_id`	INTEGER,
	`ingredient_id`	INTEGER,
	`amount`	NUMERIC,
	`unit`	TEXT,
	FOREIGN KEY(`recipe_id`) REFERENCES `recipes`(`id`),
	FOREIGN KEY(`ingredient_id`) REFERENCES ingredients(id)
);
CREATE TABLE `assets` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`type`	TEXT,
	`url`	TEXT,
	`size`	NUMERIC,
	`size_unit`	TEXT,
	`path`	TEXT,
	`filename`	TEXT
);
CREATE TABLE "ingredients" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT,
	`description`	TEXT,
	`contains`	TEXT,
	`image_asset_id`	INTEGER,
	FOREIGN KEY(`image_asset_id`) REFERENCES assets(id)
);
CREATE TABLE "instructions" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`recipe_id`	INTEGER,
	`step`	INTEGER,
	`description`	TEXT,
	`image_asset_id`	INTEGER,
	FOREIGN KEY(`recipe_id`) REFERENCES recipes(id),
	FOREIGN KEY(`image_asset_id`) REFERENCES `assets`(`id`)
);
CREATE TABLE "nutrition" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`recipe_id`	TEXT,
	`description`	TEXT,
	`amount`	NUMERIC,
	`unit`	TEXT,
	FOREIGN KEY(`recipe_id`) REFERENCES recipes(id)
);
CREATE TABLE "recipes" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`uid`	TEXT NOT NULL UNIQUE,
	`country`	TEXT,
	`name`	TEXT,
	`headline`	TEXT,
	`difficulty`	NUMERIC,
	`favorites`	INTEGER,
	`rating`	NUMERIC,
	`slug`	TEXT,
	`description`	TEXT,
	`url`	TEXT,
	`published`	TEXT,
	`downloaded`	INTEGER,
	`downloaded_date`	TEXT,
	`image_asset_id`	INTEGER,
	`thumbnail_asset_id`	INTEGER,
	`pdf_asset_id`	INTEGER,
	FOREIGN KEY(`image_asset_id`) REFERENCES `assets`(`id`),
	FOREIGN KEY(`thumbnail_asset_id`) REFERENCES `assets`(`id`),
	FOREIGN KEY(`pdf_asset_id`) REFERENCES assets(id)
);
CREATE TABLE "recipes_tags" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`recipe_id`	INTEGER,
	`tag_id`	INTEGER,
	FOREIGN KEY(`recipe_id`) REFERENCES `recipes`(`id`),
	FOREIGN KEY(`tag_id`) REFERENCES tags(id)
);
CREATE TABLE `recipes_utensils` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`recipe_id`	INTEGER,
	`utensil_id`	INTEGER,
	FOREIGN KEY(`recipe_id`) REFERENCES recipes(id),
	FOREIGN KEY(`utensil_id`) REFERENCES utensils(id)
);
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('tags',0);
INSERT INTO "sqlite_sequence" VALUES('recipes_ingredients',0);
INSERT INTO "sqlite_sequence" VALUES('ingredients',0);
INSERT INTO "sqlite_sequence" VALUES('instructions',0);
INSERT INTO "sqlite_sequence" VALUES('nutrition',0);
INSERT INTO "sqlite_sequence" VALUES('recipes',0);
INSERT INTO "sqlite_sequence" VALUES('recipes_tags',0);
COMMIT;
