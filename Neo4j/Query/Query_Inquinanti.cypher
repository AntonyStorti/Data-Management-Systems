PROFILE
MATCH (c:Città)-[:ha_stazione]->(s:StazioneMonitoraggio)-[r:ha_monitorato]->(i:Inquinante)
WITH s, i, r.valore AS valore_inquinante, s.name AS station_name, s.latitude AS latitude, s.longitude AS longitude
WITH point({latitude: latitude, longitude: longitude}) AS stazione_coord, s, i, valore_inquinante
CALL spatial.intersects('zone_omi', stazione_coord) YIELD node
WITH node.name AS zona_name, i.name AS inquinante_name, valore_inquinante
WITH zona_name, inquinante_name, collect(valore_inquinante) AS valori_inquinante
UNWIND valori_inquinante AS valore
RETURN zona_name, inquinante_name, avg(valore) AS media_inquinante;
