CREATE INDEX hr.LOC_STATE_PROVINCE_IX ON hr.LOCATIONS 
    ( 
     STATE_PROVINCE ASC 
    ) 
    NOLOGGING 
    NOCOMPRESS 
    NOPARALLEL 
;