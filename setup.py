from setuptools import setup, find_packages

setup(
    name="helix-py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy", "pyarrow", "tqdm"],
)