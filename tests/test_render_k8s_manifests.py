from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RENDER_SCRIPT = REPO_ROOT / "scripts" / "deploy" / "render_k8s_manifests.py"


def test_render_k8s_manifests_injects_image_into_job_and_deployment(
    tmp_path: Path,
) -> None:
    env_file = tmp_path / "k8s.env"
    output_dir = tmp_path / "rendered-k8s"
    image = "ghcr.io/example/service-order-api:sha-test"
    env_file.write_text(
        "\n".join(
            [
                "DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db",
                "JWT_SECRET=jwt-secret-for-tests",
                "APPROVAL_TOKEN_SECRET=approval-secret-for-tests",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(RENDER_SCRIPT),
            "--env-file",
            str(env_file),
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
