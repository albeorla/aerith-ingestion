#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import List


def read_gitignore(gitignore_path: str) -> List[str]:
    """Read and process .gitignore patterns."""
    if not os.path.exists(gitignore_path):
        return []

    patterns = []
    with open(gitignore_path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Remove leading slashes and normalize patterns
            if line.startswith("/"):
                line = line[1:]
            patterns.append(line)
    return patterns


def should_ignore(path: str, ignore_patterns: List[str]) -> bool:
    """Check if a path should be ignored based on gitignore patterns."""
    for pattern in ignore_patterns:
        if pattern.startswith("!"):  # Skip negation patterns for now
            continue
        if pattern.endswith("/"):  # Directory pattern
            if path.startswith(pattern) or f"/{pattern}" in path:
                return True
        else:  # File pattern
            if path.endswith(pattern) or f"/{pattern}" in path or pattern in path:
                return True
    return False


def print_tree(
    directory: str,
    prefix: str = "",
    ignore_patterns: List[str] = None,
    max_depth: int = None,
    current_depth: int = 0,
) -> None:
    """Print the directory tree structure."""
    if ignore_patterns is None:
        ignore_patterns = []

    if max_depth is not None and current_depth > max_depth:
        return

    path = Path(directory)
    if should_ignore(str(path), ignore_patterns):
        return

    # Print current directory
    if current_depth == 0:
        print(path.name)

    # Get and sort directory contents
    try:
        entries = sorted(list(path.iterdir()))
    except PermissionError:
        return

    # Process each entry
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        entry_str = str(entry.relative_to(path))

        if should_ignore(str(entry), ignore_patterns):
            continue

        # Determine the prefix for the current line
        current_prefix = "└── " if is_last else "├── "
        # Determine the prefix for subsequent lines
        next_prefix = "    " if is_last else "│   "

        print(f"{prefix}{current_prefix}{entry_str}")

        if entry.is_dir():
            print_tree(
                str(entry),
                prefix + next_prefix,
                ignore_patterns,
                max_depth,
                current_depth + 1,
            )


def main():
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(workspace_root)

    gitignore_path = ".gitignore"
    ignore_patterns = read_gitignore(gitignore_path)

    # Add some common patterns that might not be in .gitignore
    additional_patterns = [
        ".git",
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        "node_modules",
        ".next",
        "out",
        "coverage",
        "build",
    ]
    ignore_patterns.extend(additional_patterns)

    max_depth = 7  # Default depth limit
    if len(sys.argv) > 1:
        try:
            max_depth = int(sys.argv[1])
        except ValueError:
            print(f"Invalid depth argument: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)

    print_tree(".", ignore_patterns=ignore_patterns, max_depth=max_depth)


if __name__ == "__main__":
    main()
