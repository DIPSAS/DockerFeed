# Changelog DockerFeed
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

<!-- the topmost header version must be set manually in the VERSION file -->
## [1.3.11] - 2020-03-16
- Fixed pypi readme

## [1.3.10] - 2020-02-28
- Changed warning to error when detecting no files to push.

## [1.3.9] - 2020-02-27
- Updated dependencies.

## [1.3.8] - 2020-02-27
- Updated dependencies.

## [1.3.7] - 2020-02-24
- Updated dependencies.

## [1.3.6] - 2020-02-18
- Added argument options to set artifact identifiers.

## [1.3.5] - 2020-01-10
- Updated dependencies.

## [1.3.4] - 2020-01-09
- Updated dependencies with bugfix.

## [1.3.3] - 2020-01-08
- Updated dependencies with bugfix.

## [1.3.2] - 2019-11-20
- Added with registry auth argument to stack deployment.

## [1.3.1] - 2019-11-18
- Fixed minor bug with skipping deploy when run section fails when deploying a module.

## [1.3.0] - 2019-11-15
- Implemented the module concept.

## [1.2.5] - 2019-11-13
- Minor bug with setting output folder with pull feature.

## [1.2.4] - 2019-11-13
- Improved pull information.

## [1.2.3] - 2019-11-13
- Fixed bug with invalid stack files not following the filename convention.

## [1.2.2] - 2019-11-12
- Fixed bug with source identification.

## [1.2.1] - 2019-11-12
- Improved push feature with file search pattern.

## [1.2.0] - 2019-11-11
- Major restructure and moved implementation to using `source` instead of uri and feed.

## [1.1.1] - 2019-11-01
- Fixed issue with defining env variables file from swarm.management.yml.

## [1.1.0] - 2019-11-01
- Removed docker-compose.infrastructure.yml feature, with focus on using swarm.management.yml.

## [1.0.17] - 2019-11-01
- Added feature to provide a swarm.management.yml file with swarm infrastructure details.

## [1.0.16] - 2019-11-01
- Added feature to provide files with list of stacks to handle.

## [1.0.15] - 2019-10-31
- Moved cache folder to user's own home folder.

## [1.0.14] - 2019-10-18
- Fixed probable bug with output folder argument input.

## [1.0.13] - 2019-10-14
- Added logs output to file for batch processes.

## [1.0.12] - 2019-10-14
- Implemented 'run' feature for running stacks as batch processes.

## [1.0.11] - 2019-10-11
- Added missing main script for module.

## [1.0.10] - 2019-10-10
- Upgraded docker build system due to bug with docker image label extraction.

## [1.0.9] - 2019-10-10
- Added no ports validation check and feature to ignore stacks to handle.

## [1.0.8] - 2019-10-10
- Added no configs/secrets or volumes validation check.

## [1.0.7] - 2019-10-09
- Updated docker build system due to yaml merge bug with lists.

## [1.0.6] - 2019-10-09
- Updated docker build system due to yaml merge bug.

## [1.0.5] - 2019-10-09
- Updated docker build system due to bug.

## [1.0.4] - 2019-10-09
- Updated docker build system.

## [1.0.3] - 2019-10-04
- Updated docker build system.

## [1.0.2] - 2019-10-03
- Added verification action.

## [1.0.1] - 2019-09-30
- Changed project description.

## [1.0.0] - 2019-09-30
- Initial release
