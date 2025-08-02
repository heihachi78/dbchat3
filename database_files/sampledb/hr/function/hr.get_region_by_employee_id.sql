CREATE OR REPLACE FUNCTION hr.get_region_by_employee_id(p_employee_id IN NUMBER)
RETURN VARCHAR2 IS
  v_region_name VARCHAR2(100);
BEGIN
  SELECT r.region_name
    INTO v_region_name
    FROM hr.employees e
    JOIN hr.departments d ON e.department_id = d.department_id
    JOIN hr.locations l ON d.location_id = l.location_id
    JOIN hr.countries c ON l.country_id = c.country_id
    JOIN hr.regions r ON c.region_id = r.region_id
   WHERE e.employee_id = p_employee_id;

  RETURN v_region_name;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    RETURN NULL;
END;