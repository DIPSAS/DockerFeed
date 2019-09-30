# Docker Feed

Docker Feed is a simple and convenient tool for handling deployment of docker compose files to a Swarm environment.
By convention, it locates all stacks to deploy on a [JFrog](https://jfrog.com/) feed with every stack following a docker-compose filename pattern of `docker-compose.my-stack-name.yml`.

Additionally, the Swarm probably needs to initialize some network infrastructure before any stacks are deployed. This is also handled by a simple convention of treating a set of `infrastructure` stacks as yaml files with network details. By default the stack named `infrastructure`, thus the filename `docker-compose.infrastructure.yml`, will be considered as infrastructure deployment.

The content of `docker-compose.infrastructure.yml` should contain network details for the Swarm which will be created on `init`, as such:

```yaml
networks:
  swarm_encrypted_network:
    encrypted: true
  swarm_unencrypted_network:
    encrypted: false
```

## Installation

[![PyPI version](https://badge.fury.io/py/DockerFeed.svg)](https://badge.fury.io/py/DockerFeed)
[![Build Status](https://travis-ci.com/DIPSAS/DockerFeed.svg?branch=master)](https://travis-ci.com/DIPSAS/DockerFeed)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

## Install Or Upgrade
- pip install --upgrade DockerFeed

## Prerequisites
- python3x
- Docker:
  - https://www.docker.com/get-docker

## Usage
The Docker Feed tool is available as a command line tool `dockerf`.
- Initialize swarm with `init`:
  - `dockerf init`
- Deploy stacks with `deploy`:
  - `dockerf deploy`
- Remove stacks with `rm`/`remove`:
  - `dockerf rm`
- List stacks with `ls`:
  - `dockerf ls`
    - Hint, add search criterias following `ls`, such as:
    - `dockerf ls first-stack second-stack`
- Add specific stacks to deploy/remove:
  - `dockerf deploy first-stack second-stack`
- Optional arguments:
  - `-u/--user` to specify user credentials for jfrog as `user:password`.
  - `-t/--token` to specify a token for jfrog.
  - `-f/--feed` to specify the jfrog feed. Default is `docker-delivery`.
  - `-s/--storage` to specify a storage folder to use for local storage of compose files.
  - `-e/--env` with environment variables to expose as `envKey=envValue`:
    - `dockerf dp -e key1=variable1 key2=variable2`
    - Alternatively, any present `.env` will be considered as a file with environment variables to expose.
  - `--uri` to specify the jfrog uri. Default is `https://artifacts/`.
  - `--offline` to work offline.
  - `--remove-files` to remove matching docker-compose file from local storage when removing stacks from the Swarm.
  - `--verify-uri` to verify the jfrog uri certificate.
  - `-i/--infrastructure` to specify which infrastructure stacks to use. Default is `infrastructure`.
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