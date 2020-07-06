#! /bin/bash

# This script syncs out dirs from all your AWS instances to your local computer.

# Parameters.
#KEY_FILE="aws-key.pem"  # your private key file for AWS
KEY_FILE="/Users/jrieke/Desktop/johannes-aws-key.pem"  # your private key file for AWS
USER="ubuntu"  # the username on the AWS instance (depends on your AMI)
REMOTE_OUT_DIR="test-project/out/"  # the out dir of your remote instances
LOCAL_SYNC_DIR="aws-synced-out"  # the dir where to store all downloaded out dirs

echo "$(date)"
echo ""

# Get dns of all instances (remove instances that don't have a dns).
dns_list=$(aws ec2 describe-instances --query 'Reservations[].Instances[].PublicDnsName' | jq -r '.[] | select(length > 0)')
echo "Found the following instances on your AWS account:"
echo "$dns_list"

# Iterate through instances and sync out dir to local dir.
for dns in $dns_list; do
    echo ""
    echo "Getting output files from $dns:"
    echo "--------------------------------------------------------------------------------"
    rsync -a -e "ssh -i $KEY_FILE -o 'StrictHostKeyChecking=no'" $USER@$dns:$REMOTE_OUT_DIR $LOCAL_SYNC_DIR  # --stats
    echo "--------------------------------------------------------------------------------"
done

echo "================================================================================"
echo ""
