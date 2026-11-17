# 院方 API 抓取腳本的維運

> - 狀態：**現行**（常備參考）。院內主機整體的現況與待辦在《[院內主機現況與未完成事項](ref-status.md)》，這一份只管抓取腳本 `hd-hospital-fetch` 本身
> - 1117 由舊第二十二冊第 3 節（出錯訊息總表）與第 6 節（一頁速查）、第十九冊之一第 1 節（出錯對照）與第 2 節（一頁速查）、第十九冊第 3 節（退回）、第二十一冊第 2 節（退回）合成，訊息原文對 `hd-hospital-fetch` v0.3.0 的程式補齊
> - 編號：`FS-xx`（1117 新開）；退回各步附上舊編號（第十九冊、第二十一冊各有一套 `R-1`～`R-3`，意思不同）

> **公開範圍**：院方位址、帳號、主機名稱不寫在這裡，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；`C:\API_Fetch\…` 是通用位置，直接寫。

> 訊息原文綁在 `hd-hospital-fetch` 的 `fetch_dialysis.py`、`install-task.ps1`、`uninstall-task.ps1`、`transcode_history.py`；腳本改了訊息或參數，回頭改這一份（進院冊已凍結的不改）。

## 摘要

- 現在的樣子：v0.3.0 在 `C:\API_Fetch\hd-hospital-fetch`，排程 `hd-hospital-fetch` 每 3 分鐘、只在 07:00～23:00 抓，留底與狀態檔都在 `C:\API_Fetch\IDH_interface`；本系統 `v0.5.0` 與 APP 組只讀那個資料夾（第 1 節）
- 看狀態：排程的 `LastTaskResult`、狀態檔的 `result` 與 `last_success_at`、不印病人資料看檔尾（FS-02～FS-05）
- 停、恢復、改頻率、改時段（FS-06～FS-09）：停了本系統會在提示時段顯示「未更新」
- 換版與換版退回（FS-10～FS-15）：先停排程、留舊檔、只換 Release 說明裡改過的檔
- 退回整支腳本（FS-16～FS-19）：1116 學長刪了 D 槽舊資料夾，「改回原名」做不到；院內 1109 沒轉碼，沒有轉碼備份可還原
- 出錯訊息總表（第 6 節）：每一列標出從哪一版起有；設定錯誤不寫狀態檔，排程上看 `LastTaskResult` `2`
- 一頁速查（第 7 節）
- 腳本歸負責 IDH 系統的學長管；平常的停、改頻率、看最近一輪由學長做

## 1. 現在的樣子（1116 起）

| 哪裡 | 🏥 院內主機 | 🧪 開發機演練 |
|---|---|---|
| 腳本 | `hd-hospital-fetch` v0.3.0（Release 只有 `.py`，沒有 `.exe`），用主機的 Python 3.13 跑 | 同版本 |
| 腳本資料夾 `$sf` | `C:\API_Fetch\hd-hospital-fetch`（`config.json`、`state\` 也在這裡） | `C:\hd-sim-fetch\API_Fetch\hd-hospital-fetch` |
| 指定資料夾 `$dir` | `C:\API_Fetch\IDH_interface`：月份檔 `YYYY-MM.txt`（1116 時 24 個，`2024-12`～`2026-11`，當月檔約 90 MB）＋狀態檔 `fetch-status.json` | `C:\hd-sim-fetch\API_Fetch\IDH_interface` |
| 排程 | 工作名稱 `hd-hospital-fetch`；每 3 分鐘；只在使用者登入時執行（醫師的帳號）；用 `pythonw.exe` 跑，不跳視窗；不重疊；1116 14:45 起跑 | 同，用自己的帳號 |
| 抓取時段 | `fetch_hours` `07:00-23:00`（開始含、結束不含，不跨午夜）；時段外不打院方 API、不寫任何檔 | 同；演練不在這個時段才暫改 `00:00-24:00` |
| 院方 API | 院方位址在 `config.json` 的 `endpoint`（值在 `values.md`） | 開發端開的模擬院方 API |
| 誰讀 | 本系統 `v0.5.0` 唯讀掛 `$dir`，每 3 分鐘讀一次（《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》）；APP 組讀同一個資料夾（《[院方 API 介接之五](../notes/hospital-api-fetch-methods-app-team.md)》） | 本系統讀開發端準備的資料夾 |
| 其他 | D 槽的舊 `API_Fetch` 1116 已被學長刪掉；`C:\API_Fetch\Hb_API_Fetch`（學長的檢驗資料，跟著搬來、內容沒動，這台沒有程式在更新它）不歸這支腳本 | — |

腳本每一輪做的事：問院方 API `?date=今天`（以 +08:00 算），把**新的或變了的列**附加到當月檔（`Date:` 一行＋`{"data_list":[…]}` 一行），沒有要寫的列就不寫；再覆寫狀態檔。去重的鍵是第 0、6、8 欄（病歷號＋透析開始時間＋紀錄時間），去重狀態放在 `state\`（鍵加隨機值雜湊，不存病歷號明文、保留 3 天；整個刪掉只會讓下一輪重寫一次當天的列）。主控台只印時間、結果、列數，不印網址與回應內容。

結束碼（`$LASTEXITCODE`，排程上是 `LastTaskResult`）：`0` 成功、跳過、時段外；`1` 失敗；`2` 參數或設定錯。

### 1.1 `config.json` 裡會動到的欄位

改完下一輪就生效（每一輪都重讀設定）；寫錯了那一輪印「設定錯誤」、結束碼 `2`。不認得的欄位會拒絕啟動。相對路徑以 `config.json` 所在的資料夾為準。

| 欄位 | 院內的值 | 說明 |
|---|---|---|
| `endpoint` | 院方位址（`http://` 開頭到 `.php`，不加 `?date=`） | 腳本自己加 `?date=` |
| `output_dir` | `C:\\API_Fetch\\IDH_interface` | 寫月份檔的地方 |
| `status_file` | `C:\\API_Fetch\\IDH_interface\\fetch-status.json` | 放在指定資料夾裡，本系統才讀得到；不寫的預設是腳本資料夾的 `fetch-status.json` |
| `state_dir` | `state` | 去重狀態、鎖檔、隨機值 |
| `fetch_hours` | `07:00-23:00` | 空字串＝全天（v0.3.0 起） |
| `timeout_seconds`、`retries`、`retry_delay_seconds` | 30、3、5 | 逾時與重試；出錯訊息裡的「3 次」「30 秒」跟著這裡 |
| `dedup`、`line_format` | `row`、`segment` | 不要改：本系統與 APP 組的讀法依這兩個 |
| `lock_stale_seconds` | 900 | 鎖檔超過這麼久當成當掉留下的，接手 |
| `encrypt`、`use_system_proxy` | `false`、`false` | 院內不加密、不繞系統 Proxy |

### 1.2 狀態檔 `fetch-status.json` 的欄位

每一輪覆寫（先寫暫存檔再改名，不會讀到一半）；`--dry-run`、時段外、設定錯誤都不寫。

| 欄位 | 意思 |
|---|---|
| `script_version` | 腳本版本，院內是 `0.3.0` |
| `last_attempt_at` | 這一輪開始的時間 |
| `result` | `ok`、`failed`、`skipped`（上一輪還沒結束） |
| `reason` | 失敗或跳過的原因（中文，與主控台同一句；不含網址與欄位值）；成功是 `null` |
| `query_date` | 查的日期 |
| `response_rows`、`written_rows` | 院方回了幾列、這一輪寫進留底幾列；失敗與跳過是 `null` |
| `non_numeric_id_rows` | 病歷號不是純數字的列數，列照樣寫（v0.3.0 起；1116 是 `0`） |
| `output_file` | 當月檔的檔名 |
| `last_success_at` | 最後一次成功的時間；**資料多新看這個**，不看最後一段的 `Date:`（沒有新量測就不寫段落） |

## 2. 看狀態

### FS-01 開 PowerShell、設變數

開一般的 PowerShell（開始 → 打 `powershell` → 直接按 Enter）；`Ctrl+Shift+Enter`、`Win+X` 再按 `A` 是系統管理員，不要用（用系統管理員建的檔，排程以一般權限跑時可能寫不進去）。先貼：

```powershell
$new = 'C:\API_Fetch'; $dir = "$new\IDH_interface"; $sf = "$new\hd-hospital-fetch"; cd -LiteralPath $sf
```

🧪 `$new` 換成 `'C:\hd-sim-fetch\API_Fetch'`。

**成功**：提示字元變成 `…\API_Fetch\hd-hospital-fetch>`。

### FS-02 排程跑了沒

```powershell
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch | Select-Object LastRunTime, LastTaskResult, NextRunTime
```

| `LastTaskResult` | 意思 |
|---|---|
| `0` | 那一輪成功（含時段外、跳過） |
| `1` | 那一輪失敗，看狀態檔的 `reason`（FS-03），對照第 6 節 |
| `2` | 設定錯誤：`config.json` 寫壞了，**狀態檔不會更新**；手動跑 FS-05 看是哪一句 |
| `267009` | 正在跑 |
| `267011` | 還沒跑過，`LastRunTime` 會是 `1999/11/30`；過了 `NextRunTime` 再看（剛裝好時會這樣；1116 模擬實測裝完約 2 分鐘才跑第一輪） |

- **正常**：`LastRunTime` 每 3 分鐘往前跳、`LastTaskResult` `0`
- 印紅字「找不到」：排程沒裝或被移除了，看 FS-07
- 主機重開機後沒人登入：排程不會跑（只在使用者登入時執行，跟本系統的 Docker Desktop 一樣）
- 過了 5 分鐘 `LastRunTime` 都沒變，或連續兩輪 `failed`：查第 6 節

### FS-03 最近一輪的結果

```powershell
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
```

- **正常**：`last_attempt_at` 跟著排程變、`result` `ok`；`written_rows` 多半是 `0`，有新量測時是幾列
- 07:00 前、23:00 後狀態檔停在 22:5x 那一輪：時段外不抓，正常，不是抓取停了
- `failed`：看 `reason`，對照第 6 節；`last_success_at` 是最後一次成功的時間
- 本系統這邊：系統管理 →「院方資料同步」卡的「抓取腳本最近一輪」讀的就是這個檔；讀檔檢查怎麼看在《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》

### FS-04 當月檔最後幾段（不印病人資料）

```powershell
$m = Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt'); (Get-Item -LiteralPath $m).LastWriteTime
Get-Content -LiteralPath $m -Tail 6 -Encoding UTF8 | ForEach-Object { if ($_ -like 'Date:*') { $_ } else { '（{0} 字）' -f $_.Length } }
```

- **會看到**：`Date: …` 與 `（N 字）` 交錯；JSON 那一行只印字數，不印內容
- 每段之間夾一行 `（0 字）` 是舊檔（舊腳本）的寫法，不影響；新腳本每段兩行、不夾空行
- 第一行的修改時間只在有新列時才變；資料多新以狀態檔的 `last_success_at` 為準

### FS-05 手動跑一輪

```powershell
py fetch_dialysis.py --dry-run
py fetch_dialysis.py --once
$LASTEXITCODE
```

- `--dry-run`：只印 `… 成功 回應 N 列、會寫入 M 列（預演，沒有寫任何檔）`，不寫月份檔與狀態檔
- `--once`：真的跑一輪，印 `… 成功 回應 N 列、寫入 M 列`，結束碼 `0`；排程在跑時手動多跑一輪沒關係（有鎖檔，撞到就印「跳過」）
- 07:00 前、23:00 後只印 `時段外 只在 07:00-23:00 抓，這一輪不打院方 API`（預演再加「（預演）」），不是錯
- 兩個參數都沒給：印 `要加 --once（跑一輪）或 --dry-run（預演）`、結束碼 `2`
- 看版本：`py fetch_dialysis.py --version`，院內印 `0.3.0`

## 3. 停、恢復、改頻率、改時段

都在 `$sf` 裡打（FS-01）。🏥 平常由學長做。

### FS-06 停排程

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1
```

**成功**：`已移除工作 hd-hospital-fetch（腳本、設定、留底檔、狀態檔都沒動）`。正在跑的那一輪會先被停掉。本來就沒裝：`沒有叫 hd-hospital-fetch 的工作，不用移除`（結束碼 `0`）。

- 停了之後月份檔與狀態檔都不再更新；本系統在「未更新」提示時段（營運參數預設 8 時到 23 時）超過「院方資料多久未更新就提示」（預設 10 分鐘）就會提示院方資料未更新，APP 組讀到的也停在那一刻
- 要停很久或不要了：本系統那邊照《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》停用讀檔；整支不要了照第 5 節

### FS-07 恢復排程

```powershell
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
```

**成功**：

```text
已建立工作 hd-hospital-fetch
  帳號：<電腦名稱>\<帳號>（只在使用者登入時執行）
  頻率：每 3 分鐘，第一次在 1 分鐘後
  執行：…pythonw.exe "C:\API_Fetch\hd-hospital-fetch\fetch_dialysis.py" --once --config "C:\API_Fetch\hd-hospital-fetch\config.json"
  狀態：Ready
看結果：狀態檔（設定檔的 status_file）每輪覆寫；或 Get-ScheduledTaskInfo -TaskName hd-hospital-fetch
```

接著每 3 分鐘看一次 FS-02、FS-03，三輪都是 `LastTaskResult` `0`、`result` `ok` 才算回來。🧪 路徑是 `C:\hd-sim-fetch\API_Fetch\…`，帳號是自己的。

- 排程跑的時候不會跳視窗，是正常的
- `執行：` 指到不是 `$sf` 的地方：不是在 `$sf` 裡打的；`cd -LiteralPath $sf`、加 `-Force` 重裝
- 帳號要是醫師的那個：用別的帳號登入時裝，排程會變成只在那個帳號登入時才跑

### FS-08 改頻率

```powershell
powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -IntervalMinutes 5 -Force
```

**成功**：同 FS-07，`頻率：每 5 分鐘`。改回來把 `5` 換成 `3`。範圍 1～1440 分鐘。

- 本系統多久讀一次檔是它自己的營運參數「院方資料讀檔頻率」（預設 3 分鐘），不跟著這裡變；本系統的「院方資料多久未更新就提示」預設 10 分鐘（預設頻率下連續三次沒抓到），抓取改得比這個慢就會一直提示，兩邊要一起決定
- 不加 `-Force` 會出現 `已經有一個叫 hd-hospital-fetch 的工作；要換掉就加 -Force，要移除用 uninstall-task.ps1`

### FS-09 改抓取時段

```powershell
notepad config.json
```

把 `"fetch_hours": "07:00-23:00"` 改成新的時段（半形冒號與減號、開始早於結束、不跨午夜；`""` 是全天），存檔，再檢查：

```powershell
Get-Content -Raw -Encoding UTF8 config.json | ConvertFrom-Json | Select-Object output_dir, status_file, fetch_hours, dedup, line_format
py fetch_dialysis.py --dry-run
```

**成功**：`fetch_hours` 是新的值；預演印「成功」或「時段外 只在 <新時段> 抓」。下一輪排程就照新時段。

- 07:00～23:00 是學長 1114 答 F-6 ① 定的，要改先問學長
- 本系統的「未更新」提示時段（營運參數「院方資料未更新提示的起始時刻」「結束時刻」，預設 8、23）是對齊這個時段的；抓取時段改了，提示時段要不要跟著改一起決定

## 4. 換版

做法來自第五次進院 AF-05～AF-11（v0.1.0 → v0.3.0 只換 `fetch_dialysis.py`）；之後的版本照 Release 說明決定換哪些檔。學長在場或同意才做，約 20 分鐘（含看三輪）。

### FS-10 先看 Release 說明

在自己的電腦登入 GitHub（帳號 `94sh09sh19sh`，repo 是私人的；404 就是帳號不對），開 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases`，看新版的說明：

- 改了哪些檔：v0.3.0 只改 `fetch_dialysis.py`；`transcode_history.py`、`install-task.ps1`、`hb/` 與 v0.2.0 相同
- `config.json` 要不要加欄位：v0.3.0 加 `fetch_hours`
- 有沒有 `.exe`：只有 v0.1.0 附 `.exe`（`fetch_dialysis.exe`、`fetch_dialysis_w.exe`、`transcode_history.exe`、`SHA256SUMS.txt`）；v0.2.0、v0.3.0 只有 `.py`
- 腳本的訊息或參數有改的話，先改這一份與還沒出發的進院冊

### FS-11 停排程、留舊檔

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1
$oldv = py fetch_dialysis.py --version
Copy-Item -LiteralPath (Join-Path $sf 'fetch_dialysis.py') -Destination (Join-Path $sf ('fetch_dialysis.py.' + $oldv + '.bak'))
Copy-Item -LiteralPath (Join-Path $sf 'config.json') -Destination (Join-Path $sf ('config.json.' + $oldv + '.bak'))
```

**成功**：`已移除工作 hd-hospital-fetch（…）`；`$sf` 裡多兩個 `.bak` 檔。要換的不只 `fetch_dialysis.py` 時，每個要換的檔都照樣先複製一份。

- 停排程是為了換檔時不會剛好有一輪在跑；停到 FS-14 裝回來，中間本系統可能出現「未更新」提示，正常

### FS-12 下載、換檔

Edge 或 Chrome 按 `Ctrl+Shift+N` 開 InPrivate／無痕視窗 → 登入自己的 GitHub（不勾保持登入、不存密碼）→ 開新版的 Release 頁 → Assets 的 `Source code (zip)` 存到「下載」→ **關掉整個 InPrivate 視窗**。接著（`$v` 換成新版號）：

```powershell
$v = '0.3.0'
$z = "$env:USERPROFILE\Downloads\hd-hospital-fetch-$v.zip"; $tmp = Join-Path $env:TEMP "hd-fetch-$v"
Expand-Archive -LiteralPath $z -DestinationPath $tmp -Force
Copy-Item -LiteralPath (Join-Path $tmp "hd-hospital-fetch-$v\fetch_dialysis.py") -Destination $sf -Force
Remove-Item -LiteralPath $tmp -Recurse -Force; Remove-Item -LiteralPath $z
Unblock-File -LiteralPath (Join-Path $sf 'fetch_dialysis.py')
py fetch_dialysis.py --version
```

**成功**：最後一行是新版號。`config.json`、`state\` 不動；Release 說明有寫的其他檔照第四行一樣一個一個複製、`Unblock-File`。

- 找不到 zip：看「下載」裡的實際檔名（例如 `hd-hospital-fetch-0.3.0 (1).zip`），改 `$z`
- 印的還是舊版號：複製沒成功，從 `$z` 那一行再做一次
- Edge 擋下載：在下載清單選「…」→「保留」
- 院內網路連不上 GitHub：停，排程照 FS-07 裝回舊版
- 用 `.exe` 的版本：另外下載 `.exe` 與 `SHA256SUMS.txt`，放進 `$sf` 後 `Get-FileHash .\fetch_dialysis.exe, .\fetch_dialysis_w.exe, .\transcode_history.exe -Algorithm SHA256 | Select-Object Hash, Path` 與 `Get-Content .\SHA256SUMS.txt` 對，雜湊不同就刪掉重新下載

### FS-13 改設定（新版要的欄位）

Release 說明沒有新欄位就跳過。有的話 `notepad config.json`，在最後一個欄位後面加逗號、下一行加新欄位；反斜線一律寫成 `\\`。存檔後檢查：

```powershell
Get-Content -Raw -Encoding UTF8 config.json | ConvertFrom-Json | Select-Object output_dir, status_file, fetch_hours, dedup, line_format
```

**成功**：`C:\API_Fetch\IDH_interface`、其中的 `fetch-status.json`、`07:00-23:00`、`row`、`segment`（再加上新欄位的值）。紅字「無效的 JSON」多半是少了逗號或反斜線只寫一個。

### FS-14 預演、跑一輪、裝回排程、看三輪

```powershell
py fetch_dialysis.py --dry-run
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
```

**成功**：預演、跑一輪都是「成功」，`$LASTEXITCODE` `0`，狀態檔 `result` `ok`、`script_version` 是新版號；跑一輪寫入的不會是整天的列（`state\` 沒動）；排程照 FS-07 裝好、看三輪。

- 時段外做不了預演與跑一輪：等進時段，或排程先裝回去、進時段後看三輪
- 有一步不對：照 FS-15 退回舊版

### FS-15 換版退回（回上一版）

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1
Copy-Item -LiteralPath (Join-Path $sf ('fetch_dialysis.py.' + $oldv + '.bak')) -Destination (Join-Path $sf 'fetch_dialysis.py') -Force
Copy-Item -LiteralPath (Join-Path $sf ('config.json.' + $oldv + '.bak')) -Destination (Join-Path $sf 'config.json') -Force
py fetch_dialysis.py --version
```

**成功**：印舊版號；接著照 FS-14 從預演做到看三輪。`$oldv` 不見了（PowerShell 重開過）就先 `$oldv = '<舊版號>'`，或用 `dir *.bak` 看檔名。

- 設定一定要跟著退：舊版看到新版的欄位會拒絕啟動，例如退回 v0.1.0 會印 `設定錯誤 設定檔有不認得的欄位：fetch_hours`
- 退回 v0.1.0 就沒有抓取時段，會整天抓（夜間也打院方 API）；要先問學長
- 換版成功、看完三輪後，`.bak` 留著也不影響（腳本只讀 `config.json` 與 `fetch_dialysis.py`）；要刪等下一次換版前

## 5. 退回（不要抓取腳本了）

學長說「不要了」或斷點決定退回時，在 `$sf` 裡依序做。

| 舊編號 | 原本寫在 |
|---|---|
| 第十九冊 R-1 停排程、R-2 歷史 txt 回到轉碼前、R-3 刪腳本 | 第四次進院（1109）：《[第四次進院（1109）· 放上院方 API 抓取腳本之一：詳細版](visit-4-api-detail.md)》 |
| 第二十一冊 R-1 停排程、R-2 舊資料夾改回原名、R-3 C 槽那份留著 | 第五次進院（1116）：《[第五次進院（1116）任務一 · 抓取腳本上線](visit-5-api.md)》 |

### FS-16 停排程（兩冊的 R-1）

照 FS-06。**成功**：`已移除工作 hd-hospital-fetch（腳本、設定、留底檔、狀態檔都沒動）`。

- 本系統那邊接著照《[讀檔：啟用、檢查、停用](ref-dialysis-files.md)》停用讀檔，不然會一直提示「未更新」
- 進院途中退回的：那一趟本系統不換版

### FS-17 舊資料夾改回原名（第二十一冊 R-2）

**1116 起做不到**：院內 D 槽的 `API_Fetch_搬到C槽_1116` 學長在 AF-11 三輪成功後整個刪掉了，退回只能用 C 槽那一份。留著做法給還有舊資料夾的情形（學長同意才做）：

```powershell
cd C:\
Rename-Item -LiteralPath '<舊資料夾 API_Fetch_搬到C槽_MMDD 的完整路徑>' 'API_Fetch'
```

🧪 可以實際練一次：舊資料夾是 `C:\hd-sim-fetch\D槽\API_Fetch_搬到C槽_MMDD`。

### FS-18 歷史 txt 回到轉碼前（第十九冊 R-2）

**院內不必做**：1109 轉碼預演 24 個檔全是 UTF-8、要轉 0 個，沒有實轉，指定資料夾裡沒有 `_backup_…` 備份。留著做法給有轉過碼的主機：用轉碼時最後一行抄下的「還原：…」那一行（工具印的是 `python`，依第十九冊 B-05 看到的換成 `py`）：

```powershell
py transcode_history.py --restore "<指定資料夾>\_backup_YYYYMMDD-HHMM"
```

**成功**：每個檔 `- <檔名>：已還原`，最後 `已還原 N 個檔到 <指定資料夾>；備份資料夾保留`。

- 還原是整個檔換回備份：轉碼之後（第十九冊是 B-16 起）附加到當月檔的那幾段也會一起被蓋回去
- 備份資料夾 `_backup_…` 不刪，留給學長
- `找不到備份資料夾：…`：路徑抄錯；`備份資料夾裡沒有 txt`：選錯資料夾；`- <檔名>：還原後比對不合`：停，回報

### FS-19 C 槽那份與腳本資料夾（第二十一冊 R-3、第十九冊 R-3）

- **C 槽那份（`C:\API_Fetch\IDH_interface` 的月份檔）留著，學長決定**：APP 組也在讀，不要動
- 刪腳本資料夾只在學長說要刪時做；刪的只有腳本、`config.json`、`state\`，留底與狀態檔在 `$dir`，不受影響：

```powershell
cd ..
Remove-Item -Recurse -LiteralPath $sf
```

`$sf` 是空的就先照 FS-01 設好。🧪 FS-16、FS-17 都可以實際練一次。

## 6. 出錯訊息總表

主控台每一行開頭是時間（`YYYY-MM-DD HH:MM:SS`），接著是結果（`成功`、`失敗`、`跳過`、`時段外`、`設定錯誤`）與原因；`失敗`、`跳過` 的原因也寫進狀態檔的 `reason`。「版本」欄是這句話從哪一版起有：v0.1.0 是 1109 第四次進院用的、v0.3.0 是 1116 起院內在跑的。查不出來就**停**，回報。

### 6.1 抓取腳本 `fetch_dialysis.py`

| 畫面上看到 | 版本 | 意思 | 怎麼做 |
|---|---|---|---|
| `can't open file '…fetch_dialysis.py': [Errno 2] No such file or directory` | — | 不在 `$sf` 裡打的（這是 Python 的訊息） | `cd -LiteralPath $sf` 再試（FS-01） |
| `設定錯誤 找不到設定檔：<路徑>` | v0.1.0 | 腳本旁邊沒有 `config.json`（沒從 `config.example.json` 複製、或改了名）；腳本找的是自己旁邊的 `config.json`，跟目前在哪個資料夾無關 | 確認 `$sf` 裡有 `config.json`；新放的腳本照《[第五次進院（1116）任務一 · 抓取腳本上線之一：詳細版](visit-5-api-detail.md)》第 4 節 `Copy-Item config.example.json config.json` 再填 |
| `設定錯誤 設定檔不是合法的 JSON：<細節>` | v0.1.0 | `config.json` 寫壞了，最常見是反斜線只寫一個、少了引號或逗號 | 每個 `\` 寫成 `\\`、每個欄位之間有逗號；改完照 FS-13 檢查 |
| `設定錯誤 設定檔的最外層要是物件` | v0.1.0 | 整個檔不是 `{ … }` | 從 `config.example.json` 重抄，或用換版留下的 `.bak` |
| `設定錯誤 設定檔有不認得的欄位：<欄位>` | v0.1.0 | 欄位名打錯，或把新版的欄位放進舊版（例如 v0.1.0 看到 `fetch_hours`） | 改正或拿掉那個欄位（FS-15） |
| `設定錯誤 endpoint 沒有填`、`設定錯誤 output_dir 沒有填` | v0.1.0 | 那個欄位是空的 | 照 `values.md`、第 1.1 節填 |
| `設定錯誤 endpoint 要是 http 或 https 開頭` | v0.1.0 | 位址抄錯或被改壞 | 對照 `values.md`（`http://` 開頭到 `.php`，不加 `?date=`） |
| `設定錯誤 dedup 只接受 "row" 或 "off"`、`設定錯誤 line_format 只接受 "segment" 或 "row"` | v0.1.0 | 這兩欄被改了 | 改回 `"row"`、`"segment"` |
| `設定錯誤 <欄位> 要是 0 以上的數字`、`… 要是 1 以上的整數`、`… 要是非空的欄位位置清單（0 起算）`、`設定錯誤 encrypt、use_system_proxy 要是 true 或 false`、`設定錯誤 encrypt 開了，encrypt_key_file 要填` | v0.1.0 | 其他欄位寫錯 | 對照 `config.example.json` 改回第 1.1 節的值 |
| `設定錯誤 fetch_hours 要是字串，例 "07:00-23:00"；空字串表示全天`、`設定錯誤 fetch_hours 的格式是 "HH:MM-HH:MM"，例 "07:00-23:00"`、`…開始要早於結束（不跨午夜）`、`…時刻要在 00:00～24:00 之間` | v0.3.0 | `fetch_hours` 那一行寫錯 | 改成 `"fetch_hours": "07:00-23:00"`（半形冒號與減號，有引號） |
| `失敗 重試 3 次仍失敗；最後一次：連線失敗：…`（後面是 `找不到主機`、`對方拒絕連線`、`逾時` 或錯誤類型與 `errno=`） | v0.1.0 | 連不到院方 API | 確認位址；用瀏覽器開 `<院方位址>?date=<今天，YYYY-MM-DD>` 看得到資料嗎；看不到就**停**。🧪 模擬院方 API 沒開，請開發端開 |
| `失敗 重試 3 次仍失敗；最後一次：HTTP 404` 或其他數字 | v0.1.0 | 院方回錯誤 | 位址的路徑抄錯（`.php` 前面那段）；對了還是錯就**停** |
| `失敗 重試 3 次仍失敗；最後一次：逾時（>30 秒）` | v0.1.0 | 院方太慢 | 再試一次；連續逾時就**停** |
| `失敗 重試 3 次仍失敗；最後一次：回應不完整：<類型>` | v0.1.0 | 院方回到一半斷了 | 再試一次；連續出現就**停** |
| `失敗 回應不是 UTF-8` | v0.1.0 | 院方回的內容編碼不對（不重試） | **停**，回報 |
| `失敗 回應裡找不到 JSON 內容`、`失敗 回應的 JSON 無法解析`、`失敗 回應裡沒有 data_list 陣列` | v0.1.0 | 院方回的不是透析清單（維護頁、登入頁） | **停** |
| `失敗 當月的留底檔不是 UTF-8，先用 transcode_history.py 轉檔` | v0.1.0 | 當月檔還是舊寫法（cp950） | 轉碼：照《[第五次進院（1116）任務一 · 抓取腳本上線之一：詳細版](visit-5-api-detail.md)》第 4 節第 3 步（1109 的完整做法在《[第四次進院（1109）· 放上院方 API 抓取腳本之一：詳細版](visit-4-api-detail.md)》B-12、B-13）；轉不了就**停** |
| `失敗 encrypt 開了，但這台主機沒有安裝 cryptography`、`失敗 讀不到加密金鑰檔`、`失敗 加密金鑰檔的格式不對`、`失敗 加密金鑰長度不對` | v0.1.0 | 只有 `encrypt` 開了才會出現；院內不加密 | `encrypt` 改回 `false`；真的要加密先問學長 |
| `失敗 不預期的錯誤：<類型>` | v0.1.0 | 腳本沒料到的錯（只留類型，不帶欄位值） | **停**，記下類型回報開發端 |
| `狀態檔寫不進去：<類型>` | v0.1.0 | `status_file` 的資料夾不存在、沒權限，或有程式一直開著狀態檔；這一輪結束碼 `1` | 核對 `status_file`（第 1.1 節）；用系統管理員建過的檔改回一般權限建；讀的程式讀完要關 |
| `跳過 上一輪還沒結束` | v0.1.0 | 另一輪正在跑（鎖檔）；鎖檔超過 900 秒會當成當掉留下的、自動接手 | 正常，等一下再看 |
| `時段外 只在 07:00-23:00 抓，這一輪不打院方 API` | v0.3.0 | 現在不在 `fetch_hours` 的時段內；沒打院方 API、沒寫任何檔（含狀態檔），結束碼 `0` | 正常；要現場試跑就等到 07:00 之後 |
| `成功 … 病歷號不是純數字的 N 列（照樣保留）` | v0.3.0 | 回應裡有病歷號帶英文字母的列（之二 B-2）；照樣寫進留底，只是計數 | 不是錯；記下 N，不記病歷號 |
| `要加 --once（跑一輪）或 --dry-run（預演）` | v0.1.0 | 兩個參數都沒給，結束碼 `2` | 照 FS-05 加參數 |

### 6.2 排程 `install-task.ps1`、`uninstall-task.ps1`

| 畫面上看到 | 意思 | 怎麼做 |
|---|---|---|
| 紅字有「執行原則」或「無法載入」 | 院方群組原則擋 PowerShell 腳本 | **停**，學長決定 |
| `已經有一個叫 hd-hospital-fetch 的工作；要換掉就加 -Force，要移除用 uninstall-task.ps1` | 已經裝過 | 不是自己裝的就**停**，跟學長確認；確定要換才加 `-Force` |
| `找不到設定檔：<路徑>（先把 config.example.json 複製成 config.json 並填好）` | `$sf` 裡沒有 `config.json` | 先填好設定、跑過 FS-05 再裝 |
| `找不到 <…\fetch_dialysis.py>`、`找不到 <-Exe 給的檔>` | 腳本或 `.exe` 不在那裡 | 在 `$sf` 裡打；`.exe` 的路徑寫對 |
| `找不到 pythonw.exe：用 -Python 指定 python.exe 的位置，或用 -Exe 改用打包好的 .exe`、`找不到 Python：<路徑>` | 找不到 Python | `-Python` 指到 `python.exe` 的完整路徑；都沒有就**停**，學長決定 |
| `執行：` 指到不是 `$sf` 的地方（例如 D 槽） | 不在 `$sf` 裡打的 | `cd -LiteralPath $sf`、加 `-Force` 重裝 |
| `沒有叫 hd-hospital-fetch 的工作，不用移除` | 本來就沒裝 | 不用做什麼 |
| `移除失敗：hd-hospital-fetch 還在` | 移除沒成功 | 關掉工作排程器視窗再試；還是不行就**停**，回報 |

排程的 `LastTaskResult` 數字見 FS-02。

### 6.3 其他

| 畫面上看到 | 意思 | 怎麼做 |
|---|---|---|
| `py` 說找不到指令 | 沒有 Python launcher | 換成 `python`；兩個都沒有就**停**（學長決定裝 Python 或用 `.exe`；`.exe` 只有 v0.1.0 有，沒有抓取時段） |
| Windows 跳出「Windows 已保護您的電腦」 | `.exe` 第一次執行 | 有做 `Unblock-File` 就不會出現；出現了按「其他資訊」→「仍要執行」，雜湊對過才可以（FS-12） |
| `找不到 raw_txt 的月份檔，停在這裡` | `hb` 現況盤點腳本的訊息（不是這支腳本）：`$hb` 貼錯資料夾，或 `config.json` 的 `output_dir` 不是 `hospital_dataset` | 盤點 1111 起不跑。真的要跑時：用盤點第一步列出的最近改過的檔找 `raw_txt` 在哪，`$hb` 改成它上兩層的資料夾；盤點的做法在《[檢驗資料（hb）抓取（未採用）](ref-hb-fetch.md)》 |

1117 對 v0.3.0 程式補進來、舊冊沒列的：Python 的 `can't open file`、`設定檔的最外層要是物件`、`設定檔有不認得的欄位`、`endpoint 沒有填`、`output_dir 沒有填`、`dedup`／`line_format` 與其他欄位的設定錯誤、`回應不完整`、`回應不是 UTF-8`、加密的四種、`不預期的錯誤`、`狀態檔寫不進去`、缺 `--once`／`--dry-run`、`LastTaskResult` `2`、`install-task.ps1` 的四種「找不到」、`uninstall-task.ps1` 的兩種。舊冊寫「`找不到設定檔` 是不在腳本資料夾裡」不對：腳本找的是自己旁邊的 `config.json`，不在 `$sf` 裡打會先出現 Python 的 `can't open file`。

## 7. 一頁速查

```powershell
$new = 'C:\API_Fetch'; $dir = "$new\IDH_interface"; $sf = "$new\hd-hospital-fetch"; cd -LiteralPath $sf
py fetch_dialysis.py --version
py fetch_dialysis.py --dry-run
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 C:\API_Fetch\IDH_interface\fetch-status.json
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -IntervalMinutes 5 -Force
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1
py transcode_history.py "<指定資料夾>"
py transcode_history.py "<指定資料夾>" --apply
py transcode_history.py --restore "<指定資料夾>\_backup_YYYYMMDD-HHMM"
```

| 指令 | 做什麼 |
|---|---|
| 第 1 行 | 設變數、進腳本資料夾（FS-01） |
| `--version` | 院內印 `0.3.0` |
| `--dry-run` | 抓取預演，不寫檔 |
| `--once`、`$LASTEXITCODE` | 跑一輪；`0` 成功、`1` 失敗、`2` 設定錯 |
| `Get-Content … fetch-status.json` | 最近一輪的結果（狀態檔 1116 起在指定資料夾裡） |
| `Get-ScheduledTaskInfo` | 排程跑了沒 |
| `install-task.ps1` | 裝排程；加 `-IntervalMinutes 5 -Force` 是改頻率 |
| `uninstall-task.ps1` | 停排程 |
| `transcode_history.py` | 轉碼預演、實轉（`--apply`）、還原（`--restore`）；院內不必轉 |

🧪 路徑的 `C:\API_Fetch` 換成 `C:\hd-sim-fetch\API_Fetch`。用 `.exe` 的話 `py fetch_dialysis.py` 換成 `.\fetch_dialysis.exe`、`py transcode_history.py` 換成 `.\transcode_history.exe`，其餘照舊。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
