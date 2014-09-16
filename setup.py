from distutils.core import setup

setup(
    name="tsheets-client",
    version="0.1.0",
    author="Eleuterio Millan Jr.",
    author_email="eleuteriomillanjr@gmail.com",
    packages=["tsheets"],
    include_package_data=True,
    url="http://pypi.python.org/pypi/tsheets-client/",
    license="LICENSE.txt",
    description="A wrapper for the TSheets REST API",
    long_description=open("README.md").read(),
    install_requires=[
        "requests",
    ],
)
