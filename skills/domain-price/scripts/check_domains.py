#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_domains.py -- disponibilite (RDAP) + prix multi-sources (Porkbun USD, OVH EUR)
Usage: python check_domains.py domaine1.com domaine2.fr ...
Sans dependance externe (urllib uniquement). Sortie ASCII (console Windows).

Sources:
- Disponibilite : RDAP via https://rdap.org/domain/<d> (registre officiel; 404 = libre, 200 = pris)
- Prix Porkbun  : https://api.porkbun.com/api/json/v3/pricing/get (gratuit, sans cle, ~900 TLDs, USD)
- Prix OVH      : https://api.ovh.com/1.0/order/catalog/public/domain?ovhSubsidiary=FR (gratuit, sans cle, EUR HT)
Cache: %TEMP%\\domain-price-cache\\ (Porkbun 24h, OVH 7j - le catalogue fait ~30 Mo, on n'en garde qu'un extrait)
"""
import json, os, sys, time, tempfile, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

CACHE_DIR = os.path.join(tempfile.gettempdir(), "domain-price-cache")
os.makedirs(CACHE_DIR, exist_ok=True)
UA = {"User-Agent": "domain-price-skill/1.0"}

def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

def cached(path, max_age_s, fetch):
    if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < max_age_s:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    data = fetch()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data

def porkbun_pricing():
    def fetch():
        _, body = http_get("https://api.porkbun.com/api/json/v3/pricing/get", timeout=60)
        return json.loads(body)["pricing"]
    return cached(os.path.join(CACHE_DIR, "porkbun.json"), 24 * 3600, fetch)

def ovh_pricing():
    def fetch():
        _, body = http_get("https://api.ovh.com/1.0/order/catalog/public/domain?ovhSubsidiary=FR", timeout=180)
        slim = {}
        for p in json.loads(body).get("plans", []):
            creates = [pr["price"] / 1e8 for pr in p.get("pricings", [])
                       if pr.get("mode") == "create-default" and pr.get("price", 0) < 9e13]
            if creates:
                slim[p["planCode"]] = {"create_min": min(creates), "create_std": max(creates)}
        return slim
    return cached(os.path.join(CACHE_DIR, "ovh_slim.json"), 7 * 24 * 3600, fetch)

def rdap_status(domain):
    """404 = libre, 200 = pris, autre = inconnu (verifier a la main)."""
    try:
        status, _ = http_get("https://rdap.org/domain/" + domain, timeout=25)
        return "PRIS" if status == 200 else "?" + str(status)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "LIBRE"
        return "?" + str(e.code)
    except Exception as e:
        return "ERREUR:" + type(e).__name__

def tld_of(domain):
    return domain.split(".", 1)[1].lower() if "." in domain else ""

def main(argv):
    domains = [d.strip().lower() for d in argv if d.strip()]
    if not domains:
        print("Usage: python check_domains.py domaine1.com domaine2.fr ...")
        return 1
    pb = porkbun_pricing()
    try:
        ovh = ovh_pricing()
    except Exception as e:
        print("[avertissement] catalogue OVH indisponible: %s" % e)
        ovh = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        statuses = list(ex.map(rdap_status, domains))

    fmt = "%-35s %-8s %-22s %-22s"
    print(fmt % ("DOMAINE", "RDAP", "PORKBUN USD (reg/ren)", "OVH EUR HT (promo/std)"))
    print("-" * 92)
    for d, st in zip(domains, statuses):
        tld = tld_of(d)
        p = pb.get(tld)
        pbs = "%s / %s" % (p["registration"], p["renewal"]) if p else "TLD absent"
        o = ovh.get(tld)
        os_ = "%.2f / %.2f" % (o["create_min"], o["create_std"]) if o else "TLD absent"
        print(fmt % (d, st, pbs, os_))
    print("\nRappels: RDAP 404=libre (fiable, registre direct). Porkbun = prix reels achetables.")
    print("OVH create_std ~ prix de renouvellement [approximation]. Croiser avec Vercel MCP et,")
    print("pour les promos 1ere annee, tld-list.com via navigateur (bloque les bots HTTP).")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
