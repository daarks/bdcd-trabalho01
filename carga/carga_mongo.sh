#!/usr/bin/env bash
# Item (d) do enunciado: carga das duas bases no MongoDB local (mongod em localhost:27017).
# Rodar da raiz do projeto: ./carga/carga_mongo.sh
set -euo pipefail

# --drop garante que rodar o script duas vezes nao duplique documentos
mongoimport --db dengue_br --collection alertas --drop --jsonArray --file dados/alertas.json
mongoimport --db ibge --collection municipios --drop --jsonArray --file dados/municipios.json
mongoimport --db ibge --collection populacao --drop --jsonArray --file dados/populacao.json
