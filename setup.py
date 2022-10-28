from setuptools import setup, find_namespace_packages

setup(
    name="spiir",
    version="0.0.2",
    packages=find_namespace_packages(where="src", include=["spiir.*"]),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "wheel",
        "setuptools",
        "lalsuite",
        "astropy",
        "python-ligo-lw>=1.8.1",
        "ligo.skymap",
        "igwn-alert",
        "ligo-gracedb",
        "toml",
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "click",
    ],
    extras_require={
        "pycbc": ["pycbc"],
    },
    description="A Python library for the SPIIR gravitational wave search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
)
