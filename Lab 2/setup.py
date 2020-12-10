from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="javaccflab",
    packages=["javaccflab"],
    entry_points={
        "console_scripts": ['javaccflab = javaccflab.java_ccf:main']
    },
    version='0.1.11',
    description="JavaCCF is utility to fix style in Java files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Vladislav Tochanenko",
    author_email="itochanenko@gmail.com",
    url="https://github.com/tochanenko/MetaProgramming/tree/lab-2",
)