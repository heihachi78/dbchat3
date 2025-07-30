CREATE TABLE hr.REGIONS 
    ( 
     REGION_ID NUMBER  NOT NULL , 
     REGION_NAME VARCHAR2 (25 BYTE) 
    ) LOGGING 
;



COMMENT ON COLUMN hr.REGIONS.REGION_ID IS 'Primary key of regions table.' 
;

COMMENT ON COLUMN hr.REGIONS.REGION_NAME IS 'Names of regions. Locations are in the countries of these regions.' 
;

ALTER TABLE hr.REGIONS 
    ADD CONSTRAINT REG_ID_PK PRIMARY KEY ( REGION_ID ) ;