from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tw_vid',
    version='0.1.0',
    description='A simple library for extracting and corrupting frames from videos.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='TheZoidMaster, JaegerwaldDev',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'tdqm',
        'numpy'
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    project_urls={
        "Source": "https://github.com/Martyrdome/12Vid",
    }
)
