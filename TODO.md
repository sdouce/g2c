# ✅ TODO - Projet `G2C ==> GLPI to CENTREON`

## 🎯 Objectif général

Déployer et valider une API Python packagée en Docker, utilisée pour Intégrer depuis la CMDB GLPI vers CENTREON.
Gérer Unitairement :
  les filesystems Unix et Windows, 
  Les ports de Switchs 
  Les cartes réseaux .
  etc.... 
  
---

## 🛠️ Pré-requis

- [ ] GitLab Runner configuré sur environnement CI/CD
- [ ] Docker et docker-compose installés
- [ ] Accès aux ressources Centreon, GLPI, VMware, IPAM
- [ ] Fichiers `.sdb` SQLite présents et valides dans `/sqlite`
- [ ] Variables d’environnement sensibles gérées en `.env` ou GitLab CI Variables

---

## 🔧 Étapes techniques

### 🔹 1. Mise en place de l'environnement
- [ ] Construire l’image Docker locale :  
  ```bash
  docker build -t python-api-docker .
