# HR.JOB_HISTORY (Table) – Comprehensive Documentation

---

## Object Overview

**Type:** Table  
**Schema:** HR  
**Object Name:** JOB_HISTORY

**Primary Purpose:**  
The `JOB_HISTORY` table records the historical job assignments of employees within the organization. It tracks each period during which an employee held a specific job role in a particular department, including the start and end dates of each assignment.

**Business Context & Use Cases:**  
- **Audit Trail:** Maintains a complete employment history for each employee, supporting audit and compliance requirements.
- **HR Analytics:** Enables analysis of employee mobility, tenure in roles, and departmental transitions.
- **Reporting:** Supports reporting on employee career progression, departmental staffing history, and job role occupancy over time.
- **Data Integrity:** Ensures that historical job data is preserved even after employees change roles or departments.

---

## Detailed Structure & Components

| Column Name     | Data Type         | Nullable | Description                                                                                  | Constraints / Notes                                  |
|-----------------|------------------|----------|----------------------------------------------------------------------------------------------|------------------------------------------------------|
| EMPLOYEE_ID     | NUMBER(6)        | No       | Employee identifier. Part of the composite primary key. Foreign key to `EMPLOYEES.EMPLOYEE_ID`. | Not null, PK, FK                                     |
| START_DATE      | DATE             | No       | Start date of the job assignment. Part of the composite primary key. Must be less than `END_DATE`. | Not null, PK, CHECK                                  |
| END_DATE        | DATE             | No       | Last day of the employee in this job role. Must be greater than `START_DATE`.                | Not null, CHECK                                      |
| JOB_ID          | VARCHAR2(10 BYTE)| No       | Job role held by the employee. Foreign key to `JOBS.JOB_ID`.                                | Not null, FK                                         |
| DEPARTMENT_ID   | NUMBER(4)        | Yes      | Department in which the employee worked. Foreign key to `DEPARTMENTS.DEPARTMENT_ID`.         | Nullable, FK                                         |

**Table Properties:**  
- **LOGGING:** Table changes are logged for recovery and auditing.

---

## Component Analysis

### EMPLOYEE_ID
- **Type:** NUMBER(6)
- **Required:** Yes (NOT NULL)
- **Role:** Uniquely identifies the employee for each job history record.
- **Business Meaning:** Links each job history entry to a specific employee.
- **Constraints:**  
  - Part of the composite primary key (`EMPLOYEE_ID`, `START_DATE`).
  - Foreign key to `EMPLOYEES.EMPLOYEE_ID`.
- **Comment:** "A not null column in the complex primary key employee_id+start_date. Foreign key to employee_id column of the employee table."

### START_DATE
- **Type:** DATE
- **Required:** Yes (NOT NULL)
- **Role:** Marks the beginning of the job assignment period.
- **Business Meaning:** Indicates when the employee started the job role.
- **Constraints:**  
  - Part of the composite primary key.
  - Must be less than `END_DATE` (enforced by `JHIST_DATE_INTERVAL`).
- **Comment:** "A not null column in the complex primary key employee_id+start_date. Must be less than the end_date of the job_history table. (enforced by constraint jhist_date_interval)"

### END_DATE
- **Type:** DATE
- **Required:** Yes (NOT NULL)
- **Role:** Marks the end of the job assignment period.
- **Business Meaning:** Indicates when the employee left the job role.
- **Constraints:**  
  - Must be greater than `START_DATE` (enforced by `JHIST_DATE_INTERVAL`).
- **Comment:** "Last day of the employee in this job role. A not null column. Must be greater than the start_date of the job_history table. (enforced by constraint jhist_date_interval)"

### JOB_ID
- **Type:** VARCHAR2(10 BYTE)
- **Required:** Yes (NOT NULL)
- **Role:** Identifies the job role held by the employee.
- **Business Meaning:** Specifies the position or title during the job history period.
- **Constraints:**  
  - Foreign key to `JOBS.JOB_ID`.
- **Comment:** "Job role in which the employee worked in the past; foreign key to job_id column in the jobs table. A not null column."

### DEPARTMENT_ID
- **Type:** NUMBER(4)
- **Required:** No (nullable)
- **Role:** Identifies the department where the employee worked.
- **Business Meaning:** Associates the job history record with a specific department.
- **Constraints:**  
  - Foreign key to `DEPARTMENTS.DEPARTMENT_ID`.
- **Comment:** "Department id in which the employee worked in the past; foreign key to department_id column in the departments table."

---

## Complete Relationship Mapping

### Foreign Key Relationships

- **EMPLOYEE_ID**  
  - References: `HR.EMPLOYEES(EMPLOYEE_ID)`  
  - **Purpose:** Ensures that every job history record is associated with a valid employee.

- **JOB_ID**  
  - References: `HR.JOBS(JOB_ID)`  
  - **Purpose:** Ensures that the job role exists in the jobs master table.

- **DEPARTMENT_ID**  
  - References: `HR.DEPARTMENTS(DEPARTMENT_ID)`  
  - **Purpose:** Ensures that the department exists in the departments master table.

### Primary Key

- **Composite Key:** (`EMPLOYEE_ID`, `START_DATE`)
  - **Purpose:** Uniquely identifies each job history record for an employee, allowing multiple non-overlapping job history entries per employee.

### Self-Referencing / Hierarchical Structures

- **None:** No self-referencing or hierarchical relationships are defined.

### Dependencies

- **Depends on:**  
  - `HR.EMPLOYEES`
  - `HR.JOBS`
  - `HR.DEPARTMENTS`

- **Dependent Objects:**  
  - Any views, reports, or procedures referencing job history data.

### Impact Analysis

- **Cascading Operations:**  
  - Deleting referenced employees, jobs, or departments will fail unless corresponding job history records are removed or foreign key constraints are set to cascade (not specified here).
  - Changes to referenced keys in parent tables will impact referential integrity.

---

## Comprehensive Constraints & Rules

### Constraints

- **Primary Key:**  
  - `JHIST_EMP_ID_ST_DATE_PK` on (`EMPLOYEE_ID`, `START_DATE`)
  - **Business Justification:** Ensures uniqueness of job history periods per employee.

- **Check Constraint:**  
  - `JHIST_DATE_INTERVAL`: `END_DATE > START_DATE`
  - **Business Justification:** Prevents illogical or invalid job history periods.

- **Foreign Keys:**  
  - `JHIST_EMP_FK` (`EMPLOYEE_ID` → `EMPLOYEES.EMPLOYEE_ID`)
  - `JHIST_JOB_FK` (`JOB_ID` → `JOBS.JOB_ID`)
  - `JHIST_DEPT_FK` (`DEPARTMENT_ID` → `DEPARTMENTS.DEPARTMENT_ID`)
  - **Business Justification:** Maintains referential integrity with master data.

### Business Rules Enforced

- No job history record can exist without a valid employee, job, and (optionally) department.
- No job history period can have an end date before or equal to the start date.
- Each employee can have multiple job history records, but not with the same start date.

### Security, Access, and Data Integrity

- **Data Integrity:** Enforced via primary key, foreign keys, and check constraints.
- **Security:** Not specified in DDL; typically managed via schema privileges.

### Performance Implications

- **Primary Key:** Supports efficient lookups by employee and start date.
- **Foreign Keys:** May impact performance on insert/update if parent tables are large, but ensure data integrity.

---

## Usage Patterns & Integration

### Business Process Integration

- **HR Onboarding/Offboarding:** Updates when employees change roles or departments.
- **Payroll & Benefits:** Used to determine eligibility based on historical roles.
- **Reporting:** Supports queries for employee movement, tenure, and departmental history.

### Common Query Patterns

- Retrieve all job history for a given employee.
- Find employees who held a specific job or worked in a specific department during a time period.
- Analyze job or department turnover rates.

### Performance & Tuning

- Composite primary key and foreign keys support efficient joins and lookups.
- Indexing on foreign keys may be beneficial for large datasets.

### Application Integration

- Used by HR management systems, reporting tools, and analytics platforms.
- May be referenced by triggers or procedures for auditing or workflow automation.

---

## Implementation Details

### Storage Specifications

- **LOGGING:** All changes are logged, supporting recovery and auditing.

### Special Database Features

- **Check Constraint:** Enforces business logic at the database level.
- **Composite Primary Key:** Ensures uniqueness and supports efficient access patterns.

### Maintenance & Operational Considerations

- **Data Growth:** Table may grow large over time; consider partitioning or archiving strategies.
- **Constraint Management:** All constraints are enabled and validated, ensuring ongoing data integrity.
- **Foreign Key Maintenance:** Parent table changes must consider dependent job history records.

---

## Summary Table

| Column         | Data Type         | Required | Key/Constraint         | Foreign Key Reference         | Description                                                                 |
|----------------|------------------|----------|------------------------|------------------------------|-----------------------------------------------------------------------------|
| EMPLOYEE_ID    | NUMBER(6)        | Yes      | PK, FK                 | EMPLOYEES(EMPLOYEE_ID)       | Employee identifier                                                        |
| START_DATE     | DATE             | Yes      | PK                     |                              | Start date of job assignment                                               |
| END_DATE       | DATE             | Yes      | CHECK                  |                              | End date of job assignment                                                 |
| JOB_ID         | VARCHAR2(10 BYTE)| Yes      | FK                     | JOBS(JOB_ID)                 | Job role identifier                                                        |
| DEPARTMENT_ID  | NUMBER(4)        | No       | FK                     | DEPARTMENTS(DEPARTMENT_ID)   | Department identifier                                                      |

---

**This documentation provides a complete, detailed reference for the `HR.JOB_HISTORY` table, supporting both technical and business users in understanding its structure, constraints, relationships, and role within the HR schema.**