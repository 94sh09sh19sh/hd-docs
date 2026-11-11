# 第十九冊之三 · 檢驗資料（hb）抓取的安裝（新手版）

版本：v0.1　文件狀態：草案（1110 依《[院方 API 之四](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-next-visit-plan/index.md)》第 4、5 節與 `hd-hospital-fetch` v0.2.0 實際的輸出寫成）　編號：`BH-xx`

上層手冊：《[第十九冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/19-hospital-fetch/index.md)》　出錯對照：《[第十九冊之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/19a-hospital-fetch-reference/index.md)》

> **1111 起這一冊不做。** 學長答《[院方 API 之二](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-questions/index.md)》A-5：`hb_online_v2.py` 不用這邊處理。下一次進院做完第十九冊 B-19 直接接 B-20，`hb\` 資料夾不動、`hd-hospital-fetch-hb` 排程不裝。本冊保留為紀錄，日後真的要接再照做（先重問之二之一第 3.4 節的 I 組）。
>
> **這一冊回答一件事：在同一台主機上，讓學長的檢驗資料程式（`hb_online_v2.py`）每 6 小時自己跑一次，並且看得到每一輪的結果。** 現場排在第十九冊 **B-19 之後、B-20 之前**：透析清單先做完，再做這一冊。學長的程式**原樣不改**，排程、狀態檔、只讀檢查、病人清單都是外面包的一層（`hd-hospital-fetch` 的 `hb\` 資料夾）。
>
> 每一步都有「會看到」與「不對的話」。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。** 這一冊停下來不影響透析清單，B-20、B-21 照做。
>
> **公開範圍**：文件站是公開的。院方的檢驗 API 位址、`Hb_API_Fetch` 的完整路徑、帳號一律不寫進這一冊；本冊用 `<Hb_API_Fetch>`、`<檢驗 API 位址>` 代稱，值記在私人 repo 的 `deploy/records/` 底下。**`Hb_API_Fetch` 的檔不能帶出、不能拍**：本冊每一步都只印筆數與統計，不印病歷號與檢驗值。

## 摘要

- 時間：透析清單 B-19 做完後約 35 分鐘；透析清單做完已超過約 40 分鐘或學長要先走，這一冊整本延後（第 4 節）
- 出發前（BH-01～BH-02）：確認看得到 v0.2.0 的 Release 頁；《之四》第 3 節的六題哪些有答案
- 先看現況（BH-03）：照《第十九冊之一》第 3 節查有沒有程式在跑、跑盤點；**有程式在跑就停在這裡**
- 帶進（BH-04）：InPrivate 視窗下載 v0.2.0，只把 `hb\` 搬進腳本資料夾；透析清單的檔與設定不動
- 設定（BH-05）：`<Hb_API_Fetch>` 已有實際的 `config.json` 就照用；病人清單沒有就從透析清單當月檔產生
- 檢查與預演（BH-06～BH-07）：只讀檢查既有留底，有壞行就停；在留底的複本上跑一輪
- 正式（BH-08～BH-10）：跑一輪 → 裝排程（`hd-hospital-fetch-hb`，每 360 分鐘）→ 手動觸發一次 → 教學長怎麼停、怎麼看
- 退回在第 3 節；延後條件在第 4 節；狀態檔的 `reason` 對照在第 5 節

## 0. 開始前先懂的四件事

1. **學長的程式做什麼**：讀病人清單（`active_patients.txt`），一位一位問院方檢驗 API，把**沒看過的**檢驗結果一筆一行附加到 `<Hb_API_Fetch>\hospital_dataset\raw_txt\YYYY-MM.txt`，再重建同月的 `csv\YYYY-MM.csv`。同一筆內容不會重複寫；值改過就算新的一筆
1. **外面包的那一層（`run_hb.py`）多做的**：先切到 `<Hb_API_Fetch>` 再跑（學長的程式用相對路徑）；每輪覆寫 `hb-status.json`（新／重複／空／錯誤四個數與錯誤種類）；學長程式印的字存進 `hb-logs\`（留最近 30 輪）；同時只跑一輪。這三樣都寫在 `<Hb_API_Fetch>` 裡
1. **它會動到的檔**：`<Hb_API_Fetch>` 裡的 `hospital_dataset\raw_txt\`（只附加）、`hospital_dataset\csv\`（重建）、`hb-status.json`、`hb-logs\`、`hb-run.lock`（跑的時候才有）；BH-05 產生病人清單的話多一個 `active_patients.txt`。透析清單的指定資料夾、腳本資料夾裡的透析清單檔都不動
1. **三個變數**：沿用第十九冊的 `$dir`（透析清單的指定資料夾）、`$sf`（腳本資料夾），BH-03 再設 `$hb`（`<Hb_API_Fetch>`）。PowerShell 視窗關掉就會不見；重開後先照第十九冊第 0 節第 6 點設 `$dir`、`$sf`，再貼 BH-03 的第一行設 `$hb`

結束碼沿用第十九冊第 0 節第 5 點：每跑完一支打 `$LASTEXITCODE`，`0` 成功（或跳過）、`1` 有東西失敗、`2` 參數、設定或留底有問題。

## 1. 出發前

| #     | 做什麼                                                                                                                                                                                                                                                       | 會看到／不對的話                                             |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| BH-01 | 在自己的電腦登入 GitHub，開啟 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.2.0`                                                                                                                                                                | 看到 v0.2.0 與 `Source code (zip)`；顯示 404 是帳號不對      |
| BH-02 | 對《[之四](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-next-visit-plan/index.md)》第 3 節的六題（I-8、I-10、I-2、I-11、A-5、I-6），在現場筆記寫下哪些學長已經答了、答案是什麼；I-8 的位址記在私人紀錄，不寫在筆記的公開處 | I-8 沒答也可以出發：BH-03 的盤點看得到主機上有沒有實際的設定 |

## 2. 現場步驟

### BH-03 看有沒有程式在跑、跑盤點（約 10 分鐘）

照《[第十九冊之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/19a-hospital-fetch-reference/index.md)》第 3 節做 3.1～3.3（第一行就是設 `$hb`）。這一步只讀、不寫任何檔。

- **會看到**：3.1 三行的結果；3.3 的五段輸出
- 3.1 找到工作，或 `CommandLine` 有 `hb_online`：**停**。主機上已有程式在寫，記下工作名稱與狀態，問學長；盤點照樣跑完、第 5 段照樣抄
- 3.3 第 1 段 `範本佔位字還在： False`：主機上有實際的設定，BH-05 照用
- 3.3 第 2 段有「壞」：先記下，BH-06 會再用學長的同一套檢查看一次
- 第 5 段整段抄在紙上（不含病人資料）

### BH-04 帶進 `hb\`（約 5 分鐘）

1. 照第十九冊 B-09 的做法開 InPrivate（Chrome 叫無痕）視窗、登入自己的 GitHub，到 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.2.0` 下載 `Source code (zip)`，存到「下載」、檔名不改；**關掉整個 InPrivate 視窗**
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

- 位址是 `http` 開頭：學長的程式預設只打 `https`。**學長說可以**才把 `"allow_approved_http": false` 改成 `true`；學長沒說可以 → 停，`hb` 延後（第 4 節）
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
- **不對的話**：`一個病歷號都沒取到：病歷號看起來加密過` → 停，透析清單的留底有加密，不能拿來查檢驗；`--out 所在的資料夾不存在` → `<Hb_API_Fetch>` 底下沒有 `hospital_dataset`，停，問學長留底放在哪

### BH-06 只讀檢查既有留底（約 2 分鐘）

**一定要做，BH-03 的盤點沒有「壞」也要做**：盤點只看每行是不是 JSON；學長的程式還會檢查病歷號、日期格式與有沒有不認得的欄位，任何一行過不了就整支停。這一支用學長的同一套檢查，只讀、不印內容。

```
py -I .\check_hb_store.py $hb
$LASTEXITCODE
```

- **會看到**：每個月份檔一行，例如 `2026-10.txt：420 行（空行 0），壞 0`；最後 `沒有壞行：學長的程式讀得過全部 N 個月份檔`；`$LASTEXITCODE` 是 `0`
- `raw_txt 底下沒有 YYYY-MM.txt`：還沒抓過，結束碼 `0`，往下
- **不對的話**：結束碼 `1`、最後寫 `學長的程式啟動時會停在 … 第 N 行`：**停**。把整個 `hospital_dataset` 交學長處理（不帶出、不修），這次 `hb` 延後；把印出的檔名、行號與原因抄下來（不含病人資料）。結束碼 `2`：給的資料夾不對，確認 `$hb`

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
- `failed` 加 `每一位都查詢失敗`，或 `partial` 而 `錯誤` 超過人數的一半 → 停；把 `error_kinds` 抄下來（第 5 節對照），問學長
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

- 透析清單的工作 `hd-hospital-fetch` 不受影響；本腳本拒用那個名稱
- **不對的話**：紅字寫「執行原則」或「無法載入」→ 停（同 B-17）；寫「已經有一個叫 hd-hospital-fetch-hb 的工作」→ 有人裝過，停

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
- **不對的話**：等了 5 分鐘狀態檔的 `started_at` 都沒變 → 停，照《第十九冊之一》第 1 節查排程

### BH-10 教學長

| 要做的                | 指令（在 `<腳本資料夾>\hb` 裡打）                                                                                                 |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 停掉                  | `powershell -ExecutionPolicy Bypass -File .\uninstall-hb-task.ps1`                                                                |
| 改頻率（例：12 小時） | `powershell -ExecutionPolicy Bypass -File .\install-hb-task.ps1 -Config "<Hb_API_Fetch>\config.json" -IntervalMinutes 720 -Force` |
| 看最近一輪            | `Get-Content -Encoding UTF8 "<Hb_API_Fetch>\hb-status.json"`：`result`、`reason`、四個數、`last_success_at`                       |
| 看學長程式印的字      | `<Hb_API_Fetch>\hb-logs\` 最新的檔                                                                                                |
| 留底有壞行時          | `py -I .\check_hb_store.py "<Hb_API_Fetch>"`                                                                                      |

- 學長自己手動跑 `hb_online_v2.py` 之前，先停掉排程：學長的程式沒有鎖，兩支同時寫同一個資料夾會壞

接著回第十九冊 **B-20**：除了透析清單，下面這些也記進私人紀錄：

- BH-03 第 5 段的結論、3.1 有沒有找到程式在跑
- BH-04 的雜湊對不對；BH-05 設定檔是照用還是新填、病人清單是照用還是產生的（人數）
- BH-06 每個月份檔的行數與壞行數；BH-07、BH-08、BH-09 三輪的四個數與 `error_kinds`
- 每個斷點學長怎麼決定
- 不記：病歷號、檢驗值、院方回應的內容

B-21 多看一眼：`Get-ScheduledTaskInfo -TaskName hd-hospital-fetch-hb` 的 `LastTaskResult` 是 `0`；`<Hb_API_Fetch>` 底下沒有留下 `hospital_dataset_rehearsal`；「下載」裡沒有留下 v0.2.0 的 zip。

## 3. 退回

學長說「hb 不要了」時，在 `<腳本資料夾>\hb` 裡依序做；透析清單不受影響：

```
powershell -ExecutionPolicy Bypass -File .\uninstall-hb-task.ps1
Remove-Item -Force -LiteralPath (Join-Path $hb 'hb-status.json') -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -LiteralPath (Join-Path $hb 'hb-logs') -ErrorAction SilentlyContinue
cd -LiteralPath $sf
Remove-Item -Recurse -Force .\hb
```

- **會看到**：`已移除工作 hd-hospital-fetch-hb（…都沒動）`；其餘不印東西
- BH-05 產生了病人清單的話，問學長要不要留；不留就 `Remove-Item -LiteralPath (Join-Path $hb 'hospital_dataset\active_patients.txt')`
- BH-08 起寫進留底的筆數看各輪狀態檔的 `新`；那幾行每一行都有 `FetchedAt`（抓取時間），要不要刪由學長決定，這一冊不動
- 學長的 `config.json`：BH-05 新填的才問學長要不要留；原本就有的不動

## 4. 什麼情況這一冊延後（透析清單照做）

照《[之四](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-next-visit-plan/index.md)》第 6 節：

- 沒有位址可填（I-8 沒答，BH-03 也找不到實際設定）
- 主機上已有程式在寫 `<Hb_API_Fetch>`（BH-03）
- 既有留底有壞行（BH-06）
- 位址是 `http`，學長沒說可以（BH-05）
- 透析清單做完已超過約 40 分鐘，或學長要先走

延後時：BH-04 做了就照第 3 節移除 `hb` 資料夾，或留著（沒有排程就不會跑），跟學長說一聲；BH-03 的結論照記。

## 5. 狀態檔的 `reason` 與 `error_kinds`

| 看到                                                                            | 意思                                                        | 怎麼做                                               |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| `設定檔的 url_template 還是範本的佔位字…`                                       | 位址還沒填                                                  | BH-05                                                |
| `找不到病人清單（設定檔的 patients_file）`                                      | 病人清單不在設定指的位置                                    | BH-05                                                |
| `病人清單有不是純數字的病歷號`                                                  | 學長的程式不接受；不自動補零或去零                          | 停，問學長                                           |
| `留底有壞行：YYYY-MM.txt 第 N 行損壞…`                                          | 學長的程式讀不過既有留底                                    | BH-06                                                |
| `上一輪還沒結束`                                                                | 正常（排程與手動同時跑）；一直出現就看 `hb-run.lock` 的時間 | 鎖檔超過 3 小時會自動接手                            |
| `HTTP 需要院方核准後，才可在設定檔明確允許`                                     | 位址是 `http`，設定沒開                                     | BH-05                                                |
| `逾時`、`URLError（…）`                                                         | 連不到或太慢                                                | 透析清單也連不到就是網路；只有這支連不到，問學長位址 |
| `HTTPError 404`、`HTTPError 500` 等                                             | 院方 API 回錯誤                                             | 抄下數字，問學長                                     |
| `回應不是 JSON`                                                                 | 回了網頁或錯誤訊息                                          | 同上                                                 |
| `有未知欄位，需確認 Schema 更新（不自動丟棄）`                                  | 院方多了欄位，學長的程式拒收                                | 停，問學長（I-9）                                    |
| `回傳 MedicalId 與查詢不一致`、`回傳日期不在查詢區間內`、`未知的 API 回應格式…` | 院方回的跟問的對不上                                        | 抄下次數，問學長                                     |
| `學長的程式中途停了（…）`                                                       | 查到一半整支停（例如重建 CSV 時讀不過留底）                 | 看 `hb-logs\` 最新的檔，停                           |

______________________________________________________________________

## 版本歷程

| 定版 | 日期       | 異動                                                                                                 |
| ---- | ---------- | ---------------------------------------------------------------------------------------------------- |
| 1111 | 2026-11-11 | 首次定版。檢驗資料（hb）抓取的安裝 BH-01～BH-10；1111 學長答 hb 不用這邊處理，整冊不做、留作日後參考 |

[← 回第十九冊](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/19-hospital-fetch/index.md)　[← 回部署手冊總覽](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
