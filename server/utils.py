def allowed_file(filename):
    """
    Check if a filename has an allowed file extension.

    Parameters:
        filename (str): The name of the file to be checked.

    Returns:
        bool: True if the filename has an allowed extension, False otherwise.

    """
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
