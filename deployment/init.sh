#!/bin/bash

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Restarting Postgresql${NC}"

if [[ $(hostname) == "master" ]]; then
	service postgresql restart
	echo -e "${GREEN}Creating Sample User and Data${NC}"
	su - postgres -c bash << EOF
	psql -c "create database test"
	psql -c "create role testuser with login superuser password 'test-pass'"
	psql -d test -c "CREATE TABLE Persons (ID int NOT NULL, LastName varchar(255) NOT NULL, FirstName varchar(255), Age int, PRIMARY KEY (ID))"
	psql -d test -c "insert into persons (ID, LastName, FirstName, Age) values (1, 'Doe', 'John', 99)"
EOF
else
	pg_lsclusters
	echo "Don't forget to run postgresql manually!"
	echo "Run pg_ctlcluster 12 main stop && pg_ctlcluster 12 main restart"
fi

echo -e "${GREEN}Setup Completed!${NC}"
