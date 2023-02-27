cd /D "%~dp0"

robocopy ../src/abba_python abba_python /E

tar -cvzf abba-pack-win.tar.gz abba_python img win