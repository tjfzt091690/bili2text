function pollTask(taskId, statusEl, progressTextEl, logEl, containerEl, onComplete) {
    containerEl.style.display = 'block';
    const interval = setInterval(async () => {
        try {
            const resp = await fetch(`/api/task/${taskId}`);
            const data = await resp.json();
            statusEl.textContent = data.status;
            statusEl.className = 'ms-2 status-badge status-' + data.status;
            if (data.progress) progressTextEl.textContent = data.progress;
            if (logEl) {
                logEl.textContent = `[${data.status}] ${data.progress || ''}\n` + (data.error ? `ERROR: ${data.error}\n` : '');
            }
            if (data.status === 'done' || data.status === 'error') {
                clearInterval(interval);
                if (data.status === 'done' && onComplete) onComplete(data);
            }
        } catch (e) {
            clearInterval(interval);
            statusEl.textContent = 'error';
            statusEl.className = 'ms-2 status-badge status-error';
        }
    }, 1500);
}

async function startDownload() {
    const url = document.getElementById('videoUrl').value.trim();
    if (!url) { alert('请输入视频 URL 或 BV 号'); return; }
    const resp = await fetch('/api/download', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url})
    });
    const data = await resp.json();
    if (data.error) { alert(data.error); return; }
    pollTask(
        data.task_id,
        document.getElementById('dlStatus'),
        document.getElementById('dlProgressText'),
        document.getElementById('dlLog'),
        document.getElementById('downloadProgress'),
        () => { loadVideoDirs(); }
    );
}

async function loadVideoDirs() {
    const resp = await fetch('/api/video-dirs');
    const data = await resp.json();
    const sel = document.getElementById('videoDirSelect');
    sel.innerHTML = '';
    if (data.dirs.length === 0) {
        sel.innerHTML = '<option value="">暂无已下载视频</option>';
        return;
    }
    data.dirs.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.name;
        opt.textContent = `${d.name} (${d.video_count} 个视频)`;
        sel.appendChild(opt);
    });
}

async function startAudioSplit() {
    const dirName = document.getElementById('videoDirSelect').value;
    if (!dirName) { alert('请选择视频目录'); return; }
    const resp = await fetch('/api/audio-split', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({dir_name: dirName})
    });
    const data = await resp.json();
    if (data.error) { alert(data.error); return; }
    pollTask(
        data.task_id,
        document.getElementById('auStatus'),
        document.getElementById('auProgressText'),
        document.getElementById('auLog'),
        document.getElementById('audioProgress'),
        () => { loadSliceDirs(); }
    );
}

async function loadSliceDirs() {
    const resp = await fetch('/api/slice-dirs');
    const data = await resp.json();
    const sel = document.getElementById('sliceDirSelect');
    sel.innerHTML = '';
    if (data.dirs.length === 0) {
        sel.innerHTML = '<option value="">暂无切片数据</option>';
        return;
    }
    data.dirs.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.name;
        opt.textContent = `${d.name} (${d.slice_count} 个切片)`;
        sel.appendChild(opt);
    });
}

async function startTranscribe() {
    const folderName = document.getElementById('sliceDirSelect').value;
    const model = document.getElementById('modelSelect').value;
    const prompt = document.getElementById('promptInput').value;
    if (!folderName) { alert('请选择切片文件夹'); return; }
    const resp = await fetch('/api/transcribe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({folder_name: folderName, model: model, prompt: prompt})
    });
    const data = await resp.json();
    if (data.error) { alert(data.error); return; }
    pollTask(
        data.task_id,
        document.getElementById('stStatus'),
        document.getElementById('stProgressText'),
        document.getElementById('stLog'),
        document.getElementById('sttProgress'),
        () => { loadOutputs(); }
    );
}

async function loadOutputs() {
    const resp = await fetch('/api/outputs');
    const data = await resp.json();
    const container = document.getElementById('outputList');
    if (data.files.length === 0) {
        container.innerHTML = '<p class="text-muted">暂无转写结果</p>';
        return;
    }
    let html = '<div class="list-group">';
    data.files.forEach(f => {
        html += `<div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
            <span>${f.name}</span>
            <a href="/api/output/${f.name}" class="btn btn-sm btn-outline-primary">⬇️ 下载</a>
        </div>`;
    });
    html += '</div>';
    container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', () => {
    loadVideoDirs();
    loadSliceDirs();
});
