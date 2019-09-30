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

## Install
- `pip install --trusted-host vt-optimus-solr02 --no-cache DockerFeed -i http://vt-optimus-solr02:8181/simple/`
## Upgrade
- `pip install --trusted-host vt-optimus-solr02 --no-cache --upgrade DockerFeed -i http://vt-optimus-solr02:8181/simple/`
## Reinstall
- `pip install --trusted-host vt-optimus-solr02 --no-cache --force-reinstall --no-deps DockerFeed -i http://vt-optimus-solr02:8181/simple/`
## Uninstall
- `pip uninstall DockerFeed`

## Prerequisites
- Docker:
  - https://www.docker.com/get-docker

## Deploy/Remove Services
- Deploy all stacks with `dp`/`deploy`:
  - `DockerFeed dp`
- Remove all stacks with `rm`/`remove`:
  - `DockerFeed rm`
- List services with `ls`:
  - `DockerFeed ls`
- Add  with one or more modules to deploy/remove individually:
  - `DockerFeed dp -m infrastructure classicpump`
- Add `-t` with an environment to deploy (`dev`/`stable`):
  - `DockerFeed dp -t dev`
- Add `-e` with environment variables to expose during deployment/removal:
  - `DockerFeed dp -e key1=variable1 key2=variable2`
  - Alternatively, any present `.env` will be considered as a file with environment variables to expose.
- Add `-h` for help:
  - `DockerFeed -h`

### Dependencies:
  - `pip install twine`
  - `pip install wheel`
  - `pip install -r requirements.txt`

### Publish New Version.
1. Configure CHANGELOG.md with new version.
2. Package: `python setup.py bdist_wheel`
  - Note that `dist` and `build` folder should be removed before building the solution.
3. Publish: `twine upload --repository-url http://vt-optimus-solr02:8181/ dist/*`
   - username and password is not required (leave empty). 

### Run Unit Tests
- python -m unittest