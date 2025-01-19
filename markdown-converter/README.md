# MarkDown Converter

Converts your markdown files into pdf or docx documents

###How to use

1. Install python 3.9 or newer
2. Create and activate virtual environment
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # This will work only in Linux and MacOS
    ```
3. Run the script to view help arguments
    ```bash
    python3 markdown_converter.py -h
    ```
4. Run the script with your actual file. If you do not specify a converter it will covnert to both.
    ```bash
    python3 markdown_converter.py -f test-file.md -o output
    ```
    This can also work with absolute file paths
