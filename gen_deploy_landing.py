"""Deploy landing page + login fix + context_processors + urls.py to server."""
import base64, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, 'deploy_landing.php')

files = [
    'templates/select_institution.html',
    'templates/login.html',
    'lmdmanagersystem/urls.py',
    'core/context_processors.py',
]

php = '<?php\nheader("Content-Type: text/plain; charset=utf-8");\n'
php += 'echo "=== Deploy: landing + login + urls ===\\n\\n";\n'
php += '$base = "/home/tumxxzse/lmdmanagerpro/";\n\n'

for f in files:
    path = os.path.join(BASE_DIR, f)
    with open(path, 'rb') as fh:
        b64 = base64.b64encode(fh.read()).decode()
    php += '$d = base64_decode("' + b64 + '");\n'
    php += '$dir = dirname($base . "' + f + '");\n'
    php += 'if (!is_dir($dir)) { mkdir($dir, 0755, true); }\n'
    php += 'file_put_contents($base . "' + f + '", $d);\n'
    php += 'echo "[' + f + '] " . strlen($d) . " bytes\\n";\n\n'

php += '$patterns = array($base."lmdmanagersystem/__pycache__/*.pyc", $base."core/__pycache__/*.pyc");\n'
php += '$n=0; foreach($patterns as $p){foreach(glob($p) as $cf){unlink($cf);$n++;}}\n'
php += 'echo "\\n__pycache__ cleared: ".$n." files\\n";\n'
php += 'touch($base . "tmp/restart.txt");\n'
php += 'echo "restart.txt touched\\n\\nDone! Restart + delete this file.\\n";\n'
php += '?>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(php)
print(f"Created {OUT} ({os.path.getsize(OUT)} bytes)")
