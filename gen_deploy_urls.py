"""Generate deploy_urls.php to deploy only urls.py fix."""
import base64
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'lmdmanagersystem', 'urls.py'), 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

php = '<?php\n'
php += 'header("Content-Type: text/plain; charset=utf-8");\n'
php += 'echo "=== Deploy urls.py fix ===\\n\\n";\n'
php += '$base = "/home/tumxxzse/lmdmanagerpro/";\n'
php += '$d = base64_decode("' + b64 + '");\n'
php += 'file_put_contents($base . "lmdmanagersystem/urls.py", $d);\n'
php += 'echo "[urls.py] " . strlen($d) . " bytes\\n";\n'
php += '$cache = glob($base . "lmdmanagersystem/__pycache__/*.pyc");\n'
php += 'foreach ($cache as $cf) { unlink($cf); }\n'
php += 'echo "__pycache__ cleared: " . count($cache) . " files\\n";\n'
php += 'touch($base . "tmp/restart.txt");\n'
php += 'echo "restart.txt touched\\n\\nDone! Restart the app.\\n";\n'
php += '?>'

out = os.path.join(BASE_DIR, 'deploy_urls.php')
with open(out, 'w', encoding='utf-8') as f:
    f.write(php)

print(f"Created {out} ({os.path.getsize(out)} bytes)")
