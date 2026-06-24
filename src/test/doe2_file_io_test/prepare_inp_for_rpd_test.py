from pathlib import Path

from rpd_generator.doe2_file_io.prepare_inp_for_rpd import prepare_inp


def test_prepare_inp_writes_to_requested_output_dir_and_replaces_default_loads(
    tmp_path,
):
    source = tmp_path / "model.inp"
    output_dir = tmp_path / "prepared"
    output_dir.mkdir()
    source.write_text(
        "\n".join(
            [
                "INPUT ..",
                "   LIGHTING-KW = &D",
                "   EQUIPMENT-KW = &D",
                "   OTHER = &D",
                "..",
            ]
        )
    )

    prepared_path = Path(prepare_inp(source, output_dir))

    assert prepared_path == output_dir / "model.inp"
    assert prepared_path.read_text().splitlines() == [
        "INPUT ..",
        "   LIGHTING-KW = 0",
        "   EQUIPMENT-KW = 0",
        "   OTHER = &D",
        "..",
    ]
    assert source.read_text().splitlines()[1] == "   LIGHTING-KW = &D"


def test_prepare_inp_defaults_to_temp_file_next_to_model(tmp_path):
    source = tmp_path / "building.inp"
    source.write_text("INPUT ..\n..\n")

    prepared_path = Path(prepare_inp(source))

    assert prepared_path == tmp_path / "building_temp.inp"
    assert prepared_path.read_text() == "INPUT ..\n..\n"
