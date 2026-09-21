"""Gate fixed HIGH/CRITICAL vulnerabilities; retain the full scan for review."""
import json
import sys


def blockers(report):
    return [
        issue
        for result in report.get("Results", [])
        for issue in (result.get("Vulnerabilities") or [])
        if issue.get("Severity") in ("HIGH", "CRITICAL") and issue.get("FixedVersion")
    ]


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as source:
        report = json.load(source)
    # Reject an empty/unexpected document instead of accidentally passing it.
    if report.get("SchemaVersion") != 2 or "ArtifactName" not in report:
        raise SystemExit("Invalid Trivy report")
    found = blockers(report)
    for issue in found:
        print(f"BLOCK: {issue['VulnerabilityID']} {issue['PkgName']} "
              f"{issue['InstalledVersion']} -> {issue['FixedVersion']}")
    print(f"{len(found)} fixable HIGH/CRITICAL vulnerabilities. Review trivy.json for all findings.")
    raise SystemExit(1 if found else 0)
