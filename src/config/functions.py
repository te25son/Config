from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pipe import traverse, where
from pydantic.v1.utils import deep_update

if TYPE_CHECKING:
    from pathlib import Path

    from .sources import EnvSourceConfig, FileSourceConfig

Content = dict[str, Any]


def traverse_non_empty_file_paths(source: FileSourceConfig) -> list[Path]:
    return list(
        [source.path] | traverse | where(lambda p: p.is_file() and p.stat().st_size > 0)
    )


def filter_headers(data: Content, headers: tuple[str, ...]) -> Content:
    for header in headers:
        if isinstance(header_result := data.get(header, {}), dict):
            data = header_result
        else:
            return {}
    return data


def read_files_from_source(source: FileSourceConfig) -> Content:
    for path in traverse_non_empty_file_paths(source):
        with open(path, mode="rb") as file:
            return filter_headers(source.load(file), source.headers)
    return {}


def build_content_from_base(keys: list[str], value: Any) -> Content:
    try:
        content = {keys.pop(0): value}
        for key in keys:
            content = {key: content}
        return content
    except IndexError:
        return {}


def build_content_from_environment_variables(source: EnvSourceConfig) -> Content:
    content: Content = {}
    for key, value in source.read():
        traverable_keys = list(reversed(key.split(source.env_nested_delimiter)))
        content = deep_update(content, build_content_from_base(traverable_keys, value))
    return content
