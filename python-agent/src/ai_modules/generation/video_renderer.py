"""DH_live mini digital human video rendering service."""

from __future__ import annotations

import gzip
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import cv2
import numpy as np
import torch


_DH_LIVE_DIR = Path(__file__).resolve().parent / "dh_live"
if str(_DH_LIVE_DIR) not in sys.path:
    sys.path.insert(0, str(_DH_LIVE_DIR))


class VideoRendererService:
    """Wraps the DH_live mini pipeline for talking-head video generation."""

    def __init__(self, checkpoint_dir: Path | str | None = None, avatar_data_dir: Path | str | None = None) -> None:
        if checkpoint_dir is None:
            checkpoint_dir = _DH_LIVE_DIR / "checkpoint"
        if avatar_data_dir is None:
            avatar_data_dir = _DH_LIVE_DIR / "avatar_data"
        self.checkpoint_dir = Path(checkpoint_dir)
        self.avatar_data_dir = Path(avatar_data_dir)
        self._setup_headless_display()

    @staticmethod
    def _setup_headless_display() -> None:
        if sys.platform == "linux" and not os.environ.get("DISPLAY"):
            os.environ.setdefault("DISPLAY", ":99")

    # ── Avatar preprocessing (one-time) ──────────────────────────────────

    def preprocess_avatar(self, video_path: Path | str, output_dir: Path | str | None = None) -> Path:
        """Preprocess an avatar video for DH_live, producing combined_data.json.gz.

        Returns the avatar data directory.
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir) if output_dir else self.avatar_data_dir

        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is required for avatar preprocessing")

        # Stage 1: data_preparation_mini — convert video + extract keypoints
        from data_preparation_mini import data_preparation_mini

        data_preparation_mini(str(video_path), str(output_dir), resize_option=False)

        # Stage 2: data_preparation_web — generate combined_data.json.gz
        from data_preparation_web import data_preparation_web

        data_preparation_web(str(output_dir))

        return output_dir

    # ── Video rendering ──────────────────────────────────────────────────

    def render_talking_video(
        self,
        audio_path: Path | str,
        output_video_path: Path | str,
    ) -> Path:
        """Generate a talking-head video from audio + preprocessed avatar.

        Args:
            audio_path: Path to audio file (WAV 16kHz mono preferred).
            output_video_path: Desired output MP4 path.

        Returns:
            Path to the rendered video.
        """
        audio_path = Path(audio_path)
        output_video_path = Path(output_video_path)
        assets_dir = self.avatar_data_dir / "assets"

        if not (assets_dir / "combined_data.json.gz").exists():
            raise FileNotFoundError(
                f"Avatar data not found at {assets_dir}. Run preprocess_avatar() first."
            )

        lstm_ckpt = str(self.checkpoint_dir / "lstm" / "lstm_model_epoch_325.pkl")
        dinet_ckpt = str(self.checkpoint_dir / "DINet_mini" / "epoch_40.pth")

        if not Path(lstm_ckpt).exists():
            raise FileNotFoundError(f"LSTM checkpoint not found: {lstm_ckpt}")
        if not Path(dinet_ckpt).exists():
            raise FileNotFoundError(f"DINet checkpoint not found: {dinet_ckpt}")

        # Prepare audio: convert MP3 → WAV if needed
        wav_path = self._ensure_wav(audio_path)

        # Load models
        from talkingface.model_utils import Audio2bs, LoadAudioModel

        audio_model = LoadAudioModel(lstm_ckpt)

        from talkingface.render_model_mini import RenderModel_Mini
        from mini_live.render import create_render_model
        from talkingface.models.DINet_mini import input_height, input_width, model_size
        from talkingface.data.few_shot_dataset import get_image

        render_model_mini = RenderModel_Mini()
        render_model_mini.loadModel(dinet_ckpt)

        standard_size = model_size * 2
        crop_rotio = [0.5, 0.5, 0.5, 0.5]
        out_w = int(standard_size * (crop_rotio[0] + crop_rotio[1]))
        out_h = int(standard_size * (crop_rotio[2] + crop_rotio[3]))
        out_size = (out_w, out_h)
        render_model_gl = create_render_model(out_size, floor=20)

        # Load preprocessed avatar data
        combined_data_path = assets_dir / "combined_data.json.gz"
        with gzip.open(combined_data_path, "rt", encoding="UTF-8") as f:
            combined_data = json.load(f)

        face3D_obj = combined_data["face3D_obj"]
        json_data = combined_data["json_data"]
        ref_data = np.array(combined_data["ref_data"], dtype=np.float32).reshape(
            [1, 20, input_height // 4, input_width // 4]
        )

        render_model_mini.net.infer_model.ref_in_feature = (
            torch.from_numpy(ref_data).float().to(self._device())
        )

        # Read avatar video frames
        video_path = str(self.avatar_data_dir / "assets" / "01.mp4")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open avatar video: {video_path}")
        vid_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        list_source_crop_rect = []
        list_video_img = []
        list_standard_img = []
        list_standard_v = []

        for frame_index in range(min(vid_frame_count, len(json_data))):
            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            standard_v = json_data[frame_index]["points"][16:]
            source_crop_rect = json_data[frame_index]["rect"]
            standard_img = get_image(frame, source_crop_rect, input_type="image", resize=standard_size)

            list_video_img.append(frame)
            list_source_crop_rect.append(source_crop_rect)
            list_standard_img.append(standard_img)
            list_standard_v.append(np.array(standard_v).reshape(-1, 2) * 2)
        cap.release()

        mat_list = [np.array(i["points"][:16]).reshape(4, 4) * 2 for i in json_data]

        # Reverse-padding for smoother loop
        list_video_img += list_video_img[::-1]
        list_source_crop_rect += list_source_crop_rect[::-1]
        list_standard_img += list_standard_img[::-1]
        list_standard_v += list_standard_v[::-1]
        mat_list += mat_list[::-1]

        # Generate VBO from face wrap data
        from talkingface.models.DINet_mini import model_size

        v_ = []
        for line in face3D_obj:
            if line.startswith("v "):
                parts = line[2:].split()
                v_.extend(float(p) for p in parts)
        face_wrap_entity = np.array(v_).reshape(-1, 5)
        render_model_gl.GenVBO(face_wrap_entity)

        # Audio → BlendShape
        bs_array = Audio2bs(str(wav_path), audio_model)[5:] * 0.5

        # Render frames
        task_id = str(uuid.uuid1())
        temp_video = self.avatar_data_dir / f"_temp_{task_id}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            str(temp_video), fourcc, 25, (int(vid_width), int(vid_height))
        )

        device = self._device()
        for frame_index in range(len(bs_array)):
            src_idx = frame_index % len(mat_list)
            bs = np.zeros([12], dtype=np.float32)
            bs[:6] = bs_array[src_idx, :6]
            bs[1] = bs[1] / 2 * 1.6

            verts_frame_buffer = np.array(list_standard_v)[src_idx, :, :2].copy() / model_size - 1

            rgba = render_model_gl.render2cv(
                verts_frame_buffer,
                out_size=out_size,
                mat_world=mat_list[src_idx],
                bs_array=bs,
            )
            rgba = rgba[::2, ::2, :]
            gl_tensor = torch.from_numpy(rgba / 255.0).float().permute(2, 0, 1).unsqueeze(0)
            source_tensor = cv2.resize(list_standard_img[src_idx], (model_size, model_size))
            source_tensor = torch.from_numpy(source_tensor / 255.0).float().permute(2, 0, 1).unsqueeze(0)

            warped_img = render_model_mini.interface(source_tensor.to(device), gl_tensor.to(device))

            image_numpy = warped_img.detach().squeeze(0).cpu().float().numpy()
            image_numpy = np.transpose(image_numpy, (1, 2, 0)) * 255.0
            image_numpy = image_numpy.clip(0, 255).astype(np.uint8)

            x_min, y_min, x_max, y_max = list_source_crop_rect[src_idx]
            img_face = cv2.resize(image_numpy, (x_max - x_min, y_max - y_min))
            img_bg = list_video_img[src_idx][:, :, :3].copy()
            img_bg[y_min:y_max, x_min:x_max, :3] = img_face[:, :, :3]

            video_writer.write(img_bg[:, :, ::-1])
        video_writer.release()

        # Merge audio + video with ffmpeg
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(temp_video),
                "-i", str(wav_path),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-shortest",
                str(output_video_path),
            ],
            capture_output=True,
            timeout=120,
            check=True,
        )

        try:
            temp_video.unlink()
        except OSError:
            pass

        return output_video_path

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _device() -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _ensure_wav(self, audio_path: Path) -> Path:
        """Convert audio to 16kHz mono WAV if needed."""
        if audio_path.suffix.lower() == ".wav":
            return audio_path

        wav_path = audio_path.with_suffix(".wav")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(audio_path),
                "-ar", "16000",
                "-ac", "1",
                str(wav_path),
            ],
            capture_output=True,
            timeout=30,
            check=True,
        )
        return wav_path
