from setuptools import setup, find_packages

setup(
    name="helix-py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy", "pyarrow", "tqdm"],
)


# NOTE: possibly pull and setup helix instance via this and then run it when runing `db = helix.Client(local=True)`
