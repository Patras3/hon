import os
import re
import sys

def preserve_case_replace(match):
    original_text = match.group(0)
    if original_text.islower():
        return 'hon22'
    elif original_text.isupper():
        return 'HON22'
    elif original_text.istitle():
        return 'Hon22'
    else:
        # Handle mixed case or other variations
        result = []
        for i, char in enumerate(original_text):
            if char.islower():
                result.append('hon22'[i % 4].lower())
            else:
                result.append('hon22'[i % 4].upper())
        return ''.join(result)

def replace_string_in_name(name):
    pattern = re.compile(r'hon2', re.IGNORECASE)
    # Replace only if the name contains 'hon2' but not 'hon22'
    if re.search(r'hon2', name, re.IGNORECASE) and not re.search(r'hon22', name, re.IGNORECASE):
        new_name = pattern.sub(preserve_case_replace, name)
        return new_name
    return name

def replace_string_in_file(filepath):
    try:
        pattern = re.compile(r'hon2', re.IGNORECASE)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        new_content = pattern.sub(preserve_case_replace, content)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as file:
                file.write(new_content)
    except PermissionError:
        # Skip files that cannot be accessed
        print(f"Permission denied: {filepath}")

def rename_files_and_directories(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Skip directories containing 'git'
        dirnames[:] = [d for d in dirnames if 'git' not in d]

        # Rename files
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            new_filename = replace_string_in_name(filename)
            new_filepath = os.path.join(dirpath, new_filename)
            if new_filename != filename:
                os.rename(filepath, new_filepath)
                filepath = new_filepath

            # Replace content in text files
            replace_string_in_file(filepath)

        # Rename directories
        for dirname in dirnames:
            new_dirname = replace_string_in_name(dirname)
            if new_dirname != dirname:
                os.rename(
                    os.path.join(dirpath, dirname),
                    os.path.join(dirpath, new_dirname)
                )

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python2 rename_hon2.py <directory_path>")
        sys.exit(1)

    root_directory = sys.argv[1]
    if not os.path.isdir(root_directory):
        print(f"The specified directory does not exist: {root_directory}")
        sys.exit(1)

    rename_files_and_directories(root_directory)
