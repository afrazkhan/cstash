# pylint: disable=missing-module-docstring

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cstash",
    python_requires='>=3.3.0',
    version="0.0.1",
    author="Afraz Ahmadzadeh",
    author_email="afrazkhan@gmail.com",
    description="Use S3 for storing encrypted objects, without trusting keys to AWS",
    long_description_content_type="text/markdown",
    url="https://github.com/afrazkhan/cstash",
    packages=["cstash"],
    install_requires=[
        "click >= 7.0",
        "boto3",
        'datetime',
        'sqlitedict',
        'python-gnupg',
        'daemon',
        'persist-queue',
        'cryptography'
        ],
    tests_require=[
        "coverage",
        "moto"
    ],
    license="GPL3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["cstash=cstash.main:main"]},
    scripts=[],
    zip_safe=False
)
