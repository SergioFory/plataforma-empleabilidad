from types import SimpleNamespace
from employ_toolkit.modules import cv_builder
from pathlib import Path

def test_cv_export(tmp_path):
    client = SimpleNamespace(full_name="Tester", id=1)
    data = {
        "role_target":"Analyst",
        "summary":"Soy analista...",
        "hard_skills":["SQL"],
        "soft_skills":["Comunicación"],
        "achievements":[{"text":"Mejoré..."}],
    }
    paths = cv_builder.generate_cv_files(client, data)
    assert Path(paths["pdf"]).exists()
    assert Path(paths["docx"]).exists()
    # limpieza
    for p in paths.values(): Path(p).unlink()
