# -*- coding: utf-8 -*-
# 字幕工坊 · 本地配音助手
# 为字幕工坊.html 提供 http://127.0.0.1:8765 本地配音服务（edge-tts）
# 双击「启动配音服务.bat」即可运行；关掉窗口即停止
import io
import asyncio
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import edge_tts

PORT = 8765
DEFAULT_VOICE = 'zh-CN-YunxiNeural'


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _reply(self, code, body, ctype='text/plain; charset=utf-8'):
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path == '/ping':
                self._reply(200, b'pong')
                return
            if u.path == '/tts':
                text = (q.get('text') or [''])[0].strip()
                if not text:
                    self._reply(400, 'error: no text')
                    return
                voice = (q.get('voice') or [DEFAULT_VOICE])[0]
                rate = (q.get('rate') or ['-8%'])[0]
                mp3 = asyncio.run(self.synth(text, voice, rate))
                self._reply(200, mp3, 'audio/mpeg')
                print('[ok] %d bytes | %s' % (len(mp3), text[:24]))
                return
            self._reply(404, 'error: not found')
        except Exception as e:
            print('[error]', e)
            try:
                self._reply(500, ('error: %s' % e).encode('utf-8'))
            except Exception:
                pass

    async def synth(self, text, voice, rate):
        c = edge_tts.Communicate(text, voice, rate=rate)
        buf = io.BytesIO()
        async for chunk in c.stream():
            if chunk['type'] == 'audio':
                buf.write(chunk['data'])
        return buf.getvalue()

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    print('==============================================')
    print('  字幕工坊 · 本地配音助手已启动')
    print('  服务地址: http://127.0.0.1:%d' % PORT)
    print('  请保持本窗口开着；回到字幕工坊点 AI 配音即可')
    print('  关闭本窗口 = 停止服务')
    print('==============================================')
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
