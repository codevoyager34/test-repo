SELECT
  p.property_name,
  MAX(CASE WHEN p.machine_name LIKE 'prod01%' THEN p.machine_name END) AS prod01_machine,
  MAX(CASE WHEN p.machine_name LIKE 'prod02%' THEN p.machine_name END) AS prod02_machine,
  MAX(CASE WHEN p.machine_name LIKE 'prod01%' THEN p.property_value END) AS prod01_ip,
  MAX(CASE WHEN p.machine_name LIKE 'prod02%' THEN p.property_value END) AS prod02_ip
FROM your_table p
WHERE p.property_name = 'server.ip'
  AND (p.machine_name LIKE 'prod01%' OR p.machine_name LIKE 'prod02%')
GROUP BY p.property_name;
