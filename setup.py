from setuptools import setup, find_packages

setup(
    name="database-explorer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "databases",
        "aiosqlite",
    ],
    entry_points={
        "console_scripts": [
            "database-explorer=main:main",
        ],
    },
)
