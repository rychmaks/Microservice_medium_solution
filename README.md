test service
======================

Checkout
---
    git clone <GIT_SERVER_URL>/<PROJECT_SPACE>/rfadjustments.git

    git submodule update --init

Installation
---

    # For production environment:
    # Create virtualenv
    export VENV_DIR=venv
    python3.7 -m venv "${VENV_DIR}"
    "${VENV_DIR}"/bin/python3.7 -m ensurepip --upgrade
    "${VENV_DIR}"/bin/python3.7 -m pip install -e . --extra-index-url=http://192.168.240.173:50081/repository/pypi/simple --trusted-host 192.168.240.173

    # If in development environment:
    make setup

Environment variables
---
These environment variables will be defined in any runtime environment and could be used in program code:

    MSP_DOCKER_IP=<IP.ADD.RE.SS>  # IP address where SDA listens on port 5000, no default value
    DB_USER=<string>              # DB user name, no default value
    DB_PASSWORD=<string>          # DB password, no default value
    DB_PORT=<int>                 # DB listen port, default should be set to 5432 in program code
    DEFAULT_DB=<string>           # Name of DB to use for connection to postgresql engine, no defalut value, shoul NEVER be modified (use for login only)

DB schema changes
---
* To update database schema please create relevant xml changesets in `migrations/changesets` directory.
* To apply changesets run `MSP_DOCKER_IP=<IP.ADD.RE.SS> DB_USER=<user> DB_PASSWORD=<password> DB_PORT=<5432> DEFAULT_DB=<db_name> ./maintenancectl.sh migrate_db`.

Running
---
    # Run service locally
    make run-dev

    # for checking just send GET request to the next URL.

    curl -Lv localhost:5000/rfadjustments/v1/smoke/

    # expected result: status code 200.


Create docker container
---
* Make sure your `docker-entrypoint.sh` is up-to-date.
* To create docker image run `docker build --pull=false --tag=apiservice/rfadjustments:latest .` (Note trailing dot)

Run docker container
---
    docker run -d -P -e MSP_DOCKER_IP=<IP.ADD.RE.SS> -e DB_USER=<user> -e DB_PASSWORD=<password> -e DB_PORT=<5432> -e DEFAULT_DB=<db_name> apiservice/rfadjustments:latest

Run tests
---
    # Run flake8:
    make flake

    # Run tests:
    make test

    # Generate coverage report:
    make coverage

Maintenancectl.sh operations
---
`maintenancectl.sh` is a shell (/bin/sh) script used by deployment scenarios during service delivery to run different maintenance operations in uniform fashion.

Make sure your maintenancectl.sh is up-to-date. Refer [link](https://confluence.softserveinc.com/display/CISDMSP/Action+from+DevOps-team+side+for+new+service+creation) for more information.


Pre commit hook
---
You should copy `pre-commit` to `.git/hooks/` for running this hook.


Dependencies version management and adding new dependencies
---

###How dependencies management works?
`setup.py` read `requirements/*requirements.txt` files as its dependencies. All `requirements/*requirements.txt` files have all versions pinned.

###How versions management works?
`requirements/*requirements.txt` files are generated from `requirements/*requirements.in` files by [pip-tools](https://pypi.org/project/pip-tools/).
`pip-tools` detects conflicts and discover the whole dependency tree and write it down into `requirements/*requirements.txt` files.

###How to add a new dependency?
To add a new dependency edit `requirements/*requirements.in` and run then `make compile-versions`. It will add a specific version to `requirements/*requirements.txt` file.
Changes in both `requirements/*requirements.in` and `requirements/*requirements.txt` files to VCS.

###How to upgrade a dependency?
Check `Updating requirements` in [pip-tools](https://pypi.org/project/pip-tools/). Follow code is an example of upgrading `sanic` version


    pip-compile --output-file requirements/requirements.txt requirements/requirements.in -P sanic

Add `requirements/requirements.txt` to VCS.

###How to manage submodules dependencies
Each submodule which requires additional package should contain requirements.in file with listed dependencies. All requirements.in files from all submodules should be added in `setup` procedure of "head" package to `pip-compile` with it dependencies.


    pip-compile --output-file requirements/requirements.txt requirements/requirements.in rfcommon_api/requirements.in

and


    pip-compile --output-file requirements/test_requirements.txt requirements/requirements.in requirements/test_requirements.in rfcommon_api/requirements.in

It will generate `requirements/requirements.txt` and `requirements/test_requirements.txt` files with complete list of dependencies.
