"""Metriques GitHub pour le depot Simeis (issues + labels)."""

import io
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = "evanferron/simeis"
# Token optionnel au cas où on dépasse la limite de requêtes par heure
TOKEN = os.environ.get("GITHUB_TOKEN")


def fetch_issues():
    """Récupère toutes les issues paginées depuis l'API GitHub."""
    all_issues = []
    page = 1
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    # Récupération des issues - 100 max par page (paginées)
    while True:
        url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            # Envoi de la requête et récupération de la réponse
            with urllib.request.urlopen(req, timeout=10) as resp:
                batch = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(
                    "Erreur 401 : définissez la variable d'environnement GITHUB_TOKEN"
                )
            elif e.code == 403:
                print("Erreur 403 : limite de taux atteinte, utilisez un GITHUB_TOKEN")
            elif e.code == 404:
                print(f"Erreur 404 : dépôt '{REPO}' introuvable")
            else:
                print(f"Erreur HTTP {e.code}")
            return []

        if not batch:
            break

        # Ajout des issues sans les pull requests à la liste
        # L'api de GitHub retourne les issues avec les pull requests inclues, on les filtre ici
        all_issues.extend(i for i in batch if "pull_request" not in i)
        page += 1

    return all_issues


def compute_metrics(issues):
    """Calcule les métriques à partir de la liste des issues."""
    total = len(issues)
    # Compte le nombre d'issues ouvertes et fermées
    open_count = sum(1 for i in issues if i["state"] == "open")
    closed_count = total - open_count

    label_counter = Counter()
    no_label_count = 0
    for issue in issues:
        labels = issue.get("labels", [])
        if not labels:
            no_label_count += 1
        for label in labels:
            label_counter[label["name"]] += 1

    return {
        "total": total,
        "open": open_count,
        "closed": closed_count,
        "by_label": label_counter.most_common(),
        "no_label": no_label_count,
    }


def print_metrics(metrics):
    """Affiche les métriques dans le terminal."""
    sep = "-" * 40

    print(sep)
    print(f"  Dépôt : {REPO}")
    print(sep)
    print(f"  Total issues : {metrics['total']}")
    print(f"  Ouvertes     : {metrics['open']}")
    print(f"  Fermées      : {metrics['closed']}")
    print(sep)
    print("  Issues par label :")
    if metrics["by_label"]:
        for label, count in metrics["by_label"]:
            pct = count / metrics["total"] * 100 if metrics["total"] else 0
            print(f"    {label:<30} {count:>4}  ({pct:.1f}%)")
    else:
        print("    (aucun label utilisé)")
    print(f"    {'(sans label)':<30} {metrics['no_label']:>4}")
    print(sep)


def main():
    """Point d'entrée du script."""
    if not TOKEN:
        print(
            "Utilisez GITHUB_TOKEN pour augmenter la limite de taux (60 -> 5000 req/h)"
        )

    print(f"Récupération des issues de {REPO}...")
    issues = fetch_issues()
    if not issues:
        return

    print(f"{len(issues)} issues récupérées.\n")
    metrics = compute_metrics(issues)
    print_metrics(metrics)


if __name__ == "__main__":
    main()
