from setuptools import find_namespace_packages, setup

setup(
    name="ampel-contrib-weizmann",
    version="0.7.0",
    packages=find_namespace_packages(),
    package_data={
        "conf": [
            "*.json",
            "**/*.json",
            "**/**/*.json",
            "*.yaml",
            "**/*.yaml",
            "**/**/*.yaml",
            "*.yml",
            "**/*.yml",
            "**/**/*.yml",
        ],
    },
    install_requires=[
        "ampel-interface",
        "ampel-photometry",
        "ampel-contrib-hu",
        "astropy",
    ],
)
