# 第二十一冊 · 抓取腳本上線（簡易版）

版本：v0.1　文件狀態：草案（1116 由第十九冊、之一與第二十冊 GO-03 整理）　編號：`AF-xx`　詳細版：《[第二十二冊](22-api-detail.md)》（同一套編號）

> **這一冊只回答：抓取腳本要按什麼、怎樣算成功、模擬和正式哪裡不同。** 出錯、為什麼、1109 的現場經驗都在第二十二冊同一個編號底下。這一趟部署只看第二十一～二十四冊，其他冊不必翻。
>
> 這一趟分兩階段：**第一階段是這一冊（抓取腳本跑起來）**，成功了才做第二階段《[第二十三冊](23-system-quick.md)》（本系統跑起來）。
>
> 標記：**🏥 正式**＝院內主機才這樣做；**🧪 模擬**＝開發機上演練才這樣做；沒標的兩邊一樣。🧪 演練開始前，開發機已由開發端準備成跟院內主機一樣（1109 留下的樣子），演練完也由開發端撤除，手冊不寫。

> **公開範圍**：院方位址、D 槽的舊路徑、帳號不寫在這裡，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`。`C:\API_Fetch\…` 是通用位置，直接寫。

## 摘要

- 起點：1109 已把 `hd-hospital-fetch` v0.1.0 放在 D 槽、`config.json` 填好、預演成功；排程沒裝
- 要做：整個 `API_Fetch` 搬 C 槽 → 換 `fetch_dialysis.py` 成 v0.3.0 → 改設定三處 → 預演 → 跑一輪 → 裝排程 → 看三輪 → 教學長
- 成功的定義：AF-11 三輪都是 `LastTaskResult` `0`、狀態檔 `result` `ok`
- 模擬與正式的差別只有位置、帳號、時段三種（第 0 節一張表）
- 學長在場；約 60～90 分鐘
- 失敗就停在那裡，本系統不換版（C 級）；退回在第 2 節

## 0. 兩邊的差別一覽

| 哪裡 | 🏥 正式 | 🧪 模擬 |
|---|---|---|
| 機器 | 院內三台裡最右邊那台、醫師的帳號 | 自己的開發機 |
| 院方 API | 院方位址（1109 已填在 `config.json`，不用改） | 開發端開好的模擬院方 API（已填在 `config.json`，不用改） |
| 舊位置 `$old` | D 槽的 `API_Fetch`（路徑在 `values.md`） | `C:\hd-sim-fetch\D槽\API_Fetch` |
| 新位置 `$new` | `C:\API_Fetch` | `C:\hd-sim-fetch\API_Fetch` |
| 抓取時段 | `07:00-23:00` | 同；演練不在這個時段就暫改 `00:00-24:00`（AF-06） |
| 學長 | 在場，斷點由他決定 | 自己決定，紀錄寫「院內要問學長」 |

**PowerShell 一律開一般的**（開始 → 打 `powershell` → 直接按 Enter），不要用系統管理員。視窗關掉後變數會不見，重開先貼 AF-04 最後那個方框裡的一行。

## 1. 步驟

### AF-01 出發前

**做什麼**：手機裡有 GitHub 兩步驟驗證、`values.md`（私人 repo）、現場筆記；自己的電腦開得了 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.3.0`。🏥 約好學長。

**成功**：Release 頁看得到 `Source code (zip)`；手機看得到 `values.md`。

### AF-02 對的主機、對的帳號，把這一冊開在主機上

**做什麼**：🏥 最右邊那台。主機的瀏覽器一般視窗（不登入 GitHub）開公開文件站的這一冊，指令從頁面複製貼進 PowerShell。開一般 PowerShell：

```powershell
whoami
```

**成功**：🏥 是醫師的帳號；🧪 自己的帳號。PowerShell 標題沒有「系統管理員」。

### AF-03 看現況：排程沒裝、沒有 Python 在跑、C 槽還沒有

**做什麼**：🏥 照貼，出現提示時貼上 D 槽 `API_Fetch` 的路徑；🧪 第一行改貼 `$old = 'C:\hd-sim-fetch\D槽\API_Fetch'; $new = 'C:\hd-sim-fetch\API_Fetch'`。

```powershell
$old = (Read-Host '貼上 D 槽 API_Fetch 的路徑').Trim().Trim('"', "'"); $new = 'C:\API_Fetch'
Get-ScheduledTask -TaskName hd-hospital-fetch -ErrorAction SilentlyContinue
Get-Process python*, py -ErrorAction SilentlyContinue
Test-Path -LiteralPath "$old\hd-hospital-fetch\config.json"; Test-Path -LiteralPath $new
"C 槽可用 {0:N1} GB" -f ((Get-PSDrive C).Free/1GB) Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { ($_.Actions | Out-String) -match 'API_Fetch|online' } | Select-Object TaskName, State
```

**成功**：第二、三行沒印東西；接著 `True`、`False`；C 槽有幾百 GB（🏥 1109 是 763 GB）；最後一行沒印東西（沒有別的排程指著 `API_Fetch`，含學長 `Hb_API_Fetch` 裡的 `hb_online_v2.py`）。

### AF-04 整個 `API_Fetch` 搬到 C 槽

**做什麼**：

```powershell
robocopy $old $new /E /COPY:DAT /DCOPY:T /R:1 /W:1 /NFL /NDL /NP
$LASTEXITCODE
foreach ($p in $old, $new) { $f = Get-ChildItem -LiteralPath $p -Recurse -File -Force; '{0} 個檔、{1:N0} 位元組' -f $f.Count, ($f | Measure-Object Length -Sum).Sum }
```

**成功**：robocopy 表格的「失敗」欄全是 `0`、`$LASTEXITCODE` 是 `1`；最後兩行一模一樣。然後舊的改名留著（不刪），換到新位置：

```powershell
Rename-Item -LiteralPath $old ('API_Fetch_搬到C槽_' + (Get-Date -Format 'MMdd'))
$dir = "$new\IDH_interface"; $sf = "$new\hd-hospital-fetch"; cd -LiteralPath $sf; dir config.json
```

**成功**：列出 `config.json`；提示字元變成 `…\API_Fetch\hd-hospital-fetch>`。

> 之後 PowerShell 重開，先貼：🏥 `$new = 'C:\API_Fetch'; $dir = "$new\IDH_interface"; $sf = "$new\hd-hospital-fetch"; cd -LiteralPath $sf`　🧪 同一行，`$new` 換成 `'C:\hd-sim-fetch\API_Fetch'`

### AF-05 `fetch_dialysis.py` 換成 v0.3.0

**做什麼**：Edge 或 Chrome 按 `Ctrl+Shift+N` 開 InPrivate／無痕視窗 → 登入自己的 GitHub（不勾保持登入、不存密碼）→ 開 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.3.0` → Assets 的 `Source code (zip)` 存到「下載」→ **關掉整個 InPrivate 視窗**。接著：

```powershell
$z = "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.3.0.zip"; $tmp = Join-Path $env:TEMP 'hd-fetch-0.3.0'
Expand-Archive -LiteralPath $z -DestinationPath $tmp -Force
Copy-Item -LiteralPath (Join-Path $tmp 'hd-hospital-fetch-0.3.0\fetch_dialysis.py') -Destination $sf -Force
Remove-Item -LiteralPath $tmp -Recurse -Force; Remove-Item -LiteralPath $z
Unblock-File -LiteralPath (Join-Path $sf 'fetch_dialysis.py')
py fetch_dialysis.py --version
```

**成功**：最後一行 `0.3.0`。只換這一個檔，其他檔、`config.json`、`state\` 不動。

### AF-06 改設定三處

**做什麼**：

```powershell
Set-Clipboard $dir.Replace('\', '\\'); notepad config.json
```

| 欄位 | 改成 |
|---|---|
| `"output_dir"` | 引號中間原本的路徑選起來、`Ctrl+V` |
| `"status_file"` | 🏥 `"C:\\API_Fetch\\IDH_interface\\fetch-status.json"`　🧪 `"C:\\hd-sim-fetch\\API_Fetch\\IDH_interface\\fetch-status.json"` |
| 新加一行 | 最後一個欄位（`"lock_stale_seconds": 900`）後面加逗號，下一行 `"fetch_hours": "07:00-23:00"`。🧪 演練時間不在 07:00～23:00 就寫 `"00:00-24:00"`；**🏥 一律 `07:00-23:00`** |

存檔、關掉記事本，檢查：

```powershell
Get-Content -Raw -Encoding UTF8 config.json | ConvertFrom-Json | Select-Object output_dir, status_file, fetch_hours, dedup, line_format
```

**成功**：`$dir` 的路徑、`$dir` 底下的 `fetch-status.json`、`07:00-23:00`、`row`、`segment`。

### AF-07 寫檔前兩個檢查

**做什麼**：

```powershell
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$w = Join-Path $sf 'write-test.tmp'; Set-Content -LiteralPath $w 'x'; Test-Path -LiteralPath $w; Remove-Item -LiteralPath $w
$m = Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt'); (Get-Item -LiteralPath $m).LastWriteTime
```

**成功**：`False`、`True`；當月檔的修改時間不是幾分鐘內（是的話等 5 分鐘再看一次，時間沒變才往下）。

### AF-08 預演一輪（不寫檔）

**做什麼**：

```powershell
py fetch_dialysis.py --dry-run
```

**成功**：`… 成功 回應 N 列、會寫入 M 列（預演，沒有寫任何檔）`。07:00 前、23:00 後是 `時段外 …`，不是錯，等進時段再做。

### AF-09 跑一輪、看結果

**做什麼**：

```powershell
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
$m = Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt')
$t = Get-Content -Encoding UTF8 -LiteralPath $m -Tail 2; $t[0]; $t[1].StartsWith('{"data_list":['); $t[1].Length
py fetch_dialysis.py --once
```

**成功**：第一輪 `… 成功 回應 N 列、寫入 M 列`；`$LASTEXITCODE` `0`；狀態檔 `"result": "ok"`；當月檔最後是剛剛時間的 `Date: …`、`True`、一個很大的數字；第二輪 `寫入 0 列`（剛好有新量測就是幾列，不會是整天）。主控台不會印姓名或病歷號。

### AF-10 裝排程

**做什麼**：

```powershell
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
```

**成功**：`已建立工作 hd-hospital-fetch`、頻率每 3 分鐘、`執行：` 那一行指到 `$sf` 裡的 `fetch_dialysis.py`、狀態 `Ready`。跑的時候不會跳視窗。

### AF-11 看三輪（約 10 分鐘）

**做什麼**：每 3 分鐘貼一次：

```powershell
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
```

**成功**：三次都是 `LastRunTime` 往前跳、`LastTaskResult` `0`、狀態檔 `last_attempt_at` 跟著變、`result` `ok`。裝完馬上看會是 `1999/11/30` 與 `267011`（排程還沒跑過，狀態檔是 AF-09 手動那一輪），過了 `NextRunTime` 再看，從那一次起算三輪。**這一步過了，第一階段就成功了**，接著做第二十三冊。

### AF-12 教學長、記錄、收工

**做什麼**：

1. 教學長三件事（都在 `$sf` 裡打）：停 `powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1`；改頻率 `powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -IntervalMinutes 5 -Force`；看最近一輪 `Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')`。🧪 自己講一遍給自己聽、不必真的停
2. 🏥 跟學長講：舊資料夾 `API_Fetch_搬到C槽_MMDD` 還在 D 槽，何時刪由他決定；他的文件與 APP 組讀檔的路徑要改成 C 槽
3. 照第二十二冊 AF-12 的清單記在手機上
4. InPrivate 視窗已關、「下載」裡沒有 zip；🏥 **不重開機**（同機有另一個專案）

**成功**：`Get-ScheduledTaskInfo -TaskName hd-hospital-fetch` 的 `LastTaskResult` 還是 `0`。

## 2. 退回（學長說不要了）

| # | 做什麼 | 指令（在 `$sf` 裡） |
|---|---|---|
| R-1 | 停排程 | `powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1` → `已移除工作 hd-hospital-fetch` |
| R-2 | 舊資料夾改回原名（學長同意才做） | `cd C:\`，再 `Rename-Item -LiteralPath <舊資料夾 API_Fetch_搬到C槽_MMDD 的完整路徑> 'API_Fetch'` |
| R-3 | C 槽那份留著，學長決定 | — |

退回之後本系統不換版。🧪 R-1、R-2 都可以實際練一次。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊總覽](index.md)　[第二十二冊 · 抓取腳本上線（詳細版） →](22-api-detail.md)
