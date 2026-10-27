import io, os, shutil, subprocess, sys

ASAR = r'J:\Reasonix Studio\resources\app.asar'
WORK = r'G:\Temp\asar-sendkey3'
NEW = r'G:\Temp\app-sendkey3.asar'
LOG = r'J:\Reasonix\dev\voix-winh\patch-sendkey.log'

def log(m):
    print(m)
    with io.open(LOG, 'a', encoding='utf-8') as f:
        f.write(m + '\n')

io.open(LOG, 'w', encoding='utf-8').write('')
log('=== handler instrumente (v3, decoupage par accolades) ===')

if os.path.exists(WORK):
    shutil.rmtree(WORK, ignore_errors=True)

log('1. extraction...')
r = subprocess.run('npx -y @electron/asar extract "%s" "%s"' % (ASAR, WORK),
                   shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode != 0:
    log('ECHEC extraction : ' + ((r.stderr or r.stdout) or '')[:400]); sys.exit(2)

MAIN = os.path.join(WORK, 'src', 'main.js')
m = io.open(MAIN, encoding='utf-8').read()

debut = m.find('ipcMain.handle("shell:send-key"')
if debut < 0:
    log('ECHEC : handler introuvable'); sys.exit(3)

# fin reelle : comptage des accolades a partir de la premiere '{'
k = m.find('{', debut)
prof = 0
j = k
while j < len(m):
    c = m[j]
    if c == '{':
        prof += 1
    elif c == '}':
        prof -= 1
        if prof == 0:
            j += 1
            break
    j += 1
if prof != 0:
    log('ECHEC : accolades non equilibrees'); sys.exit(4)
fin = j
while fin < len(m) and m[fin] == ')':
    fin += 1
if fin < len(m) and m[fin] == ';':
    fin += 1

log('2. handler : %d caracteres (debut %d, fin %d)' % (fin - debut, debut, fin))
log('   dernier morceau : ' + repr(m[fin - 40:fin]))

bloc = '''ipcMain.handle("shell:send-key", (event, combo) => {
  const __fs = require("node:fs");
  const __L = (msg) => {
    try {
      __fs.appendFileSync(
        "J:\\\\Reasonix\\\\dev\\\\voix-winh\\\\sendkey.log",
        new Date().toISOString() + " " + msg + "\\n"
      );
    } catch (e) {}
  };
  try {
    __L("appel recu combo=" + String(combo));
    if (combo !== "winh") { __L("combo ignore"); return false; }
    const exe = (process.env.SystemRoot || "C:\\\\Windows") + "\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe";
    __L("exe=" + exe + " existe=" + __fs.existsSync(exe));
    const cp = require("node:child_process");
    __L("child_process : spawn=" + typeof cp.spawn);
    const p = cp.spawn(
      exe,
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File",
       "J:\\\\Reasonix\\\\dev\\\\voix-winh\\\\winh.ps1"],
      { detached: false, stdio: "ignore", windowsHide: true }
    );
    p.on("error", (e) => { __L("spawn ECHEC : " + String(e && e.message || e)); });
    p.unref();
    __L("spawn lance, pid=" + String(p.pid));
    return true;
  } catch (e) {
    __L("EXCEPTION : " + String(e && e.message || e));
    return false;
  }
});'''

m2 = m[:debut] + bloc + m[fin:]
io.open(MAIN, 'w', encoding='utf-8').write(m2)
log('3. handler remplace')

r = subprocess.run('node --check "%s"' % MAIN, shell=True, capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
if r.returncode != 0:
    log('ECHEC syntaxe : ' + ((r.stderr or '') or '')[:400]); sys.exit(6)
log('4. syntaxe main.js : OK')

log('5. repaquetage...')
r = subprocess.run('npx -y @electron/asar pack "%s" "%s"' % (WORK, NEW),
                   shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode != 0 or not os.path.exists(NEW):
    log('ECHEC pack : ' + ((r.stderr or r.stdout) or '')[:400]); sys.exit(7)
log('   app-sendkey3.asar : %d octets' % os.path.getsize(NEW))

bak = ASAR + '.avant-sendkey3'
if not os.path.exists(bak):
    shutil.copy2(ASAR, bak)
    log('6. sauvegarde : ' + bak)
shutil.copy2(NEW, ASAR)
log('7. app.asar remplace (%d octets)' % os.path.getsize(ASAR))
log('=== TERMINE ===')
