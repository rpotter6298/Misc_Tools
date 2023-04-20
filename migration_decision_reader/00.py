import subprocess
subprocess.run(["powershell", "-Command", "pip install -r install_files/pip_reqs.txt"])
import os
from pathlib import Path
import shutil
import json



def main():
    install_files = Path("install_files")
    os.startfile(install_files / "tesseract-ocr.exe")
    tess_path = Path(input("Paste Tesseract path: "))
    lang_path = Path("install_files") / "tessdata"
    for file in lang_path.iterdir():
        #print(file, tess_path / file.name)
        shutil.copy(file, tess_path / "tessdata" / file.name)
    poppler = Path("install_files") / "poppler"
    for folder in poppler.iterdir():
        pop = folder.name
    shutil.copytree(poppler, tess_path, dirs_exist_ok=True)
    poppler_path = tess_path / pop
    fpdic = {
        "poppler_path" : str(poppler_path),
        "tess_path" : str(tess_path)
    }
    configdir = Path.home() / ".migration_decision_reader"
    Path.mkdir(configdir, exist_ok=True)
    with open(configdir / "local_config.json", "w") as file:
        file.write(json.dumps(fpdic))
    input("Process complete. Press return to exit.")

#subprocess.run(["powershell", "-Command", "pip install -r install_files/pip_reqs.txt"])
main()

