import setuptools

setuptools.setup(
    name                                = "sosin",
    version                             = "1.2.8",
    license                             = 'MIT',
    author                              = "Jason Choi",
    author_email                        = "sosincomp@gmail.com",
    description                         = "Python utils for general works",
    long_description                    = open('README.md').read(),
    url                                 = "https://github.com/devsosin/sosin",
    install_requires                    = ['requests', 'requests-toolbelt', 'httpx'],
    packages                            = ['sosin', 'sosin.databases', 'sosin.rpa', 'sosin.utils', 'sosin.web'],
    python_requires                     = '>=3.9',
    classifiers                         = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)