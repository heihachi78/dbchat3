CREATE TABLE HR.COUNTRIES 
    ( 
     COUNTRY_ID CHAR (2 BYTE)  NOT NULL , 
     COUNTRY_NAME VARCHAR2 (40 BYTE) , 
     REGION_ID NUMBER 
    ) LOGGING 
;

COMMENT ON COLUMN HR.COUNTRIES.COUNTRY_ID IS 'Primary key of countries table.' ;

COMMENT ON COLUMN HR.COUNTRIES.COUNTRY_NAME IS 'Country name' ;

COMMENT ON COLUMN HR.COUNTRIES.REGION_ID IS 'Region ID for the country. Foreign key to region_id column in the departments table.' ;

ALTER TABLE HR.COUNTRIES 
    ADD CONSTRAINT COUNTRY_C_ID_PK PRIMARY KEY ( COUNTRY_ID ) ;

ALTER TABLE hr.COUNTRIES 
    ADD CONSTRAINT COUNTR_REG_FK FOREIGN KEY 
    ( 
     REGION_ID
    ) 
    REFERENCES hr.REGIONS 
    ( 
     REGION_ID
    ) 
    NOT DEFERRABLE 
;