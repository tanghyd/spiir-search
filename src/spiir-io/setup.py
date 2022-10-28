from setuptools import find_namespace_packages, setup

setup(
    name="spiir-io",
    version="0.0.2",
    packages=find_namespace_packages(include=["spiir.*"]),
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
        "tqdm",
    ],
    extras_require={"pycbc": ["pycbc"], "igwn": ["igwn-alert", "ligo-gracedb", "toml"]},
    description="A utilities and IO tooling library for the SPIIR search pipeline.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
    zip_safe=False,
)
