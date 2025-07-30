CREATE TABLE HR.JOB_HISTORY 
    ( 
     EMPLOYEE_ID NUMBER (6)  NOT NULL , 
     START_DATE DATE  NOT NULL , 
     END_DATE DATE  NOT NULL , 
     JOB_ID VARCHAR2 (10 BYTE)  NOT NULL , 
     DEPARTMENT_ID NUMBER (4) 
    ) LOGGING 
;



ALTER TABLE HR.JOB_HISTORY 
    ADD CONSTRAINT JHIST_DATE_INTERVAL 
    CHECK (end_date > start_date)
        INITIALLY IMMEDIATE 
        ENABLE 
        VALIDATE 
;




COMMENT ON COLUMN HR.JOB_HISTORY.EMPLOYEE_ID IS 'A not null column in the complex primary key employee_id+start_date.
Foreign key to employee_id column of the employee table' 
;

COMMENT ON COLUMN HR.JOB_HISTORY.START_DATE IS 'A not null column in the complex primary key employee_id+start_date. 
Must be less than the end_date of the job_history table. (enforced by 
constraint jhist_date_interval)' 
;

COMMENT ON COLUMN HR.JOB_HISTORY.END_DATE IS 'Last day of the employee in this job role. A not null column. Must be 
greater than the start_date of the job_history table. 
(enforced by constraint jhist_date_interval)' 
;

COMMENT ON COLUMN HR.JOB_HISTORY.JOB_ID IS 'Job role in which the employee worked in the past; foreign key to 
job_id column in the jobs table. A not null column.' 
;

COMMENT ON COLUMN HR.JOB_HISTORY.DEPARTMENT_ID IS 'Department id in which the employee worked in the past; foreign key to deparment_id column in the departments table' 
;




ALTER TABLE HR.JOB_HISTORY 
    ADD CONSTRAINT JHIST_EMP_ID_ST_DATE_PK PRIMARY KEY ( EMPLOYEE_ID, START_DATE ) ;

ALTER TABLE hr.JOB_HISTORY 
    ADD CONSTRAINT JHIST_DEPT_FK FOREIGN KEY 
    ( 
     DEPARTMENT_ID
    ) 
    REFERENCES hr.DEPARTMENTS 
    ( 
     DEPARTMENT_ID
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE hr.JOB_HISTORY 
    ADD CONSTRAINT JHIST_EMP_FK FOREIGN KEY 
    ( 
     EMPLOYEE_ID
    ) 
    REFERENCES hr.EMPLOYEES 
    ( 
     EMPLOYEE_ID
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE hr.JOB_HISTORY 
    ADD CONSTRAINT JHIST_JOB_FK FOREIGN KEY 
    ( 
     JOB_ID
    ) 
    REFERENCES hr.JOBS 
    ( 
     JOB_ID
    ) 
    NOT DEFERRABLE 
;