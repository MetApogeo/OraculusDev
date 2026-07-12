from setuptools import setup, find_packages

setup(
    name="oraculus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "radon>=6.0.0",
        "pandas>=2.0.0",
        "plotly>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "oraculus=oraculus.main:main",
        ],
    },
)
