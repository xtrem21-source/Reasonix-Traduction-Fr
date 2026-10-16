"""Ajoute le français aux chaines NATIVES de l'Electron (asar).

Couvre : page de demarrage, menu contextuel, dialogues d'erreur, dialogue
ancienne version, menu du tray (libelles + ligne d'etat reconstruite en FR).

Ecrit le resultat dans build/asar_fr/ (copie de build/asar_orig/, patchee).
"""
import os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = paths.ASAR_ORIG
DST = paths.ASAR_FR

if not os.path.isdir(SRC):
    raise SystemExit(
        f'source pristine introuvable : {SRC}\n'
        'Lancez d\'abord : python3 setup_asar_orig.py'
    )
if os.path.isdir(DST):
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

def patch(name, reps):
    p = os.path.join(DST, 'src', name)
    t = open(p, encoding='utf-8').read()
    for tag, old, new in reps:
        c = t.count(old)
        if c != 1:
            print(f'  !! {name} {tag}: {c} occurrence(s) -> IGNORE')
            continue
        t = t.replace(old, new, 1)
        print(f'  ok {name} {tag}')
    open(p, 'w', encoding='utf-8').write(t)

# ---- uilang.js : accepter fr ----
patch('uilang.js', [
    ('lang',
     '  if (want === "zh" || want === "en") return want;\n  return isChinese(machineLocale) ? "zh" : "en";',
     '  if (want === "zh" || want === "en" || want === "fr") return want;\n  if (isFrench(machineLocale)) return "fr";\n  return isChinese(machineLocale) ? "zh" : "en";'),
    ('isFrench',
     'module.exports = { uiLanguage };',
     'function isFrench(tag) {\n  return String(tag ?? "").toLowerCase().startsWith("fr");\n}\n\nmodule.exports = { uiLanguage };'),
])

# ---- starting.js : page de demarrage ----
patch('starting.js', [
    ('text',
     '  zh: ["Reasonix Studio 正在启动", "安装或重启电脑后的首次启动可能需要一分钟。"],\n};',
     '  zh: ["Reasonix Studio 正在启动", "安装或重启电脑后的首次启动可能需要一分钟。"],\n  fr: ["Reasonix Studio démarre", "Le premier démarrage après l\'installation ou le redémarrage peut prendre une minute."],\n};'),
    ('pick',
     '  const [title, note] = String(locale).toLowerCase().startsWith("zh") ? TEXT.zh : TEXT.en;',
     '  const loc = String(locale).toLowerCase();\n  const [title, note] = loc.startsWith("zh") ? TEXT.zh : loc.startsWith("fr") ? TEXT.fr : TEXT.en;'),
])

# ---- editmenu.js : menu contextuel ----
patch('editmenu.js', [
    ('fr-block',
     '  en: {\n    edit: "Edit",',
     '  fr: {\n'
     '    edit: "Édition",\n    undo: "Annuler",\n    redo: "Rétablir",\n    cut: "Couper",\n'
     '    copy: "Copier",\n    paste: "Coller",\n    selectAll: "Tout sélectionner",\n'
     '    pasteAndMatchStyle: "Coller et adapter au style",\n    delete: "Supprimer",\n'
     '    substitutions: "Substitutions",\n    showSubstitutions: "Afficher les substitutions",\n'
     '    smartQuotes: "Guillemets intelligents",\n    smartDashes: "Tirets intelligents",\n'
     '    textReplacement: "Remplacement de texte",\n    speech: "Dictée",\n'
     '    startSpeaking: "Commencer la dictée",\n    stopSpeaking: "Arrêter la dictée",\n  },\n'
     '  en: {\n    edit: "Edit",'),
])

# ---- hostexit.js : avis de plantage du noyau ----
patch('hostexit.js', [
    ('fr',
     '  return {\n    message: "The kernel exited unexpectedly last time",',
     '  if (String(locale).toLowerCase().startsWith("fr")) {\n'
     '    return {\n'
     '      message: "Le noyau s\'est arrêté de façon inattendue la dernière fois",\n'
     '      ok: "OK",\n'
     '      detail: `Le processus du noyau s\'est arrêté en cours de route lors de la dernière session (${how}). Vos sessions ne sont pas affectées. Pour signaler un problème, joignez shell.log, host.log et le dossier crash depuis :\\n\\n${logsDir}`,\n'
     '    };\n  }\n'
     '  return {\n    message: "The kernel exited unexpectedly last time",'),
])

# ---- shelllog.js : erreurs de demarrage ----
patch('shelllog.js', [
    ('hints',
     'const HINTS = {\n  timeout: [\n    "The kernel started but did not finish starting in time. Security software scanning a new or updated install is a common cause; starting Studio again usually works.",\n    "内核已启动，但没有在限定时间内完成启动。安全软件扫描新安装或刚更新的程序是常见原因；再次启动通常可以。",\n  ],\n  exited: [\n    "The kernel process stopped before it was ready. Anything it printed is above; host.log has the rest.",\n    "内核进程在就绪前就停止了。它输出过的内容在上面，host.log 里有更多。",\n  ],\n  spawn: [\n    "The kernel program could not be run. Security software blocking or locking it is a common cause.",\n    "无法运行内核程序。安全软件拦截或占用它是常见原因。",\n  ],\n};',
     'const HINTS = {\n  timeout: [\n    "The kernel started but did not finish starting in time. Security software scanning a new or updated install is a common cause; starting Studio again usually works.",\n    "内核已启动，但没有在限定时间内完成启动。安全软件扫描新安装或刚更新的程序是常见原因；再次启动通常可以。",\n    "Le noyau a démarré mais n\'a pas fini de démarrer dans les temps. Un logiciel de sécurité qui analyse une installation nouvelle ou mise à jour en est souvent la cause ; relancer Studio suffit généralement.",\n  ],\n  exited: [\n    "The kernel process stopped before it was ready. Anything it printed is above; host.log has the rest.",\n    "内核进程在就绪前就停止了。它输出过的内容在上面，host.log 里有更多。",\n    "Le processus du noyau s\'est arrêté avant d\'être prêt. Ce qu\'il a affiché se trouve ci-dessus ; le reste est dans host.log.",\n  ],\n  spawn: [\n    "The kernel program could not be run. Security software blocking or locking it is a common cause.",\n    "无法运行内核程序。安全软件拦截或占用它是常见原因。",\n    "Le programme du noyau n\'a pas pu être lancé. Un logiciel de sécurité qui le bloque ou le verrouille en est souvent la cause.",\n  ],\n};'),
    ('pick',
     '  const zh = String(locale).toLowerCase().startsWith("zh");\n  const hint = HINTS[code]?.[zh ? 1 : 0];\n  const body = hint ? `${reason}\\n\\n${hint}` : reason;\n  if (zh) {\n    return { title: "Reasonix Studio 无法启动", detail: `${body}\\n\\n日志位于：\\n${logDir}` };\n  }',
     '  const loc = String(locale).toLowerCase();\n  const zh = loc.startsWith("zh");\n  const fr = loc.startsWith("fr");\n  const hint = HINTS[code]?.[zh ? 1 : fr ? 2 : 0];\n  const body = hint ? `${reason}\\n\\n${hint}` : reason;\n  if (zh) {\n    return { title: "Reasonix Studio 无法启动", detail: `${body}\\n\\n日志位于：\\n${logDir}` };\n  }\n  if (fr) {\n    return { title: "Reasonix Studio n\'a pas pu démarrer", detail: `${body}\\n\\nLes journaux se trouvent dans :\\n${logDir}` };\n  }'),
])

# ---- packagegrants.js : fenetre non peinte ----
patch('packagegrants.js', [
    ('fr',
     '  return {\n    title: "Reasonix Studio could not open its window",',
     '  if (String(locale).toLowerCase().startsWith("fr")) {\n'
     '    return {\n'
     '      title: "Reasonix Studio n\'a pas pu ouvrir sa fenêtre",\n'
     '      detail:\n'
     '        "Les fichiers chargés par Reasonix Studio portent des entrées d\'accès accordant un paquet d\'application Windows (AppContainer) précis, " +\n'
     '        "et les processus isolés de Chromium se ferment en chargeant un tel fichier. Studio a tenté de les retirer et a été refusé pour :\\n\\n" +\n'
     '        shown + (more > 0 ? `\\n…et ${more} de plus` : "") +\n'
     '        "\\n\\nLancez Reasonix Studio une fois en tant qu\'administrateur et il les retirera lui-même.",\n'
     '    };\n  }\n'
     '  return {\n    title: "Reasonix Studio could not open its window",'),
])

# ---- main.js : dialogue de l'ancienne installation ----
patch('main.js', [
    ('legacy',
     '        buttons: ["移到废纸篓", "先留着"],\n        defaultId: 0,\n        cancelId: 1,\n        message: "找到一个旧版本的 Reasonix Studio",\n        detail: `${bundle}\\n\\n它和当前这个共用同一份数据，所以两个图标打开的是同一个窗口。移到废纸篓不会动你的会话和设置。`,',
     '        buttons: ["Placer dans la corbeille", "Garder"],\n        defaultId: 0,\n        cancelId: 1,\n        message: "Une ancienne version de Reasonix Studio a été trouvée",\n        detail: `${bundle}\\n\\nElle partage les mêmes données que l\'actuelle : les deux icônes ouvrent la même fenêtre. La placer dans la corbeille ne touchera ni vos sessions ni vos réglages.`,'),
])

# ---- tray.js : libelles + ligne d'etat en francais ----
patch('tray.js', [
    ('fr-labels',
     '    const line = state.fold?.line ?? "";\n    const words = state.fold?.labels ?? {};',
     '    // Libelles et ligne d\'etat francais, reconstruits depuis les compteurs\n'
     '    // (le noyau ne fournit que zh/en).\n'
     '    const fold = state.fold ?? {};\n'
     '    const bits = [];\n'
     '    if (fold.attention > 0) bits.push(`${fold.attention} en attente`);\n'
     '    if (fold.working > 0) bits.push(`${fold.working} en cours`);\n'
     '    if (fold.jobs > 0) bits.push(`${fold.jobs} tâches en arrière-plan`);\n'
     '    const line = bits.length ? bits.join(" · ") : "Rien en cours";\n'
     '    const words = {\n'
     '      open: "Ouvrir Reasonix Studio",\n'
     '      closeToTray: "Continuer en arrière-plan à la fermeture",\n'
     '      quit: "Quitter Reasonix",\n'
     '    };'),
])

print('Phase 3 OK — tray')
print('Phase 2 OK — shelllog/packagegrants/main')
print('Phase 1 OK — uilang/starting/editmenu/hostexit')
