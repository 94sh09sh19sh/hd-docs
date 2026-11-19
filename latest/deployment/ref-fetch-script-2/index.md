# 院方 API 抓取腳本的維運（第 2 份，FS-10～FS-19 與一頁速查）

上層文件：《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script/index.md)》

> 狀態：**現行**（常備參考）。1117 由舊第二十二冊第 6 節與第十九冊之一第 2 節（一頁速查）、第十九冊第 3 節與第二十一冊第 2 節（退回）合成，換版做法來自第五次進院 AF-05～AF-11。編號：`FS-xx`；退回各步附上舊編號（第十九冊、第二十一冊各有一套 `R-1`～`R-3`，意思不同）。
>
> **公開範圍**：院方位址、帳號、主機名稱不寫在這裡，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；`C:\API_Fetch\…` 是通用位置，直接寫。

## 摘要

- 這一份接《第 1 份》：第 4 節換版（FS-10～FS-15）、第 5 節退回（FS-16～FS-19）、第 7 節一頁速查；第 6 節出錯訊息總表在《[之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script-errors/index.md)》
- 換版與換版退回（FS-10～FS-15）：先停排程、留舊檔、只換 Release 說明裡改過的檔
- 退回整支腳本（FS-16～FS-19）：1116 學長刪了 D 槽舊資料夾，「改回原名」做不到；院內 1109 沒轉碼，沒有轉碼備份可還原
- 一頁速查（第 7 節）
- 都在 `$sf` 裡打；PowerShell 重開過、`$dir`／`$sf` 是空的，先照《第 1 份》FS-01 設好

## 4. 換版

做法來自第五次進院 AF-05～AF-11（v0.1.0 → v0.3.0 只換 `fetch_dialysis.py`）；之後的版本照 Release 說明決定換哪些檔。學長在場或同意才做，約 20 分鐘（含看三輪）。

### FS-10 先看 Release 說明

在自己的電腦登入 GitHub（帳號 `94sh09sh19sh`，repo 是私人的；404 就是帳號不對），開 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases`，看新版的說明：

- 改了哪些檔：v0.3.0 只改 `fetch_dialysis.py`；`transcode_history.py`、`install-task.ps1`、`hb/` 與 v0.2.0 相同
- `config.json` 要不要加欄位：v0.3.0 加 `fetch_hours`
- 有沒有 `.exe`：只有 v0.1.0 附 `.exe`（`fetch_dialysis.exe`、`fetch_dialysis_w.exe`、`transcode_history.exe`、`SHA256SUMS.txt`）；v0.2.0、v0.3.0 只有 `.py`
- 腳本的訊息或參數有改的話，先改這一份與還沒出發的進院冊

### FS-11 停排程、留舊檔

```
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1
$oldv = py fetch_dialysis.py --version
Copy-Item -LiteralPath (Join-Path $sf 'fetch_dialysis.py') -Destination (Join-Path $sf ('fetch_dialysis.py.' + $oldv + '.bak'))
Copy-Item -LiteralPath (Join-Path $sf 'config.json') -Destination (Join-Path $sf ('config.json.' + $oldv + '.bak'))
```

**成功**：`已移除工作 hd-hospital-fetch（…）`；`$sf` 裡多兩個 `.bak` 檔。要換的不只 `fetch_dialysis.py` 時，每個要換的檔都照樣先複製一份。

- 停排程是為了換檔時不會剛好有一輪在跑；停到 FS-14 裝回來，中間本系統可能出現「未更新」提示，正常

### FS-12 下載、換檔

Edge 或 Chrome 按 `Ctrl+Shift+N` 開 InPrivate／無痕視窗 → 登入自己的 GitHub（不勾保持登入、不存密碼）→ 開新版的 Release 頁 → Assets 的 `Source code (zip)` 存到「下載」→ **關掉整個 InPrivate 視窗**。接著（`$v` 換成新版號）：

```
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

```
Get-Content -Raw -Encoding UTF8 config.json | ConvertFrom-Json | Select-Object output_dir, status_file, fetch_hours, dedup, line_format
```

**成功**：`C:\API_Fetch\IDH_interface`、其中的 `fetch-status.json`、`07:00-23:00`、`row`、`segment`（再加上新欄位的值）。紅字「無效的 JSON」多半是少了逗號或反斜線只寫一個。

### FS-14 預演、跑一輪、裝回排程、看三輪

```
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

```
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

| 舊編號                                                        | 原本寫在                                                                                                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 第十九冊 R-1 停排程、R-2 歷史 txt 回到轉碼前、R-3 刪腳本      | 第四次進院（1109）：《[第四次進院（1109）· 放上院方 API 抓取腳本之三：詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api-detail-3/index.md)》 |
| 第二十一冊 R-1 停排程、R-2 舊資料夾改回原名、R-3 C 槽那份留著 | 第五次進院（1116）：《[第五次進院（1116）任務一 · 抓取腳本上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-api/index.md)》                        |

### FS-16 停排程（兩冊的 R-1）

照 FS-06。**成功**：`已移除工作 hd-hospital-fetch（腳本、設定、留底檔、狀態檔都沒動）`。

- 本系統那邊接著照《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》停用讀檔，不然會一直提示「未更新」
- 進院途中退回的：那一趟本系統不換版

### FS-17 舊資料夾改回原名（第二十一冊 R-2）

**1116 起做不到**：院內 D 槽的 `API_Fetch_搬到C槽_1116` 學長在 AF-11 三輪成功後整個刪掉了，退回只能用 C 槽那一份。留著做法給還有舊資料夾的情形（學長同意才做）：

```
cd C:\
Rename-Item -LiteralPath '<舊資料夾 API_Fetch_搬到C槽_MMDD 的完整路徑>' 'API_Fetch'
```

🧪 可以實際練一次：舊資料夾是 `C:\hd-sim-fetch\D槽\API_Fetch_搬到C槽_MMDD`。

### FS-18 歷史 txt 回到轉碼前（第十九冊 R-2）

**院內不必做**：1109 轉碼預演 24 個檔全是 UTF-8、要轉 0 個，沒有實轉，指定資料夾裡沒有 `_backup_…` 備份。留著做法給有轉過碼的主機：用轉碼時最後一行抄下的「還原：…」那一行（工具印的是 `python`，依第十九冊 B-05 看到的換成 `py`）：

```
py transcode_history.py --restore "<指定資料夾>\_backup_YYYYMMDD-HHMM"
```

**成功**：每個檔 `- <檔名>：已還原`，最後 `已還原 N 個檔到 <指定資料夾>；備份資料夾保留`。

- 還原是整個檔換回備份：轉碼之後（第十九冊是 B-16 起）附加到當月檔的那幾段也會一起被蓋回去
- 備份資料夾 `_backup_…` 不刪，留給學長
- `找不到備份資料夾：…`：路徑抄錯；`備份資料夾裡沒有 txt`：選錯資料夾；`- <檔名>：還原後比對不合`：停，回報

### FS-19 C 槽那份與腳本資料夾（第二十一冊 R-3、第十九冊 R-3）

- **C 槽那份（`C:\API_Fetch\IDH_interface` 的月份檔）留著，學長決定**：APP 組也在讀，不要動
- 刪腳本資料夾只在學長說要刪時做；刪的只有腳本、`config.json`、`state\`，留底與狀態檔在 `$dir`，不受影響：

```
cd ..
Remove-Item -Recurse -LiteralPath $sf
```

`$sf` 是空的就先照 FS-01 設好。🧪 FS-16、FS-17 都可以實際練一次。

## 7. 一頁速查

```
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

| 指令                              | 做什麼                                                       |
| --------------------------------- | ------------------------------------------------------------ |
| 第 1 行                           | 設變數、進腳本資料夾（FS-01）                                |
| `--version`                       | 院內印 `0.3.0`                                               |
| `--dry-run`                       | 抓取預演，不寫檔                                             |
| `--once`、`$LASTEXITCODE`         | 跑一輪；`0` 成功、`1` 失敗、`2` 設定錯                       |
| `Get-Content … fetch-status.json` | 最近一輪的結果（狀態檔 1116 起在指定資料夾裡）               |
| `Get-ScheduledTaskInfo`           | 排程跑了沒                                                   |
| `install-task.ps1`                | 裝排程；加 `-IntervalMinutes 5 -Force` 是改頻率              |
| `uninstall-task.ps1`              | 停排程                                                       |
| `transcode_history.py`            | 轉碼預演、實轉（`--apply`）、還原（`--restore`）；院內不必轉 |

🧪 路徑的 `C:\API_Fetch` 換成 `C:\hd-sim-fetch\API_Fetch`。用 `.exe` 的話 `py fetch_dialysis.py` 換成 `.\fetch_dialysis.exe`、`py transcode_history.py` 換成 `.\transcode_history.exe`，其餘照舊。

上一份：《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script/index.md)》（第 1～3 節）；出錯訊息總表在《[…之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script-errors/index.md)》

______________________________________________________________________

## 版本歷程

| 定版                                                                               | 日期       | 異動                                                                                      |
| ---------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-fetch-script-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《院方 API 抓取腳本的維運》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
