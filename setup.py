import setuptools


with open("README.md", "r", encoding="utf8") as file:
    long_description = file.read()


setuptools.setup(
    name="nscrap",
    version="0.0.4",
    author="pparkddo",
    author_email="ehdud3453@gmail.com",
    description="Articles notification by scheduled web scrapers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pparkddo/nscrap",
    packages=setuptools.find_packages(),
    install_requires=[
        "APScheduler",
        "python-telegram-bot",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
