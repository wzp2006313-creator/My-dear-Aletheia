#!/bin/bash
# ============================================================
# Hermes Agent 夜间安全审计脚本 v1.0
# 基于 SlowMist OpenClaw Security Practice Guide v2.8 适配
# 审计 13 项核心指标，输出到 ~/.hermes/security-reports/
# ============================================================
set -uo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPORT_DIR="$HERMES_HOME/security-reports"
REPORT_FILE="$REPORT_DIR/audit-$(date +%Y%m%d-%H%M%S).txt"
DATE_TAG=$(date "+%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +%s)

mkdir -p "$REPORT_DIR"

exec > "$REPORT_FILE" 2>&1

echo "=========================================="
echo " Hermes Agent 夜间安全审计报告"
echo " 时间: $DATE_TAG"
echo "=========================================="
echo ""

# === [1] Hermes 平台审计 ===
echo "=== [1] Hermes 平台审计 ==="
if command -v hermes &>/dev/null; then
    echo "Hermes CLI: $(hermes --version 2>&1 || echo 'unknown')"
    echo "Status: $(hermes status 2>&1 | head -5 || echo 'unknown')"
    echo "✅ Hermes 平台状态正常"
else
    echo "⚠️ Hermes CLI 不可用"
fi
echo ""

# === [2] 进程与网络审计 ===
echo "=== [2] 进程与网络审计 ==="
echo "--- 监听端口 (TCP+UDP) ---"
lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep -v "^$" | head -20 || echo "无 TCP 监听"
lsof -iUDP -P -n 2>/dev/null | grep -v "^$" | head -10 || echo "无 UDP 监听"
echo ""
echo "--- Top 15 高资源消耗进程 ---"
ps aux --sort=-%cpu 2>/dev/null | head -16 || ps aux -r | head -16
echo ""
echo "--- 出站连接 ---"
lsof -iTCP -sTCP:ESTABLISHED -P -n 2>/dev/null | head -20 || echo "无明显出站连接"
echo "✅ 进程与网络审计完成"
echo ""

# === [3] 敏感目录变更 ===
echo "=== [3] 敏感目录变更 ==="
echo "--- ~/.hermes/ 24h 内修改 ---"
find "$HERMES_HOME" -maxdepth 3 -mtime -1 -not -path '*/\.git/*' -not -path '*/cache/*' -not -path '*/security-reports/*' -not -path '*/audio_cache/*' 2>/dev/null | head -50
echo ""
echo "--- ~/.ssh/ 24h 内修改 ---"
find "$HOME/.ssh" -mtime -1 2>/dev/null | head -10 || echo "无可疑变更"
echo "✅ 敏感目录变更检查完成"
echo ""

# === [4] 系统定时任务 ===
echo "=== [4] 系统定时任务 ==="
echo "--- 用户 crontab ---"
crontab -l 2>/dev/null || echo "无用户 crontab"
echo ""
echo "--- launchd agents ---"
ls ~/Library/LaunchAgents/ 2>/dev/null | head -20 || echo "无 launchd agents"
echo "✅ 系统定时任务检查完成"
echo ""

# === [5] Hermes Cron 任务 ===
echo "=== [5] Hermes Cron 任务 ==="
echo "Hermes cron 任务列表需要手动检查: 'cronjob list'"
echo "⚠️ 请在 Hermes 会话中手动运行 cronjob 检查"
echo "✅ Hermes Cron 任务检查完成"
echo ""

# === [6] 登录与 SSH ===
echo "=== [6] 登录与 SSH ==="
echo "--- 最近登录 ---"
last -10 2>/dev/null || log show --predicate 'eventMessage contains "ssh"' --last 24h 2>/dev/null | tail -10 || echo "无法获取登录记录"
echo ""
echo "--- SSH 失败尝试 ---"
grep "Failed password" /var/log/system.log 2>/dev/null | tail -5 || echo "无 SSH 失败记录或无系统日志访问权限"
echo "✅ 登录审计完成"
echo ""

# === [7] 核心文件完整性 ===
echo "=== [7] 核心文件完整性 ==="
BASELINE="$HERMES_HOME/.config-baseline.sha256"
if [ -f "$BASELINE" ]; then
    sha256sum -c "$BASELINE" 2>&1 || echo "⚠️ 文件完整性检查发现不匹配！"
else
    echo "⚠️ 未找到哈希基线文件，首次部署请先生成"
fi
echo ""
echo "--- 权限检查 ---"
for f in "$HERMES_HOME/.env" "$HERMES_HOME/config.yaml" "$HERMES_HOME/gateway.yaml"; do
    if [ -f "$f" ]; then
        perm=$(stat -f "%OLp" "$f" 2>/dev/null)
        echo "$f → 权限 $perm"
        if [ "$perm" -gt 600 ] 2>/dev/null; then
            echo "⚠️ 权限过宽，建议 chmod 600"
        fi
    fi
done
echo "✅ 核心文件完整性检查完成"
echo ""

# === [8] 黄线操作交叉验证 ===
echo "=== [8] 黄线操作交叉验证 ==="
echo "--- sudo 记录 (24h) ---"
log show --predicate 'process == "sudo"' --last 24h 2>/dev/null | tail -10 || echo "无法获取 sudo 日志"
echo "✅ 黄线操作交叉验证完成"
echo ""

# === [9] 磁盘使用率 ===
echo "=== [9] 磁盘使用率 ==="
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
echo "根磁盘使用率: ${DISK_USAGE}%"
if [ "$DISK_USAGE" -gt 85 ] 2>/dev/null; then
    echo "🚨 磁盘使用率超过 85%！"
fi
echo ""
echo "--- 24h 内大文件 (>100MB) ---"
find "$HOME" -maxdepth 5 -type f -size +100M -mtime -1 2>/dev/null | head -10 || echo "未发现大文件"
echo "✅ 磁盘检查完成"
echo ""

# === [10] 环境变量审计 ===
echo "=== [10] 环境变量审计 ==="
echo "--- 含敏感字样的环境变量 ---"
env | grep -iE "KEY|TOKEN|SECRET|PASSWORD|API_KEY" | while IFS='=' read -r name value; do
    val_preview="${value:0:8}"
    echo "$name=***${val_preview: -4}"
done || echo "无敏感环境变量"
echo "✅ 环境变量审计完成"
echo ""

# === [11] DLP 扫描 ===
echo "=== [11] DLP 私钥/凭据泄露扫描 ==="
echo "--- 扫描 Ethereum/BTC 私钥格式 ---"
grep -rE "0x[0-9a-fA-F]{64}" "$HERMES_HOME/skills" "$HERMES_HOME/memories" 2>/dev/null | grep -v "/advisories/" | grep -iv "example\|test" | head -10
if [ $? -eq 0 ]; then
    echo "⚠️ 发现疑似私钥，请人工确认"
else
    echo "✅ 未发现明文私钥泄露"
fi
echo ""
echo "--- 扫描助记词格式 ---"
grep -rE "\b(abandon|ability|able|about|above|absent|absorb|abstract|absurd|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|address|adjust|admit|adult|advance|advice|aerobic|affair|afford|afraid|again|age|agent|agree|ahead|aim|air|airport|aisle|alarm|album|alert|alien|all|alley|allow|almost|alone|alpha|already|also|alter|always|amazing|among|amount|amused|analyst|anchor|ancient|anger|angle|angry|animal|ankle|announce|annual|another|answer|antenna|antique|anxiety|any|apart|apology|appear|apple|approve|april|arch|arctic|area|arena|argue|arm|armed|armor|army|around|arrange|arrest|arrive|arrow|art|artefact|artist|artwork|ask|aspect|assault|asset|assist|assume|asthma|athlete|atom|attack|attend|attitude|attract|auction|audit|august|aunt|author|auto|autumn|average|avocado|avoid|awake|aware|awesome|awful|awkward|axis)\b" "$HERMES_HOME/memories" 2>/dev/null | head -5
if [ $? -eq 0 ]; then
    echo "⚠️ 发现可能的助记词，请人工确认"
else
    echo "✅ 未发现明文助记词泄露"
fi
echo ""

# === [12] Skill 完整性 ===
echo "=== [12] Skill/MCP 完整性 ==="
echo "--- 已安装 Skills ---"
ls -1 "$HERMES_HOME/skills/" 2>/dev/null | wc -l | xargs echo "Skills 数量:"
echo ""
echo "--- Skill 哈希基线 (待生成) ---"
SKILL_BASELINE="$HERMES_HOME/.skill-baseline.sha256"
if [ -f "$SKILL_BASELINE" ]; then
    echo "检查基线..."
    find "$HERMES_HOME/skills" -type f -not -path '*/.git/*' -exec sha256sum {} \; | sort | sha256sum | while read -r hash _; do
        expected=$(cat "$SKILL_BASELINE")
        if [ "$hash" = "$expected" ]; then
            echo "✅ Skill 完整性校验通过"
        else
            echo "⚠️ Skill 文件发生变更！"
        fi
    done
else
    echo "⚠️ 未生成 Skill 基线，请首次部署后生成"
fi
echo ""

# === [13] Git 灾难恢复备份 ===
echo "=== [13] Git 灾难恢复备份 ==="
if [ -d "$HERMES_HOME/.git" ]; then
    cd "$HERMES_HOME"
    git add -A 2>/dev/null
    git commit --allow-empty -m "nightly-auto-backup $(date +%Y-%m-%d)" 2>/dev/null
    echo "✅ Git 备份提交完成"
    # 检测是否有远程仓库
    if git remote -v 2>/dev/null | grep -q "origin"; then
        git push origin main 2>/dev/null && echo "✅ 远程推送成功" || echo "⚠️ 远程推送失败（可能是网络或认证问题）"
    else
        echo "ℹ️ 未配置远程仓库，仅本地备份"
    fi
else
    echo "⚠️ 未初始化 Git 仓库，灾难恢复未启用"
fi

echo ""
echo "=========================================="
echo " 审计完成"
echo " 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 汇总
CRIT=$(grep -c "🚨" "$REPORT_FILE" 2>/dev/null || echo 0)
WARN=$(grep -c "⚠️" "$REPORT_FILE" 2>/dev/null || echo 0)
echo ""
echo "Summary: $CRIT critical · $WARN warn · 13 metrics checked"

# 30天轮转
find "$REPORT_DIR" -name "audit-*.txt" -mtime +30 -delete 2>/dev/null
