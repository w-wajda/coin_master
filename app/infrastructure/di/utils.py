import os
import pkgutil
from importlib.machinery import FileFinder
from pathlib import Path


def get_import_path(path: Path, root_path: Path) -> str:
    """Get import path for a file"""
    relative_path = path.relative_to(root_path)
    return str(relative_path).replace(os.sep, ".").strip(".")


def generate_modules_list(directories: list[str], root_directory: str) -> list[str]:
    modules = []
    root_path = Path(root_directory)

    for module_info in pkgutil.walk_packages([str(directory) for directory in directories]):
        if not isinstance(module_info.module_finder, FileFinder):
            raise ValueError("Module finder is not a file finder")

        module_path = Path(module_info.module_finder.path)
        module_dotted_path = get_import_path(module_path, root_path)
        import_path = f"{module_dotted_path}.{module_info.name}".strip(".")
        modules.append(import_path)

        if module_info.ispkg:
            sub_directory = str(module_path / module_info.name)
            modules.extend(generate_modules_list([sub_directory], root_directory))

    modules_paths = [Path(path) for path in directories if not os.path.isdir(path)]
    for path in modules_paths:
        modules.append(get_import_path(path, root_path))

    return modules
