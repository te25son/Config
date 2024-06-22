from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Generator

import pytest
from config.sources import JsonSourceConfig, TomlSourceConfig, YamlSourceConfig
from faker import Faker

if TYPE_CHECKING:
    from pathlib import Path

fake = Faker()
file_sources = (
    "source, extension",
    [
        pytest.param(JsonSourceConfig, "json", id="json source config"),
        pytest.param(TomlSourceConfig, "toml", id="toml source config"),
        pytest.param(YamlSourceConfig, "yaml", id="yaml source config"),
    ],
)


@pytest.fixture(scope="module")
def test_dir(tmp_path_factory: pytest.TempPathFactory) -> Generator[Path, None, None]:
    test_dir = tmp_path_factory.mktemp("test")
    yield test_dir
    shutil.rmtree(str(test_dir))
