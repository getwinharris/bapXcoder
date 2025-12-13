from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qwen3vl-local-cli",
    version="0.1.0",
    author="Harris",
    author_email="getwinharris@gmail.com",
    description="A CLI tool to run Qwen3VL model locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/getwinharris/qwen3VL-Local-CLI",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "llama-cpp-python>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "qwen3vl-cli=qwen3VL_local_cli:main",
        ],
    },
)