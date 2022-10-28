from setuptools import setup, find_packages

setup(
    name="spiir",
    version="0.0.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "spiir.data",
        "spiir.io",
        "spiir.search",
        "spiir.workflow",
    ],
    description="A Python library for the SPIIR gravitational wave search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
)
