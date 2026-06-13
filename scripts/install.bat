@echo off
setlocal enabledelayedexpansion

curl -L -k -o iprad.zip https://github.com/deltaaa00/iprad/archive/refs/heads/main.zip


set "hash_file=%USERPROFILE%\iprad.hash"


for /f "skip=1 tokens=*" %%i in ('certutil -hashfile "iprad.zip" SHA256 ^| findstr /v "CertUtil"') do (
    set "new_hash=%%i"
    goto :break_loop
)
:break_loop


set "new_hash=%new_hash: =%"

if exist "%hash_file%" (
    set /p old_hash=<"%hash_file%"
    
    if "!old_hash!" == "!new_hash!" (
        echo You have the latest version
        del iprad.zip
        exit /b 0
    )
)


(echo|set /p="!new_hash!") > "%hash_file%"

echo New version detected! Starting extraction...

powershell -Command "Expand-Archive -Path 'iprad.zip' -DestinationPath '.' -Force"

cd iprad-main

pip install -e .

cd ..
del iprad.zip
pause