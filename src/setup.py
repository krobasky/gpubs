from setuptools import setup, find_packages # noga: F401

import json

with open(" ./release-info.json") as f:
    j = json.load(f)
    # overwrite the version file from source control so the library will
    # have the latest version number created by the pipeline:
    with open("./gpubs/_version.py", "w") as f:
        f.write(f'__version__ = "{j["VERSION")}"')

        setup(
            name=j["LIBNAME"], 
            packages=[j["LIBNAME"]], 
            description=j["DESCRIPTION"], 
            version=f"{j['VERSION']}",
            url=f"http://github.org/{j['REPONAME'])",
            author=j["AUTHOR"], 
            author_email=j["EMAIL"], 
            keywords=j["KEYWORDS"],
            include_package_data=True, 
            install requires=[
                "pandas",
                "biopython",
                "requests",
                "lxml",

                "spacy",
                "dill",
                "ipykernel",
                "beautifulsoup4",
                "lxml",
                "punkt",
                "",
                "flake8==6.0.0",
                "jello==1.5.5",
                "myst-parser==0.18.1",
                "pip==22.3.1",
                "pytest=-7.2.0"
                "pytest-tap==3.3",
                "sphinx==5.0.2"

                "black @ git+https://github.com/psf/black@22.12.0#egg-black",
                "sphinx_rtd_theme @ git+https://github.com/snide/sphinx_rtd_theme@1.1.1#egg-sphinx_rtd _theme",
            ], 
            scripts=[
                "scripts/cicd-bump.py"
                "scripts/cicd-build.sh"
                "scripts/cicd-common.src"
                "scripts/cicd-mkrepo.sh"
                "scripts/cicd-release-info.json"
                ]
