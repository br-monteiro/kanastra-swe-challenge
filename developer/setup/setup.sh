#!/bin/bash

projects=(importer-api billing-worker send-mail-worker)

function build_env_file() {
    echo ">> Creating .env file for $1"
    cp $1/.env.example $1/.env
}

for project in ${projects[@]}; do
    echo ">> Setting up $project"
    build_env_file $project
done
