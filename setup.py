from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="shareable",
    url="https://github.com/greysonlalonde/shareable",
    download_url="https://github.com/greysonlalonde/shareable/v0.1-alpha.tar.gz",
    author="Greyson R. LaLonde",
    author_email="greyson.r.lalonde@gmail.com",
    packages=find_packages(),
    install_requires=["psutil"],
    version="v0.1-alpha",
    license="MIT",
    description='Dynamic python object access & manipulation across threads/processes.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
    ],

)