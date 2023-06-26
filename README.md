# gpubs

Enables easy fetch and parsing of NCBI pubmed abstracts into tabular format, and then tags them with gene symbols/accession id's.

## Quick Start

### Create environment for development
On linux (ubuntu), firt install conda or miniconda, install mamba for speed, and then create the environment and activate gpubs environment
```
mamba env create -f conda_env.yml
```
```
conda activate gpubs
```
### Run pipeline to get 1 baseline and 1 update abstract XML file from NCBI
```
from gpubs.models import ReferenceData
from gpubs.api import pipeline
# set num_abstract_xml_files=-1 to get all; will need about 60GB
m=ReferenceData(num_abstract_xml_files=1, version="v1", verbose=2)
```

## Install with pip
```
pip install gpubs
```

## To upload the package to PyPi

```
cd src
```

Bump the `VERSION` variable in `release-info.json`, then:

```
make clean
make
```
## Prepare for checkin
`black` the code (changes code in-place to fit style guide)
```
black src
```
Lint the code with `flak8`
```
flake8 src
```
Run tests

TBD


## Make documents
```
cd docs
make clean
make html
```
