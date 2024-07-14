import json
import difflib

from pathlib import Path
from typing import Dict, List, Optional

from utils.file_repr import FileRepr, FileReprEncoder
from utils.utils import Utils

class FileHistoryHandler:
    def __init__(self, utils: Utils, tree: dict = {}) -> None:
        self.root_path = Path('.')
        self.tree = tree
        self.utils = utils
        self.visited: set[Path] = set() # Cache for visited directories to avoid RecursionError
    
    def get_directory_tree(self, current_path = None) -> Dict:
        if current_path is None:
            current_path = self.root_path
        tree = {}
    

        for path in current_path.iterdir():
            file_repr = FileRepr()

            if path.is_dir():
                if path.name not in self.utils.excluded_dirs and path.resolve() not in self.visited:
                    self.visited.add(path.resolve())
                    tree[path.name] = self.get_directory_tree(path)
                    file_repr.file_path = f"{current_path}/{path.name}"

            else:
                if path.name not in self.utils.excluded_files:
                    file_repr.file_path = f"{current_path}/{path.name}"
                    try:
                        with path.open('r', encoding='utf-8') as file:
                            file_content = file.read()
                            file_repr.file_content = file_content
                    except Exception as e:
                        file_content = f"Error reading file: {e}"
                        file_repr.file_content = file_content

                    tree[path.name] = file_repr
        return tree

    def construct_tree(self) -> None:
        self.visited.clear() # Clear visited cache before constructing
        self.tree = {'.': self.get_directory_tree()}

    def show_directory_tree(self) -> None:
        print(json.dumps(self.tree, cls=FileReprEncoder, indent=4))

    def get_file_repr(self) -> Optional[FileRepr]:
        path_parts = self.utils.modified_file_path.split('\\')

        if path_parts[0] != '.':
            path_parts[0] = '.'

        current = self.tree
  
        for part in path_parts:
            if part in self.utils.excluded_dirs or part in self.utils.excluded_files:
                return f"Warning: '{self.utils.modified_file_path}' found in excluded."
            try:
                current = current[part]
            except KeyError:
                continue
        return current



    def compare_files(self, old_file: str, new_file: str) -> List[str]:
        diff = difflib.ndiff(old_file.splitlines(), new_file.splitlines())
        differences = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]

        return differences

