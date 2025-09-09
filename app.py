
from flask import Flask, render_template, request, jsonify
import requests
import os
import time
import traceback
import json
import re

app = Flask(__name__)

# Config (change via env if you want)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2:7b")
# Per-request timeout (seconds). We keep this large to tolerate slower models.
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "600"))

# Chunking settings: approximate max characters per chunk.
# Tune to be smaller on low-RAM/slow machines. ~2000-3000 chars works well.
MAX_CHUNK_CHARS = int(os.environ.get("MAX_CHUNK_CHARS", "2500"))

def chunk_text_by_sentence(text, max_chars=MAX_CHUNK_CHARS):
    """Split text into sentence-based chunks, each <= max_chars (approx)."""
    # Rough sentence split (keeps punctuation)
    sentences = re.split(r'(?<=[\.\?\!\n])\s+', text.strip())
    chunks = []
    cur = []
    cur_len = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # If a single sentence is larger than max_chars, break it by chars
        if len(s) > max_chars:
            # flush current
            if cur:
                chunks.append(" ".join(cur).strip())
                cur = []
                cur_len = 0
            # split the long sentence into subparts
            for i in range(0, len(s), max_chars):
                chunks.append(s[i:i+max_chars].strip())
            continue

        # if adding this sentence would exceed max, flush current chunk
        if cur_len + len(s) + 1 > max_chars:
            chunks.append(" ".join(cur).strip())
            cur = [s]
            cur_len = len(s)
        else:
            cur.append(s)
            cur_len += len(s) + 1
    if cur:
        chunks.append(" ".join(cur).strip())
    return chunks

def call_ollama_generate(prompt, model=OLLAMA_MODEL, timeout=OLLAMA_TIMEOUT):
    payload = {"model": model, "prompt": prompt, "stream": False}
    print(">>> [OLLAMA] send (len chars):", len(prompt))
    t0 = time.time()
    r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=timeout)
    elapsed = time.time() - t0
    print(f"<<< [OLLAMA] status: {getattr(r, 'status_code', 'no-status')} elapsed: {elapsed:.2f}s")
    text_resp = getattr(r, "text", "")[:4000]
    print("<<< [OLLAMA] raw (truncated):", text_resp[:800].replace("\n","\\n"))
    r.raise_for_status()
    try:
        data = r.json()
    except Exception as e:
        raise RuntimeError("Ollama returned non-JSON response: " + str(text_resp[:1000])) from e

    # Try to extract the model's text from typical response shapes
    if isinstance(data, dict):
        if "response" in data and data["response"]:
            return data["response"]
        # choices/outputs might contain text
        choices = data.get("choices") or data.get("outputs") or []
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                return first.get("content") or first.get("text") or (first.get("message") or {}).get("content") or json.dumps(first)
            return str(first)
    # fallback
    return json.dumps(data)

def summarize_with_ollama_simple(text, prompt_extra="Summarize the following text in 3-4 sentences:"):
    prompt = f"{prompt_extra}\n\n{text}"
    return call_ollama_generate(prompt)

def hierarchical_summarize(text):
    """
    1) Split the input into chunks by sentence (approx)
    2) Summarize each chunk individually
    3) Combine chunk summaries and summarize them to get final summary
    Returns dict with final summary and intermediate summaries.
    """
    # 1) chunk text
    chunks = chunk_text_by_sentence(text, max_chars=MAX_CHUNK_CHARS)
    print(f"[INFO] input length {len(text)} chars -> {len(chunks)} chunk(s) (max {MAX_CHUNK_CHARS})")

    chunk_summaries = []
    for i, ch in enumerate(chunks, start=1):
        try:
            print(f"[INFO] Summarizing chunk {i}/{len(chunks)} (len {len(ch)} chars)")
            # Customize the chunk summarization instruction if you want
            chunk_summary = summarize_with_ollama_simple(ch, prompt_extra="Summarize this passage in 2-3 sentences, focusing on the main points:")
            chunk_summaries.append(chunk_summary.strip())
        except Exception as e:
            print(f"[ERROR] chunk {i} failed: {e}")
            # include a placeholder and continue
            chunk_summaries.append(f"[Error summarizing chunk {i}: {e}]")

    # If only one chunk, return that as final (no extra combine step needed)
    if len(chunk_summaries) == 1:
        final = chunk_summaries[0]
        return {"final_summary": final, "chunks": len(chunks), "chunk_summaries": chunk_summaries}

    # 3) combine chunk summaries and summarize them
    combined = "\n\n".join(chunk_summaries)
    try:
        print("[INFO] Combining chunk summaries into final summary (len chars:", len(combined), ")")
        final_prompt = "Combine the following short summaries into a single clear 4-6 sentence cohesive summary. Make it natural and remove repetition:\n\n" + combined
        final_summary = call_ollama_generate(final_prompt)
    except Exception as e:
        print("[ERROR] final combine failed:", e)
        final_summary = " ".join(chunk_summaries)  # fallback: stitched summaries

    return {"final_summary": final_summary.strip(), "chunks": len(chunks), "chunk_summaries": chunk_summaries}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.form.get("text", "").strip()
    if not text:
        return jsonify({"error": "no text provided"}), 400

    try:
        result = hierarchical_summarize(text)
        return jsonify({"summary": result["final_summary"],
                        "chunks": result["chunks"],
                        "chunk_summaries": result["chunk_summaries"]})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(debug=True)
