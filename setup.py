from setuptools import setup, find_namespace_packages

setup(
    name="spiir-search",
    version="0.0.2",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", include=["spiir*"]),
    namespace_packages=["spiir"],
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
        "scikit-learn",
        "p_astro @ git+https://git.ligo.org/lscsoft/p-astro.git@master#egg=p_astro",
    ],
    extras_require={"pycbc": ["pycbc"]},
    description="A Python library for SPIIR gravitational wave search algorithms.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
)
