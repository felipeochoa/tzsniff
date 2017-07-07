from os import path
from setuptools import setup

README = path.join(path.dirname(path.abspath(__file__)), "README.md")

setup(
    name="tzsniff",
    version="0.0.1",
    description=("Sniff out the IANA code for a user's timezone"),
    long_description=open(README).read(),
    author="Felipe Ochoa",
    author_email="find me through Github",
    url="https://github.com/felipeochoa/tzsniff",
    license="MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=['attrs', 'pytz'],
    modules=["tzsniff"],
)
