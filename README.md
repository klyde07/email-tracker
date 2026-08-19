# 📧 Email Tracker - Projet Éducatif

Projet scolaire complet pour comprendre le fonctionnement du tracking d'emails via pixel invisible.

## 🎯 Fonctionnalités

- ✅ **Pixel invisible** : Image 1x1 transparente qui se charge à l'ouverture
- ⏱️ **Temps passé** : Calcule la durée de chaque session de lecture
- 🔄 **Réouvertures** : Compte le nombre de fois où l'email est rouvert
- 📍 **Géolocalisation** : Détecte la ville approximative via l'IP
- 📊 **Dashboard** : Interface web pour visualiser les statistiques
- 📡 **API JSON** : Export des données brutes

## 🚀 Installation (VS Code)

### 1. Ouvrir le dossier dans VS Code
```
Fichier → Ouvrir le dossier → Sélectionne "email_tracker_project"
```

### 2. Créer un environnement virtuel (recommandé)
Ouvre le terminal intégré de VS Code (`Ctrl + ù`) et tape :
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer le serveur
```bash
python app.py
```
Tu verras dans le terminal :
```
📧 EMAIL TRACKER - Mode Éducatif
============================================
Accueil    : http://127.0.0.1:5000/
Dashboard  : http://127.0.0.1:5000/dashboard
API JSON   : http://127.0.0.1:5000/api/data
```

### 5. Tester
- Ouvre ton navigateur sur `http://127.0.0.1:5000/`
- Va sur le Dashboard
- Envoie-toi un email HTML avec le pixel (voir exemple ci-dessous)
- Rafraîchis le dashboard pour voir les stats

## 📧 Comment envoyer un email de test

### Option A : Gmail (mode HTML)
1. Ouvre Gmail dans ton navigateur
2. Clique sur "Composer"
3. Dans le corps du message, clique sur les 3 points (⋮) → "Insérer du HTML"
4. Colle le code HTML avec le pixel

### Option B : Thunderbird / Outlook
1. Crée un nouvel email
2. Passe en mode "Édition HTML" (souvent via un bouton `< >`)
3. Colle le code HTML

### Code HTML à copier
```html
<html>
  <body>
    <h1>Bonjour !</h1>
    <p>Ceci est un email de test pour mon projet scolaire.</p>
    <img src="http://192.168.1.42:5000/pixel?id=marie_dupont" 
         width="1" height="1" 
         style="display:block;">
  </body>
</html>
```

**⚠️ Important :** Remplace `192.168.1.42` par **ton IP locale**.
Pour la trouver :
- **Windows** : ouvre CMD → tape `ipconfig` → cherche "Adresse IPv4"
- **Mac** : Terminal → `ifconfig | grep inet`
- **Linux** : Terminal → `ip addr show`

## 📊 Structure du projet

```
email_tracker_project/
├── app.py                 ← Serveur Flask (code principal)
├── requirements.txt       ← Dépendances Python
├── templates/
│   └── dashboard.html     ← Page du dashboard
└── README.md              ← Ce fichier
```

## ⚖️ Cadre légal & éthique

Ce projet est **strictement éducatif**. En vrai :
- Le tracking d'emails est soumis au **RGPD** en Europe
- Il faut le **consentement explicite** du destinataire
- Il faut **informer** que l'email est tracké
- Ne jamais utiliser à des fins malveillantes

## 🛠️ Dépannage

| Problème | Solution |
|----------|----------|
| "ModuleNotFoundError" | Lance `pip install -r requirements.txt` |
| Le pixel ne se charge pas | Vérifie que ton firewall autorise le port 5000 |
| La ville est "Local" | Normal en localhost, teste depuis un autre appareil |
| Images bloquées dans Gmail | Le destinataire doit cliquer "Afficher les images" |
| Port 5000 déjà utilisé | Change le port dans `app.py` : `app.run(port=5001)` |

## 📝 Pour ton oral

Points à souligner :
1. **Le token unique** (`id=marie_dupont`) permet d'identifier chaque destinataire
2. **Les sessions** : si 2 requêtes du même token sont espacées de < 2 min = même session
3. **Géolocalisation** : approximation via IP, pas d'adresse exacte
4. **Limites** : images bloquées par défaut, VPNs, mode texte brut
5. **RGPD** : nécessité du consentement

Bonne chance pour ton projet ! 🎓
