-- Script SQLite para fazer a correção manual do banco de dados, adicionando os postos novos e organizando eles.

-- SQLite não suporta mudar o UPDATE de uma tabela por meio de ALTER TABLE, então:
-- 1. Criar uma nova tabela com as alterações desejadas e renomear a velha
-- 2. Copiar os dados velhos para a tabela nova
-- 3. Deletar a velha


PRAGMA foreign_keys=off;
BEGIN TRANSACTION;
ALTER TABLE "Precos" RENAME TO "Precos_OLD";
ALTER TABLE "PostosGasolina" RENAME TO "PostosGasolina_OLD";

CREATE TABLE "Precos" (
    "IdPreco"	INTEGER NOT NULL,
    "IdPesquisa"	INTEGER,
    "IdPosto"	INTEGER,
    "PrecoGasolinaComum"	NUMERIC,
    "PrecoGasolinaAditivada"	NUMERIC,
    "PrecoEtanol"	NUMERIC,
    "PrecoDiesel"	NUMERIC,
    "PrecoGNV"	NUMERIC,
    "PrecoGasolinaPremium"	NUMERIC,
    PRIMARY KEY("IdPreco"),
    FOREIGN KEY("IdPesquisa") REFERENCES "Pesquisas"("IdPesquisa") ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY("IdPosto") REFERENCES "PostosGasolina"("IdPosto") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "PostosGasolina" (
	"IdPosto"	INTEGER NOT NULL,
	"IdDistribuidora"	INTEGER NOT NULL,
	"NomePosto"	VARCHAR(255) NOT NULL,
	"EnderecoPosto"	VARCHAR(255) NOT NULL,
	"BairroPosto"	VARCHAR(32),
	PRIMARY KEY("IdPosto"),
	UNIQUE("IdPosto","NomePosto","EnderecoPosto","BairroPosto") ON CONFLICT REPLACE,
	FOREIGN KEY("IdDistribuidora") REFERENCES "Distribuidoras"("IdDistribuidora") ON DELETE RESTRICT ON UPDATE CASCADE
);

INSERT INTO "Precos" SELECT * FROM "Precos_OLD";
INSERT INTO "PostosGasolina" SELECT * FROM "PostosGasolina_OLD";

DROP TABLE "Precos_OLD";
DROP TABLE "PostosGasolina_OLD";

COMMIT;

PRAGMA foreign_keys=on;
