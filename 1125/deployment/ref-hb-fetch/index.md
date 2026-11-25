# 檢驗資料（hb）抓取（未採用）

> **狀態：未採用，保留為參考。** 1111 學長答《[院方 API 介接之二](https://94sh09sh19sh.github.io/hd-docs/1125/notes/hospital-api-fetch-methods-questions/index.md)》A-5：`hb_online_v2.py` 不用這邊處理，I 組題目跟著刪（《[之二之一](https://94sh09sh19sh.github.io/hd-docs/1125/notes/hospital-api-fetch-methods-questions-answered/index.md)》第 3.4、3.5 節）。這一份從沒在院內照做過：1116 第五次進院做完抓取腳本直接接本系統，`hb\` 資料夾沒帶進主機、`hd-hospital-fetch-hb` 排程沒裝。日後真的要接再照做，先重問之二之一第 3.4 節的 I 組。
>
> 改寫自舊第十九冊之三（檢驗資料（hb）抓取的安裝，新手版；1110 依《[院方 API 介接之四](https://94sh09sh19sh.github.io/hd-docs/1125/notes/hospital-api-fetch-methods-next-visit-plan/index.md)》第 4、5 節與 `hd-hospital-fetch` v0.2.0 實際的輸出寫成）全部，加舊第十九冊之一第 3 節（`hb` 現況盤點，1109 晚上加）。編號：`BH-xx`。
>
> 透析清單那支（`fetch_dialysis.py`）的出錯總表、速查、換版與退回在《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-fetch-script/index.md)》。
>
> 這一份分兩份加一份子文件：這一份是第 0～3 節（現況、開始前先懂的四件事、出發前、現場步驟 BH-01～BH-10）；第 4 節 `hb` 現況盤點在子文件《[檢驗資料（hb）抓取（未採用）之一：現況盤點](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-hb-fetch-survey/index.md)》；第 5～7 節（退回、延後條件、狀態檔的 `reason` 與 `error_kinds`）在《[第 2 份](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-hb-fetch-2/index.md)》。
>
> **這一份回答一件事：在同一台主機上，讓學長的檢驗資料程式（`hb_online_v2.py`）每 6 小時自己跑一次，並且看得到每一輪的結果。** 當時排在透析清單 B-19 之後、B-20 之前（《[第四次進院（1109）· 放上院方 API 抓取腳本](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/visit-4-api/index.md)》）：透析清單先做完，再做這一份。學長的程式**原樣不改**，排程、狀態檔、只讀檢查、病人清單都是外面包的一層（`hd-hospital-fetch` 的 `hb\` 資料夾）。
>
> 每一步都有「會看到」與「不對的話」。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。** 這一份停下來不影響透析清單。
>
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
- 第 4 節 `hb` 現況盤點（只讀、只印統計，腳本整段在那一節）在子文件《之一》；退回在第 5 節、延後條件在第 6 節、狀態檔的 `reason` 對照在第 7 節，都在《第 2 份》

## 0. 現況（1117）

- 1111 學長答 A-5 不用這邊處理；《之四》的 `hb` 部分（第 1～6 節的 `hb`、T-7～T-14 做好的 `hb/`）與這一份都不做，保留為規劃紀錄
- 院內主機：1116 第五次進院，學長的 `hb_online_v2.py` 與它的資料（`Hb_API_Fetch`）跟著整個 `API_Fetch` 搬到 `C:\API_Fetch`、內容不動；AF-03 查過沒有別的排程指著 `API_Fetch`、沒有 Python 在跑；資料停在 11/06，跟學長 1114 答的「這台沒有別的程式在寫」一致，它是在正式 IDH 主機上跑的，所以不必特別通知學長（《[第五次進院紀錄（1116，讀檔上線、平板與交接待補）](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/record-5-1116/index.md)》SR-03、SR-04）
- 院內主機的 `C:\API_Fetch\hd-hospital-fetch` 是 1109 帶進的 v0.1.0，1116 只把 `fetch_dialysis.py` 換成 v0.3.0；**沒有 `hb\` 資料夾**（v0.1.0 還沒有 `hb\`）
- 程式：`hb\` 從 `hd-hospital-fetch` v0.2.0 起有；v0.3.0 只改透析清單那支，`hb\` 與 v0.2.0 完全相同，下面的指令寫 v0.2.0，用 v0.3.0 的 Release 也可以（zip 名稱與解出的資料夾名稱跟著改成 `0.3.0`）
- 本系統：迭代 32 的檢驗資料讀檔程式留著，院內 `.env` 的 `HD_LAB_DIR` 留空、不掛；要讀時 I-9、I-12、I-13 再問

## 1. 開始前先懂的四件事

1. **學長的程式做什麼**：讀病人清單（`active_patients.txt`），一位一位問院方檢驗 API，把**沒看過的**檢驗結果一筆一行附加到 `<Hb_API_Fetch>\hospital_dataset\raw_txt\YYYY-MM.txt`，再重建同月的 `csv\YYYY-MM.csv`。同一筆內容不會重複寫；值改過就算新的一筆
1. **外面包的那一層（`run_hb.py`）多做的**：先切到 `<Hb_API_Fetch>` 再跑（學長的程式用相對路徑）；每輪覆寫 `hb-status.json`（新／重複／空／錯誤四個數與錯誤種類）；學長程式印的字存進 `hb-logs\`（留最近 30 輪）；同時只跑一輪。這三樣都寫在 `<Hb_API_Fetch>` 裡
1. **它會動到的檔**：`<Hb_API_Fetch>` 裡的 `hospital_dataset\raw_txt\`（只附加）、`hospital_dataset\csv\`（重建）、`hb-status.json`、`hb-logs\`、`hb-run.lock`（跑的時候才有）；BH-05 產生病人清單的話多一個 `active_patients.txt`。透析清單的指定資料夾、腳本資料夾裡的透析清單檔都不動
1. **三個變數**：透析清單的 `$dir`（指定資料夾）、`$sf`（腳本資料夾），BH-03 再設 `$hb`（`<Hb_API_Fetch>`）。PowerShell 視窗關掉就會不見；1116 起三個都在 C 槽，重開後直接貼：

```
$dir = 'C:\API_Fetch\IDH_interface'; $sf = 'C:\API_Fetch\hd-hospital-fetch'; $hb = 'C:\API_Fetch\Hb_API_Fetch'
```

結束碼：每跑完一支打 `$LASTEXITCODE`，`0` 成功（或跳過）、`1` 有東西失敗、`2` 參數、設定或留底有問題。

## 2. 出發前

### BH-01 確認 Release 頁

在自己的電腦登入 GitHub，開啟 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.2.0`。

- **會看到**：v0.2.0 與 `Source code (zip)`；顯示 404 是帳號不對

### BH-02 哪些題目有答案

對《[之四](https://94sh09sh19sh.github.io/hd-docs/1125/notes/hospital-api-fetch-methods-next-visit-plan/index.md)》第 3 節的六題（I-8、I-10、I-2、I-11、A-5、I-6），在現場筆記寫下哪些學長已經答了、答案是什麼；I-8 的位址記在私人紀錄，不寫在筆記的公開處。

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
1. 在 PowerShell 貼（先確認腳本資料夾裡還沒有 `hb`，有的話第一行會印 `True`，停）：

```
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

```
(Get-FileHash .\hb_online_v2.py, .\collector_common.py -Algorithm SHA256).Hash
```

- **會看到**：`7ABFE3D6E2D00FEB…` 開頭與 `4555AEC809E29C7B…` 開頭兩行
- **不對的話**：雜湊不同 → 刪掉 `hb` 資料夾（`cd ..; Remove-Item -Recurse -Force .\hb`），回第 1 點重新下載；還是不同就停

### BH-05 設定與病人清單（約 5 分鐘）

先看 `<Hb_API_Fetch>` 有什麼：

```
Test-Path -LiteralPath (Join-Path $hb 'config.json')
Test-Path -LiteralPath (Join-Path $hb 'hospital_dataset\active_patients.txt')
```

**設定檔**：

- 第一行 `True`，而且 BH-03 盤點寫 `範本佔位字還在： False`：照用，**不改學長的設定**
- 第一行 `False`，或佔位字還在：跟學長確認位址（I-8）後，複製範例並用記事本改 `url_template` 的 `https://REPLACE-WITH-APPROVED-API.example/api/` 那一段，`{MedicalId}_{start_date}_{end_date}` 三個佔位符照留：

```
Copy-Item .\config.example.json (Join-Path $hb 'config.json')   # 只在沒有 config.json 時做
notepad (Join-Path $hb 'config.json')
```

- 位址是 `http` 開頭：學長的程式預設只打 `https`。**學長說可以**才把 `"allow_approved_http": false` 改成 `true`；學長沒說可以 → 停，`hb` 延後（第 6 節）
- 沒有位址可填 → 停，`hb` 延後

**病人清單**：

- 第二行 `True`：照用（I-2 問誰維護）
- 第二行 `False`：從透析清單的當月檔產生。先預演，只印人數：

```
$m = Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt')
py -I .\make_patients.py --dry-run $m
```

- **會看到**：`預演，會寫入 N 人（讀了 1 個檔、… 段、… 列；略過不是純數字的病歷號 0 個、讀不了的行 0 行）`；當月檔很大時要等一兩分鐘
- 人數跟學長確認合理（大約是中心這個月透析的人數），再寫：

```
py -I .\make_patients.py --out (Join-Path $hb 'hospital_dataset\active_patients.txt') $m
```

- **會看到**：`已寫入 N 人（…）`；`$LASTEXITCODE` 是 `0`。記下「病人清單是 BH-05 產生的」（退回時要刪）
- **不對的話**：`一個病歷號都沒取到：病歷號看起來加密過，不能用來查檢驗` → 停，透析清單的留底有加密，不能拿來查檢驗；`--out 所在的資料夾不存在` → `<Hb_API_Fetch>` 底下沒有 `hospital_dataset`，停，問學長留底放在哪

### BH-06 只讀檢查既有留底（約 2 分鐘）

**一定要做，BH-03 的盤點沒有「壞」也要做**：盤點只看每行是不是 JSON；學長的程式還會檢查病歷號、日期格式與有沒有不認得的欄位，任何一行過不了就整支停。這一支用學長的同一套檢查，只讀、不印內容。

```
py -I .\check_hb_store.py $hb
$LASTEXITCODE
```

- **會看到**：每個月份檔一行，例如 `2026-10.txt：420 行（空行 0），壞 0`；最後 `沒有壞行：學長的程式讀得過全部 N 個月份檔`；`$LASTEXITCODE` 是 `0`
- `raw_txt 底下沒有 YYYY-MM.txt（學長的程式會從空的留底開始）`：還沒抓過，結束碼 `0`，往下
- `raw_txt 底下另有 N 個不是 YYYY-MM.txt 的檔或資料夾（學長的程式不讀，不影響）`：不影響，往下
- **不對的話**：結束碼 `1`、最後寫 `學長的程式啟動時會停在 … 第 N 行。先整個資料夾備份，交學長處理；這次 hb 不往下做`：**停**。把整個 `hospital_dataset` 交學長處理（不帶出、不修），這次 `hb` 延後；把印出的檔名、行號與原因抄下來（不含病人資料）。結束碼 `2`（`找不到 raw_txt 資料夾；確認給的是 Hb_API_Fetch 或 hospital_dataset`）：給的資料夾不對，確認 `$hb`

### BH-07 預演（約 5 分鐘）

在留底的複本上跑一輪，正式的留底與狀態檔都不動。預演一樣會打院方 API（只讀）。

```
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

```
Remove-Item -Recurse -Force -LiteralPath (Join-Path $hb 'hospital_dataset_rehearsal'), (Join-Path $hb 'hb-status-rehearsal.json')
```

### BH-08 正式跑一輪（約 3 分鐘）

```
py -I .\run_hb.py --config (Join-Path $hb 'config.json')
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $hb 'hb-status.json')
```

- **會看到**：與 BH-07 相近的一行與狀態檔；`"last_success_at"` 是剛剛的時間
- 再跑一次：`新 0`（剛好有新檢驗就是幾筆）、其餘算 `重複` 或 `空`
- **不對的話**：同 BH-07

### BH-09 裝排程、手動觸發一次（約 3 分鐘）

```
powershell -ExecutionPolicy Bypass -File .\install-hb-task.ps1 -Config (Join-Path $hb 'config.json')
```

- **會看到**：

```
已建立工作 hd-hospital-fetch-hb
  帳號：<電腦名稱>\<帳號>（只在使用者登入時執行）
  頻率：每 360 分鐘，第一次在 360 分鐘後
  執行：…pythonw.exe "…\hd-hospital-fetch\hb\run_hb.py" --config "<Hb_API_Fetch>\config.json"
  工作目錄：<Hb_API_Fetch>
  狀態：Ready
馬上跑一次：Start-ScheduledTask -TaskName hd-hospital-fetch-hb；看結果：Get-Content -Encoding UTF8 "<Hb_API_Fetch>\hb-status.json"
```

- 透析清單的工作 `hd-hospital-fetch` 不受影響；本腳本拒用那個名稱（`這是透析清單的工作名稱；hb 要用另一個名稱（預設 hd-hospital-fetch-hb）`）
- **不對的話**：紅字寫「執行原則」或「無法載入」→ 停，學長決定（院方的群組原則擋了 PowerShell 腳本，與透析清單裝排程時相同）；寫「已經有一個叫 hd-hospital-fetch-hb 的工作；要換掉就加 -Force，要移除用 hb\\uninstall-hb-task.ps1」→ 有人裝過，停

等 6 小時太久，手動觸發一次：

```
Start-ScheduledTask -TaskName hd-hospital-fetch-hb
```

約 1 分鐘後（人數多就再等一下）：

```
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch-hb | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content -Encoding UTF8 (Join-Path $hb 'hb-status.json')
```

- **會看到**：`LastRunTime` 是剛剛、`LastTaskResult` 是 `0`；狀態檔的 `started_at` 換成剛剛的時間、`result` 是 `ok`
- `LastTaskResult` 是 `267009`：還在跑，再等一下；`1`：有人查詢失敗，看狀態檔的 `reason` 與 `error_kinds`；`2`：設定或留底有問題，看 `reason`
- 排程跑的時候**不會跳出視窗**，這是正常的；學長的程式印的字在 `hb-logs\` 最新的那個檔
- **不對的話**：等了 5 分鐘狀態檔的 `started_at` 都沒變 → 停，照《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-fetch-script-errors/index.md)》的出錯總表查排程

### BH-10 教學長

| 要做的                | 指令（在 `<腳本資料夾>\hb` 裡打）                                                                                                 |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 停掉                  | `powershell -ExecutionPolicy Bypass -File .\uninstall-hb-task.ps1`                                                                |
| 改頻率（例：12 小時） | `powershell -ExecutionPolicy Bypass -File .\install-hb-task.ps1 -Config "<Hb_API_Fetch>\config.json" -IntervalMinutes 720 -Force` |
| 看最近一輪            | `Get-Content -Encoding UTF8 "<Hb_API_Fetch>\hb-status.json"`：`result`、`reason`、四個數、`last_success_at`                       |
| 看學長程式印的字      | `<Hb_API_Fetch>\hb-logs\` 最新的檔                                                                                                |
| 留底有壞行時          | `py -I .\check_hb_store.py "<Hb_API_Fetch>"`                                                                                      |

- 學長自己手動跑 `hb_online_v2.py` 之前，先停掉排程：學長的程式沒有鎖，兩支同時寫同一個資料夾會壞
- `-IntervalMinutes` 只收 30～1440

接著記錄（當時是第四次進院冊的 B-20）：除了透析清單，下面這些也記進私人紀錄：

- BH-03 第 5 段的結論、4.1 有沒有找到程式在跑
- BH-04 的雜湊對不對；BH-05 設定檔是照用還是新填、病人清單是照用還是產生的（人數）
- BH-06 每個月份檔的行數與壞行數；BH-07、BH-08、BH-09 三輪的四個數與 `error_kinds`
- 每個斷點學長怎麼決定
- 不記：病歷號、檢驗值、院方回應的內容

收工前（當時是 B-21）多看一眼：`Get-ScheduledTaskInfo -TaskName hd-hospital-fetch-hb` 的 `LastTaskResult` 是 `0`；`<Hb_API_Fetch>` 底下沒有留下 `hospital_dataset_rehearsal`；「下載」裡沒有留下 v0.2.0 的 zip。

下一份：《[檢驗資料（hb）抓取（未採用）（第 2 份，第 5～7 節）](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-hb-fetch-2/index.md)》；第 4 節在《[…之一：現況盤點](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/ref-hb-fetch-survey/index.md)》

______________________________________________________________________

## 版本歷程

| 定版                                                                         | 日期       | 異動                                                                                                                                            |
| ---------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-hb-fetch/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/1125/deployment/index.md)
