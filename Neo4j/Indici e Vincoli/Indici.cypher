CREATE INDEX codcom FOR (n:Feature) ON (n.CODCOM);
CREATE INDEX codzona FOR (n:Feature) ON (n.CODZONA);
CREATE INDEX name_zona FOR (n:Feature) ON (n.name);

CREATE INDEX cat_reddito FOR (n:Soggetto) ON (n.categoria_reddito);
CREATE INDEX modello FOR (n:Soggetto) ON (n.tipo_modello);
CREATE INDEX red_imp FOR (n:Soggetto) ON (n.reddito_imponibile);

CREATE INDEX codcom_cons FOR (n:Consumo) ON (n.codcom);
CREATE INDEX codzona_cons FOR (n:Consumo) ON (n.codzona);
CREATE INDEX data_ora FOR (n:Consumo) ON (n.data_ora);

