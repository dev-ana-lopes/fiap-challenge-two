from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RENDER_SCRIPT = REPO_ROOT / "scripts" / "deploy" / "render_k8s_manifests.py"
LOCAL_ENV_FILE = REPO_ROOT / "k8s.local.env"


def test_render_k8s_manifests_injects_image_into_job_and_deployment(tmp_path: Path) -> None:
    output_dir = tmp_path / "rendered-k8s"
    image = "ghcr.io/example/service-order-api:sha-test"

    result = subprocess.run(
        [
            sys.executable,
            str(RENDER_SCRIPT),
            "--env-file",
            str(LOCAL_ENV_FILE),
            "--output-dir",
            str(output_dir),
            "--image",
            image,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    deployment = (output_dir / "deployment.yaml").read_text(encoding="utf-8")
    job = (output_dir / "job-migrate.yaml").read_text(encoding="utf-8")

    assert image in deployment
    assert image in job
    assert "__API_IMAGE__" not in deployment
    assert "__API_IMAGE__" not in job
