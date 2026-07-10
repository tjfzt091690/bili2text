import os
import uuid
import threading
from typing import Optional

from flask import Flask, render_template, request, jsonify, send_from_directory

from config import config
from logger import logger


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

    task_store = {}

    from utils import download_video, get_bv_from_url_info, ensure_folders_exist
    from exAudio import process_audio_split, convert_video_to_mp3, split_mp3
    from speech2text import whisper_stt

    os.makedirs(config.VIDEO_BASE_DIR, exist_ok=True)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/download", methods=["POST"])
    def api_download():
        data = request.get_json(force=True)
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400

        task_id = str(uuid.uuid4())[:8]
        task_store[task_id] = {
            "type": "download",
            "url": url,
            "status": "pending",
            "progress": "",
            "result": None,
            "error": None,
        }

        def _run():
            try:
                task_store[task_id]["status"] = "running"
                task_store[task_id]["progress"] = "Resolving BV number..."
                bv = get_bv_from_url_info(url)
                task_store[task_id]["progress"] = f"Downloading {bv}..."
                filepath = download_video(bv, url)
                task_store[task_id]["status"] = "done"
                task_store[task_id]["result"] = filepath
                task_store[task_id]["progress"] = "Download complete"
            except Exception as e:
                logger.error("Download task failed: %s", str(e))
                task_store[task_id]["status"] = "error"
                task_store[task_id]["error"] = str(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return jsonify({"task_id": task_id})

    @app.route("/api/video-dirs", methods=["GET"])
    def api_video_dirs():
        base_dir = config.VIDEO_BASE_DIR
        if not os.path.isdir(base_dir):
            return jsonify({"dirs": []})
        dirs = []
        for entry in sorted(os.listdir(base_dir)):
            full_path = os.path.join(base_dir, entry)
            if os.path.isdir(full_path):
                files = os.listdir(full_path)
                video_files = [f for f in files if f.endswith((".mp4", ".flv", ".mkv", ".avi"))]
                dirs.append({
                    "name": entry,
                    "path": full_path,
                    "video_count": len(video_files),
                    "videos": video_files,
                })
        return jsonify({"dirs": dirs})

    @app.route("/api/audio-split", methods=["POST"])
    def api_audio_split():
        data = request.get_json(force=True)
        dir_name = data.get("dir_name", "").strip()
        if not dir_name:
            return jsonify({"error": "dir_name is required"}), 400

        full_dir = os.path.join(config.VIDEO_BASE_DIR, dir_name)
        if not os.path.isdir(full_dir):
            return jsonify({"error": f"Directory not found: {full_dir}"}), 404

        task_id = str(uuid.uuid4())[:8]
        task_store[task_id] = {
            "type": "audio_split",
            "dir_name": dir_name,
            "status": "pending",
            "progress": "",
            "result": None,
            "error": None,
        }

        def _run():
            try:
                task_store[task_id]["status"] = "running"
                task_store[task_id]["progress"] = "Extracting audio..."
                folder_name = process_audio_split(dir_name)
                task_store[task_id]["status"] = "done"
                task_store[task_id]["result"] = folder_name
                task_store[task_id]["progress"] = "Audio split complete"
            except Exception as e:
                logger.error("Audio split task failed: %s", str(e))
                task_store[task_id]["status"] = "error"
                task_store[task_id]["error"] = str(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return jsonify({"task_id": task_id})

    @app.route("/api/slice-dirs", methods=["GET"])
    def api_slice_dirs():
        base_dir = config.AUDIO_SLICE_DIR
        if not os.path.isdir(base_dir):
            return jsonify({"dirs": []})
        dirs = []
        for entry in sorted(os.listdir(base_dir), reverse=True):
            full_path = os.path.join(base_dir, entry)
            if os.path.isdir(full_path):
                files = [f for f in os.listdir(full_path) if f.endswith(".mp3")]
                dirs.append({
                    "name": entry,
                    "path": full_path,
                    "slice_count": len(files),
                })
        return jsonify({"dirs": dirs})

    @app.route("/api/transcribe", methods=["POST"])
    def api_transcribe():
        data = request.get_json(force=True)
        folder_name = data.get("folder_name", "").strip()
        model = data.get("model", "tiny")
        prompt = data.get("prompt", "以下是普通话的句子。")
        if not folder_name:
            return jsonify({"error": "folder_name is required"}), 400

        task_id = str(uuid.uuid4())[:8]
        task_store[task_id] = {
            "type": "transcribe",
            "folder_name": folder_name,
            "status": "pending",
            "progress": "",
            "result": None,
            "error": None,
        }

        def _run():
            try:
                task_store[task_id]["status"] = "running"
                task_store[task_id]["progress"] = "Loading model..."

                def on_progress(current, total, text):
                    task_store[task_id]["progress"] = f"Transcribing {current}/{total}"

                output_path = whisper_stt.run_analysis(
                    folder_name, model=model, prompt=prompt,
                    progress_callback=on_progress,
                )
                task_store[task_id]["status"] = "done"
                task_store[task_id]["result"] = output_path
                task_store[task_id]["progress"] = "Transcription complete"
            except Exception as e:
                logger.error("Transcribe task failed: %s", str(e))
                task_store[task_id]["status"] = "error"
                task_store[task_id]["error"] = str(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return jsonify({"task_id": task_id})

    @app.route("/api/task/<task_id>", methods=["GET"])
    def api_task_status(task_id):
        task = task_store.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task)

    @app.route("/api/outputs", methods=["GET"])
    def api_outputs():
        output_dir = config.OUTPUT_DIR
        if not os.path.isdir(output_dir):
            return jsonify({"files": []})
        files = []
        for f in sorted(os.listdir(output_dir), reverse=True):
            if f.endswith(".txt"):
                files.append({
                    "name": f,
                    "path": os.path.join(output_dir, f),
                })
        return jsonify({"files": files})

    @app.route("/api/output/<path:filename>", methods=["GET"])
    def api_download_output(filename):
        return send_from_directory(config.OUTPUT_DIR, filename, as_attachment=True)

    return app

