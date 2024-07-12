from pathlib import Path
from file_repr import FileRepr, FileReprEncoder

import json

class FileHistoryHandler:
    def __init__(self, utils, tree: dict = {}) -> None:
        self.root_path = Path('.')
        self.tree = tree
        self.utils = utils
        self.visited = set() # Cache for visited directories to avoid RecursionError
    
    def get_directory_tree(self, current_path = None):
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

    def construct_tree(self):
        self.visited.clear() # Clear visited cache before constructing
        self.tree = {'.': self.get_directory_tree()}

    def show_directory_tree(self):
        print(json.dumps(self.tree, cls=FileReprEncoder, indent=4))


    def get_file_repr(self):
        path_parts = self.utils.modified_file_path.split('\\')

        current = self.tree
        # Traverse tree
        try:
            for part in path_parts:
                if part in self.utils.excluded_dirs or part in self.utils.excluded_files:
                    return f"Warning: '{self.utils.modified_file_path}' found in excluded."
                current = current[part]
            return current

        except KeyError:
            print(f"Error: '{self.utils.modified_file_path}' not found in the directory tree.")

    def get_changed_file_repr(self):
        