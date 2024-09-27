from setuptools import setup, find_packages
import pathlib

# Read dependencies from requirements.txt and filter out empty lines and comments
with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name='paper-manager',
    version='0.1',
    description="A simple program to download huggingface papers (or related paper sites) and store them in LLM memory using mem0",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires=">=3.11",
    entry_points={
        'console_scripts': [
            'paper_manager=papers.main:main',
        ],
    },
    install_requires=requirements,
)
