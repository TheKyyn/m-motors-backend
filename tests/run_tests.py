#!/usr/bin/env python
"""
Script pour exécuter les tests du système RAG.

Utilisation:
    python -m tests.run_tests
"""
import os
import sys
import pytest


def run_tests():
    """Exécute tous les tests du dossier tests/rag"""
    print("=== Exécution des tests pour le système RAG ===")
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    rag_tests_dir = os.path.join(tests_dir, "rag")
    
    args = [
        "-v",                       # Mode verbeux
        "-xvs",                     # Arrêter à la première erreur, montrer les prints et ne pas capturer stdout
        "--tb=native",              # Format natif pour les traces d'erreurs
        rag_tests_dir               # Chemin des tests à exécuter
    ]
    
    print(f"Recherche de tests dans: {rag_tests_dir}")
    
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ Tous les tests ont réussi !")
    else:
        print(f"\n❌ Des tests ont échoué (exit code: {exit_code})")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests()) 