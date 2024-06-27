#!/bin/bash -xe

PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"/usr/bin/env python3.7"}

if [ -n "${DB_USER}" -a -n "${DB_PASSWORD}" -a -n "${MSP_DOCKER_IP}" ]; then
    DB_PORT=${DB_PORT:-5432};

    # Discover per-client databases
    discover_tries=${DB_DISCOVER_TRIES:-2}
    discover_delay=${DB_DISCOVER_DELAY:-60}
    database_list=""
    while (( discover_tries-- )); do
        database_list=$(${PYTHON_EXECUTABLE} ../manage.py discover_postgres_clients_db)
        test -z "$database_list" || break
        sleep $discover_delay
    done

    # Migrate per-client databases
    if [ -n "${database_list}" ]; then
        IFS=':' read -r -a PG_ARRAY <<< "${database_list}"

        for ((i = 0; i < ${#PG_ARRAY[@]}; ++i)); do
            if [ $((${i}%2)) -eq 0 ]; then
                DB_HOST=${PG_ARRAY[$i]}
                DB_NAME=${PG_ARRAY[$i+1]}

                ./liquibase --url=jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME} \
                    --classpath=jdbcdrivers/postgresql-42.2.5.jar \
                    --username="${DB_USER}" \
                    --password="${DB_PASSWORD}" \
                    --changeLogFile=changelog.xml \
                    --logLevel=warning \
                    "${@}"
            fi
        done
    fi
else
	echo "You should specify all variables: DB_USER, DB_PASSWORD, MSP_DOCKER_IP"
	exit 1
fi
