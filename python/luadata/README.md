# luadata

[![Build Status](https://travis-ci.org/leafvmaple/luadata.svg?branch=master)](https://travis-ci.org/leafvmaple/luadata)
![PyPI](https://img.shields.io/pypi/v/luadata)

This is a Python package that can serialize `Python` list &amp; dictionary to `Lua` table, or unserialize `Lua` table to `Python` list & dictionary.

## Install

Binary installers for the latest released version are available at the `Pypi`.

```
python -m pip install --upgrade luadata
```

## Usage

### write

> Serialize `python` variable to `lua` data string, and save to specific path.

```python
import luadata

luadata.write(path, data, encoding="utf-8", indent="\t", prefix="return ")
```

### read

> Unserialize `lua` data string to `python` variable from file.

```python
import luadata

data = luadata.read(path, encoding="utf-8")
```

### serialize

> Serialize `python` variable to `lua` data string.

```python
import luadata

luadata.serialize(var, encoding="utf-8", indent="\t", indent_level=0)
```

### unserialize

> Unserialize `lua` data string to `python` variable.

```python
import luadata

luadata.unserialize(luadata_str, encoding="utf-8", multival=False)
```

## License

[BSD](https://github.com/leafvmaple/luadata/blob/master/LICENSE)
