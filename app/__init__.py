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
    app.config["MAX_CONTENT_LENGTH"] = config.FLASK_MAX_CONTENT_LENGTH

    task_store = {}

    from utils import download_video, get_bv_from_url_info
    from exAudio import process_audio_split
    from speech2text import whisper_stt
    from llm_service import llm_service

    os.makedirs(config.VIDEO_BASE_DIR, exist_ok=True)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/config", methods=["GET"])
    def api_config():
        return jsonify({
            "whisper_model": config.WHISPER_MODEL,
            "whisper_default_prompt": config.WHISPER_DEFAULT_PROMPT,
            "slice_length_ms": config.SLICE_LENGTH_MS,
            "llm_provider": config.LLM_PROVIDER,
            "llm_model": config.LLM_MODEL,
        })

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
                task_store[task_id]["result"] = {"path": filepath, "bv": bv}
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
                total_size = sum(
                    os.path.getsize(os.path.join(full_path, f))
                    for f in video_files
                    if os.path.isfile(os.path.join(full_path, f))
                )
                dirs.append({
                    "name": entry,
                    "path": full_path,
                    "video_count": len(video_files),
                    "videos": video_files,
                    "size_mb": round(total_size / 1024 / 1024, 1),
                })
        return jsonify({"dirs": dirs})

    @app.route("/api/audio-split", methods=["POST"])
    def api_audio_split():
        data = request.get_json(force=True)
        dir_name = data.get("dir_name", "").strip()
        slice_length = data.get("slice_length")
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
                task_store[task_id]["result"] = {
                    "folder_name": folder_name,
                    "slice_count": len(os.listdir(
                        os.path.join(config.AUDIO_SLICE_DIR, folder_name)
                    )) if os.path.isdir(
                        os.path.join(config.AUDIO_SLICE_DIR, folder_name)
                    ) else 0,
                }
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
                files = [f for f in os.listdir(full_path) if f.endswith((".mp3", ".wav"))]
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
        engine = data.get("engine", "whisper")
        model = data.get("model") or config.WHISPER_MODEL
        prompt = data.get("prompt") or config.WHISPER_DEFAULT_PROMPT
        if not folder_name:
            return jsonify({"error": "folder_name is required"}), 400

        task_id = str(uuid.uuid4())[:8]
        task_store[task_id] = {
            "type": "transcribe",
            "folder_name": folder_name,
            "engine": engine,
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
                    task_store[task_id]["progress"] = (
                        f"Transcribing {current}/{total}"
                    )

                if engine == "whisper":
                    output_path = whisper_stt.run_analysis(
                        folder_name, model=model, prompt=prompt,
                        progress_callback=on_progress,
                    )
                else:
                    output_path = whisper_stt.run_analysis(
                        folder_name, model=model, prompt=prompt,
                        progress_callback=on_progress,
                    )

                task_store[task_id]["status"] = "done"
                task_store[task_id]["result"] = {"output_path": output_path}
                task_store[task_id]["progress"] = "Transcription complete"
            except Exception as e:
                logger.error("Transcribe task failed: %s", str(e))
                task_store[task_id]["status"] = "error"
                task_store[task_id]["error"] = str(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return jsonify({"task_id": task_id})

    @app.route("/api/output-content/<filename>", methods=["GET"])
    def api_read_output(filename):
        file_path = os.path.join(config.OUTPUT_DIR, filename)
        if not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({
            "filename": filename,
            "content": content,
            "char_count": len(content),
            "line_count": content.count("\n") + 1,
        })

    @app.route("/api/outputs", methods=["GET"])
    def api_outputs():
        output_dir = config.OUTPUT_DIR
        if not os.path.isdir(output_dir):
            return jsonify({"files": []})
        files = []
        for f in sorted(os.listdir(output_dir), reverse=True):
            if f.endswith(".txt"):
                fp = os.path.join(output_dir, f)
                stat = os.stat(fp)
                files.append({
                    "name": f,
                    "path": fp,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "modified": stat.st_mtime,
                })
        return jsonify({"files": files})

    @app.route("/api/output/<path:filename>", methods=["GET"])
    def api_download_output(filename):
        return send_from_directory(config.OUTPUT_DIR, filename, as_attachment=True)

    @app.route("/api/llm/process", methods=["POST"])
    def api_llm_process():
        data = request.get_json(force=True)
        filename = data.get("filename", "").strip()
        action = data.get("action", "summarize")
        custom_prompt = data.get("custom_prompt", "")
        target_lang = data.get("target_lang", "English")

        if not filename:
            return jsonify({"error": "filename is required"}), 400

        file_path = os.path.join(config.OUTPUT_DIR, filename)
        if not os.path.isfile(file_path):
            return jsonify({"error": f"File not found: {filename}"}), 404

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            return jsonify({"error": "File is empty"}), 400

        task_id = str(uuid.uuid4())[:8]
        task_store[task_id] = {
            "type": "llm_process",
            "action": action,
            "filename": filename,
            "status": "pending",
            "progress": "",
            "result": None,
            "error": None,
        }

        def _run():
            try:
                task_store[task_id]["status"] = "running"
                task_store[task_id]["progress"] = f"Processing {action}..."
                if action == "summarize":
                    result = llm_service.summarize(text, custom_prompt or None)
                elif action == "correct":
                    result = llm_service.correct(text, custom_prompt or None)
                elif action == "translate":
                    result = llm_service.translate(text, target_lang, custom_prompt or None)
                elif action == "custom":
                    system_prompt = custom_prompt or "请处理以下文本。"
                    result = llm_service.chat(text, system_prompt)
                else:
                    raise ValueError(f"Unknown action: {action}")

                output_filename = f"{os.path.splitext(filename)[0]}_{action}.txt"
                output_path = os.path.join(config.OUTPUT_DIR, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result)

                task_store[task_id]["status"] = "done"
                task_store[task_id]["result"] = {
                    "content": result,
                    "output_file": output_filename,
                    "char_count": len(result),
                }
                task_store[task_id]["progress"] = f"{action} complete"
            except Exception as e:
                logger.error("LLM task failed: %s", str(e))
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

    return app