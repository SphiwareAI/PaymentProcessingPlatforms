import os

def print_directory_contents(path):
    """
    This function takes a path to a directory and prints the contents
    of that directory as well as any subdirectories recursively.
    """
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print_directory_contents(full_path)
        else:
            print(full_path)

# Replace the path with the path to your project directory
print_directory_contents('/Users/james/Documents/payPlatonium')

