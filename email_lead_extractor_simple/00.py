import subprocess
subprocess.run(["powershell", "-Command", "pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r install_files/pip_reqs.txt"])
