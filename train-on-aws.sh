#! /bin/bash

# This script can be used to run a long-running script on AWS (e.g. for ML training). 
# It launches the instance, uploads a project dir (excluding subdirs .git and out), 
# executes a command via ssh (e.g. a training script), and terminates the instance 
# after training has finished.

# Note that the AWS CLI has to be installed and connected to your AWS account.

# Parameters.
#KEY_FILE="aws-key.pem"  # your private key file for AWS
KEY_FILE="/Users/jrieke/Desktop/johannes-aws-key.pem"  # your private key file for AWS
LAUNCH_TEMPLATE_ID="lt-01ca80d3c2a68e893"  # the launch template from AWS that should be used to create the instance
USER="ubuntu"  # the username on the AWS instance (depends on your AMI)
DIR="test-project"  # the path to your project dir
COMMAND="/home/ubuntu/anaconda3/bin/python train.py"  # the command to execute on the remote machine (note that PATH might not be available)


# Start instance from launch template.
id=$(aws ec2 run-instances --launch-template LaunchTemplateId=$LAUNCH_TEMPLATE_ID --query 'Instances[].InstanceId' | jq -r .[0])
echo "Starting instance with ID: $id"
echo "You can terminate it at any time via: aws ec2 terminate-instances --instance-ids $id"

# Wait for instance to run, get public DNS. 
aws ec2 wait instance-running --instance-ids $id
dns=$(aws ec2 describe-instances --instance-ids $id --query 'Reservations[].Instances[].PublicDnsName' | jq -r .[0])
echo "Instance is running at: $dns"
echo "You can connect manually via: ssh -i $KEY_FILE $USER@$dns"

# Wait a bit; otherwise, connection is refused sometimes.
echo "Waiting..."
sleep 30
echo ""

echo "Sending repo via rsync ($USER@$dns)"
echo "================================================================================"
rsync -av -e "ssh -i $KEY_FILE -o 'StrictHostKeyChecking=no'" --exclude=".git" --exclude="out" $DIR $USER@$dns:~
#scp -r -i johannes-aws-key.pem -o "StrictHostKeyChecking=no" $DIR $USER@$dns:~
echo "================================================================================"
echo "Done!"
echo ""

# Connect via SSH.
echo "Connecting via SSH ($USER@$dns)"
echo "================================================================================"
ssh -t -i $KEY_FILE -o "StrictHostKeyChecking=no" $USER@$dns "cd $DIR && screen sh -c '$COMMAND; exec bash'"
echo "================================================================================"
echo "Done!"
echo "Terminate with: aws ec2 terminate-instances --instance-ids $id"
echo ""

# Ask if script should terminate instance.
read -p "Terminate this instance now? (y/n)" -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    state=$(aws ec2 terminate-instances --instance-ids $id --query 'TerminatingInstances[].CurrentState.Name' | jq -r .[0])
    echo "New instance state: $state"
fi
