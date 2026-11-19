# 第四次進院（1109）· 放上院方 API 抓取腳本之一：詳細版（B-01～B-11）

上層文件：《[第四次進院（1109）· 放上院方 API 抓取腳本](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api/index.md)》

詳細版分三份：之一是 B-01～B-11（這一份，含第 0 節）；《[之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api-detail-2/index.md)》是 B-12～B-14c；《[之三](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api-detail-3/index.md)》是 B-15～B-21、中途收工、第 3 節退回、第 4 節與 `AF-xx` 的對照。

> **狀態：已照做 1109，凍結**——做到 B-15（預演一輪成功），B-16 起沒做；結果見《[第四次進院紀錄（1109，做到 B-15）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-4-1109/index.md)》。
>
> 改寫自舊第十九冊（院方 API 抓取腳本的安裝，新手版；1108 依《[院方 API 介接之三](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-monday-plan/index.md)》第 4 節與 `hd-hospital-fetch` v0.1.0 實際的輸出寫成，1109 現場逐步修正，1111 定版）。第 3 節退回收進《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script/index.md)》；舊第十九冊之一的出錯對照與速查也在那一份。
>
> 編號：`B-xx`，與主文件同一套。
>
> **B-14a～B-14c 與第五次進院的關係**：這三步是 1114 學長答了《[院方 API 介接之二](https://94sh09sh19sh.github.io/hd-docs/latest/notes/hospital-api-fetch-methods-questions/index.md)》之後，為第五次進院（1116）加進本冊的（整個 `API_Fetch` 搬到 C 槽、只換 `fetch_dialysis.py` 成 v0.3.0、`config.json` 改三處），1109 現場沒有這三步。1116 寫成新的一冊，**第五次實際照的是《[第五次進院（1116）任務一 · 抓取腳本上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-api/index.md)》的 `AF-xx`**（詳細版是《[…之一：詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-api-detail/index.md)》），本冊 B-14a～B-21 都收進那裡，本冊不必再翻。對照表在第 4 節。
>
> 每一步都有「會看到」與「不對的話」。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。**
>
> **公開範圍**：文件站是公開的。院方位址、指定資料夾的完整路徑、帳號一律不寫進這一冊，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；本冊用 `<指定資料夾>`、`<院方位址>`、`<腳本資料夾>` 代稱。**例外（1114）**：搬到 C 槽後的 `C:\API_Fetch\…` 是開發端提的通用位置，《院方 API 介接之二之一》K-2 與腳本的設定範例本來就公開，直接寫；D 槽原本的路徑照舊不寫。

## 摘要

- 這一冊回答一件事：在醫院那台主機上，把抓取腳本 `hd-hospital-fetch` 放上去，讓它每 3 分鐘自己抓一次院方透析清單；本系統（容器、`.env`、平板）這次**完全不動**
- 時間：1109（一）15:30 起，學長在場；全部約 60 分鐘，順序是 B-01～B-21
- **這一冊直接開在部署主機上**：主機可以連外網，用主機的 Edge 或 Chrome 開公開文件站的這一冊（1109 用 Chrome），指令從頁面複製、貼進 PowerShell；不印紙本、不用手機看手冊（B-04）
- 出發前（B-01～B-03）；先看現況（B-04～B-08）；下載與放好（B-09～B-11）；轉碼（B-12～B-13，歷史 txt 從 cp950 轉 UTF-8，先預演再實轉，隨時可還原）；試跑（B-14～B-16）；排程（B-17～B-19）；收尾（B-20～B-21）
- 這一份：第 0 節（怎麼開 PowerShell、結束碼、`$dir`／`$sf` 兩個變數）、出發前（B-01～B-03）、先看現況（B-04～B-08）、下載與放好（B-09～B-11）
- 先看現況的斷點：不是醫師的帳號（B-04）、沒有 Python（B-05）、在同步而醫師沒同意或不是透析清單的資料夾（B-06）、有舊腳本在跑（B-07）、腳本資料夾已經有人放過（B-08）
- 下載用 InPrivate／無痕視窗登入自己的 GitHub，下載完關掉整個視窗；走 `.py` 就跳過 `.exe` 專用的段落（B-09～B-11）
- 轉碼、填設定與 1114 加的 B-14a～B-14c 在《之二》；試跑、排程、收尾、中途收工、退回與 `AF-xx` 對照在《之三》

## 0. 開始前先懂的事

1. **這支腳本做什麼**：每 3 分鐘問院方 API「今天的透析清單」，把**新的或變了的列**附加到 `<指定資料夾>\YYYY-MM.txt`（一個月一個檔），再把這一輪的結果寫進狀態檔 `fetch-status.json`。同一筆資料不會重複寫
1. **它會動到的檔**：只有三處——`<指定資料夾>` 裡的當月 txt（只附加、不改舊的）、狀態檔 `fetch-status.json`（1114 起放在 `<指定資料夾>` 裡，本系統要讀，B-14c）、`<腳本資料夾>` 裡的 `state\`。轉碼工具另外會在 `<指定資料夾>` 底下建一個 `_backup_日期-時間\` 備份
1. **兩種跑法**：主機有 Python 3.8 以上就用 `.py`；沒有就用 `.exe`（學長決定）。本冊的指令寫 `.py` 版；用 `.exe` 的話，`py fetch_dialysis.py` 換成 `.\fetch_dialysis.exe`、`py transcode_history.py` 換成 `.\transcode_history.exe`，其餘照舊
1. **怎麼開 PowerShell**：按「開始」→ 打 `powershell` →「Windows PowerShell」（**不要**選「以系統管理員身分執行」，也**不要**用 `Win+X` 再按 `A`——那是系統管理員；1109 之前每次進院都是這樣開的）。搜尋到之後直接按 Enter 是一般權限，`Ctrl+Shift+Enter` 才是系統管理員。指令從主機瀏覽器上的這一冊整行複製（程式碼框右上角有複製鈕）、到 PowerShell 按滑鼠右鍵貼上、按 Enter；用 `Alt+Tab` 在瀏覽器與 PowerShell 之間切換
1. **結束碼**：每跑完一支，接著打 `$LASTEXITCODE` 看數字。`0` 是成功（或「跳過」），`1` 是失敗，`2` 是參數或設定錯
1. **兩個變數**：B-06 設 `$dir`（指定資料夾）、B-08 設 `$sf`（腳本資料夾），之後的指令直接用，不用打路徑。PowerShell 視窗關掉就會不見；重開後先貼這一行，出現提示時貼上指定資料夾的路徑（從檔案總管網址列複製）：

```
$dir = (Read-Host '貼上指定資料夾的路徑').Trim().Trim('"', "'"); $sf = Join-Path (Split-Path -Parent $dir) 'hd-hospital-fetch'; cd -LiteralPath $sf
```

腳本資料夾用 `C:\hd-hospital-fetch` 的話，`$sf =` 後面改成 `'C:\hd-hospital-fetch'`。**B-14a 搬到 C 槽之後**，指定資料夾是 `C:\API_Fetch\IDH_interface`，直接貼：

```
$dir = 'C:\API_Fetch\IDH_interface'; $sf = 'C:\API_Fetch\hd-hospital-fetch'; cd -LiteralPath $sf
```

## 1. 出發前

### B-01 帶手機

- GitHub 兩步驟驗證的驗證碼、`values.md`、現場筆記都在手機上
- 這一冊不用手機看，現場開在主機上（B-04）

### B-02 確認 Release 頁開得了

在自己的電腦登入 GitHub，開啟 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.1.0`。

- **會看到**：v0.1.0 與 `fetch_dialysis.exe`、`fetch_dialysis_w.exe`、`transcode_history.exe`、`SHA256SUMS.txt`、`Source code (zip)`
- 顯示 404 是帳號不對，換成 `94sh09sh19sh`

### B-03 手機能看 `values.md`

用手機的 GitHub App 開啟私人 repo（`v0`）的 `deploy/records/1108-hospital-api/values.md`。

- **會看到**：院方位址與指定資料夾的路徑（現場 B-08、B-14 要抄）

## 2. 現場步驟

### B-04 到對的主機、對的帳號，把這一冊開在主機上

1. 現場三台裡**最右邊那台**
1. 開 Edge 或 Chrome 的**一般視窗**（不是 InPrivate／無痕；**一般視窗不要登入 GitHub**，公開文件站不用登入），到公開文件站，左邊選「部署手冊」→「第十九冊」（1109 當時的位置；1117 起是《第四次進院（1109）· 放上院方 API 抓取腳本》與這一份詳細版）。之後的指令都從這一頁複製；B-09 的 InPrivate 是另一個視窗，關掉它不會關到手冊
1. 開 PowerShell（第 0 節第 4 點），打：

```
whoami
```

- **會看到**：`<電腦名稱>\<帳號>`，帳號是醫師的；帳號名稱看不出是誰（例如 `user`）就問學長
- **PowerShell 視窗標題有「系統管理員」**：關掉，照第 0 節第 4 點重開一般的（1109 現場開成系統管理員過）。用系統管理員建的腳本資料夾，排程以一般權限跑時可能寫不進狀態檔；已經做過的查看指令不用重做
- **不對的話**：停。不是醫師的帳號就不往下做；公開文件站打不開（主機連不到外網）→ 改用手機看這一冊，指令照著打

### B-05 看 Python

```
py -0p
python --version
```

- **會看到**：`py -0p` 列出 `-V:3.x` 與 `python.exe` 的路徑；`python --version` 印出 `Python 3.x.x`。**3.8 以上**才能用 `.py` 版
- **沒有 `py` 但 `python` 有**：本冊的 `py` 全部換成 `python`
- **`py` 有、`python --version` 什麼都沒印**：`python` 指到 Microsoft Store 的空殼，不要緊，本冊照用 `py`（1109 現場就是這樣）
- **跳出 Microsoft Store、或兩個都說找不到**：就是沒有裝。停，學長決定裝 Python 或用 `.exe`；都不行就做完 B-06、B-07 收工
- 記下結果：用 `.py` 還是 `.exe`

### B-06 看 OneDrive 有沒有在同步指定資料夾

指令抄自《[第一次進院（0922）· 部署本系統之一：進院當天詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite/index.md)》的雲端同步檢查：

```
$env:OneDrive; $env:OneDriveCommercial
Get-Process | Where-Object { $_.Name -match 'OneDrive|GoogleDrive|Dropbox|Synology|Nextcloud|Box' } | Select-Object Name
```

再用檔案總管開啟 `<指定資料夾>`，看檔案旁邊有沒有雲朵或綠色勾勾的圖示。`<指定資料夾>` 是**透析清單**的資料夾，`values.md` 裡結尾是 `IDH_interface` 的那一個；`Hb_API_Fetch` 底下（含 `hospital_dataset\raw_txt`）是檢驗資料，裡面也有「年-月.txt」，**不是這一個**（1109 現場選錯過）；檢驗資料的 txt 每一行開頭是 `{"FetchedAt"`，沒有 `Date:`。

接著點檔案總管上方的網址列、按 `Ctrl+C` 複製路徑，回 PowerShell 貼下面這段。**指令原樣貼、不要把路徑改進指令裡**；出現「貼上指定資料夾的路徑:」時才按滑鼠右鍵貼上路徑（前後有引號也沒關係）、按 Enter：

```
$dir = (Read-Host '貼上指定資料夾的路徑').Trim().Trim('"', "'"); Test-Path -LiteralPath $dir
$dir.StartsWith("$env:OneDrive\", 'OrdinalIgnoreCase')
$p = Get-Item -LiteralPath $dir; while ($p) { if ($p.LinkType) { "$($p.FullName) -> $($p.Target)" }; $p = $p.Parent }
```

- 會印兩個 `True`／`False`：第一個是資料夾在不在，第二個是它在不在 OneDrive 的路徑底下；有一段路經過連結（Junction）才會多印一行「… -> …」
- **檔案總管網址列最左邊是雲朵圖示加「開始備份」**：那是 Windows 邀請你用 OneDrive 備份「桌面」，表示**沒有**在備份；**不要按**，按了就開始同步（1109 現場：主機的「桌面」就設在 `<指定資料夾>` 的上層，資料夾名稱裡有 `OneDrive` 但不是現在同步的那個）。要再確認，在同一個視窗貼：

```
[Environment]::GetFolderPath('Desktop')
(Get-Item -LiteralPath $dir).Attributes; Get-ChildItem -LiteralPath $dir -File | Select-Object -First 3 Name, Attributes
```

- **沒在同步會看到**：第一行是桌面的實際位置；資料夾是 `Directory`，檔案只有 `Archive`（可能多 `ReadOnly`）。出現 `ReparsePoint`、`Offline`、`Pinned`、`Unpinned`、`RecallOnDataAccess` 任何一個 → 有雲端同步在管這些檔，停

第一個是 `True` 之後，在同一個視窗確認這是透析清單（只看最新一個 txt 的開頭有沒有 `Date:` 與 `"data_list"`，不印病人資料）：

```
$f = Get-ChildItem -LiteralPath $dir -Filter *.txt | Where-Object { $_.Name -match '^\d{4}-\d{2}\.txt$' } | Sort-Object Name | Select-Object -Last 1; $f.Name
$h = (Get-Content -LiteralPath $f.FullName -TotalCount 2) -join ' '; $h.StartsWith('Date:'); $h.Contains('"data_list"')
```

- **會看到**：最新的「年-月.txt」檔名（例如 `2026-11.txt`），接著兩個 `True`
- 沒印檔名、接著是紅字：資料夾裡沒有「年-月.txt」，停，跟學長確認歷史檔放在哪
- 資料夾裡另有 `data_list_sucess.txt`：舊腳本（`API_script` 版）的留底，也是透析清單，B-12 的清單會列出它並一起轉碼，不用處理（1109 現場就有）
- **不是兩個 `True`**：這不是透析清單的資料夾。停，請學長指出正確的那一個
- **在同步**：第二個是 `True`，或檔案旁有同步圖示
- **在同步而醫師還沒同意**：停。學長當場聯絡醫師；聯絡不到就只做到 B-13（轉碼，不產生新的留底），B-14 起不做
- **多印了「… -> …」**：資料夾經過連結，實際位置可能在 OneDrive 底下。停，跟學長確認
- **第一個是 `False`**（明明在檔案總管看得到）：在同一個視窗貼下面這段，逐層找出哪一層對不上。檔案總管會把某些資料夾顯示成中文（例如實際叫 `Desktop`、畫面上顯示「桌面」），複製出來的路徑就跟實際的不同

```
$parts = $dir.TrimEnd('\').Split('\'); $q = $parts[0] + '\'
foreach ($s in $parts[1..($parts.Count-1)]) { $n = Join-Path $q $s; if (Test-Path -LiteralPath $n) { "有   $n" } else { "沒有 $n"; "$q 底下實際的資料夾："; Get-ChildItem -LiteralPath $q -Directory -Force | Select-Object -ExpandProperty Name; break }; $q = $n }
```

- 印到「沒有 …」那一行就是對不上的那一層，下面列出那一層實際的資料夾名稱。把路徑那一段換成實際名稱，重貼 B-06 那段再確認一次第一個是 `True`；**之後 B-12、B-13、B-14 的 `<指定資料夾>` 都用這個實際路徑**，不用 `values.md` 的。對不出來就停，請學長指出實際的資料夾
- 沒有同步（`True`、`False`、沒有多印、檔案旁沒有圖示）：往下。第一段印的 OneDrive 路徑開頭跟 `values.md` 的路徑不一樣不要緊，以這裡的結果為準

### B-07 看有沒有舊的腳本在跑

```
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' -and "$($_.Actions.Execute) $($_.Actions.Arguments)" -match 'python|\.py|fetch|IDH' } | Select-Object TaskName, State
```

```
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Select-Object ProcessId, CommandLine
```

- 第一個指令找「會執行 Python 或抓取程式的排程工作」，第二個找「現在正在跑的 Python」
- **會看到**：兩個指令都沒印東西（1108 學長說舊腳本與 IDH 都沒在跑）
- **不對的話**：有印出東西就停，跟學長確認是什麼、停用後再往下；認不出的不要自己停

### B-08 決定兩個位置

跟學長定好，抄在手機上：

| 代稱           | 是什麼                | 建議                                                                                                                                                                                                                                               |
| -------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<指定資料夾>` | 留底 txt 所在的資料夾 | 照 `values.md`                                                                                                                                                                                                                                     |
| `<腳本資料夾>` | 腳本放哪              | 學長要跟資料放一起（1109 定）：`<指定資料夾>` 的**上一層**底下的 `hd-hospital-fetch`，跟 `<指定資料夾>` 並列；**不要**放進 `<指定資料夾>` 裡、也不要放在正在同步的 OneDrive 底下（B-06 已確認沒在同步才行）。學長沒要求就用 `C:\hd-hospital-fetch` |

在 B-06 的同一個視窗貼（`$dir` 是 B-06 填的指定資料夾，`$sf` 是腳本資料夾，B-10 起的指令都用這兩個）：

```
$sf = Join-Path (Split-Path -Parent $dir) 'hd-hospital-fetch'; $sf; Test-Path -LiteralPath $sf
```

- **會看到**：`<指定資料夾>` 的上一層加 `\hd-hospital-fetch`，接著 `False`（還沒建）
- 印出 `True`：已經有人放過，停，跟學長確認
- 學長要用 `C:\hd-hospital-fetch` 的話改貼：`$sf = 'C:\hd-hospital-fetch'`

### B-09 下載（InPrivate 視窗）

1. 開 Edge 按 `Ctrl+Shift+N` 開 InPrivate 視窗；用 Chrome 也是 `Ctrl+Shift+N`，叫「無痕視窗」（1109 用 Chrome 無痕）
1. 開啟 `github.com/login`，登入**自己的** GitHub；不勾「保持登入」；瀏覽器問要不要存密碼，選「永不」
1. 在 InPrivate 視窗的網址列貼上 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.1.0`，按 Enter；捲到頁面最下面的「Assets」區塊（收合著就點開），點 `Source code (zip)` 下載。顯示 404 是登入的帳號不對（repo 是私人的）。跳出「另存新檔」選位置時，左邊選「下載」（`C:\Users\<帳號>\Downloads`）、檔名不改，按「存檔」；B-10 的指令從這裡找 zip
1. 用 `.exe` 的話，再下載 `fetch_dialysis.exe`、`fetch_dialysis_w.exe`、`transcode_history.exe`、`SHA256SUMS.txt`
1. **關掉整個 InPrivate 視窗**（登入、Cookie、瀏覽紀錄跟著清掉）；開著這一冊的一般視窗不用關，收工時再關（B-21）
1. **不對的話**：院內網路連不上 GitHub → 停，這次只做到 B-07；Edge 擋 `.exe` 下載 → 在下載清單選「…」→「保留」，保留不了就改用 `.py` 版

### B-10 解壓縮到腳本資料夾

```
Expand-Archive "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip" -DestinationPath (Split-Path -Parent $sf)
Rename-Item -LiteralPath (Join-Path (Split-Path -Parent $sf) 'hd-hospital-fetch-0.1.0') 'hd-hospital-fetch'
cd -LiteralPath $sf
dir
```

（在 B-08 的同一個視窗做；`$sf` 是空的就回 B-08 貼那一行。）

- **會看到**：`dir` 列出 `fetch_dialysis.py`、`transcode_history.py`、`install-task.ps1`、`uninstall-task.ps1`、`config.example.json`、`README.md` 等；提示字元變成 `PS …\hd-hospital-fetch>`

接著把「下載」資料夾裡的 zip 刪掉：

```
Remove-Item "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip"
```

- **會看到**：不印東西；已經刪過再貼會出現「找不到」紅字，表示已刪，不要緊

**只有用 `.exe` 才做（走 `.py` 跳過，貼了也只會出現「找不到」紅字、不會動到任何檔）**：把四個下載的檔搬進來，逐一寫檔名，不用 `*.exe`，免得把醫師「下載」裡其他的 `.exe` 一起搬走：

```
Move-Item "$env:USERPROFILE\Downloads\fetch_dialysis.exe", "$env:USERPROFILE\Downloads\fetch_dialysis_w.exe", "$env:USERPROFILE\Downloads\transcode_history.exe", "$env:USERPROFILE\Downloads\SHA256SUMS.txt" .
```

- 下載的檔名變成 `xxx (1).exe`：「下載」裡原本就有同名的檔，停，跟學長確認

### B-11 解除下載標記、比對雜湊

```
Get-ChildItem -Recurse | Unblock-File
```

**只有用 `.exe` 才做（走 `.py` 跳過）**：比對雜湊：

```
Get-FileHash .\fetch_dialysis.exe, .\fetch_dialysis_w.exe, .\transcode_history.exe -Algorithm SHA256 | Select-Object Hash, Path
Get-Content .\SHA256SUMS.txt
```

- **會看到**：`Unblock-File` 不印東西；兩邊的雜湊一樣（大小寫不同不要緊）
- **不對的話**：雜湊不同 → 刪掉那個 `.exe`，回 B-09 重新下載

下一份：《[…之二：詳細版（B-12～B-14c）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-4-api-detail-2/index.md)》

______________________________________________________________________

## 版本歷程

| 定版                                                                               | 日期       | 異動                                                                                                                                            |
| ---------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-4-api-detail/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
