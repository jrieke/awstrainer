from setuptools import setup

setup(
    name="awstrainer",
    version="0.1.0",
    description="Command line tools for machine learning on AWS",
    url="https://github.com/jrieke/train-on-aws",
    author="Johannes Rieke (@jrieke)",
    author_email="johannes.rieke@gmail.com",
    license="MIT",
    keywords="machine-learning aws training deep-learning command-line-tool server "
    "sync amazon-web-services ec2",
    py_modules=["awstrainer.cli"],
    python_requires=">=3",
    install_requires=["click", "boto3", "timeloop"],
    entry_points="""
        [console_scripts]
        awstrainer=awstrainer.cli:awstrainer
    """,
)
