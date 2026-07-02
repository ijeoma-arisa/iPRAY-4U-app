-- Run this before creating uq_people_user_normalized_name.
SELECT
  user_id,
  lower(btrim(name)) AS normalized_name,
  count(*) AS duplicate_count,
  array_agg(id ORDER BY id) AS person_ids,
  array_agg(name ORDER BY id) AS stored_names
FROM people
GROUP BY user_id, lower(btrim(name))
HAVING count(*) > 1
ORDER BY user_id, normalized_name;
