import logging
import os
from pathlib import Path
from typing import Dict, Union, Any, Optional

from .exceptions import FolderTreeError, ValidationError, MigrationError
from .adapters import BaseStorageAdapter, LocalFileSystemAdapter

logger = logging.getLogger(__name__)

# Type alias for the tree structure
TreeStructure = Dict[str, Union[Dict, Any]]

def _resolve_path(path: Union[str, Path]) -> Path:
    """Helper to resolve paths with env vars and user expansion (Local only)."""
    s = str(path)
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    return Path(s).resolve()

def generate_tree_structure_from_path(path: Union[str, Path], limit_depth: int = -1) -> str:
    """
    Generates a visual tree structure string from a folder path.
    """
    path_obj = _resolve_path(path)
    
    if not path_obj.exists():
        return f"Path not found: {path_obj}"

    # If it's a file, just return the name
    if not path_obj.is_dir():
        return path_obj.name

    def _walk(directory: Path, prefix: str = "", current_depth: int = 0):
        if limit_depth != -1 and current_depth >= limit_depth:
            return ""

        tree = ""
        try:
            # Sort alphabetically (case-insensitive)
            entries = sorted(list(directory.iterdir()), key=lambda x: x.name.lower())
        except PermissionError:
            return f"{prefix}└── [Access Denied]\n"

        # Filter hidden files/dirs and common cache/build artifacts
        ignored_names = {'__pycache__', 'node_modules', 'venv', '.git', '.idea', '.vscode', 'build', 'dist', 'target', 'bin', 'obj'}
        ignored_exts = {'.pyc', '.pyo', '.pyd', '.ds_store'}
        
        filtered_entries = [
            e for e in entries 
            if not e.name.startswith('.') 
            and e.name not in ignored_names
            and e.suffix.lower() not in ignored_exts
        ]
        count = len(filtered_entries)
        
        for i, entry in enumerate(filtered_entries):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            
            # Add current item
            tree += f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}\n"
            
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                tree += _walk(entry, prefix + extension, current_depth + 1)
                
        return tree

    return f"{path_obj.name}/\n" + _walk(path_obj)

def generate_tree_from_path(path: Union[str, Path], limit_depth: int = -1) -> str:
    """Wrapper for backward compatibility."""
    return generate_tree_structure_from_path(path, limit_depth)

class FolderTreeManager:
    """
    Manager class to handle folder tree operations using various storage adapters.
    """
    def __init__(self, adapter: Optional[BaseStorageAdapter] = None):
        self.adapter = adapter or LocalFileSystemAdapter()

    def generate_tree_from_path(self, path: Union[str, Path], limit_depth: int = -1) -> str:
        return generate_tree_structure_from_path(path, limit_depth)

    def create_folder_tree(
        self,
        base_path: Union[str, Path],
        structure: TreeStructure,
        overwrite: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Recursively creates a folder tree starting from base_path."""
        if isinstance(self.adapter, LocalFileSystemAdapter):
            base = _resolve_path(base_path)
        else:
            base = Path(base_path)

        if not dry_run:
            try:
                self.adapter.mkdir(base, parents=True, exist_ok=True)
            except Exception as e:
                raise FolderTreeError(f"Failed to create base directory {base}: {e}")

        result_paths = {}

        for key, value in structure.items():
            if key.startswith("_"):
                continue

            current_path = base / key
            is_folder = isinstance(value, dict)

            if dry_run:
                logger.info(f"[DRY-RUN] Would create: {current_path}")
            else:
                try:
                    if is_folder:
                        self.adapter.mkdir(current_path, parents=True, exist_ok=True)
                        if "_perms" in value and isinstance(value["_perms"], int):
                            self.adapter.chmod(current_path, value["_perms"])
                    else:
                        self.adapter.mkdir(current_path.parent, parents=True, exist_ok=True)
                        if not self.adapter.exists(current_path) or overwrite:
                            content = value if isinstance(value, str) and value not in ("file", "") else ""
                            if content is None: content = ""
                            self.adapter.write_file(current_path, str(content), overwrite=overwrite)

                except Exception as e:
                    logger.error(f"Error creating {current_path}: {e}")
                    raise FolderTreeError(f"Failed to create {current_path}: {e}")

            if is_folder:
                sub_results = self.create_folder_tree(current_path, value, overwrite, dry_run)
                result_paths[key] = sub_results
            else:
                result_paths[key] = current_path

        return result_paths

    def validate_folder_tree(self, base_path: Union[str, Path], structure: TreeStructure) -> bool:
        base = _resolve_path(base_path) if isinstance(self.adapter, LocalFileSystemAdapter) else Path(base_path)
        
        if not self.adapter.exists(base):
             raise FolderTreeError(f"Base path does not exist: {base}")

        missing = []

        def _check(current_base: Path, sub_struct: Dict):
            for key, value in sub_struct.items():
                if key.startswith("_"): continue
                p = current_base / key
                if not self.adapter.exists(p):
                    missing.append(str(p))
                if isinstance(value, dict):
                    _check(p, value)

        _check(base, structure)
        if missing:
            raise ValidationError(f"Missing {len(missing)} folders: {', '.join(missing[:5])}...")
        return True

    def cleanup_folder_tree(self, base_path: Union[str, Path], structure: TreeStructure, confirm: bool = False):
        if not confirm:
            logger.warning("cleanup_folder_tree called without confirm=True. Returning.")
            return

        base = _resolve_path(base_path) if isinstance(self.adapter, LocalFileSystemAdapter) else Path(base_path)
        paths_to_delete = []

        def _collect(current_base: Path, sub_struct: Dict):
            for key, value in sub_struct.items():
                if key.startswith("_"): continue
                p = current_base / key
                paths_to_delete.append(p)
                if isinstance(value, dict):
                    _collect(p, value)

        _collect(base, structure)
        paths_to_delete.sort(key=lambda p: len(str(p)), reverse=True)

        for p in paths_to_delete:
            if self.adapter.exists(p):
                try:
                    self.adapter.remove(p, recursive=False)
                except Exception as e:
                    logger.warning(f"Could not delete {p}: {e}")

# Module-level convenience functions
def create_folder_tree(base_path: Union[str, Path], structure: TreeStructure, overwrite: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    return FolderTreeManager().create_folder_tree(base_path, structure, overwrite, dry_run)

def validate_folder_tree(base_path: Union[str, Path], structure: TreeStructure) -> bool:
    return FolderTreeManager().validate_folder_tree(base_path, structure)

def cleanup_folder_tree(base_path: Union[str, Path], structure: TreeStructure, confirm: bool = False):
    return FolderTreeManager().cleanup_folder_tree(base_path, structure, confirm)

def get_flat_path_map(base_path: Union[str, Path], structure: TreeStructure, separator: str = "_", parent_key: str = "") -> Dict[str, Path]:
    base = _resolve_path(base_path)
    flat_map = {}
    for key, value in structure.items():
        if key.startswith("_"): continue
        full_key = f"{parent_key}{separator}{key}" if parent_key else key
        current_path = base / key
        flat_map[full_key] = current_path
        if isinstance(value, dict):
            child_map = get_flat_path_map(current_path, value, separator, full_key)
            flat_map.update(child_map)
    return flat_map

def generate_tree_summary(structure: TreeStructure, indent: str = "", last: bool = True) -> str:
    """Generates a text summary of a structure dict."""
    summary = ""
    # Filter metadata
    items = {k: v for k, v in structure.items() if not k.startswith("_")}
    keys = list(items.keys())
    count = len(keys)
    
    for i, key in enumerate(keys):
        is_last_item = (i == count - 1)
        connector = "└── " if is_last_item else "├── "
        
        summary += f"{indent}{connector}{key}\n"
        
        value = items[key]
        if isinstance(value, dict):
            new_indent = indent + ("    " if is_last_item else "│   ")
            summary += generate_tree_summary(value, new_indent)
            
    return summary
