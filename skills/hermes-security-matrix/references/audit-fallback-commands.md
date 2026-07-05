# 夜间审计脚本超时恢复命令

当 `nightly-security-audit.sh` 超时时，kill 进程后按以下顺序用直接命令补全剩余指标。

## 前提
脚本通常卡在指标 8 或 9。脚本已将 stdout 重定向到报告文件，先读取已有内容：
```bash
cat /Users/eason/.hermes/security-reports/audit-$(date +%Y%m%d)-*.txt
```
找出最后完成的指标编号，从下一项开始补全。

---

## 指标 9 — 磁盘使用率（跳过慢速 find）

```bash
# 仅查磁盘使用率，不做大文件全盘扫描
df -h / | tail -1 | awk '{print $5}'
```

大文件扫描改为缩窄范围（如果必须做）：
```bash
find ~/.hermes ~/Downloads ~/Desktop -maxdepth 3 -type f -size +100M -mtime -1 2>/dev/null | head -10
```

## 指标 10 — 环境变量审计

```bash
env | grep -iE 'KEY|TOKEN|SECRET|PASSWORD|API_KEY' | sed 's/=.*/=***/' | head -20
```

## 指标 11 — DLP 凭据泄露扫描

```bash
# 私钥格式
grep -rE '0x[0-9a-fA-F]{64}' ~/.hermes/skills ~/.hermes/memories 2>/dev/null | grep -v '/advisories/' | grep -iv 'example\|test' | head -10

# 助记词格式（仅扫描 memories/，skill 文件包含 BIP39 词库误报率高）
grep -rE '\b(abandon|ability|able|about|above|absent|absorb|abstract|absurd|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|address|adjust|admit|adult|advance|advice|aerobic|affair|afford|afraid|again|age|agent|agree|ahead|aim|air|airport|aisle|alarm|album|alert|alien|all|alley|allow|almost|alone|alpha|already|also|alter|always|amazing|among|amount|amused|analyst|anchor|ancient|anger|angle|angry|animal|ankle|announce|annual|another|answer|antenna|antique|anxiety|any|apart|apology|appear|apple|approve|april|arch|arctic|area|arena|argue|arm|armed|armor|army|around|arrange|arrest|arrive|arrow|art|artefact|artist|artwork|ask|aspect|assault|asset|assist|assume|asthma|athlete|atom|attack|attend|attitude|attract|auction|audit|august|aunt|author|auto|autumn|average|avocado|avoid|awake|aware|awesome|awful|awkward|axis)\b' ~/.hermes/memories 2>/dev/null | head -5
```

## 指标 12 — Skill 完整性

```bash
# Skill 数量
ls -1 ~/.hermes/skills/ | wc -l

# 聚合哈希（需先有基线文件 ~/.hermes/.skill-baseline.sha256）
find ~/.hermes/skills -type f -not -path '*/.git/*' -exec sha256sum {} \; 2>/dev/null | sort | sha256sum | awk '{print $1}'

# 比对基线
cat ~/.hermes/.skill-baseline.sha256
```

## 指标 13 — Git 灾难恢复

```bash
# 检查是否初始化
test -d ~/.hermes/.git && echo 'EXISTS' || echo 'MISSING'

# 检查远程仓库
cd ~/.hermes && git remote -v 2>/dev/null | grep -q origin && echo 'HAS_REMOTE' || echo 'NO_REMOTE'
```
