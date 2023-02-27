REM untar the code to the install folder
REM tar -cvzf abba-code.tar.gz abba-code img
tar -xzvf "%PREFIX%\abba-pack-win.tar.gz" -C "%PREFIX%"

set shortcutPath='%userprofile%\Desktop\ABBA.lnk'
set shortcutTarget='%PREFIX%\win\run-abba.bat'
set shortcutIcon='%PREFIX%\img\logo256x256.ico'

REM '%PREFIX%\img\logo256x256.ico'

@echo off
REM set /p "id=Shortcut path: "

echo %shortcutPath%

@echo off
REM set /p "id=Shortcut target: "

echo %shortcutTarget%

@echo off
REM set /p "id=Installing shortcut: "

%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\powershell.exe "$s=(New-Object -COM WScript.Shell).CreateShortcut("%shortcutPath%");$s.IconLocation="%shortcutIcon%";$s.TargetPath="%shortcutTarget%";$s.Save()"

REM add shortcut to C:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs

set shortcutProgramsPath='%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ABBA.lnk'

%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\powershell.exe "$s=(New-Object -COM WScript.Shell).CreateShortcut("%shortcutProgramsPath%");$s.IconLocation="%shortcutIcon%";$s.TargetPath="%shortcutTarget%";$s.Save()"

echo ABBA shortcuts installed

@echo off
REM set /p "id=Shortcut installed "
