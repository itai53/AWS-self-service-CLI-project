from setuptools import setup

setup(
    name="awscli",
    version="1.0",
    py_modules=["deploy"],
    install_requires=["boto3"],
    entry_points={
        "console_scripts": ["awscli=deploy:main"]
    },
)