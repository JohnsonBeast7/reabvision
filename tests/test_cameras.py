from reabvision.app.cameras import _linux_cameras


def make_dev(root, n, name, index):
    d = root / f"video{n}"
    d.mkdir()
    (d / "name").write_text(name + "\n")
    (d / "index").write_text(f"{index}\n")


def test_linux_keeps_only_capture_nodes(tmp_path):
    make_dev(tmp_path, 0, "USB PHY 2.0: USB CAMERA", 0)
    make_dev(tmp_path, 1, "USB PHY 2.0: USB CAMERA", 1)
    make_dev(tmp_path, 2, "Logitech: C920", 0)
    make_dev(tmp_path, 3, "Logitech: C920", 1)
    make_dev(tmp_path, 10, "Integrated Webcam", 0)
    assert _linux_cameras(tmp_path) == [
        (0, "USB CAMERA"),
        (2, "C920"),
        (10, "Integrated Webcam"),
    ]
