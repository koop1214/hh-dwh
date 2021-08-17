-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


-- Справочник дат
CREATE TABLE "dim_dates" (
    -- id
    "id" int   NOT NULL,
    -- дата
    "date" date   NOT NULL,
    -- год
    "year" smallint   NOT NULL,
    -- квартал
    "quarter" smallint   NOT NULL,
    -- месяц
    "month" smallint   NOT NULL,
    -- номер недели
    "week" smallint   NOT NULL,
    -- день недели
    "week_day" smallint   NOT NULL,
    CONSTRAINT "pk_dim_dates" PRIMARY KEY (
        "id"
     )
);

INSERT INTO dim_dates
  WITH dates AS (
      SELECT dd::date AS dt
        FROM GENERATE_SERIES
                 ('2020-01-01'::timestamp
                 , '2021-12-31'::timestamp
                 , '1 day'::interval) dd
  )
SELECT TO_CHAR(dt, 'YYYYMMDD')::int  AS id,
       dt                            AS date,
       DATE_PART('year', dt)::int    AS year,
       DATE_PART('quarter', dt)::int AS quarter,
       DATE_PART('month', dt)::int   AS month,
       DATE_PART('week', dt)::int    AS week,
       DATE_PART('isodow', dt)::int  AS week_day
  FROM dates
 ORDER BY dt;


-- Справочник типов вакансий
CREATE TABLE "dim_types" (
    -- id
    "id"  SERIAL  NOT NULL,
    -- код типа вакансии
    "code" varchar(20)   NOT NULL,
    -- название
    "name" varchar(200)   NOT NULL,
    CONSTRAINT "pk_dim_types" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_dim_types_code" UNIQUE (
        "code"
    )
);

-- Справочник регионов размещения вакансии
CREATE TABLE "dim_areas" (
    -- id
    "id"  SERIAL  NOT NULL,
    -- код региона
    "code" varchar(20)   NOT NULL,
    -- название региона
    "name" varchar(200)   NOT NULL,
    CONSTRAINT "pk_dim_areas" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_dim_areas_code" UNIQUE (
        "code"
    )
);

-- Справочник графиков работы
CREATE TABLE "dim_schedules" (
    -- id
    "id"  SERIAL  NOT NULL,
    -- код
    "code" varchar(20)   NOT NULL,
    -- название
    "name" varchar(200)   NOT NULL,
    CONSTRAINT "pk_dim_schedules" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_dim_schedules_code" UNIQUE (
        "code"
    )
);

-- Справочник специальностей
CREATE TABLE "dim_specialities" (
    -- id
    "id"  SERIAL  NOT NULL,
    -- название
    "name" varchar(200)   NOT NULL,
    -- синонимы
    "aliases" text   NOT NULL,
    CONSTRAINT "pk_dim_specialities" PRIMARY KEY (
        "id"
     )
);

INSERT INTO dim_specialities(name, aliases)
VALUES ('BI-аналитик', 'BI,Business Intelligence,PowerBI,Tableau'),
       ('Data Scientist', 'Data Scientist,саентист'),
       ('Data аналитик', 'Аналитик данных,Data аналитик,Data Analyst'),
       ('Data engineer', 'Data engineer,Дата инженер,инженер данных'),
       ('ETL-разработчик', 'ETL');

-- Справочник градаций
CREATE TABLE "dim_grades" (
    -- id
    "id"  SERIAL  NOT NULL,
    -- название
    "name" varchar(200)   NOT NULL,
    -- синонимы
    "aliases" text   NOT NULL,
    CONSTRAINT "pk_dim_grades" PRIMARY KEY (
        "id"
     )
);

INSERT INTO dim_grades(id, name, aliases)
VALUES (0, 'N/A', ''),
       (1, 'Junior', 'junior,intern,джуниор,младший,стажер,стажёр'),
       (2, 'Middle', 'middle,миддл'),
       (3, 'Senior', 'senior,старший,ведущий,главный,сеньор,сеньёр,тимлид,lead,руководитель');

-- Справочник работодателей
CREATE TABLE "dim_employers" (
    -- id
    "id"  SERIAL  NOT NULL,
    -- код компании
    "code" varchar(20)   NOT NULL,
    -- название компании
    "name" varchar(200)   NOT NULL,
    -- флаг, показывающий, прошла ли компания проверку на сайте
    "trusted" boolean   NOT NULL,
    CONSTRAINT "pk_dim_employers" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_dim_employers_code" UNIQUE (
        "code"
    )
);

CREATE TABLE "fact_vacancies" (
    -- id
    "id" int   NOT NULL,
    -- название вакансии
    "name" varchar(200)   NOT NULL,
    -- дата создания
    "created_date_id" int   NOT NULL,
    -- id специальности
    "speciality_id" int   NOT NULL,
    -- id уровня
    "grade_id" int  DEFAULT 0 NOT NULL,
    -- id региона
    "area_id" int   NOT NULL,
    -- id работодателя
    "employer_id" int   NOT NULL,
    -- id графика работы
    "schedule_id" int   NOT NULL,
    -- id типа вакансии
    "type_id" int   NOT NULL,
    -- является ли данная вакансия премиум-вакансией
    "premium" boolean   NOT NULL,
    -- Информация о наличии прикрепленного тестового задании к вакансии
    "has_test" boolean   NOT NULL,
    -- Обязательно ли заполнять сообщение при отклике на вакансию
    "response_letter_required" boolean   NOT NULL,
    -- Нижняя граница вилки оклада в рублях после вычета налогов
    "salary_from" int   NULL,
    -- Верхняя граница вилки оклада в рублях после вычета налогов
    "salary_to" int   NULL,
    CONSTRAINT "pk_fact_vacancies" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_created_date_id" FOREIGN KEY("created_date_id")
REFERENCES "dim_dates" ("id");

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_speciality_id" FOREIGN KEY("speciality_id")
REFERENCES "dim_specialities" ("id");

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_grade_id" FOREIGN KEY("grade_id")
REFERENCES "dim_grades" ("id");

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_area_id" FOREIGN KEY("area_id")
REFERENCES "dim_areas" ("id");

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_employer_id" FOREIGN KEY("employer_id")
REFERENCES "dim_employers" ("id");

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_schedule_id" FOREIGN KEY("schedule_id")
REFERENCES "dim_schedules" ("id");

ALTER TABLE "fact_vacancies" ADD CONSTRAINT "fk_fact_vacancies_type_id" FOREIGN KEY("type_id")
REFERENCES "dim_types" ("id");

CREATE INDEX "idx_fact_vacancies_created_date_id"
ON "fact_vacancies" ("created_date_id");

CREATE INDEX "idx_fact_vacancies_speciality_id"
ON "fact_vacancies" ("speciality_id");

CREATE INDEX "idx_fact_vacancies_grade_id"
ON "fact_vacancies" ("grade_id");

CREATE INDEX "idx_fact_vacancies_area_id"
ON "fact_vacancies" ("area_id");

CREATE INDEX "idx_fact_vacancies_employer_id"
ON "fact_vacancies" ("employer_id");

CREATE INDEX "idx_fact_vacancies_schedule_id"
ON "fact_vacancies" ("schedule_id");

CREATE INDEX "idx_fact_vacancies_type_id"
ON "fact_vacancies" ("type_id");

-- Курсы валют
CREATE TABLE "exchange_rates" (
    -- дата
    "date" date   NOT NULL,
    -- ISO Букв. код валюты
    "currency" varchar(3)   NOT NULL,
    -- курс валюты
    "rate" numeric(16,8)   NOT NULL,
    CONSTRAINT "pk_exchange_rates" PRIMARY KEY (
       "date","currency"
    )
);