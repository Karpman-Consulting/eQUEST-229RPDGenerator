import shutil


def copy_files_to_temp_dir(inp_path, temp_dir):
    file_extensions = [".erp", ".lrp", ".srp", ".nhk"]
    model_dir = inp_path.parent
    model_name = inp_path.stem

    for ext in file_extensions:

        model_file = model_dir / f"{model_name}{ext}"
        alternate_search_file = model_dir / f"{model_name} - Baseline Design{ext}"

        if model_file.exists():
            shutil.copy2(model_file, temp_dir)

        elif alternate_search_file.exists():
            destination_file = temp_dir / f"{model_name}{ext}"
            shutil.copy2(alternate_search_file, destination_file)

        else:
            print(f"File {model_file} not found in {model_dir}")
