#!/bin/bash

function up() {
    docker-compose up -d
}

function setup() {
	mkdir -p web/db
    docker-compose up -d --build && docker-compose exec web ./manage.py createsuperuser
}

function stop() {
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

$@
