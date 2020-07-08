from datetime import datetime, timedelta
import boto3
import subprocess
import click
from timeloop import Timeloop


def sync_once(key_file, user, remote_out_dir, local_sync_dir):
    """Perform one sync from output dirs of all instances to local dir."""
    print(datetime.now())
    print()

    ec2 = boto3.resource("ec2")

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


@click.command()
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
def run(key_file, user, remote_out_dir, local_sync_dir, every):

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


if __name__ == "__main__":
    run()
