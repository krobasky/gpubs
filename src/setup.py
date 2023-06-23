from setuptools import setup, find_packages # noga: F401

import json

with open("./release-info.json") as f:
    j = json.load(f)
    # overwrite the version file from source control so the library will
    # have the latest version number created from release-info.json
    with open("./gpubs/_version.py", "w") as f:
        f.write(f'__version__ = "{j["VERSION"]}"\n')
        f.flush()

        setup(
            name=j["LIBNAME"], 
            packages=[j["LIBNAME"]], 
            description=j["DESCRIPTION"], 
            version=f"{j['VERSION']}",
            url=f'http://github.org/{j["REPONAME"]}',
            author=j["AUTHOR"], 
            author_email=j["EMAIL"], 
            keywords=j["KEYWORDS"],
            include_package_data=True, 
            install_requires=[
                "ipykernel==6.19.2",
                "pydantic==1.10.8",
                "requests==2.29.0",
                "nltk==3.7",
                "pandas==1.5.3",
            ], 
            scripts=[
                "scripts/create_search_terms_file.sh",
                "scripts/search.awk",
                "scripts/download_pubs.sh"
                ]
        )
