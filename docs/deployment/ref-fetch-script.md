# 院方 API 抓取腳本的維運

> - 狀態：**現行**（常備參考）。院內主機整體的現況與待辦在《[院內主機現況與未完成事項](ref-status.md)》，這一份只管抓取腳本 `hd-hospital-fetch` 本身
> - 1117 由舊第二十二冊第 3 節（出錯訊息總表）與第 6 節（一頁速查）、第十九冊之一第 1 節（出錯對照）與第 2 節（一頁速查）、第十九冊第 3 節（退回）、第二十一冊第 2 節（退回）合成，訊息原文對 `hd-hospital-fetch` v0.3.0 的程式補齊
> - 編號：`FS-xx`（1117 新開）；退回各步附上舊編號（第十九冊、第二十一冊各有一套 `R-1`～`R-3`，意思不同）
> - 分兩份加一份子文件：這一份是第 1～3 節（現在的樣子、看狀態 FS-01～FS-05、停／恢復／改頻率／改時段 FS-06～FS-09）；第 4、5、7 節（換版 FS-10～FS-15、退回 FS-16～FS-19、一頁速查）在《[第 2 份](ref-fetch-script-2.md)》；第 6 節出錯訊息總表在子文件《[院方 API 抓取腳本的維運之一：出錯訊息總表](ref-fetch-script-errors.md)》

> **公開範圍**：院方位址、帳號、主機名稱不寫在這裡，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；`C:\API_Fetch\…` 是通用位置，直接寫。

> 訊息原文綁在 `hd-hospital-fetch` 的 `fetch_dialysis.py`、`install-task.ps1`、`uninstall-task.ps1`、`transcode_history.py`；腳本改了訊息或參數，回頭改這一份（進院冊已凍結的不改）。

## 摘要

- 現在的樣子：v0.3.0 在 `C:\API_Fetch\hd-hospital-fetch`，排程 `hd-hospital-fetch` 每 3 分鐘、只在 07:00～23:00 抓，留底與狀態檔都在 `C:\API_Fetch\IDH_interface`；本系統 `v0.5.0` 與 APP 組只讀那個資料夾（第 1 節）
- 看狀態：排程的 `LastTaskResult`、狀態檔的 `result` 與 `last_success_at`、不印病人資料看檔尾（FS-02～FS-05）
- 停、恢復、改頻率、改時段（FS-06～FS-09）：停了本系統會在提示時段顯示「未更新」
- 出錯訊息總表（第 6 節）：每一列標出從哪一版起有；設定錯誤不寫狀態檔，排程上看 `LastTaskResult` `2`
- 腳本歸負責 IDH 系統的學長管；平常的停、改頻率、看最近一輪由學長做
- 換版（FS-10～FS-15）、退回（FS-16～FS-19）、一頁速查在《第 2 份》；第 6 節出錯訊息總表在《之一》

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

下一份：《[院方 API 抓取腳本的維運（第 2 份，FS-10～FS-19 與一頁速查）](ref-fetch-script-2.md)》；出錯訊息總表在《[…之一](ref-fetch-script-errors.md)》

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
