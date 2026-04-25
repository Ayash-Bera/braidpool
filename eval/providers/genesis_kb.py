import subprocess
import tempfile
import glob
import os
from pathlib import Path
from eval.providers import Provider


class GenesisPipelineProvider(Provider):
    """
    Wraps the genesis-kb/transcription_engine pipeline as a benchmarkable STT provider.

    The pipeline uses the `tstbtc transcribe` CLI (transcriber.py) with the local
    Whisper model so no cloud API keys are required. It outputs a plain-text file
    under local_models/<loc>/<slug>.txt which is read and returned.

    The server is auto-started by the CLI (`--auto-server` is the default). We pass
    `--no-db` to skip PostgreSQL, `--text` to get a .txt output file, and
    `--nocleanup` so we can read the output before it is deleted.
    """

    def __init__(
        self,
        pipeline_dir: str = "vendor/transcription_engine",
        model: str = "tiny.en",
    ):
        super().__init__(name="genesis-kb-pipeline")
        self._dir = Path(pipeline_dir)
        self._model = model

    def transcribe(self, audio_path: Path) -> str:
        audio_path = audio_path.resolve()

        with tempfile.TemporaryDirectory() as output_dir:
            result = subprocess.run(
                [
                    "python",
                    "transcriber.py",
                    "transcribe",
                    str(audio_path),
                    "--model", self._model,
                    "--text",
                    "--no-db",
                    "--nocleanup",
                    "--model_output_dir", output_dir,
                    "--loc", "eval",
                    "--username", "eval",
                    "--title", audio_path.stem,
                ],
                cwd=self._dir,
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"genesis-kb pipeline failed (exit {result.returncode}):\n"
                    f"stdout: {result.stdout}\nstderr: {result.stderr}"
                )

            # The CLI writes: <output_dir>/eval/<slug>.txt
            txt_files = glob.glob(
                os.path.join(output_dir, "**", "*.txt"), recursive=True
            )
            if not txt_files:
                raise RuntimeError(
                    f"genesis-kb pipeline produced no .txt output.\n"
                    f"stdout: {result.stdout}\nstderr: {result.stderr}"
                )

            with open(txt_files[0], "r", encoding="utf-8") as fh:
                return fh.read().strip()
