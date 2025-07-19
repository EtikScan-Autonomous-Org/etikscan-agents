# agents/provisioner/main.py

import os
import sys
from github import Github

def main():
    """
    Point d'entrée principal pour l'Agent Provisioner.
    """
    print("Agent Provisioner démarré.")

    # Récupérer les informations fournies par GitHub Actions
    try:
        github_token = os.environ["GITHUB_TOKEN"]
        issue_number = int(os.environ["ISSUE_NUMBER"])
        repo_name = os.environ["GITHUB_REPOSITORY"]
    except KeyError as e:
        print(f"Erreur: La variable d'environnement {e} n'a pas été trouvée.")
        sys.exit(1)

    # Se connecter à l'API de GitHub
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)

    print(f"Tâche reçue de l'issue #{issue.number}: {issue.title}")
    print(f"Demandé par: {issue.user.login}")
    print("Contenu de la demande :")
    print(issue.body)
    
    # --- C'est ici que nous ajouterons la logique de l'agent (AutoGen) ---
    print("\nPlanification en cours... (logique à implémenter)")
    
    # L'agent ajoutera un commentaire à l'issue pour montrer qu'il a bien reçu la tâche
    issue.create_comment("✅ Tâche reçue. L'Agent Provisioner commence l'analyse.")
    
    print("Agent Provisioner a terminé sa tâche initiale.")


if __name__ == "__main__":
    main()