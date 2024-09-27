from setuptools import setup, find_packages
import pathlib

import setuptools

# Read dependencies from requirements.txt and filter out empty lines and comments
with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]


setup(
    name='paper-manager',
    version='0.1',
    description="Shared utilities and modules for GENAI summarization project",
    package_dir={'': '.'},
    packages=find_packages(where='.'),
    python_requires=">=3.11",
    entry_points={
        'console_scripts': [
            'paper_manager=paper_manager.main:main',
        ],
    },
    install_requires=requirements,
)
