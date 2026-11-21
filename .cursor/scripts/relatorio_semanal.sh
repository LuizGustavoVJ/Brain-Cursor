#!/usr/bin/env bash
# Gera o relatório de custos e grava em arquivo — pensado para rodar por cron do SO,
# sobrevivendo ao fechamento da IDE (ao contrário do CronCreate, que é só da sessão).
#
# Uso manual:
#   .cursor/scripts/relatorio_semanal.sh            # 30 dias
#   .cursor/scripts/relatorio_semanal.sh 7          # 7 dias
#
# Instalar no crontab do usuário (sexta 12:00):
#   crontab -e
#   0 12 * * 5 /var/www/html/cit/.cursor/scripts/relatorio_semanal.sh >> /tmp/relatorio-custos-cron.log 2>&1
#
# Ou como systemd user timer (sobrevive a reboot, não exige sessão de login ativa):
#   ~/.config/systemd/user/custos-claude.service
#       [Service]
#       Type=oneshot
#       ExecStart=/var/www/html/cit/.cursor/scripts/relatorio_semanal.sh
#   ~/.config/systemd/user/custos-claude.timer
#       [Timer]
#       OnCalendar=Fri *-*-* 12:00:00
#       Persistent=true
#       [Install]
#       WantedBy=timers.target
#   systemctl --user enable --now custos-claude.timer
#   loginctl enable-linger "$USER"     # roda mesmo sem sessão gráfica aberta
#
# O relatório lê transcripts LOCAIS (~/.cursor/projects/) — por isso precisa rodar nesta
# máquina. Um agente agendado na nuvem não enxerga esses arquivos.

set -euo pipefail

DIAS="${1:-30}"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SAIDA="$RAIZ/.cursor/cache/relatorios"
mkdir -p "$SAIDA"

ARQ="$SAIDA/custos-$(date +%Y-%m-%d).md"
python3 "$RAIZ/.cursor/scripts/relatorio_custos.py" --dias "$DIAS" --projeto "$RAIZ" > "$ARQ"

# mantém os 12 relatórios mais recentes
ls -1t "$SAIDA"/custos-*.md 2>/dev/null | tail -n +13 | xargs -r rm --

echo "Relatório de custos ($DIAS dias): $ARQ"
echo
sed -n '1,12p' "$ARQ"
echo "..."
echo "Abrir completo: $ARQ"
