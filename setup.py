from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="shareable",
    url="https://github.com/greysonlalonde/shareable",
    download_url="https://github.com/greysonlalonde/shareable/v0.6-alpha.tar.gz",
    author="Greyson R. LaLonde",
    author_email="greyson.r.lalonde@gmail.com",
    packages=find_packages(),
    install_requires=["psutil", "pandas"],
    version="v0.6-alpha",
    license="MIT",
    description="Dynamic python object access & manipulation across threads/processes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
    ],
)
