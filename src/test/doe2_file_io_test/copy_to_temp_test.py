from rpd_generator.doe2_file_io.copy_to_temp import copy_files_to_temp_dir


def test_copy_files_to_temp_dir_copies_matching_model_files_and_baseline_aliases(
    tmp_path, capsys
):
    model_dir = tmp_path / "model"
    temp_dir = tmp_path / "temp"
    model_dir.mkdir()
    temp_dir.mkdir()
    inp_path = model_dir / "Case.inp"
    inp_path.write_text("")
    (model_dir / "Case.erp").write_text("erp")
    (model_dir / "Case - Baseline Design.lrp").write_text("baseline lrp")

    copy_files_to_temp_dir(inp_path, temp_dir)

    assert (temp_dir / "Case.erp").read_text() == "erp"
    assert (temp_dir / "Case.lrp").read_text() == "baseline lrp"
    captured = capsys.readouterr()
    assert "Case.srp" in captured.out
    assert "Case.nhk" in captured.out


def test_copy_files_to_temp_dir_prefers_exact_model_file_over_baseline_alias(tmp_path):
    model_dir = tmp_path / "model"
    temp_dir = tmp_path / "temp"
    model_dir.mkdir()
    temp_dir.mkdir()
    inp_path = model_dir / "Case.inp"
    inp_path.write_text("")
    (model_dir / "Case.srp").write_text("exact srp")
    (model_dir / "Case - Baseline Design.srp").write_text("baseline srp")

    copy_files_to_temp_dir(inp_path, temp_dir)

    assert (temp_dir / "Case.srp").read_text() == "exact srp"
