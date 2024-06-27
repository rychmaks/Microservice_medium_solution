#!/bin/sh -xe

# Determine own absolute location,
# this is important because we may rely on relative paths
# and this script may be symlinked multiple times

called_script_name="${0}"
while test -L "${called_script_name}"; do
	cd "$(dirname "${called_script_name}")"
	called_script_name="$(readlink "$(basename "${called_script_name}")")"
done

app_root_dir="$(cd "$(dirname "${called_script_name}")" && pwd -LP)"
real_script_name="${app_root_dir}"/"$(basename "${called_script_name}")"

cd "${app_root_dir}"

# !!!!!!!!!!!! NO UPDATES ABOVE THIS LINE !!!!!!!!!!!!!!!!
# Refer https://confluence.softserveinc.com/display/CISDMSP/Action+from+DevOps-team+side+for+new+service+creation for information

###############################################################################
# Handle general purpose environment variables (should not be too much)
# PLEASE UPDATE AS APPROPRIATE!

APP_ENV="${APP_ENV:-prod}"; export APP_ENV
PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"/usr/bin/env python3.7"}; export PYTHON_EXECUTABLE

###############################################################################


###############################################################################
# Maintenance commands start here (maintenance stages as functions): BEGIN
# Configure these procedures as needed, do NOT modify their names.
###############################################################################

cmd_no_effect() {
	mcmd="${1}"
	echo "Maintenance command '${mcmd}' has no effect for this service"
	return 0
}

cmd_init_db() {
	cmd_purge_db
}

cmd_populate_db() {
	cmd_init_db
}

cmd_migrate_db() {
	cd "${app_root_dir}/migrations"
	PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE}" ./docker-liquibase-wrapper.sh update
	cd "${app_root_dir}"
}

cmd_rollback_db() {
	rollback_db_tag="${1}"
	if test -z "${rollback_db_tag}"; then
		echo "ERROR: Maintenance command 'rollback_db' requires db TAG"
		exit 1
	fi
	cd "${app_root_dir}/migrations"
	PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE}" ./docker-liquibase-wrapper.sh rollback "${rollback_db_tag}"
	cd "${app_root_dir}"
}

cmd_purge_db() {
	${PYTHON_EXECUTABLE} manage.py drop_all_keyspaces
}

cmd_build_dev() {
	make clean
	${PYTHON_EXECUTABLE} setup.py install_egg_info
	${PYTHON_EXECUTABLE} -m pip install -e '.[dev,test]'
}

cmd_start_dev() {
	test -z "${APP_PORT}" || set -- -p "${APP_PORT}" "${@}"
	test -z "${APP_HOST}" || set -- -h "${APP_HOST}" "${@}"
	PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE}" APP_ROOT_DIR="${app_root_dir}" supervisord -c "${app_root_dir}"/supervisord-dev.conf
}

cmd_start_prod() {
	cd "${app_root_dir}"
	supervisord -c supervisord-prod.conf
}

cmd_start_auto() {
	test "${APP_ENV}" = "prod" && start_mode=start_prod || start_mode=start_dev
	exec "${real_script_name}" "${start_mode}" "${@}"
}

###############################################################################
# Maintenance commands end here, no updates below this line: END
# !!!!!!!!!!!! NO CHANGES BELOW THIS LINE !!!!!!!!!!!
###############################################################################


# Determine requested stage and run it
if test "${#}" = "0"; then
	echo "ERROR: ${0} requires at least one argument as maintenance command"
	exit 1
fi
maintenance_stage="${1}"
shift 1;

case "${maintenance_stage}" in
	runserver|runservice)
		cmd_start_auto "${@}"
		;;
	build_dev|start_auto|start_dev|start_prod|init_db|populate_db|migrate_db|rollback_db|purge_db)
		"cmd_${maintenance_stage}" "${@}"
		;;
	*)
		echo "ERROR: maintenance stage '${maintenance_stage}' unknown"
		exit 1
		;;
esac
