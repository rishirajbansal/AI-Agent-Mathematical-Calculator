"""
Setup script for AI Agent package
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-agent-from-scratch",
    version="1.0.0",
    author="AI Agent Developer",
    author_email="developer@example.com",
    description="A modular AI Agent built from scratch with tool integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-agent-from-scratch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-agent=main:main",
        ],
    },
)