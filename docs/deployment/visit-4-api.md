# 第四次進院（1109）· 放上院方 API 抓取腳本

> **狀態：已照做 1109，凍結**——做到 B-15（預演一輪成功，院方回應 703 列），B-16 起沒做、排程沒裝；結果見《[第四次進院紀錄（1109，做到 B-15）](record-4-1109.md)》。之後的院內主機現況看《[院內主機現況與未完成事項](ref-status.md)》。
>
> 改寫自舊第十九冊（院方 API 抓取腳本的安裝，新手版）。編號：`B-xx`。
>
> 子文件（同一套編號：為什麼、完整指令、會看到的原文、不對的話）：《[…之一：詳細版（B-01～B-11）](visit-4-api-detail.md)》（第 0 節開始前先懂的事、出發前、看現況、下載與放好）；《[…之二：詳細版（B-12～B-14c）](visit-4-api-detail-2.md)》（轉碼、填設定、1114 加的 B-14a～B-14c：搬到 C 槽、換成 v0.3.0、改設定）；《[…之三：詳細版（B-15～B-21、退回、對照）](visit-4-api-detail-3.md)》（預演、跑一輪、裝排程、看三輪、教學長、記錄、收工、中途收工、第 3 節退回、第 4 節與 `AF-xx` 的對照）。出錯總表在《[院方 API 抓取腳本的維運之一：出錯訊息總表](ref-fetch-script-errors.md)》，速查、退回在《[院方 API 抓取腳本的維運（第 2 份，FS-10～FS-19 與一頁速查）](ref-fetch-script-2.md)》。

> **這一冊只回答：在醫院那台主機上把抓取腳本 `hd-hospital-fetch` 放上去，讓它每 3 分鐘自己抓一次院方透析清單——按什麼、怎樣算成功。** 本系統（容器、`.env`、平板）這次完全不動。
>
> **B-14a～B-14c 是 1114 為第五次進院加的**（第 3 節）；第五次（1116）實際照的是《[第五次進院（1116）任務一 · 抓取腳本上線](visit-5-api.md)》的 `AF-xx`，本冊不必再翻。

> **公開範圍**：院方位址、指定資料夾的完整路徑、帳號不寫在這裡，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；用 `<指定資料夾>`、`<院方位址>`、`<腳本資料夾>` 代稱。`C:\API_Fetch\…` 是通用位置，直接寫。

## 摘要

- 1109（一）15:30 起，學長在場，約 60 分鐘；順序 B-01～B-21
- 這一冊開在部署主機的瀏覽器上（一般視窗、不登入 GitHub），指令複製貼進一般權限的 PowerShell
- 出發前 B-01～B-03 → 看現況 B-04～B-08 → 下載與放好 B-09～B-11 → 轉碼 B-12～B-13 → 試跑 B-14～B-16 → 排程 B-17～B-19 → 收尾 B-20～B-21
- 成功的定義：B-18 三輪 `LastTaskResult` `0`、狀態檔 `result` `ok`
- 1109 實際：做到 B-15；B-13 不必做（24 個檔全已是 UTF-8）；時間不夠，照詳細版的「中途收工」收
- 檢驗資料（`hb`）1111 起不做，B-19 做完直接 B-20

## 0. 兩邊的差別一覽

| 哪裡 | 🏥 院內正式主機 | 🧪 開發機 |
|---|---|---|
| 演練 | 1109 照本冊做 | 1109 前**沒有**照本冊整趟演練；1108 晚上只在開發機跑過腳本的測試與排程（《[院方 API 介接之三](../notes/hospital-api-fetch-methods-monday-plan.md)》T-1～T-6，T-4 實測每 3 分鐘各跑一次、移除乾淨） |
| 機器 | 院內三台裡最右邊那台、醫師的帳號 | 開發機、自己的帳號 |
| 院方 API | `values.md` 的院方位址 | v0 跑 `npm run dev:hospital-sim` 的模擬院方 API（腳本 README「測試」：`http://localhost:8090/dialysislist.php`） |
| Release 下載 | InPrivate／無痕視窗登入自己的 GitHub | 開發機本來就有 repo，不必下載 |
| 學長 | 在場，斷點由他決定 | 自己決定 |

**PowerShell 一律開一般的**（開始 → 打 `powershell` → 直接按 Enter），不要用 `Win+X` 再按 `A`。視窗關掉後 `$dir`、`$sf` 會不見，重開照詳細版第 0 節第 6 點貼一行。

## 1. 出發前

### B-01 帶手機

**做什麼**：手機裡有 GitHub 兩步驟驗證、`values.md`、現場筆記。

**成功**：三樣都在手機上。

### B-02 確認 Release 頁

**做什麼**：自己的電腦登入 GitHub，開 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.1.0`。

**成功**：看得到 `Source code (zip)`、三個 `.exe` 與 `SHA256SUMS.txt`。

### B-03 手機能看 `values.md`

**做什麼**：手機的 GitHub App 開私人 repo 的 `deploy/records/1108-hospital-api/values.md`。

**成功**：看得到院方位址與指定資料夾的路徑。

## 2. 現場步驟

### B-04 對的主機、對的帳號，把這一冊開在主機上

**做什麼**：🏥 最右邊那台；主機瀏覽器一般視窗（不登入 GitHub）開公開文件站的這一冊；開一般 PowerShell：

```powershell
whoami
```

**成功**：🏥 是醫師的帳號；PowerShell 標題沒有「系統管理員」。

### B-05 看 Python

**做什麼**：

```powershell
py -0p
python --version
```

**成功**：有 3.8 以上就走 `.py`，沒有就由學長決定裝 Python 或用 `.exe`。🏥 1109：`py` 有 3.13、`python` 沒輸出（Microsoft Store 空殼），照用 `py`。

### B-06 看 OneDrive 有沒有在同步指定資料夾

**做什麼**：檔案總管開 `<指定資料夾>`（透析清單 `IDH_interface`，不是 `Hb_API_Fetch`），複製網址列的路徑；PowerShell 原樣貼詳細版 B-06 的指令，出現「貼上指定資料夾的路徑:」才貼路徑。

**成功**：`True`、`False`、沒多印「… -> …」；檔案屬性只有 `Archive`；最新的「年-月.txt」開頭有 `Date:` 與 `"data_list"`（兩個 `True`）。網址列的「開始備份」不要按。

### B-07 看有沒有舊的腳本在跑

**做什麼**：貼詳細版 B-07 的兩個指令（找排程工作、找在跑的 Python）。

**成功**：兩個都沒印東西。

### B-08 決定兩個位置

**做什麼**：跟學長定好指定資料夾與腳本資料夾；貼：

```powershell
$sf = Join-Path (Split-Path -Parent $dir) 'hd-hospital-fetch'; $sf; Test-Path -LiteralPath $sf
```

**成功**：印出指定資料夾上一層的 `hd-hospital-fetch`，接著 `False`。

### B-09 下載（InPrivate 視窗）

**做什麼**：`Ctrl+Shift+N` 開 InPrivate／無痕視窗 → 登入自己的 GitHub（不保持登入、不存密碼）→ v0.1.0 Release 頁 Assets 的 `Source code (zip)` 存到「下載」→ 關掉整個 InPrivate 視窗。

**成功**：「下載」裡有 `hd-hospital-fetch-0.1.0.zip`；InPrivate 視窗已關。

### B-10 解壓縮到腳本資料夾

**做什麼**：

```powershell
Expand-Archive "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip" -DestinationPath (Split-Path -Parent $sf)
Rename-Item -LiteralPath (Join-Path (Split-Path -Parent $sf) 'hd-hospital-fetch-0.1.0') 'hd-hospital-fetch'
cd -LiteralPath $sf
dir
```

再刪 zip：`Remove-Item "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip"`。`.exe` 才要的搬檔照詳細版。

**成功**：`dir` 列出 `fetch_dialysis.py`、`transcode_history.py`、`install-task.ps1` 等；提示字元是 `…\hd-hospital-fetch>`。

### B-11 解除下載標記

**做什麼**：`Get-ChildItem -Recurse | Unblock-File`；用 `.exe` 才比對雜湊。

**成功**：不印東西。

### B-12 轉碼：先預演

**做什麼**：先看大小與可用記憶體（詳細版 B-12），合計 × 4.5 不超過可用記憶體才跑：

```powershell
py transcode_history.py $dir
```

**成功**：跑完才一次印出清單；每個檔的編碼是 `cp950` 或 `utf-8`。「要轉 0 個」就跳過 B-13。🏥 1109：24 個檔全是 `utf-8`。

### B-13 轉碼：實轉

**做什麼**：

```powershell
py transcode_history.py $dir --apply
$LASTEXITCODE
```

**成功**：每個檔「已轉成 UTF-8，比對通過」、`0`；最後一行「還原：…」整行抄在手機上。

### B-14 填設定

**做什麼**：`Copy-Item config.example.json config.json`、`notepad config.json`，只改 `endpoint`（院方位址）與 `output_dir`（`<指定資料夾>`，反斜線寫兩個，先 `Set-Clipboard $dir.Replace('\', '\\')` 再貼）。

**成功**：存檔、關掉記事本。

### B-15 預演一輪

**做什麼**：

```powershell
py fetch_dialysis.py --dry-run
```

**成功**：`… 成功 回應 N 列、會寫入 N 列（預演，沒有寫任何檔）`。🏥 1109 17:35:49：回應 703 列、會寫入 703 列。**1109 做到這裡。**

### B-16 跑一輪、看結果

**做什麼**：先做兩個檢查（權限、當月檔有沒有別的程式在寫，詳細版 B-16）；再：

```powershell
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
```

看當月檔最後兩行（詳細版），再跑一次 `--once`。

**成功**：檢查是 `False`、`True`、當月檔不是幾分鐘內改過；第一輪 `0`、`"result": "ok"`、`written_rows` 等於 `response_rows`；第二輪 `寫入 0 列`。

### B-17 裝排程

**做什麼**：

```powershell
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
```

**成功**：`已建立工作 hd-hospital-fetch`、每 3 分鐘、狀態 `Ready`。

### B-18 看三輪（約 10 分鐘）

**做什麼**：每 3 分鐘貼一次：

```powershell
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
```

**成功**：三次 `LastRunTime` 往前跳、`LastTaskResult` `0`、`result` `ok`。

### B-19 教學長三件事

**做什麼**：停（`uninstall-task.ps1`）、改頻率（`install-task.ps1 -IntervalMinutes 5 -Force`）、看最近一輪（狀態檔）；指令在詳細版 B-19。

**成功**：學長自己做得出來。

### B-20 記錄

**做什麼**：照詳細版 B-20 的清單記在手機上，回去寫進私人 repo 的 `deploy/records/`（1109 是 `1109-hospital-fetch/`）。

**成功**：做到哪一步、各步結果、學長的決定都有記。

### B-21 收工前看一眼

**做什麼**：InPrivate 視窗已關、「下載」沒留 zip 與 `.exe`、一般視窗沒登入 GitHub；🏥 **不重開機**。

**成功**：`Get-ScheduledTaskInfo -TaskName hd-hospital-fetch` 的 `LastTaskResult` 是 `0`。🏥 1109 排程沒裝，照詳細版「中途收工」收：沒有排程、zip 已刪。

## 3. 1114 為第五次進院加的三步

1114 學長答了《[院方 API 介接之二](../notes/hospital-api-fetch-methods-questions.md)》（K-2 ① 搬 C 槽、F-6 ① 只在 07:00～23:00 抓），在 B-14 與 B-15 之間加了這三步；1109 現場沒有。第五次進院改照 `AF-04`～`AF-06` 做，對照表在詳細版第 4 節。

### B-14a 搬到 C 槽

**做什麼**：確認排程沒裝、沒有 Python 在跑、C 槽沒有 `API_Fetch`；`robocopy` 整個 `API_Fetch` 到 `C:\API_Fetch`、比對檔數與位元組、舊的改名成 `API_Fetch_搬到C槽_MMDD`；換成新位置：

```powershell
$dir = 'C:\API_Fetch\IDH_interface'; $sf = 'C:\API_Fetch\hd-hospital-fetch'; cd -LiteralPath $sf; dir config.json
```

**成功**：robocopy「失敗」全是 `0`、結束碼 `1`；兩邊檔數與位元組一模一樣；列出 `config.json`。

### B-14b 換成 v0.3.0

**做什麼**：InPrivate 視窗下載 v0.3.0 的 `Source code (zip)`，只把 `fetch_dialysis.py` 複製進 `$sf`（指令在詳細版）。

**成功**：`py fetch_dialysis.py --version` 印 `0.3.0`。

### B-14c 改設定三處

**做什麼**：`output_dir` 改成 `C:\\API_Fetch\\IDH_interface`、`status_file` 改成 `C:\\API_Fetch\\IDH_interface\\fetch-status.json`、加 `"fetch_hours": "07:00-23:00"`。

**成功**：

```powershell
Get-Content -Raw -Encoding UTF8 config.json | ConvertFrom-Json | Select-Object output_dir, status_file, fetch_hours, dedup, line_format
```

印出 `C:\API_Fetch\IDH_interface`、`C:\API_Fetch\IDH_interface\fetch-status.json`、`07:00-23:00`、`row`、`segment`。

## 4. 退回

學長說不要了：停排程、歷史 txt 回到轉碼前、刪腳本——照《[院方 API 抓取腳本的維運（第 2 份，FS-10～FS-19 與一頁速查）](ref-fetch-script-2.md)》的退回（FS-16～FS-19）。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](index.md)
