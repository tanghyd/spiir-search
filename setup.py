from setuptools import find_namespace_packages, setup

setup(
    name="spiir-search",
    version="0.0.2",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", include=["spiir*"]),
    namespace_packages=["spiir"],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "matplotlib",
        "scikit-learn>=1.0",
        "pycbc @ git+https://github.com/gwastro/pycbc.git@master#egg=pycbc",
        "p_astro @ git+https://git.ligo.org/spiir-group/p-astro.git@feature/enable_pickle_compat#egg=p_astro",
    ],
    include_package_data=True,
    description="A Python library for SPIIR gravitational wave search algorithms.",
    author="Daniel Tang",
    author_email="daniel.tang@uwa.edu.au",
)
