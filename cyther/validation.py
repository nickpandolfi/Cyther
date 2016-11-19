import os


def isValid(file_path, error_stamp):
    """
    Figures out if the file had previously errored and hasn't been fixed since
    """
    modified_time = os.path.getmtime(file_path)
    valid = modified_time > error_stamp
    return valid


def isOutDated(file_path, output_name):
    """
    Figures out if Cyther should compile the given file by checking the source
    code and compiled object
    """
    if os.path.exists(output_name):
        source_time = os.path.getmtime(file_path)
        output_time = os.path.getmtime(output_name)
        if source_time > output_time:
            return True
    else:
        return True
    return False
