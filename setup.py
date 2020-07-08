from setuptools import setup

setup(
    name="train-on-aws",
    version="0.1.0",
    description="Command line tools for machine learning on AWS",
    url="https://github.com/jrieke/train-on-aws",
    author="Johannes Rieke (@jrieke)",
    author_email="johannes.rieke@gmail.com",
    license="MIT",
    keywords="machine-learning aws training deep-learning command-line-tool server "
    "sync amazon-web-services ec2",
    py_modules=["train_on_aws"],
    python_requires=">=3",
    install_requires=["click", "boto3"],
    entry_points="""
        [console_scripts]
        train-on-aws-sync=sync:run
        train-on-aws=train_on_aws:run
    """,
)
