-- Script SQLite para fazer a correção manual do banco de dados, adicionando os postos novos e organizando eles.
-- Presume-se que vai ser necessário apenas uma vez e que, na próxima coleta de dados da prefeitura,
-- irá funcionar porque o BD foi corrigido.

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

-- Terminamos isso, então podemos fazer as correções na tabela.


-- 1. "Abrir espaço" para o posto 70 (Posto Buffon) e o 72 (Auto Posto Orquídea)

UPDATE PostosGasolina SET IdPosto = IdPosto + 1000 WHERE IdPosto > 69;
INSERT INTO PostosGasolina(IdPosto, IdDistribuidora, NomePosto, EnderecoPosto, BairroPosto) VALUES (70, 5, "Posto Buffon", "Rod. BR 101, KM 33", "Pirabeiraba");
UPDATE PostosGasolina SET IdPosto = IdPosto - 1000 WHERE IdPosto >= 1000;

UPDATE PostosGasolina SET IdPosto = IdPosto + 1000 WHERE IdPosto > 71;
INSERT INTO PostosGasolina(IdPosto, IdDistribuidora, NomePosto, EnderecoPosto, BairroPosto) VALUES (72, 4, "Auto Posto Orquídea", "R. Dona Francisca, 11750", "Pirabeiraba");
UPDATE PostosGasolina SET IdPosto = IdPosto - 999 WHERE IdPosto >= 1000;

-- 2. As tabelas antigas tinham inconsistência (dois postos no exato mesmo endereço e número). Para não perdermos a série histórica,
-- o posto Mediterrâneo (Rua Max Colin, 1770) foi movido para o ID 102.

UPDATE PostosGasolina SET IdPosto = 102 WHERE IdPosto = 74;
UPDATE PostosGasolina SET NomePosto = 'Posto Mediterrâneo (antigo)' WHERE IdPosto = 102;

UPDATE PostosGasolina SET IdPosto = IdPosto - 1 WHERE IdPosto BETWEEN 75 AND 101;

-- 3. Mexemos nos IDs então agora podemos mexer nos nomes.

UPDATE PostosGasolina SET NomePosto = 'Posto Padre Reus Ltda (Galileu) - FECHADO' WHERE IdPosto = 51;
UPDATE PostosGasolina SET NomePosto = 'Posto Agricopel' WHERE IdPosto = 39;
UPDATE PostosGasolina SET NomePosto = 'Auto Posto Petroleum' WHERE IdPosto = 47;
UPDATE PostosGasolina SET NomePosto = 'Posto Bravva (Antigo posto Hardt)' WHERE IdPosto = 77;
UPDATE PostosGasolina SET NomePosto = 'Posto Estrela Odara (antigo Posto Mediterrâneo)' WHERE IdPosto = 87;
