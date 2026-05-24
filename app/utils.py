def is_supported_file(filename):

    supported_extensions = [
        ".tf",
        ".yaml",
        ".yml"
    ]

    return any(
        filename.endswith(ext)
        for ext in supported_extensions
    )
