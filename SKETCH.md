
* Posto de gasolina TEM uma única distribuidora, e uma distribuidora ATENDE vários postos
* Uma pesquisa pode conter vários postos, e cada posto tem apenas um PREÇO para cada combustível

CREATE TABLE IF NOT EXISTS Distribuidoras(
	IdDistribuidora INT PRIMARY KEY,
	NomeDistribuidora VARCHAR(24) NOT NULL
);

CREATE TABLE IF NOT EXISTS PostosGasolina(
	IdPosto INT PRIMARY KEY,
	IdDistribuidora INT NOT NULL,
	NomePosto VARCHAR(255) NOT NULL,
	EnderecoPosto VARCHAR(255) NOT NULL,
	BairroPosto VARCHAR(32) NOT NULL,
	FOREIGN KEY (IdDistribuidora)
		REFERENCES Distribuidoras(IdDistribuidora)
		ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Pesquisas(
	IdPesquisa INT PRIMARY KEY,
	DataPesquisa VARCHAR(24) NOT NULL
);

CREATE TABLE IF NOT EXISTS Precos(
	IdPreco INT PRIMARY KEY,
	IdPesquisa INT,
	IdPosto INT,
	PrecoGasolinaComum INTEGER,
	PrecoGasolinaAditivada INTEGER,
	PrecoEtanol INTEGER,
	PrecoDiesel INTEGER,
	FOREIGN KEY (IdPesquisa)
		REFERENCES Pesquisas(IdPesquisa) 
		ON DELETE RESTRICT,
	FOREIGN KEY (IdPosto)
		REFERENCES Posto(IdPosto) 
		ON DELETE RESTRICT
);
