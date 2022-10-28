from setuptools import find_packages, setup

setup(
    name="spiir.data",
    version="0.0.1",
    packages=find_packages(where="src", include=["spiir.*"]),
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
    ],
    extras_require={"pycbc": ["pycbc"]},
    description="A data processing library for the SPIIR search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
    zip_safe=False,
)
