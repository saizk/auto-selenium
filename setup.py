from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auto-selenium",
    version="1.0.0",
    author="saizk",
    author_email="sergioaizcorbe@hotmail.com",
    description="Python tool to automate the download of Selenium Web Drivers for all browsers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saizk/auto-selenium",
    project_urls={
        "Bug Tracker": "https://github.com/saizk/auto-selenium/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['selenium>=3.141.0', 'msedge-selenium-tools>=3.141.3', 'Jinja2>=3.0.2'],
    package_dir={".": ""},
    packages=["autoselenium"],
    include_package_data=True,
    python_requires=">=3.6",
)
