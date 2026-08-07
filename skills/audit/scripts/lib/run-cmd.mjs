// scripts/lib/run-cmd.mjs
import { exec } from "node:child_process";

// Why exec() and not execFile(): on Windows the tools we drive (npm/pnpm/yarn/npx)
// are .cmd shims, and since the CVE-2024-27980 mitigation Node REFUSES to spawn a
// .cmd via execFile without shell:true. shell:true + an args array triggers DEP0190,
// so we pass a single quoted string to exec() instead. SECURITY: callers MUST NOT
// pass untrusted, un-validated values as args — the only dynamic arg in this tool is
// the audited URL, which is validated by isShellSafe() before it ever reaches here.
export function isShellSafe(s) {
  // A legitimate http(s) URL never contains whitespace or shell metacharacters
  // unencoded; reject anything that does so it can never break out of the quotes.
  return typeof s === "string" && !/[\s"'`$&|;<>(){}\\]/.test(s);
}

// Quote an arg for a shell command line. Double quotes work for both cmd.exe and
// POSIX shells for our simple args (audit subcommands, flags, a validated URL).
export function quoteArg(a) {
  const s = String(a);
  if (s === "") return '""';
  if (!/[\s"'`$&|;<>(){}\\*?]/.test(s)) return s;
  return '"' + s.replace(/(["\\$`])/g, "\\$1") + '"';
}

export function buildCommand(cmd, args) {
  return [cmd, ...args.map(quoteArg)].join(" ");
}

export function runCmd(cmd, args, opts = {}) {
  const line = buildCommand(cmd, args);
  return new Promise((resolve) => {
    exec(line, { maxBuffer: opts.maxBuffer ?? 32 * 1024 * 1024, timeout: opts.timeout ?? 120000, cwd: opts.cwd, env: opts.env }, (err, stdout, stderr) => {
      resolve({ code: err?.code ?? 0, stdout: stdout ?? "", stderr: stderr ?? "", error: err && !stdout ? err.message : null });
    });
  });
}
