from __future__ import annotations

import abc
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

import tomllib
import yaml

if TYPE_CHECKING:
    from io import BufferedReader


PathLike = Path | Iterable[Path]
KeyValuePair = tuple[str, str]


@dataclass
class EnvSourceConfig:
    env_prefix: str = field(default="")
    env_nested_delimiter: str = field(default="__")

    def read(self) -> list[KeyValuePair]:
        return [
            (key.removeprefix(self.env_prefix).lower(), value)
            for key, value in os.environ.items()
            if key.startswith(self.env_prefix)
        ]


@dataclass
class FileSourceConfig(abc.ABC):
    headers: tuple[str, ...] = field(default_factory=tuple)
    path: PathLike = field(default=Path().cwd())

    @abc.abstractmethod
    def load(self, buf: BufferedReader) -> dict[str, Any]: ...


class YamlSourceConfig(FileSourceConfig):
    def load(self, buf: BufferedReader) -> dict[str, Any]:
        return yaml.safe_load(buf)


class TomlSourceConfig(FileSourceConfig):
    def load(self, buf: BufferedReader) -> dict[str, Any]:
        return tomllib.load(buf)


class JsonSourceConfig(FileSourceConfig):
    def load(self, buf: BufferedReader) -> dict[str, Any]:
        return json.load(buf)
