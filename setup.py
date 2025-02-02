from setuptools import setup, find_packages

setup(
    name="proof-of-autonomy",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "": ["*.py"],  # Include all .py files
    },
)