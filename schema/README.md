# Diagram Documentation

## dim_dates

*Справочник дат*

| **Field** | **Description**     | **Type** | **Default** | **Other** |
| --------- | ------------------- | -------- | ----------- | --------- |
| id        | id                  | int      |             | PK        |
| date      | дата                | date     |             |           |
| year      | год                 | smallint |             |           |
| quarter   | квартал             | smallint |             |           |
| month     | месяц               | smallint |             |           |
| week      | номер недели        | smallint |             |           |
| week_day  | день 		недели | smallint |             |           |

## dim_types

*Справочник типов вакансий*

| **Field** | **Description**   | **Type**     | **Default** | **Other**            |
| --------- | ----------------- | ------------ | ----------- | -------------------- |
| id        | id                | int          |             | PK, 		IDENTITY |
| code      | код типа вакансии | varchar(20)  |             | UNIQUE               |
| name      | название          | varchar(200) |             |                      |

## dim_areas

*Справочник регионов размещения вакансии*

| **Field** | **Description**          | **Type**     | **Default** | **Other**            |
| --------- | ------------------------ | ------------ | ----------- | -------------------- |
| id        | id                       | int          |             | PK, 		IDENTITY |
| code      | код региона              | varchar(20)  |             | UNIQUE               |
| name      | название 		региона | varchar(200) |             |                      |

## dim_schedules

*Справочник графиков работы*

| **Field** | **Description** | **Type**     | **Default** | **Other**            |
| --------- | --------------- | ------------ | ----------- | -------------------- |
| id        | id              | int          |             | PK, 		IDENTITY |
| code      | код             | varchar(20)  |             | UNIQUE               |
| name      | название        | varchar(200) |             |                      |

## dim_grades

*Справочник грейдов*

| **Field** | **Description** | **Type**     | **Default** | **Other**            |
| --------- | --------------- | ------------ | ----------- | -------------------- |
| id        | id              | int          |             | PK, 		IDENTITY |
| name      | название        | varchar(200) |             |                      |
| aliases   | синонимы        | text         |             |                      |

## dim_specialities

*Справочник специальностей*

| **Field** | **Description** | **Type**     | **Default** | **Other**            |
| --------- | --------------- | ------------ | ----------- | -------------------- |
| id        | id              | int          |             | PK, 		IDENTITY |
| name      | название        | varchar(200) |             |                      |
| aliases   | синонимы        | text         |             |                      |

## dim_employers

*Справочник работодателей*

| **Field** | **Description**                                              | **Type**     | **Default** | **Other**            |
| --------- | ------------------------------------------------------------ | ------------ | ----------- | -------------------- |
| id        | id                                                           | int          |             | PK, 		IDENTITY |
| code      | код компании                                                 | varchar(20)  |             | UNIQUE               |
| name      | название 		компании                                    | varchar(200) |             |                      |
| trusted   | флаг, показывающий, 		прошла ли компания проверку на сайте | boolean      |             |                      |

## fact_vacancies

| **Field**                | **Description**                                              | **Type**     | **Default** | **Other**         |
| ------------------------ | ------------------------------------------------------------ | ------------ | ----------- | ----------------- |
| id                       | id                                                           | int          |             | PK                |
| name                     | название вакансии                                            | varchar(200) |             |                   |
| created_date_id          | дата 		создания                                        | int          |             | FK, 		INDEX |
| speciality_id            | id специальности                                             | int          |             | FK, INDEX         |
| grade_id                 | id 		уровней                                           | int          | 0           | FK, 		INDEX |
| area_id                  | id региона                                                   | int          |             | FK, INDEX         |
| employer_id              | id 		работодателя                                      | int          |             | FK, 		INDEX |
| schedule_id              | id графика работы                                            | int          |             | FK, INDEX         |
| type_id                  | id 		типа вакансии                                     | int          |             | FK, 		INDEX |
| premium                  | является ли данная 		вакансия премиум-вакансией        | boolean      |             |                   |
| has_test                 | Информация 		о наличии прикрепленного тестового 		задании к вакансии | boolean      |             |                   |
| response_letter_required | Обязательно ли 		заполнять сообщение при отклике на 		вакансию | boolean      |             |                   |
| salary_from              | Нижняя 		граница вилки оклада в рублях после 		вычета налогов | int          |             | NULLABLE          |
| salary_to                | Верхняя граница 		вилки оклада в рублях после вычета 		налогов | int          |             | NULLABLE          |

## exchange_rates

*Курсы валют*

| **Field** | **Description**      | **Type**      | **Default** | **Other** |
| --------- | -------------------- | ------------- | ----------- | --------- |
| date      | дата                 | date          |             | PK        |
| currency  | ISO Букв. код валюты | varchar(3)    |             | PK        |
| rate      | курс 		валюты  | numeric(12,4) |             |           |

