import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import path from "node:path";

// Small Node-only bridge to the existing runtime compiler. No emitted tree or loader dependency.
const require = createRequire(import.meta.url);
const ts = require("typescript");
const cache = new Map();
export function loadTypeScript(filename) {
  const absolute = path.resolve(filename);
  if (cache.has(absolute)) return cache.get(absolute).exports;
  const module = {exports: {}};
  cache.set(absolute, module);
  const source = ts.transpileModule(readFileSync(absolute, "utf8"), {
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2018},
    fileName: absolute,
  }).outputText;
  const localRequire = createRequire(absolute);
  const resolve = (specifier) => specifier.startsWith(".")
    ? loadTypeScript(path.resolve(path.dirname(absolute), `${specifier}.ts`))
    : localRequire(specifier);
  new Function("require", "module", "exports", source)(resolve, module, module.exports);
  return module.exports;
}
