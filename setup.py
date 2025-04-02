from setuptools import setup, find_packages
import os

0
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="airoframework",
    version="1.0.2",
    author="MythicalCosmic",
    author_email="qodirjonov0854@gmail.com",  
    description="AiroFramework - A structured framework for Aiogram bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MythicalCosmic/airoframework",
    project_urls={
        "Bug Tracker": "https://github.com/MythicalCosmic/airoframework/issues",
        "Documentation": "https://github.com/MythicalCosmic/airoframework/wiki",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aiogram>=3.0.0",
        "fastapi>=0.70.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=2.0",
        "alembic>=1.7",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "airoframework=airoframework.cli:create_project",
        ],
    },
    package_data={
        "airoframework": ["template/**/*"],  
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
)
