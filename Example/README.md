# DockerFeed example

## Setup
1. Install [python with pip](https://www.python.org/downloads/).
2. Install [DockerFeed](https://github.com/DIPSAS/DockerFeed) tool.
   - `pip install --upgrade DockerFeed`
     - `DockerFeed` is available as a command line tool with `dockerf`.

## Initialize Swarm
1. `python -m DockerFeed init --source source/`
   - Initializes swarm and creates configs, secrets and networks given by the `swarm.management.yml` file. 
2. `python -m DockerFeed deploy -r definitions/deploy.txt --source source/`
   - Deploys all stacks given by the `definitions/deploy.txt` definition. 
   - All stacks are downloaded from the the `source` destination, which may be an uri to a [Jfrog](https://jfrog.com/) feed or a folder.
   - Point to another definition file in the definitions folder to deploy that swarm definition. 
3. `python -m DockerFeed run -r definitions/run.txt --source source/`
   - Runs all stacks as batch processes given by the `definitions/run.txt` definition. 
   - All console logs from the batch processes are exported to log files in a `logs/` folder located in the current working directory.

## Update Or Remove Stack
- Example:
  - `python -m DockerFeed deploy nginx --source source/`
  - `python -m DockerFeed remove nginx --source source/`

## Prune Swarm
1. `python -m DockerFeed prune`
   - Prune swarm by removing all stacks, and removing the configs and secrets defined in the `swarm.management.yml` file. 

## General Info
The `swarm.env` file is a list of default environment variables to expose with the swarm deployment.
