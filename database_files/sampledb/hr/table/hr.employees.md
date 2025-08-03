# HR.EMPLOYEES Table Documentation

## Object Overview
**Type:** Table  
**Purpose:** Stores core employee data for the HR department, including personal information, job details, department assignments, and managerial relationships.  
**Role:** Central repository for employee records, enabling tracking of hiring, job roles, compensation, and organizational structure.  
**Business Context:** Used for payroll processing, performance management, and organizational reporting. Supports queries for employee hierarchy, departmental statistics, and job role analysis.

---

## Detailed Structure & Components

### Columns
| Column Name        | Data Type       | Constraints                          | Description                                                                 |
|--------------------|-----------------|--------------------------------------|-----------------------------------------------------------------------------|
| EMPLOYEE_ID        | NUMBER(6)       | NOT NULL, PRIMARY KEY               | Unique identifier for employees.                                           |
| FIRST_NAME         | VARCHAR2(20)    | NULL                                 | Employee's first name.                                                     |
| LAST_NAME          | VARCHAR2(25)    | NOT NULL                            | Employee's last name.                                                      |
| EMAIL              | VARCHAR2(25)    | NOT NULL, UNIQUE                    | Employee's email address.                                                  |
| PHONE_NUMBER       | VARCHAR2(20)    | NULL                                 | Employee's phone number (includes country code).                           |
| HIRE_DATE          | DATE            | NOT NULL                            | Date employee started on current job.                                      |
| JOB_ID             | VARCHAR2(10)    | NOT NULL                            | Current job role (foreign key to JOBS table).                              |
| SALARY             | NUMBER(8,2)     | NULL, CHECK (SALARY > 0)            | Monthly salary.                                                            |
| COMMISSION_PCT     | NUMBER(2,2)     | DEFAULT 0.00                        | Commission percentage (only applicable to sales department employees).     |
| MANAGER_ID         | NUMBER(6)       | NULL, FOREIGN KEY                   | Manager's employee ID (self-referential).                                  |
| DEPARTMENT_ID      | NUMBER(4)       | FOREIGN KEY                         | Department ID (foreign key to DEPARTMENTS table).                          |

---

## Component Analysis

### Business Meaning & Constraints
- **EMPLOYEE_ID**: Primary key, uniquely identifies each employee.  
- **EMAIL**: Unique constraint ensures no duplicate email addresses.  
- **SALARY**: Must be greater than zero (enforced by check constraint).  
- **COMMISSION_PCT**: Default value of 0.00, restricted to sales department employees (business rule).  
- **MANAGER_ID**: Self-referential foreign key, enabling hierarchical queries (e.g., CONNECT BY).  
- **HIRE_DATE**: Not null, tracks when employees started their current role.  

### Data Type Specifications
- **NUMBER(6)**: 6-digit integer (e.g., EMPLOYEE_ID).  
- **VARCHAR2(25)**: 25-byte string (e.g., EMAIL).  
- **DATE**: Standard date type (e.g., HIRE_DATE).  
- **NUMBER(8,2)**: 8-digit number with 2 decimal places (e.g., SALARY).  

### Validation Rules
- **Unique Email**: Prevents duplicate email entries.  
- **Positive Salary**: Ensures valid compensation data.  
- **Manager ID Validity**: Foreign key to EMPLOYEES table.  
- **Job ID Validity**: Foreign key to JOBS table.  
- **Department ID Validity**: Foreign key to DEPARTMENTS table.  

### Default Values
- **COMMISSION_PCT**: Default 0.00 (no commission unless specified).  

### Special Handling
- **Self-referential Manager ID**: Enables recursive queries for organizational hierarchy.  
- **Phone Number Format**: Includes country code and area code (e.g., +1 555 123 4567).  

---

## Complete Relationship Mapping

### Foreign Key Relationships
1. **DEPARTMENT_ID** → **DEPARTMENTS.DEPARTMENT_ID**  
   - Links employee to their department.  
2. **JOB_ID** → **JOBS.JOB_ID**  
   - Links employee to their current job role.  
3. **MANAGER_ID** → **EMPLOYEES.EMPLOYEE_ID**  
   - Self-referential: links employee to their manager.  

### Hierarchical Structure
- **Manager-employee hierarchy**: Through MANAGER_ID, allows querying organizational charts (e.g., CONNECT BY).  

### Dependencies
- **Depends on**: JOBS, DEPARTMENTS tables (via foreign keys).  
- **Dependent on**: EMPLOYEE_ID (primary key), EMAIL (unique constraint).  

---

## Comprehensive Constraints & Rules

### Database Constraints
1. **Primary Key**: EMPLOYEE_ID ensures unique employee records.  
2. **Unique Constraint**: EMAIL prevents duplicate email addresses.  
3. **Foreign Keys**:  
   - DEPARTMENT_ID → DEPARTMENTS  
   - JOB_ID → JOBS  
   - MANAGER_ID → EMPLOYEES  
4. **Check Constraint**: SALARY > 0 enforces valid compensation data.  

### Business Rules
- **Commission Eligibility**: COMMISSION_PCT is only applicable to sales department employees (implied by comment).  
- **Manager Validity**: MANAGER_ID must reference an existing employee.  
- **Salary Minimum**: SALARY must be positive (enforced by check constraint).  

### Security & Integrity
- **Unique Email**: Prevents duplicate user accounts.  
- **Foreign Key Enforcement**: Ensures data consistency across related tables.  

---

## Usage Patterns & Integration

### Business Processes
- **Payroll**: SALARY and COMMISSION_PCT used for compensation calculations.  
- **Organizational Reports**: MANAGER_ID and DEPARTMENT_ID for hierarchy and departmental stats.  
- **Job Role Analysis**: JOB_ID for tracking employee roles over time.  

### Query Patterns
- **Hierarchical Queries**: CONNECT BY to traverse manager-employee relationships.  
- **Departmental Statistics**: GROUP BY DEPARTMENT_ID for departmental employee counts.  
- **Job Role Distribution**: COUNT(JOB_ID) per job role.  

### Performance Considerations
- **Indexing**: Implicit indexing on primary key (EMPLOYEE_ID) and foreign keys (DEPARTMENT_ID, JOB_ID, MANAGER_ID).  
- **Unique Constraint**: EMAIL column may be used for fast lookups.  

---

## Implementation Details

### Storage & Logging
- **LOGGING**: Table is logged for recovery purposes.  
- **Storage**: Standard storage for tables (no specific size or partitioning details provided).  

### Database Features
- **Primary Key**: Ensures unique, immutable employee identifiers.  
- **Foreign Keys**: Enforces referential integrity across tables.  
- **Default Values**: COMMISSION_PCT defaults to 0.00.  

### Maintenance
- **Indexing**: Foreign keys and primary key are automatically indexed.  
- **Constraints**: Checked at insert/update time to maintain data integrity.  

--- 

This documentation provides a complete, structured overview of the HR.EMPLOYEES table, including its schema, constraints, relationships, and business logic, suitable for integration into a graph database for RAG purposes.