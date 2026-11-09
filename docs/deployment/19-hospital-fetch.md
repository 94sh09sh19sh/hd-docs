# 第十九冊 · 院方 API 抓取腳本的安裝（1109，新手版）

版本：v0.1　文件狀態：草案（1108 依《[院方 API 之三](../notes/hospital-api-fetch-methods-monday-plan.md)》第 4 節與 `hd-hospital-fetch` v0.1.0 實際的輸出寫成）　編號：`B-xx`

> **這一冊回答一件事：在醫院那台主機上，把抓取腳本 `hd-hospital-fetch` 放上去，讓它每 3 分鐘自己抓一次院方透析清單。** 本系統（容器、`.env`、平板）這次**完全不動**。
>
> 每一步都有「會看到」與「不對的話」。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。**

> **公開範圍**：文件站是公開的。院方位址、指定資料夾的完整路徑、帳號一律不寫進這一冊，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；本冊用 `<指定資料夾>`、`<院方位址>`、`<腳本資料夾>` 代稱。

## 摘要

- 時間：1109（一）15:30 起，學長在場；全部約 60 分鐘，順序是 B-01～B-21
- **這一冊直接開在部署主機上**：主機可以連外網，用主機的 Edge 開公開文件站的這一冊，指令從頁面複製、貼進 PowerShell；不印紙本、不用手機看手冊（B-04）
- 出發前（B-01～B-03）：帶手機（兩步驟驗證、`values.md`、現場筆記）、確認自己的 GitHub 開得了 Release 頁、手機能看 `values.md`
- 先看現況（B-04～B-08）：帳號、Python、OneDrive、有沒有舊腳本在跑、兩個位置
- 下載與放好（B-09～B-11）：InPrivate 視窗登入自己的 GitHub 下載，關視窗、解壓縮、解除下載標記
- 轉碼（B-12～B-13）：歷史 txt 從 cp950 轉 UTF-8，先預演再實轉，隨時可還原
- 試跑（B-14～B-16）：填設定、預演、跑一輪，看狀態檔與檔尾
- 排程（B-17～B-19）：裝排程、看三輪、教學長怎麼停與怎麼看
- 收尾（B-20～B-21）：記錄；退回步驟在第 3 節；出錯對照、一頁速查在《[第十九冊之一](19a-hospital-fetch-reference.md)》

## 0. 開始前先懂的五件事

1. **這支腳本做什麼**：每 3 分鐘問院方 API「今天的透析清單」，把**新的或變了的列**附加到 `<指定資料夾>\YYYY-MM.txt`（一個月一個檔），再把這一輪的結果寫進狀態檔 `fetch-status.json`。同一筆資料不會重複寫
2. **它會動到的檔**：只有三處——`<指定資料夾>` 裡的當月 txt（只附加、不改舊的）、`<腳本資料夾>` 裡的 `fetch-status.json` 與 `state\`。轉碼工具另外會在 `<指定資料夾>` 底下建一個 `_backup_日期-時間\` 備份
3. **兩種跑法**：主機有 Python 3.8 以上就用 `.py`；沒有就用 `.exe`（學長決定）。本冊的指令寫 `.py` 版；用 `.exe` 的話，`py fetch_dialysis.py` 換成 `.\fetch_dialysis.exe`、`py transcode_history.py` 換成 `.\transcode_history.exe`，其餘照舊
4. **怎麼開 PowerShell**：按「開始」→ 打 `powershell` →「Windows PowerShell」（**不要**選「以系統管理員身分執行」）。指令從主機瀏覽器上的這一冊整行複製（程式碼框右上角有複製鈕）、到 PowerShell 按滑鼠右鍵貼上、按 Enter；用 `Alt+Tab` 在瀏覽器與 PowerShell 之間切換
5. **結束碼**：每跑完一支，接著打 `$LASTEXITCODE` 看數字。`0` 是成功（或「跳過」），`1` 是失敗，`2` 是參數或設定錯
6. **兩個變數**：B-06 設 `$dir`（指定資料夾）、B-08 設 `$sf`（腳本資料夾），之後的指令直接用，不用打路徑。PowerShell 視窗關掉就會不見；重開後先貼這一行，出現提示時貼上指定資料夾的路徑（從檔案總管網址列複製）：`$dir = (Read-Host '貼上指定資料夾的路徑').Trim().Trim('"', "'"); $sf = Join-Path (Split-Path -Parent $dir) 'hd-hospital-fetch'; cd -LiteralPath $sf`（腳本資料夾用 `C:\hd-hospital-fetch` 的話，`$sf = ` 後面改成 `'C:\hd-hospital-fetch'`）

## 1. 出發前

| # | 做什麼 | 會看到／不對的話 |
|---|---|---|
| B-01 | 帶手機：GitHub 兩步驟驗證的驗證碼、`values.md`、現場筆記都在手機上。這一冊不用手機看，現場開在主機上（B-04） | — |
| B-02 | 在自己的電腦登入 GitHub，開啟 `github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.1.0` | 看到 v0.1.0 與 `fetch_dialysis.exe`、`fetch_dialysis_w.exe`、`transcode_history.exe`、`SHA256SUMS.txt`、`Source code (zip)`；顯示 404 是帳號不對，換成 `94sh09sh19sh` |
| B-03 | 用手機的 GitHub App 開啟私人 repo（`v0`）的 `deploy/records/1108-hospital-api/values.md` | 看得到院方位址與指定資料夾的路徑（現場 B-08、B-14 要抄） |

## 2. 現場步驟

### B-04 到對的主機、對的帳號，把這一冊開在主機上

1. 現場三台裡**最右邊那台**
2. 開 Edge 的**一般視窗**（不是 InPrivate），到公開文件站，左邊選「部署手冊」→「第十九冊」。之後的指令都從這一頁複製；B-09 的 InPrivate 是另一個視窗，關掉它不會關到手冊
3. 開 PowerShell（第 0 節第 4 點），打：

```powershell
whoami
```

- **會看到**：`<電腦名稱>\<帳號>`，帳號是醫師的；帳號名稱看不出是誰（例如 `user`）就問學長
- **PowerShell 視窗標題有「系統管理員」**：關掉，照第 0 節第 4 點重開一般的（1109 現場開成系統管理員過）。用系統管理員建的腳本資料夾，排程以一般權限跑時可能寫不進狀態檔；已經做過的查看指令不用重做
- **不對的話**：停。不是醫師的帳號就不往下做；公開文件站打不開（主機連不到外網）→ 改用手機看這一冊，指令照著打

### B-05 看 Python

```powershell
py -0p
python --version
```

- **會看到**：`py -0p` 列出 `-V:3.x` 與 `python.exe` 的路徑；`python --version` 印出 `Python 3.x.x`。**3.8 以上**才能用 `.py` 版
- **沒有 `py` 但 `python` 有**：本冊的 `py` 全部換成 `python`
- **`py` 有、`python --version` 什麼都沒印**：`python` 指到 Microsoft Store 的空殼，不要緊，本冊照用 `py`（1109 現場就是這樣）
- **跳出 Microsoft Store、或兩個都說找不到**：就是沒有裝。停，學長決定裝 Python 或用 `.exe`；都不行就做完 B-06、B-07 收工
- 記下結果：用 `.py` 還是 `.exe`

### B-06 看 OneDrive 有沒有在同步指定資料夾

指令抄自第四冊的雲端同步檢查：

```powershell
$env:OneDrive; $env:OneDriveCommercial
Get-Process | Where-Object { $_.Name -match 'OneDrive|GoogleDrive|Dropbox|Synology|Nextcloud|Box' } | Select-Object Name
```

再用檔案總管開啟 `<指定資料夾>`，看檔案旁邊有沒有雲朵或綠色勾勾的圖示。`<指定資料夾>` 是**透析清單**的資料夾，`values.md` 裡結尾是 `IDH_interface` 的那一個；`Hb_API_Fetch` 底下（含 `hospital_dataset\raw_txt`）是檢驗資料，裡面也有「年-月.txt」，**不是這一個**（1109 現場選錯過）。

接著點檔案總管上方的網址列、按 `Ctrl+C` 複製路徑，回 PowerShell 貼下面這段。**指令原樣貼、不要把路徑改進指令裡**；出現「貼上指定資料夾的路徑:」時才按滑鼠右鍵貼上路徑（前後有引號也沒關係）、按 Enter：

```powershell
$dir = (Read-Host '貼上指定資料夾的路徑').Trim().Trim('"', "'"); Test-Path -LiteralPath $dir
$dir.StartsWith("$env:OneDrive\", 'OrdinalIgnoreCase')
$p = Get-Item -LiteralPath $dir; while ($p) { if ($p.LinkType) { "$($p.FullName) -> $($p.Target)" }; $p = $p.Parent }
```

- 會印兩個 `True`／`False`：第一個是資料夾在不在，第二個是它在不在 OneDrive 的路徑底下；有一段路經過連結（Junction）才會多印一行「… -> …」
- **檔案總管網址列最左邊是雲朵圖示加「開始備份」**：那是 Windows 邀請你用 OneDrive 備份「桌面」，表示**沒有**在備份；**不要按**，按了就開始同步（1109 現場：主機的「桌面」就設在 `<指定資料夾>` 的上層，資料夾名稱裡有 `OneDrive` 但不是現在同步的那個）。要再確認，在同一個視窗貼：

```powershell
[Environment]::GetFolderPath('Desktop')
(Get-Item -LiteralPath $dir).Attributes; Get-ChildItem -LiteralPath $dir -File | Select-Object -First 3 Name, Attributes
```

- **沒在同步會看到**：第一行是桌面的實際位置；資料夾是 `Directory`，檔案只有 `Archive`（可能多 `ReadOnly`）。出現 `ReparsePoint`、`Offline`、`Pinned`、`Unpinned`、`RecallOnDataAccess` 任何一個 → 有雲端同步在管這些檔，停

第一個是 `True` 之後，在同一個視窗確認這是透析清單（只看最新一個 txt 的開頭有沒有 `Date:` 與 `"data_list"`，不印病人資料）：

```powershell
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

```powershell
$parts = $dir.TrimEnd('\').Split('\'); $q = $parts[0] + '\'
foreach ($s in $parts[1..($parts.Count-1)]) { $n = Join-Path $q $s; if (Test-Path -LiteralPath $n) { "有   $n" } else { "沒有 $n"; "$q 底下實際的資料夾："; Get-ChildItem -LiteralPath $q -Directory -Force | Select-Object -ExpandProperty Name; break }; $q = $n }
```

- 印到「沒有 …」那一行就是對不上的那一層，下面列出那一層實際的資料夾名稱。把路徑那一段換成實際名稱，重貼 B-06 那段再確認一次第一個是 `True`；**之後 B-12、B-13、B-14 的 `<指定資料夾>` 都用這個實際路徑**，不用 `values.md` 的。對不出來就停，請學長指出實際的資料夾
- 沒有同步（`True`、`False`、沒有多印、檔案旁沒有圖示）：往下。第一段印的 OneDrive 路徑開頭跟 `values.md` 的路徑不一樣不要緊，以這裡的結果為準

### B-07 看有沒有舊的腳本在跑

```powershell
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' -and "$($_.Actions.Execute) $($_.Actions.Arguments)" -match 'python|\.py|fetch|IDH' } | Select-Object TaskName, State
```

```powershell
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Select-Object ProcessId, CommandLine
```

- 第一個指令找「會執行 Python 或抓取程式的排程工作」，第二個找「現在正在跑的 Python」
- **會看到**：兩個指令都沒印東西（1108 學長說舊腳本與 IDH 都沒在跑）
- **不對的話**：有印出東西就停，跟學長確認是什麼、停用後再往下；認不出的不要自己停

### B-08 決定兩個位置

跟學長定好，抄在手機上：

| 代稱 | 是什麼 | 建議 |
|---|---|---|
| `<指定資料夾>` | 留底 txt 所在的資料夾 | 照 `values.md` |
| `<腳本資料夾>` | 腳本放哪 | 學長要跟資料放一起（1109 定）：`<指定資料夾>` 的**上一層**底下的 `hd-hospital-fetch`，跟 `<指定資料夾>` 並列；**不要**放進 `<指定資料夾>` 裡、也不要放在正在同步的 OneDrive 底下（B-06 已確認沒在同步才行）。學長沒要求就用 `C:\hd-hospital-fetch` |

在 B-06 的同一個視窗貼（`$dir` 是 B-06 填的指定資料夾，`$sf` 是腳本資料夾，B-10 起的指令都用這兩個）：

```powershell
$sf = Join-Path (Split-Path -Parent $dir) 'hd-hospital-fetch'; $sf; Test-Path -LiteralPath $sf
```

- **會看到**：`<指定資料夾>` 的上一層加 `\hd-hospital-fetch`，接著 `False`（還沒建）
- 印出 `True`：已經有人放過，停，跟學長確認
- 學長要用 `C:\hd-hospital-fetch` 的話改貼：`$sf = 'C:\hd-hospital-fetch'`

### B-09 下載（InPrivate 視窗）

1. 開 Edge，按 `Ctrl+Shift+N` 開 InPrivate 視窗
2. 開啟 `github.com/login`，登入**自己的** GitHub；不勾「保持登入」；瀏覽器問要不要存密碼，選「永不」
3. 在 InPrivate 視窗的網址列貼上 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.1.0`，按 Enter；捲到頁面最下面的「Assets」區塊（收合著就點開），點 `Source code (zip)` 下載。顯示 404 是登入的帳號不對（repo 是私人的）。跳出「另存新檔」選位置時，左邊選「下載」（`C:\Users\<帳號>\Downloads`）、檔名不改，按「存檔」；B-10 的指令從這裡找 zip
4. 用 `.exe` 的話，再下載 `fetch_dialysis.exe`、`fetch_dialysis_w.exe`、`transcode_history.exe`、`SHA256SUMS.txt`
5. **關掉整個 InPrivate 視窗**（登入、Cookie、瀏覽紀錄跟著清掉）；開著這一冊的一般視窗不用關，收工時再關（B-21）

- **不對的話**：院內網路連不上 GitHub → 停，這次只做到 B-07；Edge 擋 `.exe` 下載 → 在下載清單選「…」→「保留」，保留不了就改用 `.py` 版

### B-10 解壓縮到腳本資料夾

```powershell
Expand-Archive "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip" -DestinationPath (Split-Path -Parent $sf)
Rename-Item -LiteralPath (Join-Path (Split-Path -Parent $sf) 'hd-hospital-fetch-0.1.0') 'hd-hospital-fetch'
cd -LiteralPath $sf
dir
```

（在 B-08 的同一個視窗做；`$sf` 是空的就回 B-08 貼那一行。）

- **會看到**：`dir` 列出 `fetch_dialysis.py`、`transcode_history.py`、`install-task.ps1`、`uninstall-task.ps1`、`config.example.json`、`README.md` 等；提示字元變成 `PS …\hd-hospital-fetch>`

接著把「下載」資料夾裡的 zip 刪掉：

```powershell
Remove-Item "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.1.0.zip"
```

- **會看到**：不印東西

**只有用 `.exe` 才做（走 `.py` 跳過，貼了也只會出現「找不到」紅字、不會動到任何檔）**：把四個下載的檔搬進來，逐一寫檔名，不用 `*.exe`，免得把醫師「下載」裡其他的 `.exe` 一起搬走：

```powershell
Move-Item "$env:USERPROFILE\Downloads\fetch_dialysis.exe", "$env:USERPROFILE\Downloads\fetch_dialysis_w.exe", "$env:USERPROFILE\Downloads\transcode_history.exe", "$env:USERPROFILE\Downloads\SHA256SUMS.txt" .
```

- 下載的檔名變成 `xxx (1).exe`：「下載」裡原本就有同名的檔，停，跟學長確認

### B-11 解除下載標記、比對雜湊

```powershell
Get-ChildItem -Recurse | Unblock-File
```

**只有用 `.exe` 才做（走 `.py` 跳過）**：比對雜湊：

```powershell
Get-FileHash .\fetch_dialysis.exe, .\fetch_dialysis_w.exe, .\transcode_history.exe -Algorithm SHA256 | Select-Object Hash, Path
Get-Content .\SHA256SUMS.txt
```

- **會看到**：`Unblock-File` 不印東西；兩邊的雜湊一樣（大小寫不同不要緊）
- **不對的話**：雜湊不同 → 刪掉那個 `.exe`，回 B-09 重新下載

### B-12 轉碼：先預演

```powershell
py transcode_history.py $dir
```

- `$dir` 是 B-06 填的指定資料夾，不用自己打路徑
- **會看到**（數字是範例）：

```text
== 預演 ==
- 2026-10.txt：12,345,678 位元組、9600 行；Date: 4800 段；編碼 cp950
- 2026-11.txt：1,234,567 位元組、960 行；Date: 480 段；編碼 cp950

要轉 2 個、已是 UTF-8 0 個、不轉（混合或無法判斷）0 個
這是預演，沒有改任何檔。確認後加 --apply。
```

每個檔的「編碼」怎麼看：

| 編碼 | 意思 | 怎麼做 |
|---|---|---|
| `cp950` | 舊的寫法，要轉 | 往下 B-13 |
| `utf-8` | 已經是新的寫法 | 不用管 |
| `混合` | 同一個檔裡兩種寫法都有 | 停，學長決定；這個檔 B-13 不會轉 |
| `無法判斷` | 有壞掉的字，後面寫第幾行 | 停，學長決定 |

- 後面多一段「解析不出 JSON 的行」：那個檔 B-13 也不會轉。停，學長同意才在 B-13 加 `--allow-bad-json`
- 多一段「API_script 版混寫行」：舊版留下的寫法，不算錯，照常轉
- **當月檔**（例如 `2026-11.txt`）如果停在「混合」「無法判斷」，B-14 起不能做（腳本不會往非 UTF-8 的檔附加）

### B-13 轉碼：實轉

```powershell
py transcode_history.py $dir --apply
$LASTEXITCODE
```

- **會看到**：先印一次跟預演一樣的清單（標題是「== 轉檔前的狀況 ==」），接著：

```text
已備份 2 個檔到 <指定資料夾>\_backup_20261109-1612
- 2026-10.txt：已轉成 UTF-8，比對通過
- 2026-11.txt：已轉成 UTF-8，比對通過

還原：python transcode_history.py --restore "<指定資料夾>\_backup_20261109-1612"
```

接著 `$LASTEXITCODE` 印 `0`。

- **把最後一行「還原：…」整行抄在手機上**，退回時要用（第 3 節）
- **不對的話**：任何一個檔寫「比對不合」「原檔有解析不出 JSON 的行」，或 `$LASTEXITCODE` 不是 `0` → 停。沒轉成的原檔沒被動過；要全部回到轉碼前就照第 3 節 R-2 還原

### B-14 填設定

```powershell
Copy-Item config.example.json config.json
notepad config.json
```

記事本裡只改兩行，其他不動：

| 欄位 | 改成 |
|---|---|
| `"endpoint"` | `values.md` 的院方位址（`http://` 開頭，到 `.php` 為止，**不要**加 `?date=`） |
| `"output_dir"` | `<指定資料夾>`。**每個反斜線要寫兩個**：`D:\資料\IDH` 寫成 `"D:\\資料\\IDH"`。不用自己打：開記事本前先貼 `Set-Clipboard $dir.Replace('\', '\\')`，在記事本裡把 `output_dir` 引號中間原本的值選起來、按 `Ctrl+V` |

存檔（`Ctrl+S`）、關掉記事本。

### B-15 預演一輪

```powershell
py fetch_dialysis.py --dry-run
```

- **會看到**：`2026-11-09 16:20:05 成功 回應 601 列、會寫入 601 列（預演，沒有寫任何檔）`（列數是範例；第一次跑，兩個數字一樣）
- **不對的話**：照《[第十九冊之一](19a-hospital-fetch-reference.md)》第 1 節「出錯對照」查；查不出來就停

### B-16 跑一輪、看結果

```powershell
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 .\fetch-status.json
```

- **會看到**：第一行 `… 成功 回應 601 列、寫入 601 列`；`$LASTEXITCODE` 是 `0`；狀態檔裡 `"result": "ok"`、`"written_rows"` 與 `"response_rows"` 一樣

看當月檔的最後兩行對不對（**只看開頭與長度，不把病人資料印到螢幕上**）：

```powershell
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

```powershell
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
```

用 `.exe` 的話改成：

```powershell
powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -Exe .\fetch_dialysis_w.exe
```

- **會看到**：

```text
已建立工作 hd-hospital-fetch
  帳號：<電腦名稱>\<帳號>（只在使用者登入時執行）
  頻率：每 3 分鐘，第一次在 1 分鐘後
  執行：…pythonw.exe "C:\hd-hospital-fetch\fetch_dialysis.py" --once --config "C:\hd-hospital-fetch\config.json"
  狀態：Ready
看結果：狀態檔（設定檔的 status_file）每輪覆寫；或 Get-ScheduledTaskInfo -TaskName hd-hospital-fetch
```

- 排程跑的時候**不會跳出視窗**，這是正常的
- **不對的話**：紅字寫「執行原則」或「無法載入」→ 停，學長決定（院方的群組原則擋了 PowerShell 腳本）；寫「已經有一個叫 hd-hospital-fetch 的工作」→ 有人裝過，停，跟學長確認

### B-18 看三輪（約 10 分鐘）

每 3 分鐘打一次：

```powershell
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content -Encoding UTF8 .\fetch-status.json
```

- **會看到**：`LastRunTime` 每 3 分鐘往前跳、`LastTaskResult` 是 `0`；狀態檔的 `last_attempt_at` 跟著變、`result` 是 `ok`；`written_rows` 多半是 `0`，有新量測時是幾列
- `LastTaskResult` 的其他數字：`1` 是那一輪失敗（看狀態檔的 `reason`）；`267009` 是正在跑；`267011` 是還沒跑過
- **不對的話**：過了 5 分鐘 `LastRunTime` 都沒變、或連續兩輪 `failed` → 停，照第十九冊之一第 1 節查

### B-19 教學長三件事

| 要做的 | 指令（在 `<腳本資料夾>` 裡打） |
|---|---|
| 停掉 | `powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1` |
| 改頻率（例：5 分鐘） | `powershell -ExecutionPolicy Bypass -File .\install-task.ps1 -IntervalMinutes 5 -Force` |
| 看最近一輪 | `Get-Content -Encoding UTF8 .\fetch-status.json`：`result`、`reason`、`last_success_at`（最後一次成功的時間） |

### B-20 記錄

在手機上記，回去後寫進私人 repo 的 `deploy/records/1109-hospital-fetch/`：

- 做到哪一步；每一步的「會看到」對不對
- B-05 用 `.py` 還是 `.exe`、Python 版本；B-06 有沒有同步；B-08 的兩個位置
- B-12 每個檔的編碼與大小；B-13 的備份資料夾名稱與還原指令
- B-16 的回應列數；B-18 三輪的時間與 `written_rows`
- 每個斷點學長怎麼決定
- B-09 用哪個 GitHub 帳號登入、幾點關掉 InPrivate 視窗
- 不記：院方回應的內容、病人的姓名與病歷號

### B-21 收工前看一眼

- InPrivate 視窗已關、「下載」資料夾裡沒有留下 zip 與 `.exe`；最後關掉開著這一冊的 Edge 視窗（公開文件站，不留登入，留下瀏覽紀錄也無妨）
- `Get-ScheduledTaskInfo -TaskName hd-hospital-fetch` 的 `LastTaskResult` 是 `0`
- 本系統沒有動：`.env` 的院方位址維持空白（讀檔模式排第二次進院）
- **不重開機**（同一台還有另一個專案，第十八冊之二 A-04）

## 3. 退回

學長說「不要了」或斷點決定退回時，在 `<腳本資料夾>` 裡依序做：

| # | 做什麼 | 指令 |
|---|---|---|
| R-1 | 停排程 | `powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1`，會看到「已移除工作 hd-hospital-fetch」 |
| R-2 | 歷史 txt 回到轉碼前 | B-13 抄下的那一行（`python` 依 B-05 換成 `py`）：`py transcode_history.py --restore "<指定資料夾>\_backup_…"`，每個檔會看到「已還原」 |
| R-3 | 刪腳本 | `cd ..`，再 `Remove-Item -Recurse -LiteralPath $sf`（`$sf` 是空的就照第 0 節第 6 點先設好） |

- R-2 之後，B-16 起附加到當月檔的那幾段也會一起被蓋回去（還原是整個檔換回備份）
- 備份資料夾 `_backup_…` 不刪，留給學長

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊總覽](index.md)
