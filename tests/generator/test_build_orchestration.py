from importlib import import_module

from setuptools.dist import Distribution


build_module = import_module("builder.build")
build_ext_module = import_module("builder.build_ext")


def test_build_generates_bindings_before_extension(monkeypatch, tmp_path):
    events = []
    command = build_module.build(Distribution())
    command.build_lib = str(tmp_path)
    command.model = object()

    monkeypatch.setattr(
        command,
        "get_sub_commands",
        lambda: ["build_py", "build_ext"],
    )
    monkeypatch.setattr(
        command,
        "run_command",
        lambda name: events.append(name),
    )
    monkeypatch.setattr(
        build_module.py_builder,
        "run",
        lambda path, model: events.append("generate_py"),
    )
    monkeypatch.setattr(
        build_module.mpy_builder,
        "run",
        lambda path, model: events.append("generate_mpy"),
    )
    monkeypatch.setattr(command, "_relocate_windows_extension", lambda: None)

    command.run()

    assert events == [
        "build_py",
        "generate_py",
        "generate_mpy",
        "build_ext",
    ]


def test_editable_build_generates_bindings_before_compilation(
    monkeypatch,
):
    events = []
    command = build_ext_module.build_ext(Distribution())
    command.editable_mode = True
    build_ext_module.build.model = object()

    monkeypatch.setattr(
        build_ext_module.py_builder,
        "run",
        lambda path, model: events.append("generate_py"),
    )
    monkeypatch.setattr(
        build_ext_module.mpy_builder,
        "run",
        lambda path, model: events.append("generate_mpy"),
    )
    monkeypatch.setattr(
        build_ext_module._build_ext,
        "run",
        lambda self: events.append("build_ext"),
    )

    command.run()

    assert events == ["generate_py", "generate_mpy", "build_ext"]
