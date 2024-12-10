PROFILE
MATCH (c:Città {name: 'Avellino'})-[r]-(i:Indirizzo)-[ha]->(p:Pannello)
WITH i.latitude AS lat, i.longitude AS lon, i
WITH point({latitude: lat, longitude: lon}) AS indirizzo_point, i
CALL spatial.intersects('zone_omi', indirizzo_point) YIELD node AS polygon
WITH polygon.name AS zone_name, COUNT(i) AS pannelli_count
RETURN zone_name, pannelli_count;
