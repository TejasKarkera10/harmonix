from setuptools import setup, find_packages

setup(
    name="harmonix",
    version="0.1.0",
    author="Tejas Karkera",
    description="PSG harmonization pipeline framework for NSRR",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "pandas>=1.5",
    ],
    entry_points={
        "console_scripts": [
            "harmonix=harmonix.cli:cli",
        ],
    },
)
