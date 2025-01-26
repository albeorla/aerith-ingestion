"""Utility functions for file operations."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger


def _infer_json_schema(data: Any) -> Dict:
    """Infer the schema of a JSON object.

    Args:
        data: The JSON data to analyze

    Returns:
        A dictionary representing the schema in JSON-schema format
    """
    if isinstance(data, dict):
        properties = {k: _infer_json_schema(v) for k, v in data.items()}
        return {
            "type": "object",
            "properties": properties,
            "required": list(data.keys()),
        }
    elif isinstance(data, list):
        if not data:
            return {"type": "array", "items": {"type": "unknown"}}
        # Infer from first item as representative
        return {"type": "array", "items": _infer_json_schema(data[0])}
    else:
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            type(None): "null",
        }
        return {"type": type_map.get(type(data), str(type(data).__name__))}


def write_json_file(
    data: Any,
    file_path: str | Path,
    create_dirs: bool = True,
    indent: int = 2,
    write_schema: bool = False,
) -> Optional[Path]:
    """Write data to a JSON file, optionally creating parent directories and writing schema.

    Args:
        data: The data to write to the JSON file
        file_path: Path to the output file
        create_dirs: If True, create parent directories if they don't exist
        indent: Number of spaces for JSON indentation
        write_schema: If True, also writes a schema file alongside the data file

    Returns:
        Path to the schema file if write_schema is True, None otherwise

    Example:
        data = {"name": "John", "scores": [85, 90]}
        write_json_file(data, "output.json", write_schema=True)
        # Creates:
        #   output.json
        #   output.schema.json
    """
    file_path = Path(file_path)
    logger.debug(f"Writing JSON file to {file_path}")

    if create_dirs:
        logger.trace(f"Creating parent directories for {file_path}")
        file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        logger.trace("Writing data to file")
        json.dump(data, f, indent=indent)

    logger.debug(f"Successfully wrote JSON file to {file_path}")

    if write_schema:
        schema_path = file_path.with_suffix(".schema.json")
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": f"Schema for {file_path.name}",
            **_infer_json_schema(data),
        }

        with open(schema_path, "w") as f:
            logger.trace("Writing schema file")
            json.dump(schema, f, indent=indent)

        logger.debug(f"Successfully wrote JSON schema to {schema_path}")
        return schema_path

    return None
