# Docker Feed

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