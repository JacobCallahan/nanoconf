import contextlib
import json
import os
from pathlib import Path

from box import Box
import yaml


class NanoConf:
    def __init__(self, cfg_path="."):
        self._cfg_path = Path(cfg_path)
        self._name = self._cfg_path.stem
        if self._cfg_path.is_dir():
            for sub in self._cfg_path.glob("*.nconf"):
                new_conf = NanoConf(sub)
                setattr(self, new_conf._name, new_conf)
        elif self._cfg_path.is_file() and self._cfg_path.suffix == ".nconf":
            self._load_config()
            self._pull_envars()

    def _load_config(self):
        cfg_dict = yaml.load(self._cfg_path.read_text(), Loader=yaml.SafeLoader)
        for sub_import in cfg_dict.pop("_import", []):
            new_conf = NanoConf(
                self._cfg_path / sub_import
                if self._cfg_path.is_dir()
                else self._cfg_path.parent / sub_import
            )
            setattr(self, new_conf._name, new_conf)
        self.__dict__.update(Box(cfg_dict))

    def _pull_envars(self):
        if getattr(self, "_envar_prefix", ""):
            for key, val in os.environ.items():
                if key.startswith(self._envar_prefix):
                    key_name = key.replace(f"{self._envar_prefix}_", "")
                    with contextlib.suppress(json.decoder.JSONDecodeError):
                        val = Box(json.loads(val))  # noqa: PLW2901
                    self.__dict__[key_name] = val

    def __repr__(self):
        return (
            f"<NanoConf {self._name}.("
            + ", ".join(filter(lambda x: not x.startswith("_"), self.__dict__.keys()))
            + ")>"
        )
