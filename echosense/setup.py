from setuptools import setup, find_packages

setup(
    name="echosense",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "jinja2>=3.1.2",
    ],
)
