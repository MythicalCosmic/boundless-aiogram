from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="boundless-aiogram",  
    version="1.0.6",  
    author="MythicalCosmic",
    author_email="qodirjonov0854@gmail.com",
    description="A modern, production-ready framework for building scalable Telegram bots with Aiogram 3.x",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MythicalCosmic/boundless-aiogram", 
    project_urls={
        "Bug Tracker": "https://github.com/MythicalCosmic/boundless-aiogram/issues",
        "Documentation": "https://github.com/MythicalCosmic/boundless-aiogram/wiki",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aiogram>=3.0.0",
        "alembic>=1.7",
        "pyyaml",
        "sqlalchemy>=2.0",
        "python-dotenv>=1.0.0",
        "aiosqlite" 
    ],
    entry_points={
        "console_scripts": [
            "boundless=boundless_aiogram.cli:main",  
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Communications :: Chat",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
)