import os
import yaml
import zipfile

def zip_files_flat(source_dir, output_zip, flag=None):
    """
    Zips files from the source directory. Supports flat structure with '-j' flag.

    Args:
        source_dir (str): Path to the directory containing files to be zipped.
        output_zip (str): Path to the output zip file.
        flag (str, optional): Use '-j' to zip files without directory structure.
    """
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if flag == '-j':
                    # Add file without directory structure
                    zipf.write(file_path, arcname=file)
                else:
                    # Preserve directory structure
                    zipf.write(file_path, arcname=os.path.relpath(file_path, source_dir))
    print(f"Created zip file: {output_zip}")


if __name__ == "__main__":
    dirs = ["dev_phase", "final_phase", "scoring_program", "solution"]

    for dir in dirs:
        source_dir = f"./bundle/{dir}"
        output_zip = f"./bundle/{dir}.zip"
        zip_files_flat(source_dir, output_zip)

    zip_files_flat("bundle", "bundle.zip")
    zip_files_flat("submission", "submission.zip")