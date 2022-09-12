BEGIN;
--
-- Raw SQL operation
--
CREATE SCHEMA content;
--
-- Create model Filmwork
--
CREATE TABLE "content"."film_work" (
  "id" uuid NOT NULL PRIMARY KEY,
  "created_at" timestamp with time zone NOT NULL,
  "updated_at" timestamp with time zone NOT NULL,
  "title" varchar(255) NOT NULL,
  "description" text NULL,
  "creation_date" date NULL,
  "certificate" text NULL,
  "file_path" varchar(100) NULL,
  "rating" double precision NULL,
  "type" varchar(20) NOT NULL,
  "min_access_level" smallint NOT NULL
);
--
-- Create model Genre
--
CREATE TABLE "content"."genre" (
  "id" uuid NOT NULL PRIMARY KEY,
  "created_at" timestamp with time zone NOT NULL,
  "updated_at" timestamp with time zone NOT NULL,
  "name" varchar(255) NOT NULL,
  "description" text NULL
);
--
-- Create model Person
--
CREATE TABLE "content"."person" (
  "id" uuid NOT NULL PRIMARY KEY,
  "created_at" timestamp with time zone NOT NULL,
  "updated_at" timestamp with time zone NOT NULL,
  "full_name" varchar(255) NOT NULL,
  "birth_date" date NULL
);
--
-- Create model FilmworkPerson
--
CREATE TABLE "content"."person_film_work" (
  "id" uuid NOT NULL PRIMARY KEY,
  "role" varchar(20) NOT NULL,
  "created_at" timestamp with time zone NOT NULL,
  "film_work_id" uuid NOT NULL,
  "person_id" uuid NOT NULL
);
--
-- Create model FilmworkGenre
--
CREATE TABLE "content"."genre_film_work" (
  "id" uuid NOT NULL PRIMARY KEY,
  "created_at" timestamp with time zone NOT NULL,
  "film_work_id" uuid NOT NULL,
  "genre_id" uuid NOT NULL
);
--
-- Add field genres to filmwork
--
--
-- Add field persons to filmwork
--
--
-- Create index film_work_person_role on field(s) filmwork, person, role of model filmworkperson
--
CREATE UNIQUE INDEX "film_work_person_role" ON "content"."person_film_work" ("film_work_id", "person_id", "role");
--
-- Create index film_work_genre on field(s) filmwork, genre of model filmworkgenre
--
CREATE UNIQUE INDEX "film_work_genre" ON "content"."genre_film_work" ("film_work_id", "genre_id");

ALTER TABLE
  "content"."person_film_work"
ADD
  CONSTRAINT "person_film_work_film_work_id_1724c536_fk_film_work_id" FOREIGN KEY ("film_work_id") REFERENCES "content"."film_work" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE
  "content"."person_film_work"
ADD
  CONSTRAINT "person_film_work_person_id_196d24de_fk_person_id" FOREIGN KEY ("person_id") REFERENCES "content"."person" ("id") DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX "person_film_work_film_work_id_1724c536" ON "content"."person_film_work" ("film_work_id");
CREATE INDEX "person_film_work_person_id_196d24de" ON "content"."person_film_work" ("person_id");

ALTER TABLE
  "content"."genre_film_work"
ADD
  CONSTRAINT "genre_film_work_film_work_id_65abe300_fk_film_work_id" FOREIGN KEY ("film_work_id") REFERENCES "content"."film_work" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE
  "content"."genre_film_work"
ADD
  CONSTRAINT "genre_film_work_genre_id_88fbcf0d_fk_genre_id" FOREIGN KEY ("genre_id") REFERENCES "content"."genre" ("id") DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX "genre_film_work_film_work_id_65abe300" ON "content"."genre_film_work" ("film_work_id");
CREATE INDEX "genre_film_work_genre_id_88fbcf0d" ON "content"."genre_film_work" ("genre_id");

COMMIT;
