"""Define metadata for Bind HTML."""

# Third Party
import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="bind-html",
    version="1.0a3",
    author="Chase Finch",
    author_email="chase@finch.email",
    description="Declarative data binding for HTML attributes",
    keywords=["HTML", "data binding"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BringFido/bind-html",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
