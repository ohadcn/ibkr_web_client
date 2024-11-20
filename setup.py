from setuptools import setup, find_packages

setup(
    name="ibkr_web_client",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "PyCryptodome",
        "urllib3",
        "cryptography",
        "pytest"
    ],
    python_requires=">=3.8",
    author="Nikita Sirons",
    author_email="nikita.sirons@gmail.com",
    description="A Python client for the Interactive Brokers API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nsirons/ibkr-web-client",
)
