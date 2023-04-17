import setuptools

setuptools.setup(
    name                                = "sosin",
    version                             = "0.0.1",
    license                             = 'MIT',
    author                              = "Jason Choi",
    author_email                        = "svstar94@gmail.com",
    description                         = "Python utils for general works",
    long_description                    = open('README.md').read(),
    url                                 = "https://github.com/devsosin/sosin",
    packages                            = setuptools.find_packages(),
    python_requires                     = '>=3.9',
    classifiers                         = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)