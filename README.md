# train-on-aws

These scripts enable you to launch AWS instances, run commands on them, and sync the 
output back to your local computer. This is useful for long-running processes such as 
training machine learning models.

xw
## Requirements

1. [Install](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) 
the AWS CLI and connect your AWS account via `aws configure` 
([more info](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)). 

2. [Install](https://stedolan.github.io/jq/download/) jq, e.g. on Ubuntu via `sudo apt-get install jq` and on OSX via `brew install jq`.


## Usage

Make sure to set the parameters in the scripts before you run them! (no support for 
command-line params right now)

    bash train-on-aws.sh

This launches an AWS instance (from a launch template), uploads a project dir 
(excluding subdirs .git and out), executes a command via ssh (e.g. a training script), 
and terminates the instance after training has finished.

    bash sync-out-dirs.sh

This pulls output files from all running AWS instances and syncs them to a local dir. 
It's really nice to put this script into crontab, so that it runs regularly. 
E.g., to sync output files every 15 minutes, run 

    crontab -e
    
and add this line to the bottom of the opened file:

    */15 * * * * bash sync-out-dirs.sh


