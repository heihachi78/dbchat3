CREATE OR REPLACE VIEW hr.EMP_DETAILS_VIEW
AS 
SELECT
  e.employee_id, 
  e.job_id, 
  e.manager_id, 
  e.department_id,
  d.location_id,
  l.country_id,
  e.first_name,
  e.last_name,
  e.first_name || ' ' || e.last_name AS full_name,
  e.salary,
  e.commission_pct as commission_percentage,
  d.department_name,
  j.job_title,
  l.city,
  l.state_province,
  c.country_name,
  r.region_name
FROM
  hr.employees e,
  hr.departments d,
  hr.jobs j,
  hr.locations l,
  hr.countries c,
  hr.regions r
WHERE e.department_id = d.department_id
  AND d.location_id = l.location_id
  AND l.country_id = c.country_id
  AND c.region_id = r.region_id
  AND j.job_id = e.job_id 
WITH READ ONLY ;