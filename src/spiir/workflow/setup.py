from setuptools import find_packages, setup

setup(
    name="spiir.workflow",
    version="0.0.1",
    # packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "wheel",
        "setuptools",
        "lalsuite",
        "astropy",
        "python-ligo-lw>=1.8.1",
        "ligo.skymap",
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "click",
        "spiir.io",
    ],
    description="A library for common R&D workflows used by the SPIIR search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
)
