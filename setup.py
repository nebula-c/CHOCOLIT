from setuptools import find_packages, setup

# setup()

setup(
    name="CHOCOLIT",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True
)
