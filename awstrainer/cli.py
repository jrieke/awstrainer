import boto3
import time
import subprocess
import distutils.util
import click
from datetime import datetime, timedelta
from timeloop import Timeloop
import os.path


def check_key_file_exists(key_file):
    if not os.path.isfile(key_file):
        raise IOError(f"Key file '{key_file}' not found, use --key_file to set it")


def check_project_dir_exists(project_dir):
    if not os.path.isdir(project_dir):
        raise IOError(
            f"Project dir '{project_dir}' not found, use --project_dir to set it"
        )


ec2 = boto3.resource("ec2")


@click.group()
def awstrainer():
    pass


# LAUNCH_TEMPLATE_ID = "lt-01ca80d3c2a68e893"  # the launch template from AWS that should be used to create the instance
# COMMAND = "/home/ubuntu/anaconda3/bin/python train.py"  # the command to execute on the remote machine (note that PATH might not be available)


@awstrainer.command(
    help="Launches an AWS instance, uploads your project dir, executes a command "
    "(e.g. training script), and terminates the instance afterwards. \n\n"
    'Example: python train-on-aws.py --launch_template_id <template> "/home/ubuntu/anaconda3/bin/python train.py"'
)
@click.argument("command")
@click.option("--launch_template_id", help="AWS launch template for the instance.")
@click.option(
    "--user",
    default="ubuntu",
    help="Username on the AWS instance (depends on AMI, default: ubuntu)",
)
@click.option(
    "--key_file",
    default="aws-key.pem",
    help="Your private key file for AWS (default: aws-key.pem)",
)
@click.option("--project_dir", default=".", help="Path to project dir (default: .)")
@click.option(
    "--wait_time",
    default=20,
    help="Seconds to wait after instance startup (this prevents connection refused errors, default: 20)",
)
def run(command, launch_template_id, user, key_file, project_dir, wait_time):
    check_key_file_exists(key_file)
    check_project_dir_exists(project_dir)

    # Create instance.
    (instance,) = ec2.create_instances(
        MinCount=1, MaxCount=1, LaunchTemplate={"LaunchTemplateId": launch_template_id}
    )
    print("Starting instance with ID:", instance.id)
    print(
        f"Terminate at any time with: aws ec2 terminate-instances "
        f"--instance-ids {instance.id}"
    )
    print()

    # Get public DNS.
    instance.wait_until_running()
    instance.load()  # re-load attributes to get the dns name
    print("Instance is running at:", instance.public_dns_name)
    print(f"Connect manually with: ssh -i {key_file} {user}@{instance.public_dns_name}")
    print()

    # Wait a bit (otherwise instance might refuse SSH connection).
    print("Waiting for instance...")
    time.sleep(wait_time)
    print()

    # Send repo via rsync.
    # TODO: Find a python-native alternative to rsync to 1) make it more robust and 2)
    #   make it work on Windows.
    # TODO: Maybe wrap in extra dir, because if we are using project_dir=., the file
    #   contents end up right in the home dir of the instance
    print("Sending project dir via rsync (ignoring subdirs .git and out)")
    print("=" * 80)
    # rsync -av -e "ssh -i $KEY_FILE -o 'StrictHostKeyChecking=no'" --exclude=".git" --exclude="out" $DIR $USER@$dns:~
    subprocess.call(
        [
            "rsync",
            "-av",
            "-e",
            f"ssh -i {key_file} -o 'StrictHostKeyChecking=no'",
            "--exclude=.git",
            "--exclude=out",
            project_dir,
            f"{user}@{instance.public_dns_name}:~",
        ]
    )
    print("=" * 80)
    print("Done!")
    print()

    # Connect via SSH and start training.
    print("Connecting via SSH")
    print("=" * 80)
    # TODO: Make native Python implementation, e.g. with paramiko (see notebook).
    # TODO: Maybe delete bash call at the end or make it optional at least.
    # TODO: Make path available for the command.
    # ssh -t -i $KEY_FILE -o "StrictHostKeyChecking=no" $USER@$dns "cd $DIR && screen sh -c '$COMMAND; exec bash'"
    subprocess.call(
        [
            "ssh",
            "-t",
            "-i",
            key_file,
            "-o",
            "StrictHostKeyChecking=no",
            f"{user}@{instance.public_dns_name}",
            f"cd {project_dir} && screen sh -c '{command}; exec bash'",
        ]
    )
    print("=" * 80)
    print("Done!")
    print()

    # Terminate instance.
    answer = input("Terminate this instance now? (y/N) ")
    if distutils.util.strtobool(answer.lower()):
        result = instance.terminate()
        new_state = result["TerminatingInstances"][0]["CurrentState"]["Name"]
        print("Instance is being terminated, new state:", new_state)
    else:
        print("Instance is still running")
        print(
            f"Terminate at any time with: aws ec2 terminate-instances "
            f"--instance-ids {instance.id}"
        )


def sync_once(key_file, user, remote_out_dir, local_sync_dir):
    """Perform one sync from output dirs of all instances to local dir."""
    check_key_file_exists(key_file)

    print(datetime.now())
    print()

    # Get running instances.
    filters = [{"Name": "instance-state-name", "Values": ["running"]}]
    instances = ec2.instances.filter(Filters=filters)
    print("Found the following instances on your AWS account:")
    for instance in instances:
        print(instance.public_dns_name)

    # Iterate through instances and sync out dir to local dir.
    for instance in instances:
        print()
        print("Getting out dir from", instance.public_dns_name)
        print("-" * 80)
        subprocess.call(
            [
                "rsync",
                "-av",
                "-e",
                f"ssh -i {key_file} -o 'StrictHostKeyChecking=no'",
                f"{user}@{instance.public_dns_name}:{remote_out_dir}",
                local_sync_dir,
            ]
        )
        print("-" * 80)
    print("=" * 80)
    print()


@awstrainer.command(
    help="Syncs output dirs from all AWS instances to your local computer"
)
@click.option(
    "--user",
    default="ubuntu",
    help="Username on the AWS instance (depends on AMI, default: ubuntu)",
)
@click.option(
    "--key_file",
    default="aws-key.pem",
    help="Your private key file for AWS (default: aws-key.pem)",
)
@click.option(
    "--remote_out_dir",
    default="out/",
    help="Output dir on the remote machine (default: out/)",
)
@click.option(
    "--local_sync_dir",
    default="aws-synced-out",
    help="Dir on the local machine to sync all out dirs to (default: aws-synced-out)",
)
@click.option(
    "--every",
    default=0,
    help="Seconds to wait between syncs (default: sync only once)",
)
def sync(key_file, user, remote_out_dir, local_sync_dir, every):

    if every == 0:
        # Sync only one time.
        sync_once(key_file, user, remote_out_dir, local_sync_dir)
    else:
        # Set up timer to sync regularly.
        tl = Timeloop()
        tl._add_job(
            sync_once,
            timedelta(seconds=every),
            key_file,
            user,
            remote_out_dir,
            local_sync_dir,
        )
        tl.start(block=True)

