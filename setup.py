from setuptools import setup, find_packages

setup(
    name="web_recorder",
    version="0.0.1",
    author="Pranav Raja",
    author_email="pranavraja99@gmail.com",
    description="A package for recording, storing, and replaying web interactions",
    packages=find_packages(),
    package_data={
        "web_recorder": ["rrweb/*.js"],
    },
    include_package_data=True,
)
