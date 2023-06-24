# gpubs

Under construction.

## Create environment for development:
On linux (ubuntu), firt install conda or miniconda, install mamba for speed, and then create the environment and activate gpubs environment
```
mamba env create -f conda_env.yml
```
```
conda activate gpubs
```

## Install with pip:

```
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gpubs # to get it from test registry
```

## To upload the package:

```
cd src
```

Bump the `VERSION` variable in `release-info.json`, then:

```
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


## To do

* Add a feature for filtering for a custom list.
