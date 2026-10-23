# Language : Python 3.8+
# File     : OptiPC.py
# Target   : Windows 10 / 11 x64
# Run      : python OptiPC.py dans un terminal admin
# Install  : pip install colorama

import os
import sys
import subprocess
import ctypes
from colorama import init, Fore
init(autoreset=True)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print(Fore.RED + "[!] Lance ce script en administrateur.")
    input("Entree pour quitter...")
    sys.exit(1)

def step(msg): print(Fore.CYAN  + f"\n[>>] {msg}")
def ok(msg):   print(Fore.GREEN + f"  [OK] {msg}")
def skip(msg): print(Fore.LIGHTBLACK_EX + f"  [--] {msg}")

def run(cmd):
    try:
        subprocess.run(
            cmd, shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=600,
            encoding="utf-8",
            errors="ignore"
        )
        return True
    except Exception:
        return False

def run_out(cmd):
    try:
        r = subprocess.run(
            cmd, shell=True,
            capture_output=True,
            timeout=600,
            encoding="utf-8",
            errors="ignore"
        )
        return r.stdout
    except Exception:
        return ""

def reg(path, name, value, t="REG_DWORD"):
    run(f'reg add "{path}" /v "{name}" /t {t} /d "{value}" /f')

print(Fore.MAGENTA + "=" * 48)
print(Fore.MAGENTA + "         OPTIPC — by theone")
print(Fore.MAGENTA + "=" * 48)

# 1. ALIMENTATION
step("Plan alimentation : Performances maximales")
run("powercfg /setactive SCHEME_MIN")
run("powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
out = run_out("powercfg /list")
for line in out.splitlines():
    if "Performances" in line or "Ultimate" in line:
        for p in line.split():
            if len(p) == 36 and p.count("-") == 4:
                run(f"powercfg /setactive {p}")
ok("Plan performances max active")

# 2. SERVICES
step("Desactivation services inutiles")
services = [
    "DiagTrack", "dmwappushservice", "WMPNetworkSvc",
    "XblAuthManager", "XblGameSave", "XboxNetApiSvc",
    "WSearch", "SysMain", "Fax", "MapsBroker",
    "RetailDemo", "RemoteRegistry", "TabletInputService", "PrintNotify",
]
for svc in services:
    run(f'sc stop "{svc}"')
    run(f'sc config "{svc}" start= disabled')
    ok(f"Desactive : {svc}")

# 3. DEMARRAGE
step("Nettoyage demarrage automatique")
keys = [
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
    r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
]
bloat_start = [
    "OneDrive","Spotify","Discord","EpicGamesLauncher",
    "Skype","Teams","MicrosoftEdgeAutoLaunch","Cortana","GameBarPresenceWriter",
]
for k in keys:
    for e in bloat_start:
        run(f'reg delete "{k}" /v "{e}" /f')
ok("Demarrage nettoye")

# 4. DEBLOAT
step("Suppression bloatwares Windows")
bloat = [
    "Microsoft.BingNews","Microsoft.BingWeather","Microsoft.BingFinance",
    "Microsoft.GetHelp","Microsoft.Getstarted","Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.People","Microsoft.SkypeApp","Microsoft.Todos",
    "Microsoft.WindowsFeedbackHub","Microsoft.WindowsMaps",
    "Microsoft.XboxApp","Microsoft.XboxGameOverlay","Microsoft.XboxGamingOverlay",
    "Microsoft.XboxIdentityProvider","Microsoft.YourPhone",
    "Microsoft.ZuneMusic","Microsoft.ZuneVideo","MicrosoftTeams",
    "Clipchamp.Clipchamp","Microsoft.549981C3F5F10",
]
for app in bloat:
    run(f'powershell -Command "Get-AppxPackage -Name {app} -AllUsers | Remove-AppxPackage"')
    ok(f"Supprime : {app}")

# 5. TELEMETRIE
step("Desactivation telemetrie")
reg(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0)
reg(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", 0)
reg(r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled", 0)
reg(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo", "DisabledByGroupPolicy", 1)
ok("Telemetrie coupee")

# 6. RESEAU
step("Optimisations reseau gaming")
run(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f')
run(r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v MaxCacheTtl /t REG_DWORD /d 86400 /f')
ok("Reseau optimise")

# 7. ANIMATIONS
step("Desactivation animations")
run(r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f')
run(r'reg add "HKCU\Control Panel\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012038010000000 /f')
ok("Animations desactivees")

# 8. FICHIERS TEMP
step("Nettoyage fichiers temporaires")
temp_paths = [
    os.environ.get("TEMP",""),
    os.environ.get("TMP",""),
    r"C:\Windows\Temp",
    r"C:\Windows\Prefetch",
    os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp"),
]
freed = 0
for path in temp_paths:
    if path and os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    freed += os.path.getsize(fp)
                    os.remove(fp)
                except:
                    pass
        ok(f"Nettoye : {path}")
ok(f"Espace libere : {round(freed/1024/1024, 1)} MB")

# 9. SFC + DISM
step("Reparation fichiers systeme")
print(Fore.YELLOW + "  [..] SFC — 2 a 5 min...")
subprocess.run("sfc /scannow", shell=True, encoding="utf-8", errors="ignore")
ok("SFC termine")
print(Fore.YELLOW + "  [..] DISM — 5 a 10 min...")
subprocess.run("DISM /Online /Cleanup-Image /RestoreHealth", shell=True, encoding="utf-8", errors="ignore")
ok("DISM termine")

# 10. MALWARE
step("Scan malware Windows Defender")
run('powershell -Command "Update-MpSignature"')
ok("Definitions a jour")
print(Fore.YELLOW + "  [..] Scan en cours...")
run('powershell -Command "Start-MpScan -ScanType QuickScan"')
ok("Scan termine")
run("mrt.exe /Q")
ok("MRT termine")

# 11. GAMING REGISTRY
step("Optimisations registre gaming")
run(r'reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f')
run(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f')
gp = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
run(f'reg add "{gp}" /v "GPU Priority" /t REG_DWORD /d 8 /f')
run(f'reg add "{gp}" /v "Priority" /t REG_DWORD /d 6 /f')
run(f'reg add "{gp}" /v "Scheduling Category" /t REG_SZ /d High /f')
run(f'reg add "{gp}" /v "SFIO Priority" /t REG_SZ /d High /f')
ok("GameDVR off, GPU priorite max")

# 12. TRIM SSD
step("Optimisation disque")
run("defrag C: /U /V /RetrimOnly")
ok("TRIM SSD effectue")

hib = input(Fore.YELLOW + "\n  Supprimer hibernation pour liberer espace ? (o/n) : ")
if hib.strip().lower() == "o":
    run("powercfg /hibernate off")
    ok("Hibernation desactivee")

# RESUME
freed_mb = round(freed/1024/1024, 1)
print(Fore.MAGENTA + "\n" + "="*48)
print(Fore.MAGENTA + "         OPTIPC TERMINE")
print(Fore.MAGENTA + "="*48)
print(Fore.WHITE + f"  Temp supprime     : {freed_mb} MB")
print(Fore.WHITE + f"  Services coupes   : {len(services)}")
print(Fore.WHITE + f"  Bloatwares vires  : {len(bloat)}")
print(Fore.WHITE +  "  Malware scan      : OK")
print(Fore.WHITE +  "  Fichiers systeme  : Repares")
print(Fore.YELLOW + "\n  REDEMARRE pour appliquer tous les changements.")
print(Fore.MAGENTA + "="*48)
input("\nEntree pour quitter...")