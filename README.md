# train-on-aws

🛠️ Command line tools for machine learning on AWS

train-on-aws is a set of scripts to run machine learning tasks on AWS. With one 
simple command, it spins up an AWS instance (from your own account), transfers your 
code & dataset, starts the training run, syncs all output files back to your computer, 
and terminates the instance after training has finished.


## Demo

![](docs/images/demo.gif)


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


## Known issues

If the `train-on-aws.sh` script shows a "Connection refused" error, try increasing the 
waiting time in the script. Sometimes, the instance doesn't allow a connection even 
though the AWS API reports it as ready, which may lead to this type of error. 


