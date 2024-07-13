# VCWatcher

VCWatcher (Version Control Watcher) is an automated tool that helps you generate professional commit messages, without the need to manually track changes, or remember what was modified.

VCWatcher does not rely on any third-party version control systems such as git, and so it can be used with any. 

After making changes to your project, just use the 'commit-generate' command, and VCWatcher will create a concise and informative commit message for your changes, leveraging the OpenAI LLM to process the differences.

## Features
- Automatic Change Tracking: Monitor file changes automatically.
- Automatic Commit Messages: Generate detailed commit messages with an LLM.
- Easy to Use: A single command to generate commit message for all changes.
- Customizable: Easily specify which directory to observe, and which should be excluded.
- Low dependency count: Only 4 external dependencies.

## Table of Contents
- [Installation]()
- [Usage]()
- [Configuration]()
- [License]()

## Installation

To get started with VCWatcher, follow these steps:

1. Clone or download the repository:
    ```
    $ git clone https://github.com/Arivald8/VCWatcher.git
    $ cd vcwatcher
    ```

2. Install required dependencies:
    It is recommended to use a virutal environment for your dependencies.
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
    -------------------------------------
    VCWatcher is observing ....
    ```
    To use the root directory of vcwatcher.py (Note the trailing dot):
    ```
    $ python vcwatcher.py .
    ```

2. Start making changes to your files.

3. When ready, use the commands:
    - To generate a commit message, simply save all your files and then use `commit-generate` in the terminal.
    - To exit, type `exit` or `quit`

Example:
```
$ python vcwatcher.py .

VCWatcher is observing ....

Enter 'commit-generate' to collect diffs and generate a message.

Enter 'exit' or 'quit' to close VCWatcher.

> commit-generate

 Generated commit message:
+ Updated README.md to reflect changes in VCWatcher functionality and usage.
+ Improved description of how VCWatcher automates the generation of professional commit messages.
+ Clarified that VCWatcher does not rely on third-party version control systems like git.
+ Added instructions on how to use the 'commit-generate' command for creating informative commit messages.
+ Enhanced information on the automatic generation of detailed commit messages using an LLM.
+ Made README.md more user-friendly by specifying how to exclude directories or files from monitoring.
+ Expanded the guide on cloning or downloading the repository, highlighting the importance of using a virtual environment for dependencies.
+ Provided detailed steps on how to utilize the root directory of vcwatcher.py for monitoring changes.
+ Enhanced the list of excluded directories and files to be more explicit.
+ Included a new section in README.md explaining how VCWatcher works, including details on vcwatcher.py and its dependencies.
+ Added information on the entry point of VCWatcher and its utilization of watchdog and dotenv dependencies.
+ Updated README.md with an explanation of how to configure and customize the API key in VCWatcher.
+ Included details on helper class objects in the constructor for efficient state management.
+ Expanded the documentation on the utility classes and their roles within VCWatcher.
```


## Configuration
Customize VCWatcher by modifying the `utils/utils.py` file:

- **Debounce Time**: Set the time interval to check for changes:
    ```
    self.debounce_time: int = 1 # Debounce time in seconds
    ```

- **Excluded Directories and Files**: Speficy directories and files to be excluded from monitoring. By default they are:
    ```
    self.excluded_dirs = {'node_modules', '.git', '__pycache__', 'venv'}
    self.excluded_files = {'db.sqlite3', '.gitignore', 'package-lock.json', '.env'}
    ```

- **Completion prompts**: Modify system, or user prompts for the LLM.

    You can modify the default system and user prompts for the LLM to resolve. You can add additional instructions, or change them completely.

## How it works

### vcwatcher.py
This is the entry point for the tool. It imports some importatnt built-ins, third-party dependencies and self-defined utilities.

At its core, VCWatcher utilizes [watchdog](https://pypi.org/project/watchdog/) to monitor any changes within a directory. It also uses [dotenv](https://pypi.org/project/python-dotenv/) to help load the API key from the `.env` file. This is only imported in vcwatcher.py, and loaded in the `__init__` method of VCWatcher. If you don't want to use it, you only have to remove three lines of code. You can simply remove it from the requirements, then the import statement, and finally `load_dotenv()` from VCWatcher `__init__` method.

---
### class VCWatcher
When creating an instance of VCWatcher, you must pass the `API_KEY` as an argument. If using `.env`, this will be populated automatically by `self.api_key = os.getenv(API_KEY)`:
```
watch = VCWatcher("API_KEY")
```
If you would like to name your key differently in the `.env` file, you would then change it accordingly:
```
watch = VCWacher("YOU_CALLED_IT_SUPER_KEY")
```
---
Four helper class objects are included in the constructor, so as to easily manage state across the tool:

1. `Utils`

    A small utility class - contains some constant values such as completion prompt, directories and files to be excluded from monitoring, debounce time and others. 

2. `CompletionHandler`

    Holds staged/saved changes throghout the lifecycle, and calls the OpenAI API to generate a commit message. 

3. `FileHistoryHandler`

    Utilizes pathlib to traverse directories. It is responsible for constructing a directory tree in a Python dictionary format, as well as it allows to view the constructed tree in a nicely formatted json dump:

    ```
    {
        ".": {
            "handlers": {
                "completion_handler.py": {
                    "FileRepr Object @": "handlers/completion_handler.py"
                },
                "file_event_handler.py": {
                    "FileRepr Object @": "handlers/file_event_handler.py"
                },
                "file_history_handler.py": {
                    "FileRepr Object @": "handlers/file_history_handler.py"
                }
            },
            "LICENSE": {
                "FileRepr Object @": "./LICENSE"
            },
            "README.md": {
                "FileRepr Object @": "./README.md"
            },
            "requirements.txt": {
                "FileRepr Object @": "./requirements.txt"
            },
            "test_watcher.py": {
                "FileRepr Object @": "./test_watcher.py"
            },
            "utils": {
                "file_repr.py": {
                    "FileRepr Object @": "utils/file_repr.py"
                },
                "utils.py": {
                    "FileRepr Object @": "utils/utils.py"
                }
            },
            "vcwatcher.py": {
                "FileRepr Object @": "./vcwatcher.py"
            }
        }
    }
    ```
    It is within this class that you can find file comparison methods or get file representation objects.

4. `FileEventHandler`
    This helper is defined within the constructor last, because it requires the previous utilities and helper states.

    This class has only a single method `on_modified` which is triggered every time a monitored file is saved by the user.

    First, it checks if debounce time is greater than the time of last modification. If so, it stores the file path of the modified files in a Utils constant. 
    
    Then, it stores the state of the file contents **before** modification, it reconstructs the tree with new changes, and stores the state of the file **after** changes. Both are then compared and stored in memory. 
---
#### def log_api_key(self) -> str:
This is just a convenience method to verify that an API key was indeed loaded correctly. 

#### def observe_dir(self) -> None:
Creates an instance of `Observer` from `watchdog.observers`, and runs the observer.

#### def start_observing_in_thread(self) -> None:
A simple method to run the `observe_dir` method with the use of threading. This is because watchdog is blocking, and users must be able to provide a command to generate a commit message.

#### def run(self) -> None:
It ingests sys.argvs passed when calling `python vcwatcher.py` and creates a pathlib Path object from the root path. 

Once path is set, it constructs a directory tree for the first time, storing all file states as they appear **before** any changes. Finally, it calls `start_observing_in_thread` and awaits user command input. 


