PROFILE
MATCH (c:Città)-[:divisa_in]->(z:Feature)-[r:ha_consumo]->()
WITH z, AVG(r.consumo_energetico) AS media_consumo
RETURN z.nome AS zona, media_consumo;
