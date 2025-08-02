CREATE TABLE HR.DEPARTMENTS 
    ( 
     DEPARTMENT_ID NUMBER (4)  NOT NULL , 
     DEPARTMENT_NAME VARCHAR2 (30 BYTE)  NOT NULL , 
     MANAGER_ID NUMBER (6) , 
     LOCATION_ID NUMBER (4) 
    ) LOGGING 
;



COMMENT ON COLUMN HR.DEPARTMENTS.DEPARTMENT_ID IS 'Primary key column of departments table.' 
;

COMMENT ON COLUMN HR.DEPARTMENTS.DEPARTMENT_NAME IS 'A not null column that shows name of a department. Administration, 
Marketing, Purchasing, Human Resources, Shipping, IT, Executive, Public 
Relations, Sales, Finance, and Accounting. ' 
;

COMMENT ON COLUMN HR.DEPARTMENTS.MANAGER_ID IS 'Manager_id of a department. Foreign key to employee_id column of employees table. The manager_id column of the employee table references this column.' 
;

COMMENT ON COLUMN HR.DEPARTMENTS.LOCATION_ID IS 'Location id where a department is located. Foreign key to location_id column of locations table.' 
;


ALTER TABLE HR.DEPARTMENTS 
    ADD CONSTRAINT DEPT_ID_PK PRIMARY KEY ( DEPARTMENT_ID ) ;

ALTER TABLE hr.DEPARTMENTS 
    ADD CONSTRAINT DEPT_LOC_FK FOREIGN KEY 
    ( 
     LOCATION_ID
    ) 
    REFERENCES hr.LOCATIONS 
    ( 
     LOCATION_ID
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE hr.DEPARTMENTS 
    ADD CONSTRAINT DEPT_MGR_FK FOREIGN KEY 
    ( 
     MANAGER_ID
    ) 
    REFERENCES hr.EMPLOYEES 
    ( 
     EMPLOYEE_ID
    ) 
    NOT DEFERRABLE 
;