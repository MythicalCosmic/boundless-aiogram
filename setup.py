from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="boundless-aiogram",  
    version="1.0.4",  
    author="MythicalCosmic",
    author_email="qodirjonov0854@gmail.com",
    description="Boundless Aiogram - A structured, fast, and scalable framework for Telegram bots using Aiogram",
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
        "fastapi>=0.70.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=2.0",
        "alembic>=1.7",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "boundless=boundless_aiogram.cli:create_project",
        ],
    },
    package_data={
        "boundless_aiogram": ["template/**/*"],  
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
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
)
