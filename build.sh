python -m nuitka --standalone --onefile --include-package=psutil --include-package=pynvml --include-package=rich --include-package=asciichartpy moni.py
mv ./moni.bin ./moni
sudo chmod -R 777 ./moni
sudo mv ./moni /usr/local/bin