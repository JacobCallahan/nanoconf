NanoConf
========
NanoConf is a tiny, opinionated, and easy to use configuration library for Python. It is designed to be used in small to medium sized projects where a full blown configuration library is overkill.

Installation
------------
```bash
pip install nanoconf
```

Usage
-----
```python
from nanoconf import NanoConf
# or if NanoConf if too long of a name
from nanoconf import NC

# Create a new configuration object
config = NanoConf("/path/to/config.nconf")

# Use the configuration object
print(config["key"])
# Since all values are also loaded as attributes, you can also do
print(config.key)
```

Configuration File Format
-------------------------
NanoConf uses a simple configuration file format that is easy to read and write.
Each File is YAML formatted and contains a single top-level dictionary.
Even though the top-level must be a dictionary, you can nest dictionaries and lists as deep as you want.
Each config file also must have the .nconf extension. This ensures that NanoConf will only load files that are meant to be configuration files.
```yaml
key: value
test: 1
overriden: false
things:
    - thing1
    - thing2
    - thing3
top:
    v1: 1
    middle:
        v2: 2
        inner:
            v3: 3
            deep:
                v4: 4
```
If you have multiple config files you want to load into a single config object, you can put them all in the same directory and pass that directory to NanoConf.
NanoConf will automatically place sub-files by their filename as an attribute of the parent file.
The contents of that file will be accessible as you'd expect under the corresponding filename attribute.

```
<project root>
conf_dir
  |__ cfg1.nconf
  |__ cfg2.nconf
  |__ cfg3.nconf
```

```python
# load an entire directory
proj_config = NanoConf("/path/to/conf_dir")
print(proj_config.cfg1.test)
```

Or you can import additional files or directories from within any config file by using the `_import` keyword.
```yaml
# main.nconf
_import:
    - /path/to/project/more_config
key: value
test: 1
```

```
<project root>
main.nconf
more_config
  |__ subcfg1.nconf
  |__ subcfg2.nconf
  |__ subcfg3.nconf
```

```python
# loading the main config file will also load the sub-configs
proj_config = NanoConf("/path/to/project/main.nconf")
print(proj_config.more_config.subcfg1.test)
```
Notice how the directory structure was also maintained in the attribute path. This makes it easier to find the file that a value came from.

Environment Variables
---------------------
NanoConf supports environment variables either as overrides to existing values or as additions to the loaded config.
Envars are evaluated on a per-file basis, so you can have different envars for different config files.
The way we manage this is by having a special `_envar_prefix` key in the config file.
**Note:** NanoConf will not modify the case of any environment varable name or value. It is up to you to ensure that the case is correct.
```yaml
_envar_prefix: myapp
key: value
overrideme: original
```
```bash
export myapp_overrideme=changed
```
```python
config = NanoConf("/path/to/config.nconf")
print(config.overrideme)
```

You can also pass complex data structures as JSON strings in environment variables.
```bash
export myapp_abc='{"a": 1, "b": 2, "c": 3}'
```
```python
config = NanoConf("/path/to/config.nconf")
print(config.abc.b)
```