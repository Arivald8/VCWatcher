# VCWatcher

VCWatcher (Version Control Watcher) is an automated tool that helps you generate professional commit messages without the need to manually track changes, or remember what was modified. 

After making changes to your project, just use the 'commit-generate' command, and VCWatcher will create a concise and informative commit message for you, leveraging the OpenAI LLM API to process the differences.

## Features
- Automatic Change Tracking: Monitor file changes automatically.
- Professional Commit Message: Generate detailed commit messages using OpenAI API.
- Easy to Use: A single command to generate commit message for all changes.
- Customizable: Easily exclude directories or files from monitoring.

## Table of Contents
- [Installation]()
- [Usage]()
- [Configuration]()
- [License]()

## Installation

To get started with VCWatcher, follow these steps:

1. Clone the repository:
    ```
    $ git clone https://github.com/Arivald8/VCWatcher.git
    $ cd vcwatcher
    ```

2. Install required dependencies:
    ```
    $ pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    echo "API_KEY=your_openai_api_key" > .env
    ```

## Usage
VCWatcher is easy to use. 

Here is a quick guide to get you started:

1. Initialize VCWatcher:
    ```
    $ python vcwatcher.py <directory/to/monitor>
    ```
    For example:
    ```
    $ python vcwatcher.py G:/dev/project/
    ```

2. Start making changes to your files.

3. When ready, use the commands:
    - To generate a commit message, save all your files and use `commit-generate` in the terminal.
    - To exit, type `exit` or `quit`


## Configuration
Customize VCWatcher by modifying the `utils/utils.py` file:

- **Debounce Time**: Set the time interval to check for changes:
    ```
    self.debounce_time: int = 1 # Debounce time in seconds
    ```

- **Excluded Directories and Files**: Speficy directories and files to exclude from monitoring. By default they are:
    ```
    self.excluded_dirs = {'node_modules', '.git', '__pycache__', 'venv'}
    self.excluded_files = {'db.sqlite3', '.gitignore', 'package-lock.json', '.env'}
    ```

- **Completion prompts**: Modify system or user prompts for the LLM.

    You can modify the default system and user prompts for the LLM to resolve. You can add additional instructions, or change them completely.

