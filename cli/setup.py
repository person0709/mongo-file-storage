from setuptools import setup, find_packages

setup(
    name="fs-cli",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click", "requests", "requests-toolbelt", "tqdm"],
    entry_points="""
        [console_scripts]
        fs=fs_cli.cli:cli
    """,
)
