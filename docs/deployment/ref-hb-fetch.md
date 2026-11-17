# 檢驗資料（hb）抓取（未採用）

> **狀態：未採用，保留為參考。** 1111 學長答《[院方 API 介接之二](../notes/hospital-api-fetch-methods-questions.md)》A-5：`hb_online_v2.py` 不用這邊處理，I 組題目跟著刪（《[之二之一](../notes/hospital-api-fetch-methods-questions-answered.md)》第 3.4、3.5 節）。這一份從沒在院內照做過：1116 第五次進院做完抓取腳本直接接本系統，`hb\` 資料夾沒帶進主機、`hd-hospital-fetch-hb` 排程沒裝。日後真的要接再照做，先重問之二之一第 3.4 節的 I 組。
>
> 改寫自舊第十九冊之三（檢驗資料（hb）抓取的安裝，新手版；1110 依《[院方 API 介接之四](../notes/hospital-api-fetch-methods-next-visit-plan.md)》第 4、5 節與 `hd-hospital-fetch` v0.2.0 實際的輸出寫成）全部，加舊第十九冊之一第 3 節（`hb` 現況盤點，1109 晚上加）。編號：`BH-xx`。
>
> 透析清單那支（`fetch_dialysis.py`）的出錯總表、速查、換版與退回在《[院方 API 抓取腳本的維運](ref-fetch-script.md)》。

> **這一份回答一件事：在同一台主機上，讓學長的檢驗資料程式（`hb_online_v2.py`）每 6 小時自己跑一次，並且看得到每一輪的結果。** 當時排在透析清單 B-19 之後、B-20 之前（《[第四次進院（1109）· 放上院方 API 抓取腳本](visit-4-api.md)》）：透析清單先做完，再做這一份。學長的程式**原樣不改**，排程、狀態檔、只讀檢查、病人清單都是外面包的一層（`hd-hospital-fetch` 的 `hb\` 資料夾）。
>
> 每一步都有「會看到」與「不對的話」。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。** 這一份停下來不影響透析清單。

> **公開範圍**：文件站是公開的。院方的檢驗 API 位址、帳號一律不寫進這一份；用 `<Hb_API_Fetch>`、`<檢驗 API 位址>` 代稱，值記在私人 repo 的 `deploy/records/` 底下。1116 起 `<Hb_API_Fetch>` 是 `C:\API_Fetch\Hb_API_Fetch`（通用位置，可以寫）；D 槽原本的路徑照舊不寫。**`Hb_API_Fetch` 的檔不能帶出、不能拍**：每一步都只印筆數與統計，不印病歷號與檢驗值。

## 摘要

- 現況（第 0 節）：院內主機上 `hb_online_v2.py` 沒在跑，`Hb_API_Fetch` 跟著整個 `API_Fetch` 搬到 C 槽、內容不動、資料停在 11/06；它是在正式 IDH 主機上跑的
- 時間：透析清單做完後約 35 分鐘；透析清單做完已超過約 40 分鐘或學長要先走，這一份整份延後（第 6 節）
- 出發前（BH-01～BH-02）：確認看得到 Release 頁；《之四》第 3 節的六題哪些有答案
- 先看現況（BH-03）：照第 4 節查有沒有程式在跑、跑盤點；**有程式在跑就停在這裡**
- 帶進（BH-04）：InPrivate 視窗下載 Release，只把 `hb\` 搬進腳本資料夾；透析清單的檔與設定不動
- 設定（BH-05）：`<Hb_API_Fetch>` 已有實際的 `config.json` 就照用；病人清單沒有就從透析清單當月檔產生
- 檢查與預演（BH-06～BH-07）：只讀檢查既有留底，有壞行就停；在留底的複本上跑一輪
- 正式（BH-08～BH-10）：跑一輪 → 裝排程（`hd-hospital-fetch-hb`，每 360 分鐘）→ 手動觸發一次 → 教學長怎麼停、怎麼看
- 第 4 節是 `hb` 現況盤點（只讀、只印統計，腳本整段在本節）；退回在第 5 節；延後條件在第 6 節；狀態檔的 `reason` 對照在第 7 節

## 0. 現況（1117）

- 1111 學長答 A-5 不用這邊處理；《之四》的 `hb` 部分（第 1～6 節的 `hb`、T-7～T-14 做好的 `hb/`）與這一份都不做，保留為規劃紀錄
- 院內主機：1116 第五次進院，學長的 `hb_online_v2.py` 與它的資料（`Hb_API_Fetch`）跟著整個 `API_Fetch` 搬到 `C:\API_Fetch`、內容不動；AF-03 查過沒有別的排程指著 `API_Fetch`、沒有 Python 在跑；資料停在 11/06，跟學長 1114 答的「這台沒有別的程式在寫」一致，它是在正式 IDH 主機上跑的，所以不必特別通知學長（《[第五次進院紀錄（1116，讀檔上線、平板與交接待補）](record-5-1116.md)》SR-03、SR-04）
- 院內主機的 `C:\API_Fetch\hd-hospital-fetch` 是 1109 帶進的 v0.1.0，1116 只把 `fetch_dialysis.py` 換成 v0.3.0；**沒有 `hb\` 資料夾**（v0.1.0 還沒有 `hb\`）
- 程式：`hb\` 從 `hd-hospital-fetch` v0.2.0 起有；v0.3.0 只改透析清單那支，`hb\` 與 v0.2.0 完全相同，下面的指令寫 v0.2.0，用 v0.3.0 的 Release 也可以（zip 名稱與解出的資料夾名稱跟著改成 `0.3.0`）
- 本系統：迭代 32 的檢驗資料讀檔程式留著，院內 `.env` 的 `HD_LAB_DIR` 留空、不掛；要讀時 I-9、I-12、I-13 再問

## 1. 開始前先懂的四件事

1. **學長的程式做什麼**：讀病人清單（`active_patients.txt`），一位一位問院方檢驗 API，把**沒看過的**檢驗結果一筆一行附加到 `<Hb_API_Fetch>\hospital_dataset\raw_txt\YYYY-MM.txt`，再重建同月的 `csv\YYYY-MM.csv`。同一筆內容不會重複寫；值改過就算新的一筆
2. **外面包的那一層（`run_hb.py`）多做的**：先切到 `<Hb_API_Fetch>` 再跑（學長的程式用相對路徑）；每輪覆寫 `hb-status.json`（新／重複／空／錯誤四個數與錯誤種類）；學長程式印的字存進 `hb-logs\`（留最近 30 輪）；同時只跑一輪。這三樣都寫在 `<Hb_API_Fetch>` 裡
3. **它會動到的檔**：`<Hb_API_Fetch>` 裡的 `hospital_dataset\raw_txt\`（只附加）、`hospital_dataset\csv\`（重建）、`hb-status.json`、`hb-logs\`、`hb-run.lock`（跑的時候才有）；BH-05 產生病人清單的話多一個 `active_patients.txt`。透析清單的指定資料夾、腳本資料夾裡的透析清單檔都不動
4. **三個變數**：透析清單的 `$dir`（指定資料夾）、`$sf`（腳本資料夾），BH-03 再設 `$hb`（`<Hb_API_Fetch>`）。PowerShell 視窗關掉就會不見；1116 起三個都在 C 槽，重開後直接貼：

```powershell
$dir = 'C:\API_Fetch\IDH_interface'; $sf = 'C:\API_Fetch\hd-hospital-fetch'; $hb = 'C:\API_Fetch\Hb_API_Fetch'
```

結束碼：每跑完一支打 `$LASTEXITCODE`，`0` 成功（或跳過）、`1` 有東西失敗、`2` 參數、設定或留底有問題。

## 2. 出發前

### BH-01 確認 Release 頁

在自己的電腦登入 GitHub，開啟 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.2.0`。

- **會看到**：v0.2.0 與 `Source code (zip)`；顯示 404 是帳號不對

### BH-02 哪些題目有答案

對《[之四](../notes/hospital-api-fetch-methods-next-visit-plan.md)》第 3 節的六題（I-8、I-10、I-2、I-11、A-5、I-6），在現場筆記寫下哪些學長已經答了、答案是什麼；I-8 的位址記在私人紀錄，不寫在筆記的公開處。

- I-8 沒答也可以出發：BH-03 的盤點看得到主機上有沒有實際的設定
- 1111 起 A-5 答「不用這邊處理」、I 組刪；要做之前先重問

## 3. 現場步驟

### BH-03 看有沒有程式在跑、跑盤點（約 10 分鐘）

照第 4 節做 4.1～4.3（第一行就是設 `$hb`）。這一步只讀、不寫任何檔。

- **會看到**：4.1 三行的結果；4.3 的五段輸出
- 4.1 找到工作，或 `CommandLine` 有 `hb_online`：**停**。主機上已有程式在寫，記下工作名稱與狀態，問學長；盤點照樣跑完、第 5 段照樣抄
- 4.3 第 1 段 `範本佔位字還在： False`：主機上有實際的設定，BH-05 照用
- 4.3 第 2 段有「壞」：先記下，BH-06 會再用學長的同一套檢查看一次
- 第 5 段整段抄在紙上（不含病人資料）

### BH-04 帶進 `hb\`（約 5 分鐘）

1. 開 Edge 或 Chrome 按 `Ctrl+Shift+N` 開 InPrivate（Chrome 叫無痕）視窗、登入自己的 GitHub（不勾「保持登入」、不存密碼），到 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.2.0` 的「Assets」下載 `Source code (zip)`，存到「下載」、檔名不改；**關掉整個 InPrivate 視窗**
2. 在 PowerShell 貼（先確認腳本資料夾裡還沒有 `hb`，有的話第一行會印 `True`，停）：

```powershell
Test-Path -LiteralPath (Join-Path $sf 'hb')
Expand-Archive "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.2.0.zip" -DestinationPath $env:TEMP -Force
Copy-Item -Recurse -LiteralPath (Join-Path $env:TEMP 'hd-hospital-fetch-0.2.0\hb') -Destination $sf
Remove-Item -Recurse -Force -LiteralPath (Join-Path $env:TEMP 'hd-hospital-fetch-0.2.0')
Remove-Item "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.2.0.zip"
cd -LiteralPath (Join-Path $sf 'hb')
Get-ChildItem | Unblock-File
dir
```

- **會看到**：第一行 `False`；最後 `dir` 列出 `hb_online_v2.py`、`collector_common.py`、`config.example.json`、`run_hb.py`、`check_hb_store.py`、`make_patients.py`、`install-hb-task.ps1`、`uninstall-hb-task.ps1`、`README.md`；提示字元變成 `PS …\hd-hospital-fetch\hb>`
- 只搬 `hb`：透析清單的 `fetch_dialysis.py`、`config.json`、`state\` 都不動

確認學長的兩個檔是原樣：

```powershell
(Get-FileHash .\hb_online_v2.py, .\collector_common.py -Algorithm SHA256).Hash
```

- **會看到**：`7ABFE3D6E2D00FEB…` 開頭與 `4555AEC809E29C7B…` 開頭兩行
- **不對的話**：雜湊不同 → 刪掉 `hb` 資料夾（`cd ..; Remove-Item -Recurse -Force .\hb`），回第 1 點重新下載；還是不同就停

### BH-05 設定與病人清單（約 5 分鐘）

先看 `<Hb_API_Fetch>` 有什麼：

```powershell
Test-Path -LiteralPath (Join-Path $hb 'config.json')
Test-Path -LiteralPath (Join-Path $hb 'hospital_dataset\active_patients.txt')
```

**設定檔**：

- 第一行 `True`，而且 BH-03 盤點寫 `範本佔位字還在： False`：照用，**不改學長的設定**
- 第一行 `False`，或佔位字還在：跟學長確認位址（I-8）後，複製範例並用記事本改 `url_template` 的 `https://REPLACE-WITH-APPROVED-API.example/api/` 那一段，`{MedicalId}_{start_date}_{end_date}` 三個佔位符照留：

```powershell
Copy-Item .\config.example.json (Join-Path $hb 'config.json')   # 只在沒有 config.json 時做
notepad (Join-Path $hb 'config.json')
```

- 位址是 `http` 開頭：學長的程式預設只打 `https`。**學長說可以**才把 `"allow_approved_http": false` 改成 `true`；學長沒說可以 → 停，`hb` 延後（第 6 節）
- 沒有位址可填 → 停，`hb` 延後

**病人清單**：

- 第二行 `True`：照用（I-2 問誰維護）
- 第二行 `False`：從透析清單的當月檔產生。先預演，只印人數：

```powershell
$m = Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt')
py -I .\make_patients.py --dry-run $m
```

- **會看到**：`預演，會寫入 N 人（讀了 1 個檔、… 段、… 列；略過不是純數字的病歷號 0 個、讀不了的行 0 行）`；當月檔很大時要等一兩分鐘
- 人數跟學長確認合理（大約是中心這個月透析的人數），再寫：

```powershell
py -I .\make_patients.py --out (Join-Path $hb 'hospital_dataset\active_patients.txt') $m
```

- **會看到**：`已寫入 N 人（…）`；`$LASTEXITCODE` 是 `0`。記下「病人清單是 BH-05 產生的」（退回時要刪）
- **不對的話**：`一個病歷號都沒取到：病歷號看起來加密過，不能用來查檢驗` → 停，透析清單的留底有加密，不能拿來查檢驗；`--out 所在的資料夾不存在` → `<Hb_API_Fetch>` 底下沒有 `hospital_dataset`，停，問學長留底放在哪

### BH-06 只讀檢查既有留底（約 2 分鐘）

**一定要做，BH-03 的盤點沒有「壞」也要做**：盤點只看每行是不是 JSON；學長的程式還會檢查病歷號、日期格式與有沒有不認得的欄位，任何一行過不了就整支停。這一支用學長的同一套檢查，只讀、不印內容。

```powershell
py -I .\check_hb_store.py $hb
$LASTEXITCODE
```

- **會看到**：每個月份檔一行，例如 `2026-10.txt：420 行（空行 0），壞 0`；最後 `沒有壞行：學長的程式讀得過全部 N 個月份檔`；`$LASTEXITCODE` 是 `0`
- `raw_txt 底下沒有 YYYY-MM.txt（學長的程式會從空的留底開始）`：還沒抓過，結束碼 `0`，往下
- `raw_txt 底下另有 N 個不是 YYYY-MM.txt 的檔或資料夾（學長的程式不讀，不影響）`：不影響，往下
- **不對的話**：結束碼 `1`、最後寫 `學長的程式啟動時會停在 … 第 N 行。先整個資料夾備份，交學長處理；這次 hb 不往下做`：**停**。把整個 `hospital_dataset` 交學長處理（不帶出、不修），這次 `hb` 延後；把印出的檔名、行號與原因抄下來（不含病人資料）。結束碼 `2`（`找不到 raw_txt 資料夾；確認給的是 Hb_API_Fetch 或 hospital_dataset`）：給的資料夾不對，確認 `$hb`

### BH-07 預演（約 5 分鐘）

在留底的複本上跑一輪，正式的留底與狀態檔都不動。預演一樣會打院方 API（只讀）。

```powershell
Copy-Item -Recurse -LiteralPath (Join-Path $hb 'hospital_dataset') -Destination (Join-Path $hb 'hospital_dataset_rehearsal')
py -I .\run_hb.py --config (Join-Path $hb 'config.json') --output-dir hospital_dataset_rehearsal --status (Join-Path $hb 'hb-status-rehearsal.json')
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $hb 'hb-status-rehearsal.json')
```

- **會看到**：一行 `… ok 病人 N 新 … 重複 … 空 … 錯誤 0`；`$LASTEXITCODE` 是 `0`；狀態檔裡 `"result": "ok"`、`"error_kinds": {}`
- 四個數怎麼看：`新` 是這一輪新寫入的筆數（第一次跑會接近人數）、`重複` 是跟既有留底完全相同的、`空` 是那位病人在期間內沒有檢驗值、`錯誤` 是查詢失敗
- 人數多時要等：一位最久等 `timeout_seconds`（範例 15 秒）
- **不對的話**：
  - `failed` 加 `設定檔的 url_template 還是範本的佔位字…` → 回 BH-05
  - `failed` 加 `每一位都查詢失敗`，或 `partial` 而 `錯誤` 超過人數的一半 → 停；把 `error_kinds` 抄下來（第 7 節對照），問學長
  - `partial` 而只有少數幾位錯誤 → 抄下 `error_kinds`，學長決定要不要往下
  - 主控台或狀態檔出現病歷號、網址或檢驗值 → 停

看完刪掉複本（裡面有病人資料，不留在主機上多一份）：

```powershell
Remove-Item -Recurse -Force -LiteralPath (Join-Path $hb 'hospital_dataset_rehearsal'), (Join-Path $hb 'hb-status-rehearsal.json')
```

### BH-08 正式跑一輪（約 3 分鐘）

```powershell
py -I .\run_hb.py --config (Join-Path $hb 'config.json')
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $hb 'hb-status.json')
```

- **會看到**：與 BH-07 相近的一行與狀態檔；`"last_success_at"` 是剛剛的時間
- 再跑一次：`新 0`（剛好有新檢驗就是幾筆）、其餘算 `重複` 或 `空`
- **不對的話**：同 BH-07

### BH-09 裝排程、手動觸發一次（約 3 分鐘）

```powershell
powershell -ExecutionPolicy Bypass -File .\install-hb-task.ps1 -Config (Join-Path $hb 'config.json')
```

- **會看到**：

```text
已建立工作 hd-hospital-fetch-hb
  帳號：<電腦名稱>\<帳號>（只在使用者登入時執行）
  頻率：每 360 分鐘，第一次在 360 分鐘後
  執行：…pythonw.exe "…\hd-hospital-fetch\hb\run_hb.py" --config "<Hb_API_Fetch>\config.json"
  工作目錄：<Hb_API_Fetch>
  狀態：Ready
馬上跑一次：Start-ScheduledTask -TaskName hd-hospital-fetch-hb；看結果：Get-Content -Encoding UTF8 "<Hb_API_Fetch>\hb-status.json"
```

- 透析清單的工作 `hd-hospital-fetch` 不受影響；本腳本拒用那個名稱（`這是透析清單的工作名稱；hb 要用另一個名稱（預設 hd-hospital-fetch-hb）`）
- **不對的話**：紅字寫「執行原則」或「無法載入」→ 停，學長決定（院方的群組原則擋了 PowerShell 腳本，與透析清單裝排程時相同）；寫「已經有一個叫 hd-hospital-fetch-hb 的工作；要換掉就加 -Force，要移除用 hb\uninstall-hb-task.ps1」→ 有人裝過，停

等 6 小時太久，手動觸發一次：

```powershell
Start-ScheduledTask -TaskName hd-hospital-fetch-hb
```

約 1 分鐘後（人數多就再等一下）：

```powershell
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch-hb | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content -Encoding UTF8 (Join-Path $hb 'hb-status.json')
```

- **會看到**：`LastRunTime` 是剛剛、`LastTaskResult` 是 `0`；狀態檔的 `started_at` 換成剛剛的時間、`result` 是 `ok`
- `LastTaskResult` 是 `267009`：還在跑，再等一下；`1`：有人查詢失敗，看狀態檔的 `reason` 與 `error_kinds`；`2`：設定或留底有問題，看 `reason`
- 排程跑的時候**不會跳出視窗**，這是正常的；學長的程式印的字在 `hb-logs\` 最新的那個檔
- **不對的話**：等了 5 分鐘狀態檔的 `started_at` 都沒變 → 停，照《[院方 API 抓取腳本的維運](ref-fetch-script.md)》的出錯總表查排程

### BH-10 教學長

| 要做的 | 指令（在 `<腳本資料夾>\hb` 裡打） |
|---|---|
| 停掉 | `powershell -ExecutionPolicy Bypass -File .\uninstall-hb-task.ps1` |
| 改頻率（例：12 小時） | `powershell -ExecutionPolicy Bypass -File .\install-hb-task.ps1 -Config "<Hb_API_Fetch>\config.json" -IntervalMinutes 720 -Force` |
| 看最近一輪 | `Get-Content -Encoding UTF8 "<Hb_API_Fetch>\hb-status.json"`：`result`、`reason`、四個數、`last_success_at` |
| 看學長程式印的字 | `<Hb_API_Fetch>\hb-logs\` 最新的檔 |
| 留底有壞行時 | `py -I .\check_hb_store.py "<Hb_API_Fetch>"` |

- 學長自己手動跑 `hb_online_v2.py` 之前，先停掉排程：學長的程式沒有鎖，兩支同時寫同一個資料夾會壞
- `-IntervalMinutes` 只收 30～1440

接著記錄（當時是第四次進院冊的 B-20）：除了透析清單，下面這些也記進私人紀錄：

- BH-03 第 5 段的結論、4.1 有沒有找到程式在跑
- BH-04 的雜湊對不對；BH-05 設定檔是照用還是新填、病人清單是照用還是產生的（人數）
- BH-06 每個月份檔的行數與壞行數；BH-07、BH-08、BH-09 三輪的四個數與 `error_kinds`
- 每個斷點學長怎麼決定
- 不記：病歷號、檢驗值、院方回應的內容

收工前（當時是 B-21）多看一眼：`Get-ScheduledTaskInfo -TaskName hd-hospital-fetch-hb` 的 `LastTaskResult` 是 `0`；`<Hb_API_Fetch>` 底下沒有留下 `hospital_dataset_rehearsal`；「下載」裡沒有留下 v0.2.0 的 zip。

## 4. `hb` 現況盤點（只讀、只印統計）

> 用在《[院方 API 介接之四](../notes/hospital-api-fetch-methods-next-visit-plan.md)》第 5 節第 2 步與 BH-03。1111 起不跑（A-5 答不用這邊處理，I 組題目刪了，盤點沒有要回答的題）。

`Hb_API_Fetch` 底下的檔不能帶出、不能拍，改在主機上跑這支盤點：**只讀、不寫任何檔、不印病歷號與檢驗數值**。印出來的只有筆數、日期範圍、每欄有值的次數與「數字換成 9」的樣式；第 5 段「要抄的結論」不含病人資料，抄在紙上帶回。腳本整段在本節，不靠 Release，主機有 Python 3.13 就能跑。

盤點回答 I-10（有沒有程式在跑）、I-8（端點）、I-2 前半（病人清單行數）、I-3（一次回幾筆、單位與定性寫法）、I-9（同名異欄哪個是現行的）。不印病歷號與數值：數字換成 9、中文換成〔中文〕、出現不到 3 次的樣式不列；院內規定更嚴就加 `--strict`。

### 4.1 先看有沒有程式在跑（I-10）

```powershell
$hb = Read-Host 'Hb_API_Fetch 資料夾的完整路徑'
Get-ChildItem $hb -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 15 FullName, LastWriteTime, Length
Get-ScheduledTask | Where-Object { ($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments) $($_.WorkingDirectory)" }) -match 'hb_|Hb_API' } | Select-Object TaskName, State
Get-CimInstance Win32_Process -Filter "Name LIKE 'py%'" | Select-Object ProcessId, CommandLine
```

1116 起第一行可以直接改成 `$hb = 'C:\API_Fetch\Hb_API_Fetch'`。

| 看到 | 怎麼做 |
|---|---|
| 第二行列出工作，或第三行的 `CommandLine` 有 `hb_online` | 有程式在跑：記下工作名稱與狀態，`hb` 停在這裡（第 6 節）；盤點照樣可以跑，它只讀 |
| 最新的檔在 6 小時內改過，但上面兩行都沒找到 | 可能是別台或別的帳號在寫，先問學長再往下 |
| 都沒有 | 往下 |

### 4.2 建立盤點腳本

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

### 4.3 跑

```powershell
py -I "$env:TEMP\hb_survey\hb_survey.py" $hb
```

- 後面不要接 `|`（例如 `| more`）：輸出經過管線，中文會變亂碼；太長就把視窗往上捲
- 院內規定連值的樣式（例如 `Negative`）都不能抄：最後加 ` --strict`，樣式只分成數字、數字＋後綴、比較符號＋數字、文字、其他
- 抄完刪掉：`Remove-Item -Recurse -Force "$env:TEMP\hb_survey"`（腳本本身沒有病人資料，刪掉是不留東西在主機上）
- 印 `找不到 raw_txt 的月份檔，停在這裡`：`$hb` 貼錯資料夾，或 `config.json` 的 `output_dir` 不是 `hospital_dataset`；用 4.1 第二行的清單找 `raw_txt` 在哪，`$hb` 改成它上兩層的資料夾

腳本怎麼避免印出病人資料：

- 病歷號只拿來數人數，不印
- 數字一律換成 9，`12.3` 和 `8.0` 都印成 `9.9`
- 中文換成 `〔中文〕`，只留 `陰性`、`陽性`、`弱陽性`；超過 20 字的換成 `〔長字串〕`
- 出現不到 3 次的樣式不列，併進「其他」

### 4.4 會看到（假資料的例子）

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

### 4.5 怎麼讀、抄什麼

| 段 | 看什麼 | 回答 |
|---|---|---|
| 1 | `範本佔位字還在： False` 才是實際設定；網址開頭與主機 | I-8；主機名稱抄進私人紀錄，不寫進 `docs/` |
| 1 | 病人清單的行數與最後修改時間 | I-2 前半；誰在維護要問人 |
| 2 | 每個月份檔的「壞」；有壞行，學長的程式啟動就會整支停。**這裡的「壞」只看每行是不是 JSON**，學長的程式還會擋缺病歷號、日期格式錯、有不認得的欄位的行，所以「壞 0」不代表讀得過；一律再跑 BH-06 的 `check_hb_store.py`（用學長的同一套檢查） | BH-06（有壞行就停，備份交學長） |
| 3 | 「最早抓取以前的檢驗日，每人最多 1 個」：程式開始跑以前的檢驗每人只抓到一筆，表示每次只回期間內最近一次 | I-3 |
| 4、5 | 同一項的兩個名字看「有值的最後一個月」：一個停在舊月份、另一個接著有，就是改過名，現行的是後者；兩個同時都有，是不同機台或來源 | I-9 |
| 4、5 | 樣式 `9.9 g/dL` 表示值帶單位；`Negative`、`陰性(-)` 是定性結果的寫法 | I-3 |
| 5 | 整段抄在紙上帶回，回來補進《院方 API 介接之二》 | — |

## 5. 退回

學長說「hb 不要了」時，在 `<腳本資料夾>\hb` 裡依序做；透析清單不受影響：

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall-hb-task.ps1
Remove-Item -Force -LiteralPath (Join-Path $hb 'hb-status.json') -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -LiteralPath (Join-Path $hb 'hb-logs') -ErrorAction SilentlyContinue
cd -LiteralPath $sf
Remove-Item -Recurse -Force .\hb
```

- **會看到**：`已移除工作 hd-hospital-fetch-hb（程式、設定、病人清單、留底、狀態檔、紀錄檔都沒動）`；其餘不印東西
- BH-05 產生了病人清單的話，問學長要不要留；不留就 `Remove-Item -LiteralPath (Join-Path $hb 'hospital_dataset\active_patients.txt')`
- BH-08 起寫進留底的筆數看各輪狀態檔的 `新`；那幾行每一行都有 `FetchedAt`（抓取時間），要不要刪由學長決定，這一份不動
- 學長的 `config.json`：BH-05 新填的才問學長要不要留；原本就有的不動

## 6. 什麼情況這一份延後（透析清單照做）

照《[院方 API 介接之四](../notes/hospital-api-fetch-methods-next-visit-plan.md)》第 6 節：

- 沒有位址可填（I-8 沒答，BH-03 也找不到實際設定）
- 主機上已有程式在寫 `<Hb_API_Fetch>`（BH-03）
- 既有留底有壞行（BH-06）
- 位址是 `http`，學長沒說可以（BH-05）
- 透析清單做完已超過約 40 分鐘，或學長要先走

延後時：BH-04 做了就照第 5 節移除 `hb` 資料夾，或留著（沒有排程就不會跑），跟學長說一聲；BH-03 的結論照記。

## 7. 狀態檔的 `reason` 與 `error_kinds`

訊息原文來自 `hd-hospital-fetch` 的 `hb\`（v0.2.0，v0.3.0 相同）；改了訊息要回頭核對這一節。

| 看到 | 意思 | 怎麼做 |
|---|---|---|
| `設定檔的 url_template 還是範本的佔位字，或少了 {MedicalId}、{start_date}、{end_date}` | 位址還沒填 | BH-05 |
| `找不到病人清單（設定檔的 patients_file）` | 病人清單不在設定指的位置 | BH-05 |
| `病人清單有不是純數字的病歷號` | 學長的程式不接受；不自動補零或去零 | 停，問學長 |
| `留底有壞行：YYYY-MM.txt 第 N 行損壞…（用 check_hb_store.py 看全部的壞行）` | 學長的程式讀不過既有留底 | BH-06 |
| `上一輪還沒結束` | 正常（排程與手動同時跑）；一直出現就看 `hb-run.lock` 的時間 | 鎖檔超過 3 小時（`--lock-stale-minutes` 預設 180）會自動接手 |
| `HTTP 需要院方核准後，才可在設定檔明確允許` | 位址是 `http`，設定沒開 | BH-05 |
| `逾時`、`URLError（…）` | 連不到或太慢 | 透析清單也連不到就是網路；只有這支連不到，問學長位址 |
| `HTTPError 404`、`HTTPError 500` 等 | 院方 API 回錯誤 | 抄下數字，問學長 |
| `回應不是 JSON` | 回了網頁或錯誤訊息 | 同上 |
| `有未知欄位，需確認 Schema 更新（不自動丟棄）` | 院方多了欄位，學長的程式拒收 | 停，問學長（I-9） |
| `回傳 MedicalId 與查詢不一致`、`回傳日期不在查詢區間內`、`未知的 API 回應格式（無法判定是否沒資料）` | 院方回的跟問的對不上 | 抄下次數，問學長 |
| `每一位都查詢失敗（種類見 error_kinds）` | 全部的人都查不到 | 停；抄 `error_kinds`，問學長（BH-07） |
| `學長的程式中途停了（…）` | 查到一半整支停（例如重建 CSV 時讀不過留底） | 看 `hb-logs\` 最新的檔，停 |
| 主控台 `… failed 找不到設定檔所在的資料夾` | `--config` 指到不存在的資料夾，連狀態檔都不寫 | 確認 `$hb` |
| 主控台 `狀態檔寫不了：…` | 狀態檔所在的資料夾寫不進去 | 看權限與磁碟空間；問學長 |

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
