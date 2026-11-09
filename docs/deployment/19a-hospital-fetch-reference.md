# 第十九冊之一 · 抓取腳本的出錯對照與速查

版本：v0.1　文件狀態：草案（1108 由第十九冊分出）　編號：沿用第十九冊的 `B-xx`

上層手冊：《[第十九冊 · 院方 API 抓取腳本的安裝](19-hospital-fetch.md)》

> 照第十九冊做的時候，畫面上出現看不懂的訊息就查第 1 節；現場要一眼看完所有指令看第 2 節；`hb` 的現況要在主機上盤點看第 3 節。第 1、2 節的訊息原文來自 `hd-hospital-fetch` v0.1.0，腳本改版時回頭核對。

## 摘要

- 第 1 節：透析清單抓取腳本的出錯對照，訊息原文綁 `hd-hospital-fetch` v0.1.0
- 第 2 節：透析清單那支的一頁速查
- 第 3 節（1109 晚上加）：`hb` 現況盤點。`Hb_API_Fetch` 的檔不能帶出、不能拍，改在主機上跑只讀、只印統計的腳本（腳本整段在本節，不靠 Release）
- 盤點回答 I-10（有沒有程式在跑）、I-8（端點）、I-2 前半（病人清單行數）、I-3（一次回幾筆、單位與定性寫法）、I-9（同名異欄哪個是現行的），結論抄在紙上帶回
- 盤點不印病歷號與數值：數字換成 9、中文換成〔中文〕、出現不到 3 次的樣式不列；院內規定更嚴就加 `--strict`

## 1. 出錯對照

| 畫面上看到 | 意思 | 怎麼做 |
|---|---|---|
| `設定錯誤 找不到設定檔` | 不在 `<腳本資料夾>` 裡，或 第十九冊 B-14 沒做 | `cd C:\hd-hospital-fetch` 再試 |
| `設定錯誤 設定檔不是合法的 JSON` | `config.json` 寫壞了，最常見是反斜線只寫一個、少了引號或逗號 | 回第十九冊 B-14 對照範例改 |
| `設定錯誤 endpoint 要是 http 或 https 開頭` | 位址抄錯 | 對照 `values.md` |
| `失敗 重試 3 次仍失敗；最後一次：連線失敗：…` | 連不到院方 API | 確認位址；用瀏覽器開 `<院方位址>?date=2026-11-09` 看得到資料嗎；看不到就停 |
| `失敗 重試 3 次仍失敗；最後一次：HTTP 404` 或其他數字 | 院方回錯誤 | 位址的路徑抄錯（`.php` 前面那段）；對了還是錯就停 |
| `失敗 重試 3 次仍失敗；最後一次：逾時（>30 秒）` | 院方太慢 | 再試一次；連續逾時就停 |
| `失敗 回應裡找不到 JSON 內容`、`回應的 JSON 無法解析`、`回應裡沒有 data_list 陣列` | 院方回的不是透析清單（維護頁、登入頁） | 停 |
| `失敗 當月的留底檔不是 UTF-8，先用 transcode_history.py 轉檔` | 當月檔還是舊寫法 | 回第十九冊 B-12；當月檔轉不了就停 |
| `跳過 上一輪還沒結束` | 另一輪正在跑 | 正常；等一下再看 |
| `py` 說找不到指令 | 沒有 Python launcher | 換成 `python`，或用 `.exe` |
| `找不到 raw_txt 的月份檔，停在這裡`（第 3 節盤點） | `$hb` 貼錯資料夾，或 `config.json` 的 `output_dir` 不是 `hospital_dataset` | 用 3.1 第二行的清單找 `raw_txt` 在哪，`$hb` 改成它上兩層的資料夾 |
| Windows 跳出「Windows 已保護您的電腦」 | `.exe` 第一次執行 | 第十九冊 B-11 有做 `Unblock-File` 就不會出現；出現了按「其他資訊」→「仍要執行」，雜湊對過才可以 |

## 2. 一頁速查

```powershell
cd C:\hd-hospital-fetch
py transcode_history.py "<指定資料夾>"              # 轉碼預演
py transcode_history.py "<指定資料夾>" --apply      # 轉碼
py fetch_dialysis.py --dry-run                     # 抓取預演，不寫檔
py fetch_dialysis.py --once                        # 跑一輪
$LASTEXITCODE                                      # 0 成功、1 失敗、2 設定錯
Get-Content -Encoding UTF8 .\fetch-status.json     # 狀態
powershell -ExecutionPolicy Bypass -File .\install-task.ps1      # 裝排程
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch                # 排程跑了沒
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1    # 停排程
```

## 3. `hb` 現況盤點（只讀、只印統計）

> 用在《[院方 API 之四](../notes/hospital-api-fetch-methods-next-visit-plan.md)》第 5 節第 2 步。`Hb_API_Fetch` 底下的檔不能帶出、不能拍，改在主機上跑這支盤點：**只讀、不寫任何檔、不印病歷號與檢驗數值**。印出來的只有筆數、日期範圍、每欄有值的次數與「數字換成 9」的樣式；第 5 段「要抄的結論」不含病人資料，抄在紙上帶回。腳本整段在本節，不靠 Release，主機有 Python 3.13 就能跑。

### 3.1 先看有沒有程式在跑（I-10）

```powershell
$hb = Read-Host 'Hb_API_Fetch 資料夾的完整路徑'
Get-ChildItem $hb -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 15 FullName, LastWriteTime, Length
Get-ScheduledTask | Where-Object { ($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments) $($_.WorkingDirectory)" }) -match 'hb_|Hb_API' } | Select-Object TaskName, State
Get-CimInstance Win32_Process -Filter "Name LIKE 'py%'" | Select-Object ProcessId, CommandLine
```

| 看到 | 怎麼做 |
|---|---|
| 第二行列出工作，或第三行的 `CommandLine` 有 `hb_online` | 有程式在跑：記下工作名稱與狀態，`hb` 停在這裡（之四第 6 節）；盤點照樣可以跑，它只讀 |
| 最新的檔在 6 小時內改過，但上面兩行都沒找到 | 可能是別台或別的帳號在寫，先問學長再往下 |
| 都沒有 | 往下 |

### 3.2 建立盤點腳本

從 `New-Item` 那行到最後 `Set-Content` 那行整段複製，貼進同一個 PowerShell 視窗，按 Enter。不會有任何輸出。

```powershell
New-Item -ItemType Directory -Force "$env:TEMP\hb_survey" | Out-Null
@'
# hb 現況盤點：只讀、只印統計，不印病歷號與檢驗數值，不寫任何檔
import json, re, statistics, sys, time
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

EMPTY = {'', '-', '--', 'null', 'none', 'nan', 'n/a', 'na'}
KEEP_WORDS = ('弱陽性', '陰性', '陽性')
PAIRS = [('ALBUMIN', 'ALB'), ('ALK-P', 'ALP'), ('CA', 'Ca'), ('Ferritin', 'FERR'),
         ('本次透析前NA', 'Na'), ('GLU.A.C', 'GLU, AC'), ('TRIG', 'TG'), ('T PROT', 'TP'),
         ('PTHi', 'PTH'), ('Anti-HBs', 'Anti-HBs Ab', 'HBs Ab'), ('AFP', 'AFP.')]
FOCUS = ['Hb', 'ALBUMIN', 'ALB', 'Kt/V(Daugirdas)', 'Kt/V(Gotch)', 'HBs Ag', 'HCV Ab']
STRICT = '--strict' in sys.argv
args = [a for a in sys.argv[1:] if a != '--strict']
if len(args) != 1:
    sys.exit('用法：py hb_survey.py "<Hb_API_Fetch 資料夾>" [--strict]')
root = Path(args[0])


def shape(value):
    s = re.sub(r'\d+', '9', str(value).strip())
    if STRICT:
        if re.fullmatch(r'[+-]?9(\.9)?', s): return '數字'
        if re.fullmatch(r'[<>≦≧]=?\s*9(\.9)?', s): return '比較符號＋數字'
        if re.match(r'[+-]?9(\.9)?', s): return '數字＋後綴'
        return '文字' if '9' not in s else '其他'
    for i, w in enumerate(KEEP_WORDS):
        s = s.replace(w, '\x00%d\x00' % i)
    s = re.sub(r'[\u3400-\u9fff\uf900-\ufaff]+', '〔中文〕', s)
    s = re.sub(r'\x00(\d)\x00', lambda m: KEEP_WORDS[int(m.group(1))], s)
    return s if len(s) <= 20 else '〔長字串〕'


def day(text):
    try: return date.fromisoformat(str(text)[:10])
    except ValueError: return None


print('== 1. 設定與病人清單 ==')
cfg = {}
cfg_path = root / 'config.json'
if cfg_path.is_file():
    try:
        cfg = json.loads(cfg_path.read_text(encoding='utf-8-sig'))
        m = re.match(r'(\w+)://([^/:]+)', str(cfg.get('url_template', '')))
        print('config.json 在；網址：', (m.group(1) + '，主機 ' + m.group(2)) if m else '看不出來')
        print('範本佔位字還在：', 'REPLACE-WITH' in str(cfg.get('url_template', '')))
        for k in ('start_date', 'interval_hours', 'patients_file', 'output_dir', 'timeout_seconds', 'allow_approved_http'):
            print(' ', k, '=', cfg.get(k, '（沒寫）'))
    except Exception as e:
        print('config.json 讀不了：', type(e).__name__)
else:
    print('沒有 config.json')
pf = root / cfg.get('patients_file', 'hospital_dataset/active_patients.txt')
if pf.is_file():
    ids = [l.strip() for l in pf.read_text(encoding='utf-8-sig').splitlines() if l.strip() and not l.strip().startswith('#')]
    print('病人清單在；%d 行，不重複 %d，不是純數字 %d；最後修改 %s' % (
        len(ids), len(set(ids)), sum(not (i.isascii() and i.isdigit()) for i in ids),
        time.strftime('%Y-%m-%d %H:%M', time.localtime(pf.stat().st_mtime))))
else:
    print('沒有病人清單：', pf.relative_to(root) if pf.is_relative_to(root) else '（在別處）')

print('\n== 2. 月份檔 ==')
raw = root / cfg.get('output_dir', 'hospital_dataset') / 'raw_txt'
files = sorted(raw.glob('????-??.txt')) if raw.is_dir() else []
if not files:
    sys.exit('找不到 raw_txt 的月份檔，停在這裡')
recs, bad_total = [], 0
for f in files:
    n = bad = 0; bad_lines = []; pids = set(); ed = []; fa = []
    with f.open(encoding='utf-8-sig', errors='replace') as fh:
        for no, line in enumerate(fh, 1):
            if not line.strip(): continue
            n += 1
            try:
                obj = json.loads(line); r = obj['record'] if 'record' in obj else obj
                if not isinstance(r, dict): raise ValueError
            except Exception:
                bad += 1; bad_lines.append(no); continue
            recs.append((obj.get('FetchedAt', ''), r))
            pids.add(str(r.get('MedicalId'))); ed.append(str(r.get('ExecuteDate', ''))); fa.append(str(obj.get('FetchedAt', ''))[:16])
    bad_total += bad
    print('%s：%d 行，壞 %d%s；%d 人；檢驗日 %s～%s；抓取 %s～%s；檔案最後修改 %s' % (
        f.name, n, bad, ('（行號 %s）' % ','.join(map(str, bad_lines[:10]))) if bad else '', len(pids),
        min(ed, default='-'), max(ed, default='-'), min(fa, default='-'), max(fa, default='-'),
        time.strftime('%Y-%m-%d %H:%M', time.localtime(f.stat().st_mtime))))

print('\n== 3. 一次回幾筆 ==')
first_fetch = min((day(a) for a, _ in recs if day(a)), default=None)
by_pid = defaultdict(list); same_day = Counter()
for a, r in recs:
    by_pid[str(r.get('MedicalId'))].append((day(r.get('ExecuteDate')), day(a)))
    same_day[(str(r.get('MedicalId')), r.get('ExecuteDate'))] += 1
print('共 %d 筆、%d 人；最早一次抓取 %s' % (len(recs), len(by_pid), first_fetch))
print('同一人同一檢驗日有兩筆以上（改過值）：%d 組' % sum(1 for v in same_day.values() if v > 1))
dates_per = Counter(min(len({d for d, _ in v}), 6) for v in by_pid.values())
print('每人有幾個檢驗日：', '、'.join('%s 個 %d 人' % ('6+' if k == 6 else k, dates_per[k]) for k in sorted(dates_per)))
before = [sum(1 for d in {d for d, _ in v} if d and first_fetch and d < first_fetch) for v in by_pid.values()]
print('最早抓取以前的檢驗日，每人最多 %d 個（1 就表示每次只回最近一次）' % max(before, default=0))
lags = [(min(a for _, a in g if a) - d).days for v in by_pid.values() for d, g in
        [(d, [x for x in v if x[0] == d]) for d in {d for d, _ in v}] if d and first_fetch and d >= first_fetch and any(a for _, a in g)]
if lags:
    print('啟用後的檢驗，檢驗日到第一次抓到：中位數 %s 天、最多 %d 天' % (statistics.median(lags), max(lags)))

print('\n== 4. 各欄 ==（有值筆數｜有值的第一個月～最後一個月｜值的樣式，數字一律換成 9）')
order, filled, months, shapes, empties = [], Counter(), defaultdict(set), defaultdict(Counter), Counter()
seen_keys = set()
for _, r in recs:
    mon = str(r.get('ExecuteDate', ''))[:7]
    for k, v in r.items():
        if k not in seen_keys: seen_keys.add(k); order.append(k)
        if k in ('MedicalId', 'ExecuteDate'): continue
        s = '' if v is None else str(v).strip()
        if s.casefold() in EMPTY:
            empties[s or '（空字串）'] += 1; continue
        filled[k] += 1; months[k].add(mon); shapes[k][shape(s)] += 1
for k in order:
    if k in ('MedicalId', 'ExecuteDate') or not filled[k]: continue
    top = [(s, c) for s, c in shapes[k].most_common() if c >= 3][:4]
    rest = filled[k] - sum(c for _, c in top)
    ms = sorted(months[k])
    print('%s｜%d｜%s｜%s' % (k, filled[k], ('%s～%s' % (ms[0], ms[-1])) if ms else '-',
          '、'.join('%s ×%d' % sc for sc in top) + ('、其他 ×%d' % rest if rest else '')))
print('一直沒有值的欄：', '、'.join(k for k in order if k not in ('MedicalId', 'ExecuteDate') and not filled[k]) or '無')
print('空值的寫法：', '、'.join('%s ×%d' % sc for sc in empties.most_common()))

print('\n== 5. 要抄的結論 ==')
print('I-10 raw_txt 最後一次寫：', time.strftime('%Y-%m-%d %H:%M', time.localtime(max(f.stat().st_mtime for f in files))), '；壞行共', bad_total)
print('I-3 每次只回最近一次：', '看起來是' if max(before, default=0) <= 1 else '不是（啟用前每人最多 %d 個檢驗日）' % max(before))
for g in PAIRS:
    if not any(filled[k] for k in g): print('I-9', '／'.join(g), '都沒有值'); continue
    print('I-9', '／'.join('%s %d 筆 %s' % (k, filled[k], max(months[k]) if months[k] else '-') for k in g))
for k in FOCUS:
    top = [s for s, c in shapes[k].most_common(2) if c >= 3]
    print('I-3 %s 的樣式：%s' % (k, '、'.join(top) or '（不到 3 筆，不列）'))
'@ | Set-Content -Encoding UTF8 "$env:TEMP\hb_survey\hb_survey.py"
```

### 3.3 跑

```powershell
py -I "$env:TEMP\hb_survey\hb_survey.py" $hb
```

- 後面不要接 `|`（例如 `| more`）：輸出經過管線，中文會變亂碼；太長就把視窗往上捲
- 院內規定連值的樣式（例如 `Negative`）都不能抄：最後加 ` --strict`，樣式只分成數字、數字＋後綴、比較符號＋數字、文字、其他
- 抄完刪掉：`Remove-Item -Recurse -Force "$env:TEMP\hb_survey"`（腳本本身沒有病人資料，刪掉是不留東西在主機上）

腳本怎麼避免印出病人資料：

- 病歷號只拿來數人數，不印
- 數字一律換成 9，`12.3` 和 `8.0` 都印成 `9.9`
- 中文換成 `〔中文〕`，只留 `陰性`、`陽性`、`弱陽性`；超過 20 字的換成 `〔長字串〕`
- 出現不到 3 次的樣式不列，併進「其他」

### 3.4 會看到（假資料的例子）

```text
== 1. 設定與病人清單 ==
config.json 在；網址： https，主機 <主機>
範本佔位字還在： False
  start_date = 2024-01-01
  interval_hours = 6
  ...
病人清單在；21 行，不重複 20，不是純數字 0；最後修改 2025-11-08 14:00

== 2. 月份檔 ==
2025-09.txt：20 行，壞 0；20 人；檢驗日 2025-09-03～2025-09-28；抓取 2025-10-01T08:00～2025-10-01T08:00；檔案最後修改 2025-10-01 08:00
2025-10.txt：22 行，壞 1（行號 22）；20 人；檢驗日 2025-10-01～2025-10-08；抓取 2025-10-01T14:00～2025-10-08T14:00；檔案最後修改 2025-10-08 14:00

== 3. 一次回幾筆 ==
共 62 筆、20 人；最早一次抓取 2025-10-01
同一人同一檢驗日有兩筆以上（改過值）：2 組
每人有幾個檢驗日： 3 個 20 人
最早抓取以前的檢驗日，每人最多 1 個（1 就表示每次只回最近一次）

== 4. 各欄 ==（有值筆數｜有值的第一個月～最後一個月｜值的樣式，數字一律換成 9）
ALBUMIN｜42｜2025-10～2025-11｜9.9 ×42
Hb｜62｜2025-09～2025-11｜9.9 g/dL ×62
HBs Ag｜62｜2025-09～2025-11｜Negative ×25、<9.9 ×21、陰性(-) ×16
EKG｜20｜2025-09～2025-11｜〔中文〕 ×20
ALB｜20｜2025-09～2025-09｜9.9 ×20
一直沒有值的欄： 本次透析前BUN、……
空值的寫法： （空字串） ×4960、N/A ×22、- ×20

== 5. 要抄的結論 ==
I-10 raw_txt 最後一次寫： 2025-11-08 14:00 ；壞行共 1
I-3 每次只回最近一次： 看起來是
I-9 ALBUMIN 42 筆 2025-11／ALB 20 筆 2025-09
I-9 ALK-P／ALP 都沒有值
...
I-3 Hb 的樣式：9.9 g/dL
I-3 HBs Ag 的樣式：Negative、<9.9
```

### 3.5 怎麼讀、抄什麼

| 段 | 看什麼 | 回答 |
|---|---|---|
| 1 | `範本佔位字還在： False` 才是實際設定；網址開頭與主機 | I-8；主機名稱抄進私人紀錄，不寫進 `docs/` |
| 1 | 病人清單的行數與最後修改時間 | I-2 前半；誰在維護要問人 |
| 2 | 每個月份檔的「壞」；有壞行，學長的程式啟動就會整支停 | 之四第 5 節第 5 步（有壞行就停，備份交學長） |
| 3 | 「最早抓取以前的檢驗日，每人最多 1 個」：程式開始跑以前的檢驗每人只抓到一筆，表示每次只回期間內最近一次 | I-3 |
| 4、5 | 同一項的兩個名字看「有值的最後一個月」：一個停在舊月份、另一個接著有，就是改過名，現行的是後者；兩個同時都有，是不同機台或來源 | I-9 |
| 4、5 | 樣式 `9.9 g/dL` 表示值帶單位；`Negative`、`陰性(-)` 是定性結果的寫法 | I-3 |
| 5 | 整段抄在紙上帶回，回來補進《院方 API 之二》 | — |

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回第十九冊](19-hospital-fetch.md)　[← 回部署手冊總覽](index.md)
