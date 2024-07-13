import json

class FileRepr:
    def __init__(self, file_path = None, file_content = None):
        self.file_path = file_path
        self.file_content = file_content

    def __str__(self):
        return f"File Path: {self.file_path} \n File Content: {self.file_content}"
    
    def __repr__(self):
        return f"FileRepr Object @ {self.file_path}"
    
    def to_dict(self):
        return {"FileRepr Object @": self.file_path}
    
class FileReprEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FileRepr):
            return obj.to_dict()
        return super().default(obj)
