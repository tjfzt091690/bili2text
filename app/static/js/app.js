let currentStep = 1;

function switchStep(step) {
    currentStep = step;
    document.querySelectorAll('.step-panel').forEach((el, i) => {
        el.classList.toggle('d-none', i + 1 !== step);
    });
    for (let i = 1; i <= 4; i++) {
        const btn = document.getElementById('nav-step-' + i);
        btn.classList.toggle('active', i === step);
        btn.classList.toggle('btn-primary', i === step);
        btn.classList.toggle('btn-outline-primary', i !== step);
    }
    if (step === 1) loadVideoDirs();
    if (step === 2) { loadVideoDirs(); loadSliceDirs(); }
    if (step === 3) { loadSliceDirs(); }
    if (step === 4) { loadOutputs(); loadOutputContent(); }
}

function pollTask(taskId, statusEl, progressTextEl, logEl, containerEl, progressBarEl, onComplete) {
    containerEl.style.display = 'block';
    const interval = setInterval(async () => {
        try {
            const resp = await fetch('/api/task/' + taskId);
            const data = await resp.json();
            statusEl.textContent = data.status;
            statusEl.className = 'ms-2 status-badge status-' + data.status;
            if (data.progress) progressTextEl.textContent = data.progress;
            if (progressBarEl && data.type === 'transcribe') {
                const match = data.progress.match(/Transcribing (\d+)\/(\d+)/);
                if (match) {
                    const pct = Math.round((parseInt(match[1]) / parseInt(match[2])) * 100);
                    progressBarEl.style.width = pct + '%';
                    progressBarEl.textContent = pct + '%';
                }
            }
            if (logEl) {
                logEl.textContent = '[' + data.status.toUpperCase() + '] ' + (data.progress || '') + '\n' + (data.error ? 'ERROR: ' + data.error + '\n' : '');
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
    if (!url) { alert('Please enter a video URL or BV number'); return; }
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
        null,
        () => { loadVideoDirs(); }
    );
}

async function loadVideoDirs() {
    const resp = await fetch('/api/video-dirs');
    const data = await resp.json();
    const tbody = document.getElementById('videoTableBody');
    const sel = document.getElementById('videoDirSelect');

    sel.innerHTML = '';
    if (data.dirs.length === 0) {
        sel.innerHTML = '<option value="">No downloaded videos</option>';
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">No downloaded videos yet. Download a video first.</td></tr>';
        return;
    }

    let rows = '';
    data.dirs.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.name;
        opt.textContent = d.name + ' (' + d.video_count + ' videos, ' + d.size_mb + ' MB)';
        sel.appendChild(opt);

        rows += '<tr>' +
            '<td><code>' + d.name + '</code></td>' +
            '<td>' + (d.videos.length > 0 ? d.videos.map(v => v.length > 40 ? v.substring(0, 37) + '...' : v).join('<br>') : '-') + '</td>' +
            '<td>' + d.size_mb + '</td>' +
            '<td><button class="btn btn-sm btn-outline-success" onclick="switchStep(2);document.getElementById(\'videoDirSelect\').value=\'' + d.name + '\">' +
            '<i class="bi bi-arrow-right"></i> Split Audio</button></td>' +
            '</tr>';
    });
    tbody.innerHTML = rows || '<tr><td colspan="4" class="text-center text-muted py-4">Empty</td></tr>';
}

async function startAudioSplit() {
    const dirName = document.getElementById('videoDirSelect').value;
    if (!dirName) { alert('Please select a video directory'); return; }
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
        null,
        () => { loadSliceDirs(); switchStep(3); }
    );
}

async function loadSliceDirs() {
    const resp = await fetch('/api/slice-dirs');
    const data = await resp.json();
    const tbody = document.getElementById('sliceTableBody');
    const sel = document.getElementById('sliceDirSelect');

    sel.innerHTML = '';
    if (data.dirs.length === 0) {
        sel.innerHTML = '<option value="">No sliced audio</option>';
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">No sliced audio folders yet.</td></tr>';
        return;
    }

    let rows = '';
    data.dirs.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.name;
        opt.textContent = d.name + ' (' + d.slice_count + ' slices)';
        sel.appendChild(opt);

        rows += '<tr>' +
            '<td><code>' + d.name + '</code></td>' +
            '<td><span class="badge bg-secondary">' + d.slice_count + ' slices</span></td>' +
            '<td>' + d.name.substring(0, 8).replace(/_/g, '') + '</td>' +
            '<td><button class="btn btn-sm btn-outline-warning" onclick="switchStep(3);document.getElementById(\'sliceDirSelect\').value=\'' + d.name + '\'"' +
            '><i class="bi bi-arrow-right"></i> Transcribe</button></td>' +
            '</tr>';
    });
    tbody.innerHTML = rows;
}

async function startTranscribe() {
    const folderName = document.getElementById('sliceDirSelect').value;
    const engine = document.getElementById('engineSelect').value;
    const model = document.getElementById('modelSelect').value;
    const prompt = document.getElementById('promptInput').value;
    if (!folderName) { alert('Please select a slice folder'); return; }
    const resp = await fetch('/api/transcribe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({folder_name: folderName, engine: engine, model: model, prompt: prompt})
    });
    const data = await resp.json();
    if (data.error) { alert(data.error); return; }
    const progressBar = document.getElementById('stProgressBar');
    pollTask(
        data.task_id,
        document.getElementById('stStatus'),
        document.getElementById('stProgressText'),
        document.getElementById('stLog'),
        document.getElementById('sttProgress'),
        progressBar,
        () => { loadOutputs(); switchStep(4); }
    );
}

async function loadOutputs() {
    const resp = await fetch('/api/outputs');
    const data = await resp.json();

    const fileSel = document.getElementById('outputFileSelect');
    fileSel.innerHTML = '';
    if (data.files.length === 0) {
        fileSel.innerHTML = '<option value="">No output files</option>';
    } else {
        data.files.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f.name;
            opt.textContent = f.name + ' (' + f.size_kb + ' KB)';
            fileSel.appendChild(opt);
        });
    }

    const tbody = document.getElementById('outputTableBody');
    if (data.files.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">No output files yet</td></tr>';
        return;
    }

    let rows = '';
    data.files.forEach(f => {
        const typeLabel = f.name.includes('_summarize') ? 'Summary' :
                          f.name.includes('_correct') ? 'Corrected' :
                          f.name.includes('_translate') ? 'Translation' :
                          f.name.includes('_custom') ? 'Custom' : 'Raw STT';
        const badgeClass = f.name.includes('_summarize') ? 'bg-info' :
                           f.name.includes('_correct') ? 'bg-success' :
                           f.name.includes('_translate') ? 'bg-warning' :
                           f.name.includes('_custom') ? 'bg-dark' : 'bg-secondary';

        rows += '<tr>' +
            '<td><a href="/api/output/' + f.name + '" target="_blank">' + f.name + '</a></td>' +
            '<td>' + f.size_kb + '</td>' +
            '<td><span class="badge ' + badgeClass + '">' + typeLabel + '</span></td>' +
            '<td>' +
            '<div class="btn-group btn-group-sm">' +
            '<button class="btn btn-outline-info" onclick="previewOutput(\'' + f.name + '\')" title="Preview"><i class="bi bi-eye"></i></button>' +
            '<a href="/api/output/' + f.name + '" class="btn btn-outline-primary" download title="Download"><i class="bi bi-download"></i></a>' +
            '</div></td></tr>';
    });
    tbody.innerHTML = rows;
}

async function loadOutputContent() {
    const filename = document.getElementById('outputFileSelect').value;
    const preview = document.getElementById('originalTextPreview');
    const infoBadge = document.getElementById('origInfo');
    if (!filename) {
        preview.textContent = 'Select a file to preview';
        infoBadge.textContent = '';
        return;
    }
    try {
        const resp = await fetch('/api/output-content/' + encodeURIComponent(filename));
        const data = await resp.json();
        preview.textContent = data.content;
        infoBadge.textContent = data.char_count + ' chars / ' + data.line_count + ' lines';
    } catch (e) {
        preview.textContent = 'Failed to load file content';
        infoBadge.textContent = '';
    }
}

function previewOutput(filename) {
    document.getElementById('outputFileSelect').value = filename;
    loadOutputContent();
}

document.getElementById('llmActionSelect').addEventListener('change', function() {
    const val = this.value;
    document.getElementById('targetLangGroup').style.display = val === 'translate' ? '' : 'none';
    document.getElementById('customPromptGroup').style.display = val === 'custom' ? '' : 'none';
});

async function startLLMProcess() {
    const filename = document.getElementById('outputFileSelect').value;
    const action = document.getElementById('llmActionSelect').value;
    const customPrompt = document.getElementById('customPromptInput').value;
    const targetLang = document.getElementById('targetLangSelect').value;
    if (!filename) { alert('Please select an output file'); return; }
    const resp = await fetch('/api/llm/process', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            filename: filename,
            action: action,
            custom_prompt: customPrompt,
            target_lang: targetLang
        })
    });
    const data = await resp.json();
    if (data.error) { alert(data.error); return; }
    pollTask(
        data.task_id,
        document.getElementById('llmStatus'),
        document.getElementById('llmProgressText'),
        document.getElementById('llmLog'),
        document.getElementById('llmProgress'),
        null,
        (resultData) => {
            const preview = document.getElementById('llmResultPreview');
            const infoBadge = document.getElementById('resultInfo');
            const footer = document.getElementById('llmResultFooter');
            const downloadBtn = document.getElementById('downloadLlmResultBtn');

            if (resultData.result && resultData.result.content) {
                preview.textContent = resultData.result.content;
                infoBadge.textContent = resultData.result.char_count + ' chars';
                footer.classList.remove('d-none');
                downloadBtn.href = '/api/output-content/' + encodeURIComponent(resultData.result.output_file);
            }
            loadOutputs();
        }
    );
}

async function loadConfig() {
    try {
        const resp = await fetch('/api/config');
        const data = await resp.json();
        if (data.whisper_model) document.getElementById('modelSelect').value = data.whisper_model;
        if (data.whisper_default_prompt) document.getElementById('promptInput').value = data.whisper_default_prompt;
        if (data.slice_length_ms) document.getElementById('sliceLengthInput').value = parseInt(data.slice_length_ms) / 1000;
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadVideoDirs();
    loadSliceDirs();
    loadOutputs();
});