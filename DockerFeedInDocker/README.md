# DockerFeed In Docker

Push and verify docker-compose charts with DockerFeed in docker!

The [dipsas/dockerfeed](https://hub.docker.com/repository/docker/dipsas/dockerfeed) image includes [DockerFeed](https://github.com/DIPSAS/DockerFeed) binaries, and makes it possible to push and verify docker-compose charts inside of a container.

Additionally, it is possible to push regular [Helm](https://helm.sh/) charts to a helm repository.

## Example
### Push docker-compose chart:
```
docker run -it -v C:/MyLocalDirectoryTo/charts/:/charts -w /charts dipsas/dockerfeed push docker-compose.stack-name.1.0.0.yml --source https://artifacts/docker-compose-feed
```

### Push helm chart:
```
docker run -it -v C:/MyLocalDirectoryTo/charts/:/charts -w /charts dipsas/dockerfeed push my-helm-chart-1.0.0.tgz --source https://artifacts/helm-feed
```

## Development
- Requirements:
  - python & pip
    - https://www.python.org/
  - pip install DockerBuildManagement
    - https://github.com/DIPSAS/DockerBuildManagement

- Build & Publish
```
dbm -build -publish
```