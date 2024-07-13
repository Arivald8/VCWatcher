import os
from openai  import OpenAI
from typing import List
from collections import defaultdict

from utils import Utils


class CompletionHandler:
    def __init__(self, api_key) -> None:
        self.client = OpenAI(api_key=api_key)
        self.commit_cache = defaultdict(list)

    def generate_commit_msg(self, diff_state: List[str]):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": Utils.content_prompt},
                {"role": "user", "content": str(diff_state)}
            ]
        )
        print(response.choices[0].message.content)
    
    def store_commit(self, file_path, changes):
        self.commit_cache[file_path].append(changes)

