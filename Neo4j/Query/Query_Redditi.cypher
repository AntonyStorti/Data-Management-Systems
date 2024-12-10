PROFILE
MATCH (c:Città)-[:appartiene]->(i:Indirizzo)-[:residenza_di]->(s:Soggetto)
RETURN c.name AS città, AVG(s.reddito_imponibile) AS media_reddito
ORDER BY media_reddito DESC;
