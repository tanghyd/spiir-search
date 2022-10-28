from setuptools import find_packages, setup

setup(
    name="spiir.search",
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
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "click",
        "pycbc",  # refactor p_astro to make pycbc an optional dependency
    ],
    description="Search algorithms and functions core to the SPIIR search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
)
