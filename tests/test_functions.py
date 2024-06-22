from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from config.functions import (
    Content,
    filter_headers,
    read_files_from_source,
    traverse_non_empty_file_paths,
)
from hypothesis import given
from hypothesis import strategies as st

from .conftest import fake, file_sources

if TYPE_CHECKING:
    from pathlib import Path

    from config.sources import FileSourceConfig

TOML_DATA = """
field = "top"

[one]
field = true

[one.two]
other = "inner"
field = ["nested", "items"]

[three.four]
field = "bottom"
"""

YAML_DATA = """
field: "top"
one:
    field: true
    two:
        other: "inner"
        field:
            - "nested"
            - "items"
three:
    four:
        field: "bottom"
"""

JSON_DATA = """
{
    "field": "top",
    "one": {
        "field": true,
        "two": {
            "other": "inner",
            "field": ["nested", "items"]
        }
    },
    "three": {
        "four": {
            "field": "bottom"
        }
    }
}
"""


@pytest.mark.parametrize(*file_sources)
def test_read_files_from_source_non_empty(
    source: type[FileSourceConfig], extension: str, test_dir: Path
) -> None:
    file_path = test_dir / fake.file_name(extension=extension)
    if extension == "toml":
        file_path.write_text(TOML_DATA)
    elif extension == "yaml":
        file_path.write_text(YAML_DATA)
    else:
        file_path.write_text(JSON_DATA)

    result = read_files_from_source(source(headers=("one",), path=file_path))

    assert result == {
        "field": True,
        "two": {
            "other": "inner",
            "field": ["nested", "items"],
        },
    }


@pytest.mark.parametrize(*file_sources)
def test_read_files_from_source_empty(
    source: type[FileSourceConfig], extension: str, test_dir: Path
) -> None:
    file_path = test_dir / fake.file_name(extension=extension)
    result = read_files_from_source(source(headers=("one",), path=file_path))
    assert result == {}


@pytest.mark.parametrize(
    "content, headers, expected",
    [
        pytest.param(
            {"one": {"two": {"three": "four"}}},
            ("one", "two"),
            {"three": "four"},
        ),
        pytest.param(
            {"one": {"two": {"three": "four"}}},
            ("three", "four"),
            {},
        ),
        pytest.param(
            {"one": {"two": {"three": "four"}}},
            ("one", "two", "three", "four"),
            {},
        ),
        pytest.param(
            {"one": "two"},
            ("one",),
            {},
        ),
        pytest.param(
            {"one": {"two": "three"}},
            ("four",),
            {},
        ),
        pytest.param(
            {"one": {"two": ["three", "four"]}},
            ("one",),
            {"two": ["three", "four"]},
        ),
        pytest.param(
            {"one": "two", "three": {"four": "five"}},
            (),
            {"one": "two", "three": {"four": "five"}},
        ),
    ],
)
def test_filter_headers(
    content: Content, headers: tuple[str, ...], expected: Content
) -> None:
    assert filter_headers(content, headers) == expected


@given(st.dictionaries(st.text(), st.randoms()))
def test_filter_headers_random_dict(content: Content) -> None:
    assert filter_headers(content, ()) == content


@pytest.mark.parametrize(*file_sources)
def test_traverse_non_empty_file_paths_empty_file(
    source: type[FileSourceConfig], extension: str, test_dir: Path
) -> None:
    no_file = test_dir
    single_empty_file_path = test_dir / fake.file_name(extension=extension)
    multiple_empty_file_paths = [
        test_dir / fake.file_name(extension=extension),
        test_dir / fake.file_name(extension=extension),
    ]

    # fmt: off
    no_file_result = traverse_non_empty_file_paths(source(path=no_file))
    single_file_result = traverse_non_empty_file_paths(source(path=single_empty_file_path))
    multiple_file_result = traverse_non_empty_file_paths(source(path=multiple_empty_file_paths))
    # fmt: on

    assert no_file_result == []
    assert single_file_result == []
    assert multiple_file_result == []


@pytest.mark.parametrize(*file_sources)
def test_traverse_non_empty_file_paths_non_empty_file(
    source: type[FileSourceConfig], extension: str, test_dir: Path
) -> None:
    non_empty_file = test_dir / fake.file_name(extension=extension)
    non_empty_and_empty_files = [
        non_empty_file,
        test_dir / fake.file_name(extension=extension),
    ]
    multiple_non_empty_files = [
        non_empty_file,
        (other_non_empty_file := test_dir / fake.file_name(extension=extension)),
    ]
    non_empty_file.write_text("\n")
    other_non_empty_file.write_text("\n")

    # fmt: off
    non_empty_result = traverse_non_empty_file_paths(source(path=non_empty_file))
    non_empty_and_empty_result = traverse_non_empty_file_paths(source(path=non_empty_and_empty_files))
    multiple_non_empty_result = traverse_non_empty_file_paths(source(path=multiple_non_empty_files))
    # fmt: on

    assert non_empty_result == [non_empty_file]
    assert non_empty_and_empty_result == [non_empty_file]
    assert multiple_non_empty_result == multiple_non_empty_files
