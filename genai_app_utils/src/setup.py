from setuptools import setup, find_packages
import pathlib

# Read dependencies from requirements.txt and filter out empty lines and comments
with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name='genai_app_utils',
    version='0.1',
    description="Shared utilities and modules for GENAI summarization project",
    package_dir={'': 'genai_app_utils'},
    packages=find_packages(where='genai_app_utils'),
    python_requires=">=3.11",
    install_requires=requirements,
)
