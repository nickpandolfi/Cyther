import os


def isValid(file):
    """
    Figures out if the file had previously errored and hasn't been fixed since
    Args:
        file (dict): File dict to be inspected
    Returns (bool): If the file is valid for compilation
    """
    modified_time = os.path.getmtime(file['file_path'])
    valid = modified_time > file['stamp_if_error']
    return valid


def isOutDated(file):
    """
    Figures out if Cyther should compile the given file by checking the source code and compiled object
    Args:
        file (dict): File dict to be inspected
    Returns (bool): If the file is outdated, and needs compilation
    """
    if os.path.exists(file['output_name']):
        source_time = os.path.getmtime(file['file_path'])
        output_time = os.path.getmtime(file['output_name'])
        if source_time > output_time:
            return True
    else:
        return True
    return False
