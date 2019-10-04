#!/bin/bash

function warn() {
    echo "WARNING: This script is deprecated!"
    echo "Please use the Makefile instead"
}

function up() {
    warn()
    docker-compose up -d
}

function setup() {
    warn()
	mkdir -p web/db
    docker-compose up -d --build && docker-compose exec web ./manage.py createsuperuser
}

function stop() {
    warn()
    docker-compose stop
}

function clean() {
    docker-compose down
    docker-compose rm
}

function redo() {
    clean
    setup
}

function cleardb() {
	rm -rf web/db
}

function fresh() {
	clean
	cleardb
	setup
}

$@
