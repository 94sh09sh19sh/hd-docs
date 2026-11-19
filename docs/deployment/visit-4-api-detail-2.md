# 第四次進院（1109）· 放上院方 API 抓取腳本之二：詳細版（B-12～B-14c）

上層文件：《[第四次進院（1109）· 放上院方 API 抓取腳本](visit-4-api.md)》

> **狀態：已照做 1109，凍結**——做到 B-15（預演一輪成功），B-16 起沒做；結果見《[第四次進院紀錄（1109，做到 B-15）](record-4-1109.md)》。改寫自舊第十九冊；編號 `B-xx`，與主文件同一套。

> 公開範圍與代稱（`<指定資料夾>`、`<院方位址>`、`<腳本資料夾>`）、怎麼開 PowerShell、`$dir`／`$sf` 兩個變數，見《[…之一：詳細版（B-01～B-11）](visit-4-api-detail.md)》開頭與第 0 節。**「不對的話」寫「停」就是斷點：停下來，跟學長決定，不要自己往下做。**

## 摘要

- 這一份是 B-12～B-14c：轉碼預演（B-12）、實轉（B-13）、填設定（B-14），以及 1114 為第五次進院加的 B-14a～B-14c
- B-12 先看檔案大小與可用記憶體：約每 1 GB 一分鐘、要約「合計」4.5 倍的可用記憶體；跑完前畫面不會有輸出
- 全部是 `utf-8`（「要轉 0 個」）就跳過 B-13（1109 現場就是這樣）；`混合`、`無法判斷`、解析不出 JSON 的行都是停
- B-13 實轉後把「還原：…」整行抄下，退回時用
- B-14 只改 `endpoint`、`output_dir` 兩行，反斜線要寫兩個
- 1114 加 B-14a～B-14c（第五次進院用，後來改照 `AF-04`～`AF-06`，第 4 節）
- 下一步 B-15 預演一輪在《[之三](visit-4-api-detail-3.md)》

## 2. 現場步驟（續）

### B-12 轉碼：先預演

先看檔案有多大、主機還有多少記憶體（預演會把每個檔整個讀進記憶體逐行檢查，大檔要等很久）：

```powershell
Get-ChildItem -LiteralPath $dir -Filter *.txt | Sort-Object Length -Descending | Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB,1)}}
"合計 {0:N0} MB" -f ((Get-ChildItem -LiteralPath $dir -Filter *.txt | Measure-Object Length -Sum).Sum/1MB)
"可用記憶體 {0:N1} GB" -f ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)
```

- **會看到**：每個 txt 的大小（大的排前面）、合計、可用記憶體
- 速度約每 1 GB 一分鐘；**所有檔會同時留在記憶體**，需要約「合計」的 4.5 倍可用記憶體（v0.1.0 實測；1109 現場 7.7 GB 約 35 GB，可用 40 GB，很緊）。跑的時候開「工作管理員」看記憶體，接近 100%、主機變很卡就按 `Ctrl+C`
- **合計 × 4.5 超過可用記憶體**：停，回報大小，不跑預演（1109 現場預演跑很久、按 `Ctrl+C` 中斷過；預演不寫檔，中斷不會壞任何東西）

```powershell
py transcode_history.py $dir
```

- `$dir` 是 B-06 填的指定資料夾，不用自己打路徑
- **跑完之前畫面不會有任何輸出**（全部檔讀完才一次印出清單），合計幾 GB 就大約等幾分鐘，不要按 `Ctrl+C`（1109 現場合計 7.7 GB）
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
- **全部都是 `utf-8`（「要轉 0 個」）**：不用轉碼，**B-13 跳過**，直接 B-14（1109 現場 24 個檔全是 UTF-8，學長之前已轉過）
- `utf-8` 的檔寫「解析不出 JSON 的行」：不轉碼就不受影響；不是當月檔就只回報學長（1109 現場 `2026-02.txt` 第 49 行一行）
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

- **把最後一行「還原：…」整行抄在手機上**，退回時要用（《[院方 API 抓取腳本的維運](ref-fetch-script-2.md)》的退回）
- **不對的話**：任何一個檔寫「比對不合」「原檔有解析不出 JSON 的行」，或 `$LASTEXITCODE` 不是 `0` → 停。沒轉成的原檔沒被動過；要全部回到轉碼前就照《院方 API 抓取腳本的維運》退回的 R-2 還原
- 1109 現場要轉 0 個，B-13 沒做

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

> **1111 補**：本系統之後讀檔時要讀得到狀態檔，屆時 `status_file` 要改指到 `<指定資料夾>` 裡。**1114 改**：同一趟換版，提前到 B-14c 一起改。

### B-14a 搬到 C 槽（1114 加，學長答 K-2 ①）

> 第五次進院（1116）改照《[第五次進院（1116）任務一 · 抓取腳本上線](visit-5-api.md)》`AF-03`（前置檢查）＋`AF-04`（複製、比對、改名）做；1116 改名被拒、改用檔案總管改名成功，三輪成功後學長把 D 槽舊資料夾刪了（《[第五次進院紀錄](record-5-1116.md)》SR-03）。

1109 時 D 槽只剩 13 GB，估計 12 月中旬就滿（《[院方 API 介接之二之一](../notes/hospital-api-fetch-methods-questions-answered.md)》K-2）。整個 `API_Fetch`（`IDH_interface`、`Hb_API_Fetch`、`hd-hospital-fetch`）**複製**到 `C:\API_Fetch`，比對一樣之後舊的改名留著，**不刪**；刪不刪由學長決定（B-20 記下）。腳本的 `state\` 跟著搬，搬完不會重寫整天的列。

先確認排程還沒裝、沒有 Python 在跑（有的話停，跟學長確認）、C 槽還沒有 `API_Fetch`。`$dir` 這時還是 D 槽的指定資料夾，空的就照第 0 節第 6 點用 D 槽的路徑設：

```powershell
Get-ScheduledTask -TaskName hd-hospital-fetch -ErrorAction SilentlyContinue
Get-Process python*, py -ErrorAction SilentlyContinue
$old = Split-Path -Parent $dir; $new = 'C:\API_Fetch'; $old; Test-Path -LiteralPath $new
"C 槽可用 {0:N1} GB" -f ((Get-PSDrive C).Free/1GB)
```

- **會看到**：前兩行沒印東西；接著 D 槽的 `…\API_Fetch`、`False`；C 槽可用幾百 GB（1109 是 763 GB）
- 第三行 `True`：C 槽已經有人放過，停，跟學長確認

複製（約 8 GB，幾分鐘；結束碼 0～7 都是成功，8 以上是有檔沒複製到）：

```powershell
robocopy $old $new /E /COPY:DAT /DCOPY:T /R:1 /W:1 /NFL /NDL /NP
$LASTEXITCODE
```

- **會看到**：最後一段表格的「失敗」欄都是 `0`；`$LASTEXITCODE` 是 `1`（複製了檔）
- **不對的話**：結束碼 8 以上或「失敗」不是 0 → 停，舊的完全沒動，照舊在 D 槽做也可以（學長決定）

比對兩邊的檔數與大小：

```powershell
foreach ($p in $old, $new) { $f = Get-ChildItem -LiteralPath $p -Recurse -File -Force; '{0} 個檔、{1:N0} 位元組' -f $f.Count, ($f | Measure-Object Length -Sum).Sum }
```

- **會看到**：兩行一模一樣
- **不對的話**：不一樣 → 停，不改名，回報

舊的改名（之後沒有東西會再寫到舊路徑），再換成新的位置：

```powershell
Rename-Item -LiteralPath $old ('API_Fetch_搬到C槽_' + (Get-Date -Format 'MMdd'))
$dir = 'C:\API_Fetch\IDH_interface'; $sf = 'C:\API_Fetch\hd-hospital-fetch'; cd -LiteralPath $sf; dir config.json
```

- **會看到**：`dir` 列出 `config.json`（1109 B-14 填的那一份）；提示字元變成 `PS C:\API_Fetch\hd-hospital-fetch>`
- 改名出現紅字（存取被拒、檔案正在使用中）：關掉開在那個資料夾的檔案總管與記事本再試；還是不行就停
- 學長的文件與 APP 組讀檔的路徑要跟著改成 C 槽，請學長轉告（B-20 記下）

### B-14b 換成 v0.3.0（1114 加）

> 第五次進院改照 `AF-05` 做。

主機上是 v0.1.0。v0.3.0 只改了 `fetch_dialysis.py`（加抓取時段、狀態檔多一欄），**只換這一個檔**，其他檔與 `config.json`、`state\` 不動。

照 B-09 的做法（InPrivate／無痕視窗登入自己的 GitHub），網址改成 `https://github.com/94sh09sh19sh/hd-hospital-fetch/releases/tag/v0.3.0`，下載 `Source code (zip)` 到「下載」，關掉 InPrivate 視窗。接著：

```powershell
$z = "$env:USERPROFILE\Downloads\hd-hospital-fetch-0.3.0.zip"; $tmp = Join-Path $env:TEMP 'hd-fetch-0.3.0'
Expand-Archive -LiteralPath $z -DestinationPath $tmp -Force
Copy-Item -LiteralPath (Join-Path $tmp 'hd-hospital-fetch-0.3.0\fetch_dialysis.py') -Destination $sf -Force
Remove-Item -LiteralPath $tmp -Recurse -Force; Remove-Item -LiteralPath $z
Unblock-File -LiteralPath (Join-Path $sf 'fetch_dialysis.py')
py fetch_dialysis.py --version
```

- **會看到**：最後一行 `0.3.0`
- **不對的話**：印出 `0.1.0` → 複製沒成功，從第一行再做一次；找不到 zip → 看「下載」裡的檔名（`hd-hospital-fetch-0.3.0 (1).zip` 之類），改 `$z`

### B-14c 改設定三處（1114 加）

> 第五次進院改照 `AF-06` 做。

```powershell
Set-Clipboard $dir.Replace('\', '\\')
notepad config.json
```

| 欄位 | 改成 |
|---|---|
| `"output_dir"` | 引號中間原本的 D 槽路徑選起來、按 `Ctrl+V`（變成 `C:\\API_Fetch\\IDH_interface`） |
| `"status_file"` | `"C:\\API_Fetch\\IDH_interface\\fetch-status.json"`（本系統讀檔要在指定資料夾裡看得到狀態檔，《[第五次進院（1116）任務二 · 本系統換版上線之三：上線準備清單](visit-5-system-prep.md)》A-13 第 3 步） |
| 新加一行 | 在最後一個欄位（`"lock_stale_seconds": 900`）後面加逗號，下一行加 `"fetch_hours": "07:00-23:00"`（學長答 F-6 ①：只在 07:00～23:00 抓，時段外不打院方 API） |

存檔、關掉記事本，檢查：

```powershell
Get-Content -Raw -Encoding UTF8 config.json | ConvertFrom-Json | Select-Object output_dir, status_file, fetch_hours, dedup, line_format
```

- **會看到**：`C:\API_Fetch\IDH_interface`、`C:\API_Fetch\IDH_interface\fetch-status.json`、`07:00-23:00`、`row`、`segment`
- **不對的話**：紅字「無效的 JSON」→ 多半是少了逗號或反斜線只寫一個，回記事本對照上表改；`fetch_hours` 是空的 → 那一行沒存到

上一份：《[…之一：詳細版（B-01～B-11）](visit-4-api-detail.md)》｜下一份：《[…之三：詳細版（B-15～B-21、退回、對照）](visit-4-api-detail-3.md)》

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-4-api-detail-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第四次進院（1109）· 放上院方 API 抓取腳本之一：詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
