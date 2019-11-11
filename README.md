# Docker Feed

[![PyPI version](https://badge.fury.io/py/DockerFeed.svg)](https://badge.fury.io/py/DockerFeed)
[![Build Status](https://travis-ci.com/DIPSAS/DockerFeed.svg?branch=master)](https://travis-ci.com/DIPSAS/DockerFeed)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

Docker Feed is a simple and convenient tool for handling deployment of docker compose files to a Swarm environment.
By convention, it locates all stacks to deploy on a [JFrog](https://jfrog.com/) feed with every stack following a docker-compose filename pattern of `docker-compose.stack-name.1.0.0.yml`, thus this filename convention:
- `docker-compose.<STACK_NAME>.<VERSION>.yml`
- Note! The stack name can only contain alphabetic letters and `-`/`_` signs.

Additionally, the Swarm probably needs to initialize some infrastructure before any stacks are deployed. This is handled by defining a `swarm.management.yml` file with details about which `configs`, `secrets`, `volumes` or `networks` to create. By convention, the `DockerFeed` tool will automatically detect the `swarm.management.yml` file if it exists in the current folder.
Please have a look at the [SwarmManagement](https://github.com/DIPSAS/SwarmManagement) project to get more details, but following is an example on how the `swarm.management.yml` content could look like:

```yaml
networks:
    <network_name>: 
        encrypted: true
configs:
    <config_name>: <config_file>
secrets:
    <secret_name>: <secret_file>
volumes:
    <volume_name>:
        driver: local
env_files:
    - <environment_file>
```

## Install Or Upgrade
- pip install --upgrade DockerFeed

## Prerequisites
- python3x
- Docker:
  - https://www.docker.com/get-docker

## Usage
The Docker Feed tool is available as the command line tool `dockerf`.
Handle the docker feed by adding any of the following commands with zero or more stacks to handle.
- `init` - Initialize Swarm.
- `deploy` - Deploy stacks to Swarm.
    - Adding no specific stacks to deploy will result in deploying all stacks.
    - Example: `dockerf deploy first-stack second-stack>=1.0.0 third-stack==1.2.3`
- `rm`/`remove` - Remove stacks from Swarm.
    - Adding no specific stacks to remove will result in removing all stacks.
    - Example: `dockerf remove first-stack second-stack`
- `ls/list` - List stacks on feed.
    - Hint, add search criterias following `ls`, such as:
    - `dockerf ls first-stack second-stack>=1.0.0`
- `prune` - Remove all stacks.
- `pull` - Pull stacks from feed.
- `push` - Push docker-compose files to feed.
    - Example: `dockerf push docker-compose.first-stack.yml docker-compose.second-stack.yml`
- `run` - Run stacks as batch processes.
    - Logs from each process is stored in a `logs` folder in the working directory. 
- `verify` - Verify that the stacks are properly configured.
    - Following requirements are possible to validate:
        1. Add `--verify-image-digests` to verify that All images are tagged with an immutable [digest](https://success.docker.com/article/images-tagging-vs-digests).
        2. Add `--verify-images` to verify that all images are labeled with following labels:
            - org.opencontainers.image.created
            - org.opencontainers.image.authors
            - org.opencontainers.image.revision
            - org.opencontainers.image.version
            - org.opencontainers.image.documentation
            - org.opencontainers.image.title
        3. Additional validation checks are also possible to activate:
            - `--verify-no-configs`
            - `--verify-no-secrets`
            - `--verify-no-volumes`
            - `--verify-no-ports`
- Optional arguments:
  - `-s/--source` to specify feed source. Either uri to jfrog feed, or a local folder with stack files. Default is `https://artifacts/delivery-dev`.
  - `-u/--user` to specify user credentials for jfrog as `user:password`.
  - `-t/--token` to specify a token for jfrog.
  - `--verify-uri` to verify the jfrog uri certificate.
  - `-e/--env` with environment variables to expose as `envKey=envValue`:
    - `dockerf deploy -e key1=variable1 key2=variable2`
    - Alternatively, any present `.env` will be considered as a file with environment variables to expose.
  - `-r/--read` with a list of files containing stacks to handle, thus each line in the file is the name of a stack to handle.
    - `dockerf deploy -r stackList.txt stackList2.txt`
  - `--output-folder` to specify a destination folder for pulling stack files with 'pull'. Default is `./stacks/`.
  - `--ignored-stacks` followed by a list of stacks to ignore.
  - `--logs-folder` to specify folder for storing log files when executing batch processes with 'run'. Default is './logs'.
  - `--no-logs` to drop storing log files when executing batch processes with 'run'.
  - `--verify-stacks-on-deploy` to deploy only valid stacks.
  - `--verify-image-digests` to validate that image digests are used.
  - `--verify-images` to validate required labels on images.
  - `--verify-no-configs` to validate that no Swarm configs are used in stack.
  - `--verify-no-secrets` to validate that no Swarm secrets are used in stack.
  - `--verify-no-volumes` to validate that no Swarm volumes are used in stack.
  - `--verify-no-ports` to validate that no ports are exposed in stack.
  - `-i/--infrastructure` to specify the path to swarm.management.yml files for creating the Swarm infrastructure.
  - `-c/--cache` to specify the cache folder to use for local cache storage of stack files. 
  - `-h/--help` for help:
    - `dockerf -h`

### Dependencies:
  - `pip install twine`
  - `pip install wheel`
  - `pip install -r requirements.txt`

### Publish New Version.
1. Configure [CHANGELOG.md](./CHANGELOG.md) with new version.
2. Package: `python setup.py bdist_wheel`
3. Publish: `twine upload dist/*`

### Run Unit Tests
- python -m unittest