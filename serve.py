#!/usr/bin/env python3
"""
Audit Hub — standalone QA testing server.

Serves an interactive checklist UI backed by JSON files on disk.

Usage:
  python serve.py [audits-directory]

  audits-directory: path to folder containing audit-*.json files
                    (defaults to current working directory)

Examples:
  python serve.py tasks/audits
  python ~/.claude/skills/ralph-audit/serve.py tasks/audits

Then open http://localhost:4000
Share via ngrok: ngrok http 4000
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
PORT = int(os.environ.get("AUDIT_PORT", 4000))


def validate_feature(feature):
    return bool(re.match(r"^[a-z0-9-]+$", feature))


def list_audits():
    audits = []
    for fname in sorted(os.listdir(DIR)):
        if not fname.startswith("audit-") or not fname.endswith(".json"):
            continue
        feature = fname[len("audit-") : -len(".json")]
        try:
            with open(os.path.join(DIR, fname)) as f:
                checklist = json.load(f)
        except Exception:
            continue
        total = sum(len(s.get("stories", [])) for s in checklist.get("sections", []))
        pass_count = fail_count = skip_count = 0
        results_path = os.path.join(DIR, f"results-{feature}.json")
        if os.path.exists(results_path):
            try:
                with open(results_path) as f:
                    for v in json.load(f).get("results", {}).values():
                        if v == "pass":
                            pass_count += 1
                        elif v == "fail":
                            fail_count += 1
                        elif v == "skip":
                            skip_count += 1
            except Exception:
                pass
        audits.append(
            {
                "feature": feature,
                "title": checklist.get("feature", feature).replace("-", " ").title(),
                "date": checklist.get("date"),
                "total": total,
                "pass": pass_count,
                "fail": fail_count,
                "skip": skip_count,
                "remaining": total - pass_count - fail_count - skip_count,
            }
        )
    return audits


def get_checklist(feature):
    path = os.path.join(DIR, f"audit-{feature}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def get_results(feature):
    path = os.path.join(DIR, f"results-{feature}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"feature": feature, "updated_at": None, "results": {}, "notes": {}, "new_requirements": []}


def save_results(feature, payload):
    data = {
        "feature": feature,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "results": payload.get("results", {}),
        "notes": payload.get("notes", {}),
        "new_requirements": payload.get("new_requirements", []),
    }
    with open(os.path.join(DIR, f"results-{feature}.json"), "w") as f:
        json.dump(data, f, indent=2)
    return {"status": "saved", "updated_at": data["updated_at"]}


class AuditHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # API routes
        if path == "/api/audits":
            return self._json_response(list_audits())

        m = re.match(r"^/api/audits/([^/]+)/checklist$", path)
        if m:
            feature = m.group(1)
            if not validate_feature(feature):
                return self._json_response({"error": "Invalid feature"}, 400)
            data = get_checklist(feature)
            if data is None:
                return self._json_response({"error": "Not found"}, 404)
            return self._json_response(data)

        m = re.match(r"^/api/audits/([^/]+)/results$", path)
        if m:
            feature = m.group(1)
            if not validate_feature(feature):
                return self._json_response({"error": "Invalid feature"}, 400)
            return self._json_response(get_results(feature))

        # Serve HTML for root
        if path in ("", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HUB_HTML.encode())
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        m = re.match(r"^/api/audits/([^/]+)/results$", path)
        if m:
            feature = m.group(1)
            if not validate_feature(feature):
                return self._json_response({"error": "Invalid feature"}, 400)
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            return self._json_response(save_results(feature, payload))

        self.send_error(404)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        # Quiet logging — only errors
        if args and str(args[1]).startswith("4"):
            super().log_message(format, *args)


HUB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audit Hub</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #fff;
    color: #37352f;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  /* Sidebar */
  .sidebar {
    width: 280px;
    min-width: 280px;
    border-right: 1px solid #e8e7e4;
    background: #fbfbfa;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .sidebar-header {
    padding: 20px 16px 12px;
    border-bottom: 1px solid #e8e7e4;
  }

  .sidebar-title {
    font-size: 14px;
    font-weight: 600;
    color: #9b9a97;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .sidebar-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  .sidebar-item {
    padding: 10px 12px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 2px;
    transition: background 0.1s;
  }
  .sidebar-item:hover { background: #f1f1ef; }
  .sidebar-item.active { background: #e8e7e4; }

  .sidebar-item-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 6px;
  }

  .sidebar-progress {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .sidebar-progress-bar {
    flex: 1;
    height: 4px;
    background: #e0dfdc;
    border-radius: 2px;
    overflow: hidden;
  }

  .sidebar-progress-fill-pass {
    height: 100%;
    background: #4daa57;
    float: left;
    transition: width 0.3s ease;
  }
  .sidebar-progress-fill-fail {
    height: 100%;
    background: #e03e3e;
    float: left;
    transition: width 0.3s ease;
  }

  .sidebar-stats {
    font-size: 11px;
    color: #9b9a97;
    white-space: nowrap;
  }

  .sidebar-empty {
    padding: 24px 16px;
    font-size: 14px;
    color: #9b9a97;
    text-align: center;
  }

  /* Main */
  .main {
    flex: 1;
    overflow-y: auto;
    position: relative;
  }

  .main-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #9b9a97;
    font-size: 16px;
  }

  .page {
    max-width: 900px;
    margin: 0 auto;
    padding: 48px 64px 120px;
  }

  h1 {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
    line-height: 1.2;
  }

  .meta {
    font-size: 14px;
    color: #9b9a97;
    margin-bottom: 24px;
  }

  /* Progress */
  .progress-bar-container { margin-bottom: 32px; }
  .progress-label {
    font-size: 14px;
    color: #9b9a97;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
  }
  .progress-bar {
    height: 6px;
    background: #e8e7e4;
    border-radius: 3px;
    overflow: hidden;
    display: flex;
  }
  .progress-fill-pass {
    height: 100%;
    background: #4daa57;
    transition: width 0.3s ease;
  }
  .progress-fill-fail {
    height: 100%;
    background: #e03e3e;
    transition: width 0.3s ease;
  }

  /* Sections */
  .section { margin-bottom: 8px; }

  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 4px;
    cursor: pointer;
    user-select: none;
    border-radius: 4px;
  }
  .section-header:hover { background: #f1f1ef; }

  .section-toggle {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #9b9a97;
    transition: transform 0.15s ease;
    flex-shrink: 0;
  }
  .section-toggle.open { transform: rotate(90deg); }

  .section-title {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.01em;
  }

  .section-count {
    font-size: 13px;
    color: #9b9a97;
    margin-left: 8px;
  }

  .section-body {
    padding-left: 26px;
    display: none;
  }
  .section-body.open { display: block; }

  /* Stories */
  .story {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 4px;
    border-radius: 4px;
    margin-bottom: 2px;
  }
  .story:hover { background: #f7f6f3; }

  .story-checkbox {
    width: 18px;
    height: 18px;
    border: 2px solid #c4c4c0;
    border-radius: 3px;
    flex-shrink: 0;
    margin-top: 3px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
  }
  .story-checkbox.checked {
    background: #2eaadc;
    border-color: #2eaadc;
  }
  .story-checkbox.checked::after {
    content: '\2713';
    color: white;
    font-size: 12px;
    font-weight: 700;
  }
  .story-checkbox.fail {
    background: #e03e3e;
    border-color: #e03e3e;
  }
  .story-checkbox.fail::after {
    content: '\2715';
    color: white;
    font-size: 12px;
    font-weight: 700;
  }
  .story-checkbox.skip {
    background: #9b9a97;
    border-color: #9b9a97;
  }
  .story-checkbox.skip::after {
    content: '\2014';
    color: white;
    font-size: 12px;
    font-weight: 700;
  }

  .story-content { flex: 1; min-width: 0; }

  .story-title {
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
  }
  .story.checked .story-title {
    color: #9b9a97;
    text-decoration: line-through;
  }
  .story.skipped .story-title {
    color: #9b9a97;
  }

  /* Story detail */
  .story-detail {
    display: none;
    margin-top: 8px;
    padding: 12px 16px;
    background: #fbfbfa;
    border-radius: 4px;
    border-left: 3px solid #e8e7e4;
  }
  .story-detail.open { display: block; }

  .detail-section { margin-bottom: 10px; }
  .detail-section:last-child { margin-bottom: 0; }

  .detail-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9b9a97;
    margin-bottom: 4px;
  }

  .step {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    padding: 3px 0;
    font-size: 14px;
  }
  .step-number {
    color: #9b9a97;
    font-size: 13px;
    min-width: 20px;
    text-align: right;
    flex-shrink: 0;
  }
  .step-text { color: #37352f; }

  .expected {
    font-size: 14px;
    color: #37352f;
    padding: 8px 12px;
    background: #edf8e9;
    border-radius: 4px;
    border-left: 3px solid #4daa57;
  }

  /* Result buttons */
  .result-buttons {
    display: flex;
    gap: 8px;
    margin-top: 10px;
  }
  .result-btn {
    padding: 4px 14px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid #e0dfdc;
    background: white;
    transition: all 0.15s ease;
  }
  .result-btn:hover { background: #f7f6f3; }
  .result-btn.pass-btn.active {
    background: #dbf3d8;
    border-color: #4daa57;
    color: #2a7e33;
  }
  .result-btn.fail-btn.active {
    background: #fde8e8;
    border-color: #e03e3e;
    color: #c43333;
  }
  .result-btn.skip-btn.active {
    background: #f5f0e3;
    border-color: #dfab01;
    color: #9a7800;
  }

  .notes-input {
    width: 100%;
    margin-top: 8px;
    padding: 8px 12px;
    border: 1px solid #e0dfdc;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    min-height: 36px;
  }
  .notes-input:focus { outline: none; border-color: #2eaadc; }
  .notes-input::placeholder { color: #c4c4c0; }

  /* New requirements */
  .new-requirements {
    margin-top: 40px;
    padding-top: 24px;
    border-top: 1px solid #e8e7e4;
  }
  .new-req-title {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
  }
  .new-req-subtitle {
    font-size: 13px;
    color: #9b9a97;
    margin-bottom: 16px;
  }
  .new-req-input-row {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }
  .new-req-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #e0dfdc;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
  }
  .new-req-input:focus { outline: none; border-color: #2eaadc; }
  .new-req-input::placeholder { color: #c4c4c0; }
  .new-req-add-btn {
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid #2eaadc;
    background: #2eaadc;
    color: white;
  }
  .new-req-add-btn:hover { opacity: 0.9; }
  .new-req-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 4px;
    border-radius: 4px;
  }
  .new-req-item:hover { background: #f7f6f3; }
  .new-req-text {
    flex: 1;
    font-size: 14px;
    line-height: 1.5;
  }
  .new-req-remove {
    width: 20px;
    height: 20px;
    border: none;
    background: none;
    color: #9b9a97;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 3px;
    flex-shrink: 0;
  }
  .new-req-remove:hover { background: #fde8e8; color: #e03e3e; }

  /* Summary bar */
  .summary-bar {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 280px;
    background: white;
    border-top: 1px solid #e8e7e4;
    padding: 12px 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    font-size: 14px;
    z-index: 100;
  }
  .summary-stat {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  .dot.pass { background: #4daa57; }
  .dot.fail { background: #e03e3e; }
  .dot.skip { background: #dfab01; }
  .dot.pending { background: #e0dfdc; }

  .export-btn {
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid #e0dfdc;
    background: white;
    margin-left: 16px;
  }
  .export-btn:hover { background: #f7f6f3; }

  /* Saved indicator */
  .saved-indicator {
    position: fixed;
    top: 16px;
    right: 16px;
    padding: 8px 16px;
    background: #dbf3d8;
    color: #2a7e33;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 200;
    pointer-events: none;
  }
  .saved-indicator.show { opacity: 1; }
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-title">Audits</div>
  </div>
  <div class="sidebar-list" id="sidebar-list">
    <div class="sidebar-empty">Loading...</div>
  </div>
</div>

<div class="main" id="main">
  <div class="main-empty">Select an audit from the sidebar</div>
</div>

<div class="saved-indicator" id="saved-indicator">Saved</div>

<script>
const API_BASE = '';

// State
let audits = [];
let currentFeature = null;
let checklist = null;
let results = {};
let notes = {};
let newRequirements = [];
let saveTimer = null;

// Init
async function init() {
  await loadAuditList();
  const params = new URLSearchParams(window.location.search);
  const feature = params.get('feature');
  if (feature) {
    selectAudit(feature);
  }
}

// Sidebar
async function loadAuditList() {
  try {
    const res = await fetch(`${API_BASE}/api/audits`);
    audits = await res.json();
  } catch (e) {
    audits = [];
  }
  renderSidebar();
}

function renderSidebar() {
  const list = document.getElementById('sidebar-list');
  if (audits.length === 0) {
    list.innerHTML = '<div class="sidebar-empty">No audits found</div>';
    return;
  }
  list.innerHTML = audits.map(a => {
    const pct_pass = a.total ? (a.pass / a.total * 100) : 0;
    const pct_fail = a.total ? (a.fail / a.total * 100) : 0;
    return `
      <div class="sidebar-item ${a.feature === currentFeature ? 'active' : ''}"
           onclick="selectAudit('${a.feature}')">
        <div class="sidebar-item-title">${a.title}</div>
        <div class="sidebar-progress">
          <div class="sidebar-progress-bar">
            <div class="sidebar-progress-fill-pass" style="width:${pct_pass}%"></div>
            <div class="sidebar-progress-fill-fail" style="width:${pct_fail}%"></div>
          </div>
          <div class="sidebar-stats">${a.pass + a.fail + (a.skip || 0)}/${a.total}</div>
        </div>
      </div>
    `;
  }).join('');
}

// Select audit
async function selectAudit(feature) {
  currentFeature = feature;
  const url = new URL(window.location);
  url.searchParams.set('feature', feature);
  window.history.replaceState({}, '', url);

  renderSidebar();

  const main = document.getElementById('main');
  main.innerHTML = '<div class="main-empty">Loading...</div>';

  try {
    const [checklistRes, resultsRes] = await Promise.all([
      fetch(`${API_BASE}/api/audits/${feature}/checklist`),
      fetch(`${API_BASE}/api/audits/${feature}/results`),
    ]);
    checklist = await checklistRes.json();
    const savedData = await resultsRes.json();
    results = savedData.results || {};
    notes = savedData.notes || {};
    newRequirements = savedData.new_requirements || [];
  } catch (e) {
    main.innerHTML = '<div class="main-empty">Failed to load audit</div>';
    return;
  }

  renderChecklist();
}

// Render checklist
function renderChecklist() {
  const main = document.getElementById('main');
  const title = checklist.feature.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  const total = checklist.sections.reduce((s, sec) => s + sec.stories.length, 0);
  const passCount = Object.values(results).filter(v => v === 'pass').length;
  const failCount = Object.values(results).filter(v => v === 'fail').length;
  const skipCount = Object.values(results).filter(v => v === 'skip').length;
  const done = passCount + failCount + skipCount;

  main.innerHTML = `
    <div class="page">
      <h1>${escapeHtml(title)}</h1>
      <div class="meta">PRD: ${escapeHtml(checklist.prd || '')} &middot; ${escapeHtml(checklist.date || '')} &middot; ${total} stories</div>

      <div class="progress-bar-container">
        <div class="progress-label">
          <span>Progress</span>
          <span id="progress-text">${done} / ${total}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill-pass" id="progress-fill-pass" style="width:${total ? (passCount/total*100) : 0}%"></div>
          <div class="progress-fill-fail" id="progress-fill-fail" style="width:${total ? (failCount/total*100) : 0}%"></div>
        </div>
      </div>

      <div id="sections"></div>

      <div class="new-requirements">
        <div class="new-req-title">New Requirements</div>
        <div class="new-req-subtitle">Ideas and requirements discovered during testing — not bugs, but new work</div>
        <div class="new-req-input-row">
          <input type="text" class="new-req-input" id="new-req-input" placeholder="Type a new requirement and press Enter..." onkeydown="if(event.key==='Enter')addNewRequirement()">
          <button class="new-req-add-btn" onclick="addNewRequirement()">Add</button>
        </div>
        <div id="new-req-list"></div>
      </div>
    </div>

    <div class="summary-bar">
      <div class="summary-stat"><div class="dot pass"></div> <span id="pass-count">${passCount}</span> passed</div>
      <div class="summary-stat"><div class="dot fail"></div> <span id="fail-count">${failCount}</span> failed</div>
      <div class="summary-stat"><div class="dot skip"></div> <span id="skip-count">${skipCount}</span> skipped</div>
      <div class="summary-stat"><div class="dot pending"></div> <span id="pending-count">${total - done}</span> remaining</div>
      <button class="export-btn" onclick="exportResults()">Export Results</button>
    </div>
  `;

  const container = document.getElementById('sections');

  checklist.sections.forEach(section => {
    const sectionEl = document.createElement('div');
    sectionEl.className = 'section';

    const count = section.stories.length;
    sectionEl.innerHTML = `
      <div class="section-header" onclick="toggleSection(this)">
        <div class="section-toggle open">\u25B6</div>
        <div class="section-title">${escapeHtml(section.title)}</div>
        <div class="section-count">${count} stories</div>
      </div>
      <div class="section-body open"></div>
    `;

    const body = sectionEl.querySelector('.section-body');

    section.stories.forEach(story => {
      const id = String(story.id);
      const result = results[id] || null;
      const note = notes[id] || '';

      const storyEl = document.createElement('div');
      storyEl.className = 'story' + (result === 'pass' ? ' checked' : result === 'skip' ? ' skipped' : '');
      storyEl.id = `story-${id}`;

      const stepsHtml = story.steps.map((s, i) =>
        `<div class="step"><span class="step-number">${i + 1}.</span><span class="step-text">${linkifyUrls(escapeHtml(s))}</span></div>`
      ).join('');

      const cbClass = result === 'pass' ? ' checked' : result === 'fail' ? ' fail' : result === 'skip' ? ' skip' : '';

      storyEl.innerHTML = `
        <div class="story-checkbox${cbClass}" onclick="event.stopPropagation(); cycleCheck('${id}')"></div>
        <div class="story-content">
          <div class="story-title" onclick="toggleDetail('${id}')">${escapeHtml(story.title)}</div>
          <div class="story-detail" id="detail-${id}">
            <div class="detail-section">
              <div class="detail-label">Steps</div>
              ${stepsHtml}
            </div>
            <div class="detail-section">
              <div class="detail-label">Expected Result</div>
              <div class="expected">${escapeHtml(story.expected)}</div>
            </div>
            <div class="detail-section">
              <div class="result-buttons">
                <button class="result-btn pass-btn${result === 'pass' ? ' active' : ''}" onclick="event.stopPropagation(); setResult('${id}', 'pass')">Pass</button>
                <button class="result-btn fail-btn${result === 'fail' ? ' active' : ''}" onclick="event.stopPropagation(); setResult('${id}', 'fail')">Fail</button>
                <button class="result-btn skip-btn${result === 'skip' ? ' active' : ''}" onclick="event.stopPropagation(); setResult('${id}', 'skip')">Skip</button>
              </div>
              <textarea class="notes-input" id="notes-${id}" placeholder="Notes (optional)..." rows="2" oninput="onNoteChange('${id}', this.value)">${escapeHtml(note)}</textarea>
            </div>
          </div>
        </div>
      `;

      body.appendChild(storyEl);
    });

    container.appendChild(sectionEl);
  });

  renderNewRequirements();
}

// Interactions
function toggleSection(header) {
  header.querySelector('.section-toggle').classList.toggle('open');
  header.nextElementSibling.classList.toggle('open');
}

function toggleDetail(id) {
  document.getElementById(`detail-${id}`).classList.toggle('open');
}

function cycleCheck(id) {
  const current = results[id] || null;
  if (current === null) setResult(id, 'pass');
  else if (current === 'pass') setResult(id, 'fail');
  else if (current === 'fail') setResult(id, 'skip');
  else setResult(id, null);
}

function setResult(id, result) {
  if (result === null) {
    delete results[id];
  } else {
    results[id] = result;
  }

  const story = document.getElementById(`story-${id}`);
  const cb = story.querySelector('.story-checkbox');

  cb.className = 'story-checkbox' + (result === 'pass' ? ' checked' : result === 'fail' ? ' fail' : result === 'skip' ? ' skip' : '');
  story.className = 'story' + (result === 'pass' ? ' checked' : result === 'skip' ? ' skipped' : '');

  if (result === 'fail') {
    document.getElementById(`notes-${id}`).focus();
  }

  const passBtn = story.querySelector('.pass-btn');
  const failBtn = story.querySelector('.fail-btn');
  const skipBtn = story.querySelector('.skip-btn');
  passBtn.className = 'result-btn pass-btn' + (result === 'pass' ? ' active' : '');
  failBtn.className = 'result-btn fail-btn' + (result === 'fail' ? ' active' : '');
  skipBtn.className = 'result-btn skip-btn' + (result === 'skip' ? ' active' : '');

  updateSummary();
  scheduleSave();
}

function onNoteChange(id, value) {
  if (value.trim()) {
    notes[id] = value;
  } else {
    delete notes[id];
  }
  scheduleSave();
}

function updateSummary() {
  const total = checklist.sections.reduce((s, sec) => s + sec.stories.length, 0);
  const passCount = Object.values(results).filter(v => v === 'pass').length;
  const failCount = Object.values(results).filter(v => v === 'fail').length;
  const skipCount = Object.values(results).filter(v => v === 'skip').length;
  const done = passCount + failCount + skipCount;

  document.getElementById('pass-count').textContent = passCount;
  document.getElementById('fail-count').textContent = failCount;
  document.getElementById('skip-count').textContent = skipCount;
  document.getElementById('pending-count').textContent = total - done;
  document.getElementById('progress-text').textContent = `${done} / ${total}`;
  document.getElementById('progress-fill-pass').style.width = `${total ? (passCount/total*100) : 0}%`;
  document.getElementById('progress-fill-fail').style.width = `${total ? (failCount/total*100) : 0}%`;

  const audit = audits.find(a => a.feature === currentFeature);
  if (audit) {
    audit.pass = passCount;
    audit.fail = failCount;
    audit.skip = skipCount;
    audit.remaining = total - done;
    renderSidebar();
  }
}

// Save (debounced)
function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(doSave, 500);
}

async function doSave() {
  if (!currentFeature) return;
  try {
    const res = await fetch(`${API_BASE}/api/audits/${currentFeature}/results`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ results, notes, new_requirements: newRequirements }),
    });
    if (res.ok) {
      flashSaved();
    }
  } catch (e) {}
}

function flashSaved() {
  const el = document.getElementById('saved-indicator');
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 1500);
}

// Export
function exportResults() {
  const data = {
    feature: currentFeature,
    exported_at: new Date().toISOString(),
    results: results,
    notes: notes,
    new_requirements: newRequirements,
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `audit-results-${currentFeature}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// New requirements
function addNewRequirement() {
  const input = document.getElementById('new-req-input');
  const text = input.value.trim();
  if (!text) return;
  newRequirements.push(text);
  input.value = '';
  renderNewRequirements();
  scheduleSave();
}

function removeNewRequirement(index) {
  newRequirements.splice(index, 1);
  renderNewRequirements();
  scheduleSave();
}

function renderNewRequirements() {
  const list = document.getElementById('new-req-list');
  if (!list) return;
  list.innerHTML = newRequirements.map((req, i) =>
    `<div class="new-req-item">
      <div class="new-req-text">${escapeHtml(req)}</div>
      <button class="new-req-remove" onclick="removeNewRequirement(${i})">&times;</button>
    </div>`
  ).join('');
}

// Helpers
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function linkifyUrls(text) {
  return text.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" style="color:#2eaadc">$1</a>');
}

// Boot
init();
</script>

</body>
</html>"""


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), AuditHandler)
    print(f"Audit Hub running at http://localhost:{PORT}")
    print(f"Serving audits from {DIR}")
    print("Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
