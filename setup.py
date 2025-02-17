from setuptools import setup, find_packages

setup(
    name="m-motors-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "asyncpg",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "email-validator",
    ],
) 