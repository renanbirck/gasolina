#!/usr/bin/env bash 
####
#
# Script que faz o deploy de forma automatizada, 
# copiando o container e depois reiniciando ele. 
#
####

API_TARGET=gasolina-api 
API_DOCKERFILE=api/Dockerfile 

REMOTE_LOGIN=renan
REMOTE_MACHINE=renanbirck.rocks

REMOTE_MACHINE_DATAPATH=/home/renan/gasolina 

## Adicionar o remoto 
podman system connection add BLOG $REMOTE_LOGIN@$REMOTE_MACHINE:22/usr/lib/systemd/user/podman.socket

## Reconstruir a imagem para fazermos o deploy. 
podman build -t $API_TARGET -f $API_DOCKERFILE .

## e fazer o deploy.
podman image scp gasolina-api:latest BLOG::
cowsay Terminei a Cópia

## Na máquina remota, reiniciar o container que acabamos de copiar.

ssh REMOTE_LOGIN@REMOTE_MACHINE "podman run -dt -v $REMOTE_MACHINE_DATAPATH:/data:Z --name $API_TARGET -p 8000:8000 --replace $API_TARGET"

echo FIM.
