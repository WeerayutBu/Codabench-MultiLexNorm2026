import os
import zipfile
from datetime import datetime

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
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dirs = ["dev_phase", "final_phase", "scoring_program", "solution"]

    for dir in dirs:
        source_dir = f"./bundle/{dir}"
        output_zip = f"./bundle/{dir}.zip"
        zip_files_flat(source_dir, output_zip)

    zip_files_flat("bundle", "outputs/bundle.zip")
    # Test
    zip_files_flat("bundle/dev_phase/input_data", f"outputs/{ts}-dev_input_data.zip")
    zip_files_flat("bundle/dev_phase/reference_data", f"outputs/{ts}-dev_reference_data.zip")
    # Test
    zip_files_flat("bundle/final_phase/input_data",f"outputs/{ts}-test_input_data.zip")
    zip_files_flat("bundle/final_phase/reference_data", f"outputs/{ts}-test_reference_data.zip")
    # Scoring
    zip_files_flat("bundle/scoring_program", f"outputs/{ts}-scoring_program.zip")