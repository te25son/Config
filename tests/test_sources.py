from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import hypothesis_fspaths as fst
import pytest
from hypothesis import given
from hypothesis import strategies as st

from .conftest import file_sources

if TYPE_CHECKING:
    from config.sources import (
        FileSourceConfig,
    )


@pytest.mark.parametrize(*file_sources)
def test_default_file_source_config(
    source: type[FileSourceConfig], extension: str
) -> None:
    config = source()
    assert config.headers == ()
    assert config.path == Path().cwd()


@pytest.mark.parametrize(*file_sources)
@given(fst.fspaths(), st.tuples(st.text(), st.text()))
def test_passing_arguments_to_file_source_config(
    source: type[FileSourceConfig], extension: str, path: Path, headers: tuple[str]
) -> None:
    config = source(headers, path)
    assert config.path == path
    assert config.headers == headers
