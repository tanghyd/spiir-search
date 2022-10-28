from setuptools import find_namespace_packages, setup

setup(
    name="spiir-workflow",
    version="0.0.1",
    packages=find_namespace_packages(
        where="src",
        include=["spiir-data", "spiir-io", "spiir-search", "spiir-workflow"]
    ),
    python_requires=">=3.8",
    install_requires=["wheel", "setuptools"],
    description="A library for common R&D workflows used by the SPIIR search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
    zip_safe=False,
)
