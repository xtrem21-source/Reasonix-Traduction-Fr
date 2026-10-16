// Harnais de verification : charge le bundle i18n patche et verifie que la
// traduction francaise fonctionne reellement.
//
// Export du bundle : { E as a, C as i, w as n, T as o, y as r, v as t }
//   o = T (traduire)   r = y (boot)   i = C (langue courante)   n = w (adopt)
//
// Usage: node verify_i18n.mjs <chemin_bundle.mjs> [langue]
import { pathToFileURL } from 'node:url';

const file = process.argv[2];
const lang = process.argv[3] ?? 'fr';

// --- Stubs navigateur ---
const store = { 'rx-lang': lang };
globalThis.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
};
try {
  Object.defineProperty(globalThis.navigator, 'languages', { value: [lang], configurable: true });
  Object.defineProperty(globalThis.navigator, 'language', { value: lang, configurable: true });
} catch (e) {
  console.log('navigator non patcheable:', e.message);
}
globalThis.document = { documentElement: {}, };
globalThis.location = { reload: () => { throw new Error('reload() appele'); } };

const mod = await import(pathToFileURL(file).href);

// boot : fixe la langue de session
let booted;
try {
  booted = mod.r();
} catch (e) {
  console.log('BOOT erreur:', e.message);
}
console.log('langue au boot   :', booted);

// C() renvoie la langue courante
console.log('langue courante  :', mod.i());

// Test de traduction sur quelques cles
const samples = [
  '查看大图：{alt}',
  '关闭图片',
  '图表',
  '柱状图',
  '微信支付',
  '重命名聊天',
];
let ok = 0, ko = 0;
for (const key of samples) {
  const out = mod.o(key, { alt: 'X' });
  const translated = out !== key;
  if (translated) ok++; else ko++;
  console.log(`  ${translated ? 'FR ' : 'CH '} ${JSON.stringify(key)} -> ${JSON.stringify(out)}`);
}
console.log(`\nRESULTAT: ${ok} traduites, ${ko} non traduites`);
console.log(ok > 0 ? 'VERDICT: OK' : 'VERDICT: ECHEC');
