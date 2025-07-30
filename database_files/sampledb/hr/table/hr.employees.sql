CREATE TABLE HR.EMPLOYEES 
    ( 
     EMPLOYEE_ID NUMBER (6)  NOT NULL , 
     FIRST_NAME VARCHAR2 (20 BYTE) , 
     LAST_NAME VARCHAR2 (25 BYTE)  NOT NULL , 
     EMAIL VARCHAR2 (25 BYTE)  NOT NULL , 
     PHONE_NUMBER VARCHAR2 (20 BYTE) , 
     HIRE_DATE DATE  NOT NULL , 
     JOB_ID VARCHAR2 (10 BYTE)  NOT NULL , 
     SALARY NUMBER (8,2) , 
     COMMISSION_PCT NUMBER (2,2) DEFAULT 0.00 , 
     MANAGER_ID NUMBER (6) , 
     DEPARTMENT_ID NUMBER (4) 
    ) LOGGING 
;



COMMENT ON COLUMN HR.EMPLOYEES.EMPLOYEE_ID IS 'Primary key of employees table.' 
;

COMMENT ON COLUMN HR.EMPLOYEES.FIRST_NAME IS 'First name of the employee. A not null column.' 
;

COMMENT ON COLUMN HR.EMPLOYEES.LAST_NAME IS 'Last name of the employee. A not null column.' 
;

COMMENT ON COLUMN HR.EMPLOYEES.EMAIL IS 'Email id of the employee' 
;

COMMENT ON COLUMN HR.EMPLOYEES.PHONE_NUMBER IS 'Phone number of the employee; includes country code and area code' 
;

COMMENT ON COLUMN HR.EMPLOYEES.HIRE_DATE IS 'Date when the employee started on this job. A not null column.' 
;

COMMENT ON COLUMN HR.EMPLOYEES.JOB_ID IS 'Current job of the employee; foreign key to job_id column of the 
jobs table. A not null column.' 
;

COMMENT ON COLUMN HR.EMPLOYEES.SALARY IS 'Monthly salary of the employee. Must be greater 
than zero (enforced by constraint emp_salary_min)' 
;

COMMENT ON COLUMN HR.EMPLOYEES.COMMISSION_PCT IS 'Commission percentage of the employee; Only employees in sales 
department elgible for commission percentage' 
;

COMMENT ON COLUMN HR.EMPLOYEES.MANAGER_ID IS 'Manager id of the employee; has same domain as manager_id in 
departments table. Foreign key to employee_id column of employees table.
(useful for reflexive joins and CONNECT BY query)' 
;

COMMENT ON COLUMN HR.EMPLOYEES.DEPARTMENT_ID IS 'Department id where employee works; foreign key to department_id 
column of the departments table' 
;

ALTER TABLE HR.EMPLOYEES 
    ADD CONSTRAINT EMP_EMP_ID_PK PRIMARY KEY ( EMPLOYEE_ID ) ;

ALTER TABLE HR.EMPLOYEES 
    ADD CONSTRAINT EMP_EMAIL_UK UNIQUE ( EMAIL ) 
;

ALTER TABLE hr.EMPLOYEES 
    ADD CONSTRAINT EMP_DEPT_FK FOREIGN KEY 
    ( 
     DEPARTMENT_ID
    ) 
    REFERENCES hr.DEPARTMENTS 
    ( 
     DEPARTMENT_ID
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE hr.EMPLOYEES 
    ADD CONSTRAINT EMP_JOB_FK FOREIGN KEY 
    ( 
     JOB_ID
    ) 
    REFERENCES hr.JOBS 
    ( 
     JOB_ID
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE hr.EMPLOYEES 
    ADD CONSTRAINT EMP_MANAGER_FK FOREIGN KEY 
    ( 
     MANAGER_ID
    ) 
    REFERENCES hr.EMPLOYEES 
    ( 
     EMPLOYEE_ID
    ) 
    NOT DEFERRABLE 
;