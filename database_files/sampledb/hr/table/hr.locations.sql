CREATE TABLE hr.LOCATIONS 
    ( 
     LOCATION_ID NUMBER (4)  NOT NULL , 
     STREET_ADDRESS VARCHAR2 (40 BYTE) , 
     POSTAL_CODE VARCHAR2 (12 BYTE) , 
     CITY VARCHAR2 (30 BYTE)  NOT NULL , 
     STATE_PROVINCE VARCHAR2 (25 BYTE) , 
     COUNTRY_ID CHAR (2 BYTE) 
    ) LOGGING 
;



COMMENT ON COLUMN hr.LOCATIONS.LOCATION_ID IS 'Primary key of locations table' 
;

COMMENT ON COLUMN hr.LOCATIONS.STREET_ADDRESS IS 'Street address of an office, warehouse, or production site of a company.
Contains building number and street name' 
;

COMMENT ON COLUMN hr.LOCATIONS.POSTAL_CODE IS 'Postal code of the location of an office, warehouse, or production site 
of a company. ' 
;

COMMENT ON COLUMN hr.LOCATIONS.CITY IS 'A not null column that shows city where an office, warehouse, or 
production site of a company is located. ' 
;

COMMENT ON COLUMN hr.LOCATIONS.STATE_PROVINCE IS 'State or Province where an office, warehouse, or production site of a 
company is located.' 
;

COMMENT ON COLUMN hr.LOCATIONS.COUNTRY_ID IS 'Country where an office, warehouse, or production site of a company is
located. Foreign key to country_id column of the countries table.' 
;




ALTER TABLE hr.LOCATIONS 
    ADD CONSTRAINT LOC_ID_PK PRIMARY KEY ( LOCATION_ID ) ;

ALTER TABLE hr.LOCATIONS 
    ADD CONSTRAINT LOC_C_ID_FK FOREIGN KEY 
    ( 
     COUNTRY_ID
    ) 
    REFERENCES hr.COUNTRIES 
    ( 
     COUNTRY_ID
    ) 
    NOT DEFERRABLE 
;