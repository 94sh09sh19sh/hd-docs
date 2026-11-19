# 第四次進院（1109）· 放上院方 API 抓取腳本之三：詳細版（B-15～B-21、退回、對照）

上層文件：《[第四次進院（1109）· 放上院方 API 抓取腳本](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api/index.md)》

> **狀態：已照做 1109，凍結**——做到 B-15（預演一輪成功），B-16 起沒做；結果見《[第四次進院紀錄（1109，做到 B-15）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-4-1109/index.md)》。改寫自舊第十九冊；編號 `B-xx`，與主文件同一套。
>
> 公開範圍與代稱（`<指定資料夾>`、`<院方位址>`、`<腳本資料夾>`）、怎麼開 PowerShell、`$dir`／`$sf` 兩個變數，見《[…之一：詳細版（B-01～B-11）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api-detail/index.md)》開頭與第 0 節。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。**

## 摘要

- 這一份是 B-15～B-21：預演一輪（B-15）、跑一輪（B-16，前面有兩個檢查）、裝排程（B-17）、看三輪（B-18）、教學長（B-19）、記錄（B-20）、收工前看一眼（B-21）
- 1109 現場做到 B-15：17:35:49 `成功 回應 703 列、會寫入 703 列`；B-16 起沒做
- B-16 前的兩個檢查（1109 起）：一般權限寫得進腳本資料夾、當月檔沒有別的程式在寫；第五次進院是 `AF-07`
- 成功的定義：B-18 三輪 `LastTaskResult` `0`、狀態檔 `result` `ok`
- 第 2 節最後是中途收工（B-17 排程還沒裝就得走），1109 就是照它收的
- 檢驗資料（`hb`）：**1111 起不做**——學長答 A-5 不用這邊處理，B-19 做完直接接 B-20；舊第十九冊之三收進《[檢驗資料（hb）抓取（未採用）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-hb-fetch/index.md)》
- 第 3 節退回照《院方 API 抓取腳本的維運》；第 4 節是本冊步驟與第五次進院 `AF-xx` 的對照

## 2. 現場步驟（續）

### B-15 預演一輪

```
py fetch_dialysis.py --dry-run
```

- **會看到**：`2026-11-09 16:20:05 成功 回應 601 列、會寫入 601 列（預演，沒有寫任何檔）`（列數是範例；第一次跑，兩個數字一樣）
- 1109 現場：17:35:49 `成功 回應 703 列、會寫入 703 列`
- 1114 起（v0.3.0、設了 `fetch_hours`）：07:00 前或 23:00 後跑會印 `… 時段外 只在 07:00-23:00 抓，這一輪不打院方 API（預演）`，不是錯；病歷號有不是純數字的列時，會多印「病歷號不是純數字的 N 列（照樣保留）」，記下 N（B-20）
- **不對的話**：照《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script-errors/index.md)》的出錯總表查；查不出來就停

### B-16 跑一輪、看結果

**先做兩個檢查（1109 起）**。B-16 起會真的寫進當月檔，寫之前確認：這個視窗寫得進腳本資料夾、當月檔沒有別的程式在寫。`$dir`、`$sf` 是空的就照第 0 節第 6 點先設好。第五次進院這兩個檢查是 `AF-07`。

檢查一，權限（1109 一開始用系統管理員開 PowerShell，重開後不確定是哪一種，B-10 的腳本資料夾可能是系統管理員建的）：

```
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$w = Join-Path $sf 'write-test.tmp'; Set-Content -LiteralPath $w 'x'; Test-Path -LiteralPath $w; Remove-Item -LiteralPath $w
```

- **會看到**：`False`、`True`（一般權限，寫得進去）
- 第一個 `True` 而且視窗標題有「系統管理員」：關掉，照第 0 節第 4 點重開一般的再檢查一次
- 第一個 `True` 但標題沒有「系統管理員」：這台關掉了 UAC，一般視窗也是最高權限，照樣往下
- 第二行出現紅字「存取被拒」：一般權限寫不進腳本資料夾，停，回報

檢查二，當月檔還有沒有別的程式在寫（1109 時當月檔已有上千段，是學長從別處搬來的，來源還有沒有在寫不知道）。只印時間與長度，不印病人資料：

```
$m = Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt'); (Get-Item -LiteralPath $m).LastWriteTime
Get-Content -LiteralPath $m -Tail 6 -Encoding UTF8 | ForEach-Object { if ($_ -like 'Date:*') { $_ } else { '（{0} 字）' -f $_.Length } }
```

- **會看到**：檔案的修改時間；接著最後幾行，`Date:` 行印原文，其他行只印字數（例如 `（96000 字）`、`（0 字）`）
- 修改時間與最後一個 `Date:` 都在**幾分鐘內**：有別的程式在寫，停，跟學長確認是誰在寫、要不要先停掉
- 時間是幾天前：等 5 分鐘再貼一次，修改時間沒變就往下（**1114 學長答 K-1**：月份檔是從正式在用的那台 IDH 主機搬過來的，這台沒有別的程式在寫；B-14a 搬到 C 槽後更不會有，這個檢查照做、只是確認）
- 每段之間夾一行 `（0 字）`（空行）是舊檔的寫法，本腳本每段只寫 `Date:` 與 JSON 兩行，不夾空行；記下來（B-20），不影響往下做

跑一輪：

```
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
```

- **會看到**：第一行 `… 成功 回應 601 列、寫入 601 列`；`$LASTEXITCODE` 是 `0`；狀態檔裡 `"result": "ok"`、`"written_rows"` 與 `"response_rows"` 一樣

看當月檔的最後兩行對不對（**只看開頭與長度，不把病人資料印到螢幕上**）：

```
$t = Get-Content -Encoding UTF8 -LiteralPath (Join-Path $dir ((Get-Date -Format 'yyyy-MM') + '.txt')) -Tail 2
$t[0]
$t[1].StartsWith('{"data_list":[')
$t[1].Length
```

- **會看到**：`Date: 2026-11-09 16:21:30`（剛剛的時間）、`True`、一個很大的數字

再跑一次 `py fetch_dialysis.py --once`：

- **會看到**：`寫入 0 列`（剛好有新的量測進來就是幾列，不會是整天）
- **不對的話**：結束碼不是 `0`、`result` 不是 `ok`、第二行不是 `True`、主控台印出姓名或病歷號 → 停

### B-17 裝排程

```
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
```

用 `.exe` 的話改成：

```
powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -Exe .\fetch_dialysis_w.exe
```

- **會看到**：

```
已建立工作 hd-hospital-fetch
  帳號：<電腦名稱>\<帳號>（只在使用者登入時執行）
  頻率：每 3 分鐘，第一次在 1 分鐘後
  執行：…pythonw.exe "C:\API_Fetch\hd-hospital-fetch\fetch_dialysis.py" --once --config "C:\API_Fetch\hd-hospital-fetch\config.json"
  狀態：Ready
看結果：狀態檔（設定檔的 status_file）每輪覆寫；或 Get-ScheduledTaskInfo -TaskName hd-hospital-fetch
```

- 排程跑的時候**不會跳出視窗**，這是正常的
- **不對的話**：紅字寫「執行原則」或「無法載入」→ 停，學長決定（院方的群組原則擋了 PowerShell 腳本）；寫「已經有一個叫 hd-hospital-fetch 的工作」→ 有人裝過，停，跟學長確認

### B-18 看三輪（約 10 分鐘）

每 3 分鐘打一次：

```
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content -Encoding UTF8 (Join-Path $dir 'fetch-status.json')
```

- **會看到**：`LastRunTime` 每 3 分鐘往前跳、`LastTaskResult` 是 `0`；狀態檔的 `last_attempt_at` 跟著變、`result` 是 `ok`；`written_rows` 多半是 `0`，有新量測時是幾列
- `LastTaskResult` 的其他數字：`1` 是那一輪失敗（看狀態檔的 `reason`）；`267009` 是正在跑；`267011` 是還沒跑過
- **不對的話**：過了 5 分鐘 `LastRunTime` 都沒變、或連續兩輪 `failed` → 停，照《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script-errors/index.md)》的出錯總表查

### B-19 教學長三件事

| 要做的               | 指令（在 `<腳本資料夾>` 裡打）                                                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 停掉                 | `powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1`                                                                                                                                                                |
| 改頻率（例：5 分鐘） | `powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -IntervalMinutes 5 -Force`                                                                                                                                        |
| 看最近一輪           | `Get-Content -Encoding UTF8 C:\API_Fetch\IDH_interface\fetch-status.json`（1114 起狀態檔在指定資料夾裡）：`result`、`reason`、`last_success_at`（最後一次成功的時間）。07:00 前、23:00 後不抓，狀態檔停在 22:5x 那一輪是正常的 |

**接著直接做 B-20。** 檢驗資料（`hb`）1111 起不做（學長答 A-5 不用這邊處理），《[檢驗資料（hb）抓取（未採用）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-hb-fetch/index.md)》不必翻。

### B-20 記錄

在手機上記，回去後寫進私人 repo 的 `deploy/records/`（1109 是 `1109-hospital-fetch/`，第五次另開 `MMDD-主題/`，實際是 `1116-fifth-visit/`）：

- 做到哪一步；每一步的「會看到」對不對
- B-05 用 `.py` 還是 `.exe`、Python 版本；B-06 有沒有同步；B-08 的兩個位置
- B-12 每個檔的編碼與大小；B-13 的備份資料夾名稱與還原指令
- B-16 的回應列數；B-18 三輪的時間與 `written_rows`
- 1114 起：B-14a 的檔數與位元組、舊資料夾改成什麼名字、學長說何時刪；B-14b 的 `--version`；狀態檔的 `non_numeric_id_rows`（不是 0 就記下數字，不記病歷號）
- 每個斷點學長怎麼決定
- B-09 用哪個 GitHub 帳號登入、有沒有要求兩步驟驗證、幾點關掉 InPrivate／無痕視窗
- 不記：院方回應的內容、病人的姓名與病歷號

### B-21 收工前看一眼

- InPrivate 視窗已關、「下載」資料夾裡沒有留下 zip 與 `.exe`；最後關掉開著這一冊的瀏覽器視窗（公開文件站，不留登入，留下瀏覽紀錄也無妨）；一般視窗如果登入過 GitHub，先登出
- `Get-ScheduledTaskInfo -TaskName hd-hospital-fetch` 的 `LastTaskResult` 是 `0`
- 本系統：1114 起同一趟換版上線，照《[第五次進院（1116）任務二 · 本系統換版上線之三：上線準備清單](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-prep/index.md)》第 0.3 節（1116 實際照《[第五次進院（1116）任務二 · 本系統換版上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system/index.md)》做）；沒做成的話 `.env` 的兩個資料夾維持空白
- B-14a 的舊資料夾（`API_Fetch_搬到C槽_MMDD`）還在 D 槽，學長決定何時刪（D 槽約 12 月中旬滿）；1116 學長已刪
- **不重開機**（同一台還有另一個專案，《上線準備清單》A-04）

### 中途收工（B-17 排程還沒裝就得走）

用「收工-1」到「收工-7」對照（程式碼框會打斷自動編號，所以不用 1、2、3）。1109 就是照這一節收的。

**收工-1** 預演還在跑：等它印完、拍下整份清單（每個檔的編碼）；來不及就按 `Ctrl+C`（預演不寫檔，不會壞任何東西）。

**收工-2** B-12 寫「要轉 0 個」就沒有 B-13；有要轉的話，**不要在快走前才開始 B-13 實轉**：要再讀一次全部檔、整份備份、逐檔轉寫與比對，7.7 GB 估計 30 分鐘以上；中途被關掉會留下暫存檔，下次要先處理。有要轉的檔時，再看指定資料夾那顆磁碟的可用空間（要至少是 B-12「合計」的 1.5 倍）：

```
"{0} 槽可用 {1:N1} GB" -f $dir.Substring(0,1), ((Get-PSDrive $dir.Substring(0,1)).Free/1GB)
```

**收工-3** 確認沒留下會自己跑的東西與下載檔：

```
Get-ScheduledTask -TaskName hd-hospital-fetch -ErrorAction SilentlyContinue
Test-Path "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip"
```

- **會看到**：第一行沒印東西（排程沒裝）、第二行 `False`（zip 已刪）

**收工-4** 腳本資料夾留著（程式檔，做過 B-14 的話還有 `config.json`；沒有排程就不會自己跑、不會碰資料），跟學長說一聲。

**收工-5** 關掉 PowerShell 與開著這一冊的瀏覽器視窗，確認 InPrivate／無痕視窗已關、一般視窗沒有登入 GitHub；**不重開機**。

**收工-6** 問學長、帶回來：B-04 的帳號是不是醫師的；下次接著做（B-16 起，含 B-18 看三輪約 10 分鐘）哪個時段可以；檔案總管的「開始備份」不要按。

**收工-7** B-20 照記：做到哪一步、各步驟的照片、學長的決定。

## 3. 退回

學長說「不要了」或斷點決定退回時：停排程（R-1）、歷史 txt 回到轉碼前（R-2，用 B-13 抄下的還原指令）、刪腳本（R-3）——步驟與注意事項照《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script-2/index.md)》的退回。

## 4. 本冊步驟與第五次進院 `AF-xx` 對照

1116 第五次進院照《[第五次進院（1116）任務一 · 抓取腳本上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-api/index.md)》做，起點是 1109 做完 B-15 的樣子。

| 本冊                   | 第五次進院                      | 說明                                                                                                                                                                                                                         |
| ---------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B-01～B-03             | AF-01                           | Release 頁改成 v0.3.0                                                                                                                                                                                                        |
| B-04                   | AF-02                           | 同                                                                                                                                                                                                                           |
| B-05、B-06、B-08～B-13 | —                               | 1109 已做完，不重做；主機不是 1109 的樣子時照《[第五次進院（1116）任務一 · 抓取腳本上線之一：詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-api-detail/index.md)》「主機不是 1109 的樣子時」那一節 |
| B-07＋B-14a 開頭的檢查 | AF-03                           | 加「有沒有別的排程指著 `API_Fetch`」                                                                                                                                                                                         |
| B-14                   | —                               | 1109 已填好 `config.json`，不重填                                                                                                                                                                                            |
| B-14a                  | AF-04                           | 同                                                                                                                                                                                                                           |
| B-14b                  | AF-05                           | 同                                                                                                                                                                                                                           |
| B-14c                  | AF-06                           | 🧪 時段外暫改 `00:00-24:00`                                                                                                                                                                                                  |
| B-16 前的檢查一、二    | AF-07                           | 搬到預演之前                                                                                                                                                                                                                 |
| B-15                   | AF-08                           | 順序跟檢查對調                                                                                                                                                                                                               |
| B-16                   | AF-09                           | 同                                                                                                                                                                                                                           |
| B-17                   | AF-10                           | 同                                                                                                                                                                                                                           |
| B-18                   | AF-11                           | 同                                                                                                                                                                                                                           |
| B-19～B-21             | AF-12                           | 1116 教學長改院外補                                                                                                                                                                                                          |
| 第 3 節 R-1～R-3       | 《院方 API 抓取腳本的維運》退回 | 1116 學長刪了 D 槽舊資料夾，改回原名的退回做不到                                                                                                                                                                             |

上一份：《[…之二：詳細版（B-12～B-14c）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api-detail-2/index.md)》

______________________________________________________________________

## 版本歷程

| 定版                                                                                 | 日期       | 異動                                                                                                                    |
| ------------------------------------------------------------------------------------ | ---------- | ----------------------------------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-4-api-detail-3/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第四次進院（1109）· 放上院方 API 抓取腳本之一：詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
