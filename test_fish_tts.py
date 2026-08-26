import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fish_tts import FishTTSClient


class Handler(BaseHTTPRequestHandler):
    calls = 0
    payload = None
    def do_POST(self):
        Handler.calls += 1
        length = int(self.headers["Content-Length"])
        Handler.payload = json.loads(self.rfile.read(length))
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("X-Generation-Id", "test-generation")
        self.end_headers()
        self.wfile.write(b"fake-mp3")
    def log_message(self, *_args):
        pass


def test_synthesize_raw_audio(tmp_path: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        out = tmp_path / "speech.mp3"
        result = FishTTSClient("test-key", endpoint=f"http://127.0.0.1:{server.server_port}", retries=0).synthesize(
            "你好，主人", out, voice="voice-1")
        assert out.read_bytes() == b"fake-mp3"
        assert result.generation_id == "test-generation"
        assert Handler.payload == {"model": "fish-audio/s2.1-pro-free", "input": "你好，主人", "response_format": "mp3", "voice": "voice-1"}
    finally:
        server.shutdown()
        thread.join()
