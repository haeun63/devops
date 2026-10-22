import html
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from urllib.request import Request, urlopen

MODEL = os.environ.get("MODEL", "qwen3:0.6b")
PORT = int(os.environ.get("WEB_PORT", "8000"))
APP_NAME = os.environ.get("APP_NAME", "Qwen Web")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

class Handler(BaseHTTPRequestHandler):
    def page(self, question="", answer="", status=200):
        content = f"""<!doctype html>
<html lang="ko"><meta charset="utf-8">
<title>{APP_NAME}</title>
<style>
body {{ max-width: 680px; margin: 50px auto; padding: 20px;
        font-family: sans-serif; line-height: 1.7; }}
textarea {{ box-sizing: border-box; width: 100%; padding: 12px; }}
button {{ margin-top: 12px; padding: 10px 20px; cursor: pointer; }}
pre {{ white-space: pre-wrap; background: #f1f5f9; padding: 20px; }}
</style>
<h1>짧은 대화</h1>
<p>모델: <strong>{html.escape(MODEL)}</strong></p>
<form method="post" action="/">
<label for="question">짧은 질문을 입력하세요.</label>
<textarea id="question" name="question" rows="3" maxlength="300" required>{html.escape(question)}</textarea>
<button type="submit">질문 보내기</button>
</form>
<p>첫 응답은 느릴 수 있습니다. 답변이 나올 때까지 기다려 주세요.</p>
<h2>답변</h2><pre>{html.escape(answer or "아직 질문을 보내지 않았습니다.")}</pre>
</html>"""
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        self.page()

    def do_POST(self):
        if self.path != "/":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 8192:
                self.send_error(400, "Invalid input size")
                return
            form = parse_qs(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeError):
            self.send_error(400, "Invalid input")
            return
        question = form.get("question", [""])[0].strip()[:300]
        if not question:
            self.page(answer="질문을 입력하세요.", status=400)
            return
        payload = {
            "model": MODEL,
            "prompt": question,
            "system": "한국어로 짧고 쉬운 문장 한두 개로 답하세요.",
            "think": False,
            "stream": False,
            "options": {"num_ctx": 8192, "num_predict": 512},
        }
        request = Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=90) as response:
                result = json.load(response)

            if not isinstance(result, dict):
                raise ValueError("Ollama 응답이 JSON 객체가 아닙니다.")

            # 웹 서버를 실행한 터미널에 진단 정보 출력
            print(
                f"종료 사유: {result.get('done_reason')} | "
                f"생성 토큰: {result.get('eval_count')} | "
                f"thinking 출력 있음: {bool(result.get('thinking'))}",
                flush=True,
            )

            answer = result.get("response") or ""

            if not isinstance(answer, str):
                raise ValueError("Ollama 답변이 문자열이 아닙니다.")

            answer = answer.strip() or "답변이 비어 있습니다. 짧게 다시 질문해 보세요."

            # 생성 한도에 걸렸다면 웹페이지에도 안내
            if result.get("done_reason") == "length":
                answer += "\n\n[안내: 생성 길이 제한에 도달하여 답변이 중간에 끝났을 수 있습니다.]"

            self.page(question, answer)
        except HTTPError as error:
            self.page(question, f"Ollama 오류: HTTP {error.code}. 모델 이름과 ollama list를 확인하세요.", 502)
        except (URLError, TimeoutError, OSError):
            self.page(question, "Ollama 서버에 연결하지 못했거나 응답 시간이 초과되었습니다. 서버 실행 상태를 확인하세요.", 502)
        except (ValueError, AttributeError):
            self.page(question, "Ollama 응답을 읽지 못했습니다. 서버 버전과 상태를 확인하세요.", 502)

if __name__ == "__main__":
    with HTTPServer(("127.0.0.1", PORT), Handler) as server:
        print(f"웹 접속: http://localhost:{PORT}", flush=True)
        print(f"사용 모델: {MODEL}", flush=True)
        print("종료: Ctrl+C", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("웹앱을 종료했습니다.")
