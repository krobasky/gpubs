# gpubs

Under construction.

## Install:

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

## To do

* Create doc with sphinx
* Add a feature for filtering for a custom list.
