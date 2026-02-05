#!/bin/bash
export PGPASSWORD=password

# Create User (ignore error if exists)
psql -h localhost -U postgres -c "DO \$\$ BEGIN CREATE ROLE attendance WITH LOGIN PASSWORD 'password'; EXCEPTION WHEN DUPLICATE_OBJECT THEN RAISE NOTICE 'Role attendance already exists'; END \$\$;"

# Create Database (ignore error if exists)
if psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw attendance_db; then
    echo "Database attendance_db already exists"
else
    psql -h localhost -U postgres -c "CREATE DATABASE attendance_db OWNER attendance;"
fi

# Create Extension (must be superuser)
psql -h localhost -U postgres -d attendance_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run Init SQL
psql -h localhost -U postgres -d attendance_db -f docker/init.sql
