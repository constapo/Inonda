"""Defensive containment for hosts YOU OWN/ADMINISTER.

Given an audit log of an AI agent's commands, (1) find the agent's last command and
the source IP it came from, (2) build a quarantine plan that cuts the host off
from the network while keeping an admin path, and (3) optionally apply it.

Safety: the default is a DRY RUN that only prints the plan. Applying requires
root AND --i-own-this-host. This module never connects to remote systems.
Attribution caveat: a source IP is where the command *arrived from* (often a proxy,
VPN, Tor exit or compromised relay), not proof of the actor's physical location.
"""
import csv
import ipaddress
import json
import os
import shutil
import subprocess
from . import Finding


def last_commands(log_lines):
    """JSONL records: {"ts","agent_id","src_ip","cmd"}. Returns last record per agent."""
    last = {}
    for line in log_lines:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if "agent_id" in r and (r["agent_id"] not in last or r.get("ts", 0) >= last[r["agent_id"]].get("ts", 0)):
            last[r["agent_id"]] = r
    return last


def classify_ip(ip):
    a = ipaddress.ip_address(ip)
    if a.is_loopback: return "loopback"
    if a.is_private: return "private"
    if a.is_global: return "public"
    return "reserved"


def geolocate(ip, db_csv=None):
    """Offline lookup in a user-supplied CSV (cidr,country,city,lat,lon,asn).
    Approximate; VPN/proxy/Tor exits resolve to the relay, not the person."""
    if not db_csv or not os.path.exists(db_csv):
        return None
    a = ipaddress.ip_address(ip)
    with open(db_csv, newline="") as f:
        for row in csv.DictReader(f):
            if a in ipaddress.ip_network(row["cidr"], strict=False):
                return row
    return None


def trace(log_lines, geoip_csv=None):
    out = []
    for agent, r in last_commands(log_lines).items():
        ip = r.get("src_ip")
        info = {"agent": agent, "ts": r.get("ts"), "cmd": r.get("cmd"), "src_ip": ip}
        if ip:
            info["ip_class"] = classify_ip(ip)
            info["geo"] = geolocate(ip, geoip_csv)
        out.append(info)
    return out


def quarantine_plan(admin_ip, listening=True):
    """nftables ruleset: drop everything except loopback, established, and the admin IP."""
    ipaddress.ip_address(admin_ip)  # validate to prevent rule injection
    rules = [
        "nft add table inet fs_quarantine",
        "nft add chain inet fs_quarantine in '{ type filter hook input priority -100 ; policy drop ; }'",
        "nft add chain inet fs_quarantine out '{ type filter hook output priority -100 ; policy drop ; }'",
        "nft add rule inet fs_quarantine in iif lo accept",
        "nft add rule inet fs_quarantine out oif lo accept",
        f"nft add rule inet fs_quarantine in ip saddr {admin_ip} ct state established,related,new tcp dport 22 accept",
        f"nft add rule inet fs_quarantine out ip daddr {admin_ip} ct state established,related accept",
    ]
    if listening:
        rules.append("ss -tulpn   # review listeners; stop unneeded services")
    return rules


def apply_plan(plan, confirmed_owner):
    if not confirmed_owner:
        raise PermissionError("refusing: pass --i-own-this-host")
    if os.geteuid() != 0 or not shutil.which("nft"):
        raise PermissionError("need root and nft installed")
    for cmd in plan:
        if cmd.startswith("nft "):
            subprocess.run(cmd, shell=True, check=True)  # plan is generated locally from a validated IP
    return True


def containment_findings(trace_rows):
    return [Finding("containment.agent_source", "high" if r.get("ip_class") == "public" else "medium",
                    f"Agent {r['agent']} last command from {r['src_ip']}", r) for r in trace_rows if r.get("src_ip")]
