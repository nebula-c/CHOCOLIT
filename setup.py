from setuptools import find_packages, setup

# setup()

setup(
    name="CHOCOLIT",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        'chocolit': ['images/*'],
    },
    install_requires=[
        'PyQt5',
        'numpy',
        'caen-libs'
    ],
    entry_points={
        'console_scripts': [
            'chocolit = run:main',
        ],
    }
)
