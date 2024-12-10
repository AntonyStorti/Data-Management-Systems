CREATE CONSTRAINT indirizzo_unico
IF NOT EXISTS FOR (n:Indirizzo)
REQUIRE (n.indirizzo, n.civico, n.latitude, n.longitude) IS UNIQUE;

CREATE CONSTRAINT ind_not_null
IF NOT EXISTS FOR (n:Indirizzo)
REQUIRE n.indirizzo IS NOT NULL;
CREATE CONSTRAINT civ_not_null
IF NOT EXISTS FOR (n:Indirizzo)
REQUIRE n.civico IS NOT NULL;
CREATE CONSTRAINT lat_not_null
IF NOT EXISTS FOR (n:Indirizzo)
REQUIRE n.latitude IS NOT NULL;
CREATE CONSTRAINT lon_not_null
IF NOT EXISTS FOR (n:Indirizzo)
REQUIRE n.longitude IS NOT NULL;





CREATE CONSTRAINT codcom_codzona_unico
IF NOT EXISTS FOR (n:Feature)
REQUIRE (n.CODCOM, n.CODZONA) IS UNIQUE;
CREATE CONSTRAINT name_unico
IF NOT EXISTS FOR (n:Feature)
REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT name_not_null
IF NOT EXISTS FOR (n:Feature)
REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT codcom_not_null
IF NOT EXISTS FOR (n:Feature)
REQUIRE n.CODCOM IS NOT NULL;
CREATE CONSTRAINT codzona_not_null
IF NOT EXISTS FOR (n:Feature)
REQUIRE n.CODZONA IS NOT NULL;
CREATE CONSTRAINT geom_not_null
IF NOT EXISTS FOR (n:Feature)
REQUIRE n.geometry IS NOT NULL;





CREATE CONSTRAINT soggetto_unico
IF NOT EXISTS FOR (n:Soggetto)
REQUIRE (n.name, n.data_nascita, n.reddito_imponibile) IS UNIQUE;

CREATE CONSTRAINT name_not_null
IF NOT EXISTS FOR (n:Soggetto)
REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT data_not_null
IF NOT EXISTS FOR (n:Soggetto)
REQUIRE n.data_nascita IS NOT NULL;
CREATE CONSTRAINT red_imp_not_null
IF NOT EXISTS FOR (n:Soggetto)
REQUIRE n.reddito_imponibile IS NOT NULL;
CREATE CONSTRAINT modello_not_null
IF NOT EXISTS FOR (n:Soggetto)
REQUIRE n.tipo_modello IS NOT NULL;
CREATE CONSTRAINT imp_net_not_null
IF NOT EXISTS FOR (n:Soggetto)
REQUIRE n.imposta_netta IS NOT NULL;





CREATE CONSTRAINT consumo_unico
IF NOT EXISTS FOR (n:Consumo)
REQUIRE (n.codcom, n.codzona, n.data_ora) IS UNIQUE;

CREATE CONSTRAINT codcom_not_null
IF NOT EXISTS FOR (n:Consumo)
REQUIRE n.codcom IS NOT NULL;
CREATE CONSTRAINT codzona_not_null
IF NOT EXISTS FOR (n:Consumo)
REQUIRE n.codzona IS NOT NULL;
CREATE CONSTRAINT data_not_null
IF NOT EXISTS FOR (n:Consumo)
REQUIRE n.data_ora IS NOT NULL;
