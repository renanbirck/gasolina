.PHONY: run-local build deploy 

CONTAINER_NAME := gasolina-api
CONTAINER_DOCKERFILE := api/Dockerfile

# Configurações para o host remoto 
REMOTE_LOGIN := renan
REMOTE_MACHINE := renanbirck.rocks
REMOTE_TARGET_PORT := 2222
SYSTEMD_SERVICE_NAME := gasolina

# Onde estão os dados da aplicação no host local
DATA_DIRECTORY := /home/renan/Sources/gasolina/data

run-local:
	@echo "Rodando o servidor local..."
	cd api && fastapi run  

build:
	@echo "Construíndo o container..."
	podman build -t $(CONTAINER_NAME) -f $(CONTAINER_DOCKERFILE) .
	@cowsay "Container construído!"

run-container-local:
	podman stop $(CONTAINER_NAME) || true
	podman run -dt -v $(DATA_DIRECTORY):/data:Z -p 8000:8000 --name $(CONTAINER_NAME) --replace $(CONTAINER_NAME)
	@echo "Acesse http://127.0.0.1:8000 no navegador."

deploy: build 
	podman system connection add BLOG $(REMOTE_LOGIN)@$(REMOTE_MACHINE):$(TARGET_PORT)/usr/lib/systemd/user/podman.socket
	podman image scp $(CONTAINER_NAME):latest BLOG:: 
	@cowsay "Terminei a cópia!"

restart-service: 
	ssh -p $(REMOTE_TARGET_PORT) $(REMOTE_LOGIN)@$(REMOTE_MACHINE) 'systemctl --user restart $(SYSTEMD_SERVICE_NAME)'
	cowsay "Serviço reiniciado!"