from setuptools import setup, find_packages

setup(
    name="airoframework",
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,  
    install_requires=[],
    entry_points={
        "console_scripts": [
            "airoframework=airoframework.cli:create_project",
        ],
    },
    package_data={
        "airoframework": ["template/**/*"],  
    },
)
