from setuptools import setup, find_packages
import pathlib

# Read dependencies from requirements.txt and filter out empty lines and comments
with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]


setup(
    name='llm-memory-toolkit',
    version='0.1',
    description="Simple toolkit to execute and test mem0 operations with llms",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires=">=3.11",
    entry_points={
        'console_scripts': [
            'llm_memory_toolkit=llm_memory_toolkit.main:main',
        ],
    },
    install_requires=['genai_app_utils'],
)
