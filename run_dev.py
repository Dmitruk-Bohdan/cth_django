# run_dev.py
import subprocess
import sys

print('✨ Admin panel: http://127.0.0.1:8000/admin')
subprocess.run([sys.executable, 'manage.py', 'runserver'])