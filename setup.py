from setuptools import find_packages
from setuptools import setup


setup(
    name="wabbit",
    author="Dan Davison",
    author_email="dandavison7@gmail.com",
    description="Wabbit language",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
