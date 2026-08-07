// scripts/collectors/tls.mjs
import tls from "node:tls";
import { makeFinding, na, STATUS } from "../lib/finding.mjs";

const CAT = "security.tls";
const LEGACY = new Set(["TLSv1", "TLSv1.1", "SSLv3"]);
const mk = (id, metric, value, status, reason, evidence, at, source = "tls.connect") =>
  makeFinding({ id, category: CAT, metric, value, unit: id === "tls.expiry" ? "days" : "", status, reason, evidence, source, collectedAt: at });

export function gradeCert(c, ctx) {
  const at = ctx.collectedAt;
  const out = [];
  // expiry
  if (typeof c.daysLeft !== "number") out.push(na({ id: "tls.expiry", category: CAT, metric: "Cert expiry", reason: "no cert", collectedAt: at }));
  else if (c.daysLeft < 14) out.push(mk("tls.expiry", "Cert expiry", c.daysLeft, STATUS.FAIL, "expires in < 14 days", `${c.daysLeft}d`, at));
  else if (c.daysLeft < 30) out.push(mk("tls.expiry", "Cert expiry", c.daysLeft, STATUS.WARN, "expires in < 30 days", `${c.daysLeft}d`, at));
  else out.push(mk("tls.expiry", "Cert expiry", c.daysLeft, STATUS.PASS, "valid", `${c.daysLeft}d`, at));
  // protocol
  const proto = c.protocol || "unknown";
  out.push(LEGACY.has(proto)
    ? mk("tls.protocol", "TLS protocol", proto, STATUS.FAIL, "legacy protocol accepted", proto, at)
    : mk("tls.protocol", "TLS protocol", proto, STATUS.PASS, "modern protocol", proto, at));
  // trust
  if (c.selfSigned || c.hostnameMatch === false) out.push(mk("tls.trust", "Cert trust", c.selfSigned ? "self-signed" : "hostname-mismatch", STATUS.FAIL, "untrusted certificate", c.selfSigned ? "self-signed" : "hostname mismatch", at));
  else out.push(mk("tls.trust", "Cert trust", "trusted", STATUS.PASS, "chain + hostname ok", "", at));
  return out;
}

export function parseSslLabs(json, ctx) {
  const grade = json?.endpoints?.[0]?.grade ?? null;
  if (!grade) return na({ id: "tls.ssllabs", category: CAT, metric: "SSL Labs grade", reason: "no grade returned", collectedAt: ctx.collectedAt });
  const bad = /^[CDEF]/.test(grade) || grade === "T" || grade === "M";
  return makeFinding({ id: "tls.ssllabs", category: CAT, metric: "SSL Labs grade", value: grade, unit: "", status: bad ? STATUS.FAIL : (grade.startsWith("B") ? STATUS.WARN : STATUS.PASS), reason: `SSL Labs ${grade}`, evidence: grade, source: "ssllabs", collectedAt: ctx.collectedAt });
}

export async function collect(ctx) {
  if (!ctx.host) return [na({ id: "tls.all", category: CAT, metric: "TLS", reason: "no host", collectedAt: ctx.collectedAt })];
  const cert = await new Promise((resolve) => {
    const socket = tls.connect({ host: ctx.host, port: 443, servername: ctx.host, rejectUnauthorized: false, timeout: 12000 }, () => {
      // SECURITY: rejectUnauthorized:false is intentional — we must inspect bad certs.
      // We read cert metadata only, send NOTHING, then close immediately. See spec §5.2.
      const peer = socket.getPeerCertificate();
      const protocol = socket.getProtocol();
      const authorized = socket.authorized;
      const authError = socket.authorizationError ? String(socket.authorizationError) : "";
      socket.end();
      resolve({ peer, protocol, authorized, authError });
    });
    socket.on("error", (e) => resolve({ error: e.message }));
    socket.on("timeout", () => { socket.destroy(); resolve({ error: "tls timeout" }); });
  });

  if (cert.error || !cert.peer || !cert.peer.valid_to) {
    return [na({ id: "tls.all", category: CAT, metric: "TLS", reason: cert.error || "no certificate", collectedAt: ctx.collectedAt })];
  }
  const validTo = new Date(cert.peer.valid_to).getTime();
  const daysLeft = Math.floor((validTo - ctx.now) / 86400000);
  const selfSigned = /self.signed/i.test(cert.authError) || (cert.peer.issuer && cert.peer.subject && cert.peer.issuer.CN === cert.peer.subject.CN && !cert.authorized);
  const hostnameMatch = !/hostname|altname/i.test(cert.authError);
  return gradeCert({ daysLeft, protocol: cert.protocol, selfSigned, hostnameMatch }, ctx);
}
