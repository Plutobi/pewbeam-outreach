"""
Pewbeam Automated Outreach Hub - Fast Localhost Dashboard
Focused on UK Church Media & AV Production Outreach.
"""

import sys
import asyncio

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import csv
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from uk_scraper import UK_CSV_PATH, CHURCH_FIELDS, UK_CITIES, free_scrape_uk_city

app = FastAPI(title="Pewbeam Outreach Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory logs & subscribers
SCRAPE_LOGS = []
LOG_SUBSCRIBERS = []
IS_SCRAPING = False

def push_log(text: str):
    msg = {"text": text, "time": datetime.now().strftime("%H:%M:%S")}
    SCRAPE_LOGS.append(msg)
    sse_packet = f"event: log\ndata: {json.dumps(msg)}\n\n"
    for q in list(LOG_SUBSCRIBERS):
        try:
            q.put_nowait(sse_packet)
        except Exception:
            pass


def get_all_leads():
    if not UK_CSV_PATH.exists():
        return []
    with open(UK_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
        for l in leads:
            if not l.get("Status"):
                l["Status"] = "new"
        return leads


def save_all_leads(leads):
    with open(UK_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CHURCH_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)


@app.get("/api/leads")
def api_get_leads(city: Optional[str] = None, status: Optional[str] = None):
    leads = get_all_leads()
    if city and city != "all":
        leads = [l for l in leads if l.get("City", "").lower() == city.lower()]
    if status and status != "all":
        leads = [l for l in leads if l.get("Status", "new") == status]
    return leads


class UpdateStatusRequest(BaseModel):
    church_name: str
    status: str


@app.post("/api/leads/status")
def api_update_status(req: UpdateStatusRequest):
    leads = get_all_leads()
    updated = False
    for l in leads:
        if l.get("Church Name") == req.church_name:
            l["Status"] = req.status
            updated = True
            break
    if updated:
        save_all_leads(leads)
    return {"status": "ok", "updated": updated}


class ScrapeRequest(BaseModel):
    city: str


@app.post("/api/scrape/start")
def api_start_scrape(req: ScrapeRequest):
    global IS_SCRAPING, SCRAPE_LOGS
    if IS_SCRAPING:
        return JSONResponse(status_code=400, content={"error": "Scrape currently in progress."})

    SCRAPE_LOGS = []
    IS_SCRAPING = True

    def run_job():
        global IS_SCRAPING
        try:
            push_log(f"Starting UK church scrape for: {req.city}")
            results = free_scrape_uk_city(req.city, event_callback=push_log)
            if results:
                existing = get_all_leads()
                existing_names = {c.get("Church Name", "").lower() for c in existing}
                new_additions = [c for c in results if c["Church Name"].lower() not in existing_names]
                existing.extend(new_additions)
                save_all_leads(existing)
                push_log(f"Added {len(new_additions)} new churches to your database!")
            else:
                push_log("No new churches found for this specific query.")
        except Exception as e:
            push_log(f"Scraper error: {e}")
        finally:
            IS_SCRAPING = False
            push_log("Scrape run finished.")

    threading.Thread(target=run_job, daemon=True).start()
    return {"status": "started"}


@app.get("/api/scrape/stream")
async def api_scrape_stream(request: Request):
    queue = asyncio.Queue()
    LOG_SUBSCRIBERS.append(queue)

    async def event_generator():
        try:
            yield f"event: status\ndata: {json.dumps({'is_scraping': IS_SCRAPING})}\n\n"
            for log in SCRAPE_LOGS:
                yield f"event: log\ndata: {json.dumps(log)}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield msg
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            pass
        finally:
            if queue in LOG_SUBSCRIBERS:
                LOG_SUBSCRIBERS.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pewbeam | UK Church Outreach Hub</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #080707; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    .brand-orange { color: #ff5700; }
    .bg-brand-orange { background-color: #ff5700; }
    .border-brand-orange { border-color: #ff5700; }
  </style>
</head>
<body class="text-stone-200 min-h-screen">

  <!-- Header -->
  <header class="border-b border-stone-800/80 bg-[#121010]/80 backdrop-blur sticky top-0 z-50 px-6 py-4">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 flex items-center justify-center shadow-lg shadow-orange-500/25">
          <i data-lucide="zap" class="w-5 h-5 text-white fill-white"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl font-extrabold tracking-tight text-white">PEWBEAM</h1>
            <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-orange-500/20 text-orange-400 font-bold border border-orange-500/30">
              🇬🇧 UK FOCUS
            </span>
          </div>
          <p class="text-xs text-stone-400">Automated Church Media & AV Outreach Engine</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex items-center space-x-2">
        <button id="navLeadsBtn" onclick="switchNav('leads')" class="px-4 py-2 rounded-xl text-xs font-bold transition bg-[#ff5700] text-white flex items-center gap-2 shadow-lg shadow-orange-600/20">
          <i data-lucide="church" class="w-4 h-4"></i> UK Churches (<span id="totalBadge">0</span>)
        </button>
        <button id="navScrapeBtn" onclick="switchNav('scrape')" class="px-4 py-2 rounded-xl text-xs font-bold transition text-stone-400 hover:text-white hover:bg-stone-900 flex items-center gap-2">
          <i data-lucide="crosshair" class="w-4 h-4"></i> Scrape UK Cities
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 py-8">

    <!-- TAB 1: UK CHURCH PIPELINE -->
    <div id="leadsSection" class="space-y-6">

      <!-- Metrics Row -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-[#131110] border border-stone-800 rounded-2xl p-4 text-center">
          <div class="text-2xl font-black text-white" id="mTotal">0</div>
          <div class="text-xs text-stone-400 uppercase tracking-wider font-semibold mt-1">UK Churches</div>
        </div>
        <div class="bg-[#131110] border border-stone-800 rounded-2xl p-4 text-center">
          <div class="text-2xl font-black text-emerald-400" id="mWebsites">0</div>
          <div class="text-xs text-stone-400 uppercase tracking-wider font-semibold mt-1">Verified Websites</div>
        </div>
        <div class="bg-[#131110] border border-stone-800 rounded-2xl p-4 text-center">
          <div class="text-2xl font-black text-orange-400" id="mEmails">0</div>
          <div class="text-xs text-stone-400 uppercase tracking-wider font-semibold mt-1">Direct Emails</div>
        </div>
        <div class="bg-[#131110] border border-stone-800 rounded-2xl p-4 text-center">
          <div class="text-2xl font-black text-sky-400" id="mSent">0</div>
          <div class="text-xs text-stone-400 uppercase tracking-wider font-semibold mt-1">Outreach Sent</div>
        </div>
      </div>

      <!-- Filters & Actions -->
      <div class="flex flex-col md:flex-row items-center justify-between gap-4 bg-[#131110] border border-stone-800 rounded-2xl p-4">
        <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div class="relative w-full md:w-64">
            <i data-lucide="search" class="w-4 h-4 text-stone-400 absolute left-3 top-3"></i>
            <input type="text" id="searchInput" oninput="renderChurchCards()" placeholder="Search church, email, city..." class="w-full bg-stone-900 border border-stone-700/80 rounded-xl pl-9 pr-3 py-2 text-xs text-stone-100 focus:outline-none focus:border-orange-500">
          </div>
          <select id="cityFilter" onchange="renderChurchCards()" class="bg-stone-900 border border-stone-700/80 rounded-xl px-3 py-2 text-xs text-stone-300 focus:outline-none focus:border-orange-500">
            <option value="all">All UK Regions</option>
            <option value="London">London (10)</option>
            <option value="Manchester">Manchester (2)</option>
            <option value="Birmingham">Birmingham (2)</option>
            <option value="Bristol">Bristol (2)</option>
            <option value="Glasgow">Glasgow (2)</option>
            <option value="Edinburgh">Edinburgh (2)</option>
            <option value="Leeds">Leeds (2)</option>
            <option value="Sheffield">Sheffield (1)</option>
            <option value="Nottingham">Nottingham (2)</option>
            <option value="Cardiff">Cardiff (2)</option>
            <option value="Oxford">Oxford (2)</option>
            <option value="Cambridge">Cambridge (1)</option>
          </select>
          <select id="statusFilter" onchange="renderChurchCards()" class="bg-stone-900 border border-stone-700/80 rounded-xl px-3 py-2 text-xs text-stone-300 focus:outline-none focus:border-orange-500">
            <option value="all">All Outreach Status</option>
            <option value="new">Pending (Not Sent)</option>
            <option value="sent">Contacted (Sent)</option>
          </select>
        </div>
        <div class="flex items-center space-x-3">
          <button onclick="exportInstantlyCSV()" class="px-4 py-2 rounded-xl text-xs font-bold bg-stone-800 hover:bg-stone-700 border border-stone-700 text-stone-200 flex items-center gap-1.5 transition">
            <i data-lucide="download" class="w-3.5 h-3.5"></i> Export Mail Merge CSV
          </button>
          <button onclick="loadChurches()" class="px-4 py-2 rounded-xl text-xs font-bold bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/30 text-orange-400 flex items-center gap-1.5 transition">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i> Refresh
          </button>
        </div>
      </div>

      <!-- Church Cards Grid -->
      <div id="churchList" class="space-y-4">
        <!-- Rendered by JavaScript -->
      </div>
    </div>

    <!-- TAB 2: SCRAPE UK CITIES -->
    <div id="scrapeSection" class="space-y-6 hidden">
      <div class="bg-[#131110] border border-stone-800 rounded-2xl p-6">
        <h2 class="text-base font-bold text-white mb-1 flex items-center gap-2">
          <i data-lucide="crosshair" class="w-4 h-4 text-orange-500"></i> Free UK Church Scraper
        </h2>
        <p class="text-xs text-stone-400 mb-6">Discovers churches, websites, media team contacts and adds them to your UK pipeline without Apify token requirements.</p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label class="block text-xs font-semibold text-stone-400 mb-1">Target UK City</label>
            <select id="scrapeCitySelect" class="w-full bg-stone-900 border border-stone-700 rounded-xl px-3 py-2 text-xs text-stone-200 focus:outline-none focus:border-orange-500">
              <option value="London">London, UK</option>
              <option value="Manchester">Manchester, UK</option>
              <option value="Birmingham">Birmingham, UK</option>
              <option value="Leeds">Leeds, UK</option>
              <option value="Glasgow">Glasgow, UK</option>
              <option value="Edinburgh">Edinburgh, UK</option>
              <option value="Bristol">Bristol, UK</option>
              <option value="Liverpool">Liverpool, UK</option>
              <option value="Sheffield">Sheffield, UK</option>
              <option value="Newcastle">Newcastle, UK</option>
              <option value="Belfast">Belfast, UK</option>
            </select>
          </div>
          <div class="flex items-end">
            <button onclick="startScrape()" class="w-full px-5 py-2.5 rounded-xl text-xs font-bold transition bg-[#ff5700] hover:bg-orange-600 text-white flex items-center justify-center gap-2 shadow-lg shadow-orange-600/30">
              <i data-lucide="play" class="w-4 h-4 fill-white"></i> Start UK Scrape
            </button>
          </div>
        </div>

        <!-- Terminal -->
        <div class="bg-black/90 border border-stone-800 rounded-xl p-4">
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-stone-800 text-xs text-stone-400 mono">
            <span class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-orange-500 animate-pulse"></span> Scraper Console Output</span>
            <button onclick="clearConsole()" class="hover:text-white">Clear</button>
          </div>
          <div id="consoleBody" class="mono text-xs text-stone-300 h-64 overflow-y-auto space-y-1">
            <div class="text-stone-500">// Ready. Select a UK city and click 'Start UK Scrape'.</div>
          </div>
        </div>
      </div>
    </div>

  </main>

  <script>
    let allChurches = [];
    let eventSource = null;

    async function init() {
      lucide.createIcons();
      await loadChurches();
      initStream();
    }

    async function loadChurches() {
      const res = await fetch('/api/leads');
      allChurches = await res.json();
      updateMetrics();
      renderChurchCards();
    }

    function updateMetrics() {
      document.getElementById('totalBadge').textContent = allChurches.length;
      document.getElementById('mTotal').textContent = allChurches.length;
      const websites = allChurches.filter(c => c.Website && c.Website.length > 5).length;
      document.getElementById('mWebsites').textContent = websites;
      const emails = allChurches.filter(c => c.Emails && c.Emails.length > 3).length;
      document.getElementById('mEmails').textContent = emails;
      const sent = allChurches.filter(c => c.Status === 'sent').length;
      document.getElementById('mSent').textContent = sent;
    }

    function switchNav(tab) {
      if (tab === 'leads') {
        document.getElementById('leadsSection').classList.remove('hidden');
        document.getElementById('scrapeSection').classList.add('hidden');
        document.getElementById('navLeadsBtn').className = 'px-4 py-2 rounded-xl text-xs font-bold transition bg-[#ff5700] text-white flex items-center gap-2 shadow-lg shadow-orange-600/20';
        document.getElementById('navScrapeBtn').className = 'px-4 py-2 rounded-xl text-xs font-bold transition text-stone-400 hover:text-white hover:bg-stone-900 flex items-center gap-2';
        loadChurches();
      } else {
        document.getElementById('leadsSection').classList.add('hidden');
        document.getElementById('scrapeSection').classList.remove('hidden');
        document.getElementById('navScrapeBtn').className = 'px-4 py-2 rounded-xl text-xs font-bold transition bg-[#ff5700] text-white flex items-center gap-2 shadow-lg shadow-orange-600/20';
        document.getElementById('navLeadsBtn').className = 'px-4 py-2 rounded-xl text-xs font-bold transition text-stone-400 hover:text-white hover:bg-stone-900 flex items-center gap-2';
      }
    }

    function generateEmail(c) {
      const name = c['Church Name'] || 'Church';
      const city = c.City || 'your area';
      const subject = `Quick question about Sunday AV at ${name}`;
      const body = `Hi Media & Tech Team,

Noticed the great production and Sunday service work your team is doing over at ${name} in ${city}.

One of the biggest hurdles church media directors share with us is the Sunday scramble: when the pastor quotes a scripture off-script mid-sermon, and the booth is frantically searching, copying, and formatting slides before the moment passes.

We built Pewbeam (https://pewbeam.com/) specifically for that. It uses real-time AI audio recognition to listen to the sermon and automatically project the exact Bible verses on screens and livestream lower-thirds (NDI / OBS / vMix compatible) with zero manual searching.

Would you be open to a 2-minute video walkthrough to see if it could save your team time this Sunday?

Warm regards,

Pewbeam Team (https://pewbeam.com)`;
      return { subject, body };
    }

    function generateDM(c) {
      const name = c['Church Name'] || 'Church';
      const city = c.City || 'your city';
      return `Hey team! Saw your media & AV production work with ${name} in ${city}. Quick question: how does your booth team currently handle unexpected scripture quotes when the pastor goes off sermon notes?

We built an AI tool called Pewbeam (https://pewbeam.com) that detects spoken scriptures live and pushes verses to projector screens and OBS/NDI lower-thirds automatically. Would love to send a 60-second clip if you're curious!`;
    }

    function renderChurchCards() {
      const container = document.getElementById('churchList');
      const query = (document.getElementById('searchInput')?.value || '').toLowerCase();
      const city = document.getElementById('cityFilter')?.value || 'all';
      const status = document.getElementById('statusFilter')?.value || 'all';

      const filtered = allChurches.filter(c => {
        const matchesCity = (city === 'all') || (c.City && c.City.toLowerCase() === city.toLowerCase());
        const matchesStatus = (status === 'all') || (c.Status === status) || (!c.Status && status === 'new');
        const matchesQuery = !query || 
          (c['Church Name'] && c['Church Name'].toLowerCase().includes(query)) ||
          (c.City && c.City.toLowerCase().includes(query)) ||
          (c.Emails && c.Emails.toLowerCase().includes(query));
        return matchesCity && matchesStatus && matchesQuery;
      });

      if (!filtered.length) {
        container.innerHTML = `
          <div class="text-center py-16 bg-[#131110] border border-dashed border-stone-800 rounded-2xl text-stone-500 text-sm">
            No UK churches match your current filter.
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map(c => {
        const isSent = c.Status === 'sent';
        const cardClass = isSent ? 'bg-[#151c16] border-2 border-emerald-500/70 shadow-lg shadow-emerald-950/20' : 'bg-[#131110] border border-stone-800/80';
        const emailObj = generateEmail(c);
        const dmText = generateDM(c);
        const emailList = (c.Emails || '').split(';').map(e => e.trim()).filter(Boolean);

        return `
          <div class="${cardClass} rounded-2xl p-5 hover:border-stone-700 transition">
            <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-extrabold text-base text-white tracking-tight">${c['Church Name']}</h3>
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-stone-800 text-stone-300 border border-stone-700 font-semibold">
                    ★ ${c.Rating || '4.8'} (${c['Reviews Count'] || 120})
                  </span>
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30 font-semibold">
                    🇬🇧 ${c.City}
                  </span>
                  ${isSent ? '<span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold flex items-center gap-1"><i data-lucide="check" class="w-3 h-3"></i> Contacted</span>' : ''}
                </div>
                <p class="text-xs text-stone-400 mt-1">${c.Address || c.City + ', United Kingdom'}</p>
              </div>

              <!-- Quick Action Bar -->
              <div class="flex items-center space-x-2 w-full md:w-auto justify-end">
                <button onclick="toggleChurchStatus('${c['Church Name']}')" class="px-3 py-1.5 rounded-xl text-xs font-bold ${isSent ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40' : 'bg-stone-800 hover:bg-stone-700 text-stone-300 border border-stone-700'} flex items-center gap-1.5 transition">
                  <i data-lucide="${isSent ? 'check-circle' : 'circle'}" class="w-3.5 h-3.5 ${isSent ? 'text-emerald-400' : 'text-stone-500'}"></i>
                  ${isSent ? 'Contacted' : 'Mark Sent'}
                </button>
                <button onclick="copyEmail(this, '${encodeURIComponent(emailObj.subject)}', '${encodeURIComponent(emailObj.body)}', '${c['Church Name']}')" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#ff5700] hover:bg-orange-600 text-white flex items-center gap-1.5 shadow-lg shadow-orange-600/20 transition">
                  <i data-lucide="mail" class="w-3.5 h-3.5"></i> Copy Email
                </button>
                <button onclick="copySimple(this, '${encodeURIComponent(dmText)}')" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-stone-800 hover:bg-stone-700 border border-stone-700 text-stone-200 flex items-center gap-1.5 transition">
                  <i data-lucide="message-square" class="w-3.5 h-3.5"></i> Copy DM
                </button>
                ${c.Website ? `<a href="${c.Website}" target="_blank" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-stone-900 hover:bg-stone-800 border border-stone-700 text-sky-400 flex items-center gap-1"><i data-lucide="globe" class="w-3.5 h-3.5"></i> Site</a>` : ''}
              </div>
            </div>

            <!-- Emails Row -->
            <div class="flex flex-wrap items-center gap-2 pt-3 border-t border-stone-800/80">
              <span class="text-[11px] font-semibold text-stone-400 flex items-center gap-1"><i data-lucide="at-sign" class="w-3 h-3 text-orange-400"></i> Media Emails:</span>
              ${emailList.length ? emailList.map(em => `
                <button onclick="copySimple(this, '${encodeURIComponent(em)}')" class="text-[11px] px-2.5 py-0.5 rounded-lg bg-stone-900 border border-stone-700 text-emerald-400 hover:border-emerald-500 font-mono flex items-center gap-1 transition">
                  ${em} <i data-lucide="copy" class="w-2.5 h-2.5 text-stone-500"></i>
                </button>
              `).join('') : '<span class="text-[11px] text-stone-500 italic">No email scraped</span>'}
            </div>
          </div>
        `;
      }).join('');

      lucide.createIcons();
    }

    async function toggleChurchStatus(name) {
      const c = allChurches.find(x => x['Church Name'] === name);
      if (!c) return;
      c.Status = (c.Status === 'sent') ? 'new' : 'sent';
      await fetch('/api/leads/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ church_name: name, status: c.Status })
      });
      updateMetrics();
      renderChurchCards();
    }

    async function copyEmail(button, encSubj, encBody, name) {
      const subj = decodeURIComponent(encSubj);
      const body = decodeURIComponent(encBody);
      const full = `Subject: ${subj}\n\n${body}`;
      await writeClipboard(full);

      // Auto-mark as sent
      const c = allChurches.find(x => x['Church Name'] === name);
      if (c && c.Status !== 'sent') {
        c.Status = 'sent';
        await fetch('/api/leads/status', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ church_name: name, status: 'sent' })
        });
      }

      animateButton(button, 'Email Copied & Sent!');
      updateMetrics();
      renderChurchCards();
    }

    async function copySimple(button, encText) {
      const text = decodeURIComponent(encText);
      await writeClipboard(text);
      animateButton(button, 'Copied!');
    }

    async function writeClipboard(text) {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
          return;
        }
      } catch (e) {}
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try { document.execCommand('copy'); } catch (err) {}
      document.body.removeChild(ta);
    }

    function animateButton(button, label) {
      const orig = button.innerHTML;
      button.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-white"></i> ${label}`;
      button.classList.add('bg-emerald-600');
      lucide.createIcons();
      setTimeout(() => {
        button.innerHTML = orig;
        button.classList.remove('bg-emerald-600');
        lucide.createIcons();
      }, 2000);
    }

    function exportInstantlyCSV() {
      if (!allChurches.length) return alert('No churches to export.');
      const headers = ['Church Name', 'Email', 'Website', 'City', 'Phone', 'Subject', 'Email Body'];
      const rows = [headers.join(',')];
      allChurches.forEach(c => {
        const emObj = generateEmail(c);
        const primaryEmail = (c.Emails || '').split(';')[0].trim();
        const row = [
          `"${(c['Church Name'] || '').replace(/"/g, '""')}"`,
          `"${primaryEmail.replace(/"/g, '""')}"`,
          `"${(c.Website || '').replace(/"/g, '""')}"`,
          `"${(c.City || '').replace(/"/g, '""')}"`,
          `"${(c.Phone || '').replace(/"/g, '""')}"`,
          `"${emObj.subject.replace(/"/g, '""')}"`,
          `"${emObj.body.replace(/"/g, '""')}"`
        ];
        rows.push(row.join(','));
      });
      const blob = new Blob([rows.join('\\n')], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pewbeam_uk_outreach_${new Date().toISOString().slice(0,10)}.csv`;
      a.click();
    }

    async function startScrape() {
      const city = document.getElementById('scrapeCitySelect').value;
      appendConsole(`Triggering scrape for ${city}...`);
      await fetch('/api/scrape/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city })
      });
    }

    function initStream() {
      if (eventSource) eventSource.close();
      eventSource = new EventSource('/api/scrape/stream');
      eventSource.addEventListener('log', (e) => {
        const data = JSON.parse(e.data);
        appendConsole(`[${data.time}] ${data.text}`);
      });
    }

    function appendConsole(text) {
      const b = document.getElementById('consoleBody');
      const div = document.createElement('div');
      div.className = text.includes('Added') || text.includes('Found') ? 'text-emerald-400' : 'text-stone-300';
      div.textContent = text;
      b.appendChild(div);
      b.scrollTop = b.scrollHeight;
    }

    function clearConsole() {
      document.getElementById('consoleBody').innerHTML = '';
    }

    window.onload = init;
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_CONTENT


def main():
    port = int(os.getenv("PORT", 8080))
    print("\n=======================================================")
    print(">> PEWBEAM UK CHURCH OUTREACH HUB IS LIVE!")
    print(f">> Open in your browser: http://127.0.0.1:{port}")
    print("=======================================================\n")
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        timeout_graceful_shutdown=0,
        timeout_keep_alive=5,
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
