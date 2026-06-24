from pathlib import Path


def prepare_inp(model_path: Path, output_dir: Path = None) -> str:
    """
    Prepares an inp file for processing by removing diagnostics and setting lighting and equipment to 0.
    Creates a temporary file in the same directory as the model unless an output_dir is specified.
    :param model_path:
    :param output_dir:
    :return:
    """
    model_dir = model_path.parent
    model_name = model_path.name
    base_name = model_path.stem
    extension = model_path.suffix

    if output_dir:
        temp_file_path = output_dir / model_name
    else:
        temp_file_path = model_dir / f"{base_name}_temp{extension}"

    with Path(model_path).open("r") as inp_file, temp_file_path.open("w") as out_file:
        lines_after_target = 0

        for line in inp_file:

            if "$              Abort, Diagnostics" in line:
                lines_after_target = 3

            elif lines_after_target == 1:
                out_file.write("DIAGNOSTIC COMMENTS ..")
                lines_after_target = 0
            elif lines_after_target > 0:
                lines_after_target -= 1

            elif line.lstrip().startswith("LIGHTING-KW"):
                line = line.replace("&D", "0")

            elif line.lstrip().startswith("EQUIPMENT-KW"):
                line = line.replace("&D", "0")

            out_file.write(line)
    return str(temp_file_path)
