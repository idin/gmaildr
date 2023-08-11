"""
Setup configuration for Gmail Cleaner package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file_handle:
    long_description = file_handle.read()

with open("requirements.txt", "r", encoding="utf-8") as file_handle:
    requirements = [line.strip() for line in file_handle if line.strip() and not line.startswith("#")]

setup(
    name="gmaildr",
    version="1.1.0",
    author="idin",
    author_email="",
    description="A powerful Gmail analysis, management, and automation wizard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/idin/gmaildr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gmaildr=gmaildr.utils.cli:cli",
        ],
    },
) 