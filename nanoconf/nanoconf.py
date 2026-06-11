import contextlib
import json
import os
from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML()


class NanoConf(dict):
    def __init__(self, cfg_path=".", **kwargs):
        super().__init__(**kwargs)
        # Only process cfg_path if it's actually a path (not a dict for dict init)
        if isinstance(cfg_path, str | Path):
            self._cfg_path = Path(cfg_path)
            self._name = self._cfg_path.stem
            if self._cfg_path.is_dir():
                for sub in self._cfg_path.glob("*.nconf"):
                    new_conf = NanoConf(sub)
                    self[new_conf._name] = new_conf
            elif self._cfg_path.is_file() and self._cfg_path.suffix == ".nconf":
                self._load_config()
                self._pull_envars()
        elif isinstance(cfg_path, dict):
            self.update(cfg_path)

    def __getattr__(self, name):
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'") from e

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, NanoConf):
            value = NanoConf(value)
        elif isinstance(value, list):
            value = [
                NanoConf(i) if isinstance(i, dict) and not isinstance(i, NanoConf) else i
                for i in value
            ]
        super().__setitem__(key, value)
        if key == "_envar_prefix":
            object.__setattr__(self, key, value)

    def update(self, *args, **kwargs):
        if args:
            other = args[0]
            for key, value in other.items() if isinstance(other, dict) else other:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def _load_config(self):
        cfg_dict = yaml.load(self._cfg_path)
        for sub_import in cfg_dict.pop("_import", []):
            new_conf = NanoConf(
                self._cfg_path / sub_import
                if self._cfg_path.is_dir()
                else self._cfg_path.parent / sub_import
            )
            self[new_conf._name] = new_conf
        self.update(cfg_dict)

    def _pull_envars(self):
        if getattr(self, "_envar_prefix", ""):
            for key, val in os.environ.items():
                if key.startswith(self._envar_prefix):
                    key_name = key.replace(f"{self._envar_prefix}_", "")
                    with contextlib.suppress(json.decoder.JSONDecodeError):
                        val = NanoConf(json.loads(val))  # noqa: PLW2901
                    self[key_name] = val

    def to_dict(self):
        def _conv(v):
            if isinstance(v, NanoConf):
                return v.to_dict()
            if isinstance(v, list):
                return [_conv(x) for x in v]
            return v

        return {k: _conv(v) for k, v in self.items()}

    def __dir__(self):
        return list(super().__dir__()) + [k for k in self if not k.startswith("_")]

    def __repr__(self):
        name = getattr(self, "_name", "dict")
        keys = ", ".join(k for k in self if not k.startswith("_"))
        return f"<NanoConf {name}.({keys})>"
