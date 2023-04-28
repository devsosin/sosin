import os
import zipfile

def compress(file_path_names:list[tuple], zip_path:str) -> str:
    """
    compress files to .zip
    file_path_names = [
        absolute path or relative path          target_name
        ('/Users/sosin/workspace/images/1.jpg', 'my_image.jpg')
    ]
    """
    zip_file = zipfile.ZipFile(zip_path, 'w')
    for file_path, in_file_path in file_path_names:
        zip_file.write(file_path, in_file_path, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()

    return zip_path

def extract(zip_path:str, extract_dir:str) -> str:
    """
    extract zip file to extract_dir
    """

    assert os.path.exists(extract_dir), 'extrac_dir is not exist'
    assert os.path.isdir(extract_dir), 'extract_dir is not folder'

    zip_file = zipfile.ZipFile(zip_path, 'r')
    zip_file.extractall(extract_dir)
    return extract_dir
