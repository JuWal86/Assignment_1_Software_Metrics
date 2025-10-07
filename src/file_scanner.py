import os

# Supported extensions for main languages
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
}

def get_source_files(path):
    files_to_analyze = []
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1]
        if ext in SUPPORTED_EXTENSIONS:
            files_to_analyze.append(path)
    else:
        for root, _, files in os.walk(path):
            for f in files:
                ext = os.path.splitext(f)[1]
                if ext in SUPPORTED_EXTENSIONS:
                    files_to_analyze.append(os.path.join(root, f))
    return files_to_analyze
