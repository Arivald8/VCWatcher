import os
from openai  import OpenAI
from typing import List
from collections import defaultdict

from utils.utils import Utils

class CompletionHandler:
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.commit_cache: defaultdict[str, List[str]] = defaultdict(list)
            
    def store_commit(self, file_path: str, changes: List[str]) -> None:
        self.commit_cache[file_path].append(changes)

    def generate_commit_msg(self, diff_state: List[str]) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": Utils.content_prompt},
                {"role": "user", "content": str(diff_state)}
            ]
        )
        commit_header = "\n Generated commit message: \n"
        commit_msg = response.choices[0].message.content
        return commit_header + commit_msg
    


