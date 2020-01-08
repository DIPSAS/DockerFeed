# DockerFeed example

## Setup
1. Install [python with pip](https://www.python.org/downloads/).
2. Install [DockerFeed](https://github.com/DIPSAS/DockerFeed) tool.
   - `pip install --upgrade DockerFeed`
     - `DockerFeed` is available as a command line tool with `dockerf`.
     - If the `dockerf` command fails, then use the module directly with `python -m DockerFeed -h`.

## Initialize Swarm
1. `dockerf init --source source/`
   - Initializes swarm and creates configs, secrets and networks given by the `swarm.management.yml` file. 
2. `dockerf deploy -r definitions/service_list.txt --source source/`
   - Deploys all stacks given by the `definitions/service_list.txt` definition. 
     - It is also possible to provide stacks to handle directly:
       - `dockerf deploy nginx>=1.0.0 --source source/`
   - All stacks are downloaded from the the `source` destination, which may be an uri to a [Jfrog](https://jfrog.com/) feed or a folder.
   - Point to another definition file in the definitions folder to deploy that swarm definition. 
3. `dockerf run -r definitions/batch_list.txt --source source/`
   - Runs all stacks as batch processes given by the `definitions/batch_list.txt` definition. 
   - All console logs from the batch processes are exported to log files in a `logs/` folder located in the current working directory.
4. `dockerf module deploy -r definitions/module_list.txt --source source/`
   - Deploys all modules given by the `definitions/module_list.txt` definition.

## Update Or Remove Stack
- Example:
  - `dockerf deploy nginx --source source/`
  - `dockerf remove nginx --source source/`
  - `dockerf module deploy nginx_module --source source/`
  - `dockerf module remove nginx_module --source source/`

## Prune Swarm
1. `dockerf prune`
   - Prune swarm by removing all stacks, and removing the configs and secrets defined in the `swarm.management.yml` file. 
   
## Push & Pull `docker-compose` Artifacts
1. `dockerf pull nginx --source source/`
   - Add `--output-folder` to specify a destination folder for pulling stack files with 'pull'. Default is ./output/.
2. `dockerf module pull nginx_module --source source/`
    - Add `--output-folder` to specify a destination folder for pulling module files with 'pull'. Default is ./output/.
3. `dockerf push stacks/docker-compose.my_stack.*.yml` 
   - It is possible to use wildcard signs (`*`) to find `docker-compose` artifacts to push to source feed.

## General Info
The `swarm.env` file is a list of default environment variables to expose with the swarm deployment.
