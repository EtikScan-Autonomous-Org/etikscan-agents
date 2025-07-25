#!/bin/bash
# .devcontainer/setup.sh

set -e

echo "🚀 Configuration de l'environnement n8n Provisioner..."

# Installation de n8n globalement
echo "📦 Installation de n8n..."
npm install -g n8n

# Création du répertoire de données n8n
mkdir -p ~/.n8n

# Configuration des variables d'environnement par défaut
cat > ~/.n8n/config <<EOF
# Configuration n8n pour Codespaces
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=https
EXECUTIONS_DATA_SAVE_ON_ERROR=all
EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true
EOF

# Création du script de démarrage
cat > ~/start-n8n.sh <<'EOF'
#!/bin/bash

echo "🔧 Démarrage de n8n..."

# Récupération de l'URL publique du Codespace
if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    export WEBHOOK_URL="https://${CODESPACE_NAME}-5678.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    echo "🌐 URL Webhook détectée: $WEBHOOK_URL"
else
    echo "⚠️  Variables Codespaces non détectées, utilisation de localhost"
    export WEBHOOK_URL="http://localhost:5678"
fi

# Configuration des variables d'environnement
export N8N_HOST=0.0.0.0
export N8N_PORT=5678
export N8N_PROTOCOL=https

echo "🎯 Démarrage de n8n sur $WEBHOOK_URL"
n8n start
EOF

chmod +x ~/start-n8n.sh

# Création du script de diagnostic
cat > ~/diagnose-webhook.sh <<'EOF'
#!/bin/bash

echo "🔍 Diagnostic de la configuration webhook..."

if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    WEBHOOK_URL="https://${CODESPACE_NAME}-5678.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    echo "✅ URL Webhook: $WEBHOOK_URL"
    
    echo "🌐 Test de connectivité..."
    curl -I "$WEBHOOK_URL" 2>/dev/null && echo "✅ URL accessible" || echo "❌ URL non accessible"
    
    echo "📋 Configuration à utiliser dans Telegram:"
    echo "   URL: $WEBHOOK_URL/webhook/telegram"
else
    echo "❌ Variables Codespaces non disponibles"
    echo "   Assurez-vous d'être dans un GitHub Codespace"
fi
EOF

chmod +x ~/diagnose-webhook.sh

echo "✅ Configuration terminée!"
echo ""
echo "🎯 Commandes disponibles:"
echo "   ~/start-n8n.sh     - Démarre n8n avec la configuration webhook"
echo "   ~/diagnose-webhook.sh - Test la configuration webhook"
echo ""
echo "🚀 Pour démarrer: ./start-n8n.sh"