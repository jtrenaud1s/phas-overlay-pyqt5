import os
import pathspec

def load_gitignore(gitignore_path=".gitignore"):
    with open(gitignore_path, 'r') as file:
        gitignore = file.read()
    return pathspec.PathSpec.from_lines('gitwildmatch', gitignore.splitlines())

def generate_context(base_path="."):
    gitignore = load_gitignore()
    context = {}

    for root, dirs, files in os.walk(base_path):
        for file in files:
            path = os.path.join(root, file)
            relative_path = os.path.relpath(path, base_path)

            if not gitignore.match_file(relative_path):
                with open(path, "r") as file:
                    try:
                        content = file.read()
                        context[relative_path] = content
                    except Exception as e:
                        print(f"Error reading file {path}: {e}")

    return context

def write_context_to_file(context, output_file="context.txt"):
    with open(output_file, "w") as file:
        for path, content in context.items():
            file.write(f"For context, here is the file at path '{path}':\n\n")
            file.write(content)
            file.write("\n\n")

context = generate_context()
write_context_to_file(context)