# 第二十二冊 · 抓取腳本上線（詳細版）

版本：v0.1　文件狀態：草案（1116 由第十九冊、之一整理）　編號：沿用第二十一冊的 `AF-xx`

上層手冊：《[第二十一冊 · 抓取腳本上線（簡易版）](21-api-quick.md)》

> **照第二十一冊做，畫面跟「成功」不一樣時翻這一冊同一個編號。** 這裡寫：為什麼這樣做、每一種不對的情形怎麼處理、1109 現場遇過什麼。**「停」就是斷點：停下來跟學長決定，不要自己往下做。**
>
> 訊息原文來自 `hd-hospital-fetch` v0.3.0（`fetch_dialysis.py`、`install-task.ps1`）。腳本改了訊息或參數，回頭核對這一冊與第二十一冊。

> **公開範圍**：院方位址、D 槽的舊路徑、帳號、主機名稱不寫在這裡，看私人 repo 的 `deploy/records/1108-hospital-api/values.md`；現場值記在手機，回來寫進 `deploy/records/MMDD-主題/`。

## 摘要

- 第 1 節：先懂的五件事（腳本做什麼、動到哪些檔、結束碼、兩個變數、PowerShell 怎麼開）
- 第 2 節：AF-01～AF-12 每一步的「為什麼」與「不對的話」
- 第 3 節：出錯訊息總表（抓取腳本與排程）
- 第 4 節：中途收工（排程還沒裝就得走）
- 第 5 節：主機不是 1109 的樣子時（沒有腳本或沒有 `config.json`）
- 第 6 節：一頁速查
- 檢驗資料（`hb`）1111 起不做（學長答 A-5 不用這邊處理），這一趟不碰 `Hb_API_Fetch`

## 1. 先懂的五件事

1. **腳本做什麼**：每 3 分鐘問院方 API「今天的透析清單」，把**新的或變了的列**附加到 `<指定資料夾>\YYYY-MM.txt`（一個月一個檔），再把這一輪的結果寫進狀態檔 `fetch-status.json`；同一筆不會重複寫。v0.3.0 起只在 `fetch_hours`（07:00～23:00）裡抓，時段外不打院方 API
2. **動到的檔只有三處**：當月 txt（只附加）、狀態檔（每輪覆寫；這一趟起放在 `<指定資料夾>` 裡，本系統要讀它）、腳本資料夾的 `state\`（去重用，跟著搬到 C 槽，所以搬完不會把整天的列重寫一次）
3. **結束碼**：每跑完一支打 `$LASTEXITCODE`。`0` 成功（含「跳過」「時段外」），`1` 失敗，`2` 參數或設定錯
4. **兩個變數**：`$dir`＝指定資料夾（`…\API_Fetch\IDH_interface`），`$sf`＝腳本資料夾（`…\API_Fetch\hd-hospital-fetch`）。PowerShell 關掉就不見，重開先貼第二十一冊 AF-04 方框那一行
5. **PowerShell 開一般的**：開始 → 打 `powershell` → 直接 Enter。`Ctrl+Shift+Enter`、`Win+X` 再按 `A` 都是系統管理員。用系統管理員建的檔，排程以一般權限跑時可能寫不進去（1109 現場開成系統管理員過）

## 2. 各步驟

### AF-01 出發前

- Release 頁 404：登入的不是 `94sh09sh19sh`（repo 是私人的），換帳號
- 手機看不到 `values.md`：用手機的 GitHub App 開私人 repo `v0` 的 `deploy/records/1108-hospital-api/values.md`；開不了就先在電腦上把 D 槽路徑抄到手機筆記（院方位址 `config.json` 已有）

### AF-02 對的主機、對的帳號

- 為什麼開在主機上：主機連得到外網，用主機的瀏覽器開公開文件站、整行複製（程式碼框右上角有複製鈕），比看手機打字少打錯；`Alt+Tab` 在瀏覽器與 PowerShell 之間切換
- 一般視窗**不要登入 GitHub**；下載用 AF-05 的 InPrivate 視窗，關掉就清乾淨
- `whoami` 的帳號看不出是誰（例如 `user`）：問學長
- 不是醫師的帳號：**停**
- 標題有「系統管理員」：關掉重開一般的；已經做過的查看指令不用重做
- 公開文件站打不開：改用手機看這一冊，指令照著打

### AF-03 看現況

| 不對的情形 | 怎麼做 |
|---|---|
| 第二行印出 `hd-hospital-fetch` 工作 | 有人裝過排程。**停**，跟學長確認；確定要搬才先 `uninstall-task.ps1` |
| 第三行印出 Python 的程式 | 有東西正在跑。**停**，跟學長確認是什麼，認不出的不要自己停 |
| 第四行第一個 `False` | 最常見：把路徑改進第一行 `Read-Host` 的引號裡（1109、1116 都發生過），畫面只把路徑當提示印出來、按 Enter 時沒貼東西，`$old` 是空的。第一行原樣重貼、提示出現後才貼路徑，再重貼第四～六行。不是這個就是路徑貼錯，或主機不是 1109 的樣子。核對 `values.md`；真的沒有就照第 5 節 |
| 第四行第二個 `True` | C 槽已有人放過 `API_Fetch`。**停**，跟學長確認 |
| C 槽可用不到 20 GB | **停**，回報；搬過去的約 8 GB，之後每月還會長 |
| 最後一行列出工作 | 有排程指著 `API_Fetch`（多半是學長自己排的 `hb_online_v2.py`）。**停**，跟學長確認：搬完改名後它找不到 D 槽舊路徑，會失敗或在 D 槽重建資料夾；由學長先停掉，或搬完後他自己改成 C 槽路徑。認不出的不要自己停 |

為什麼搬 C 槽：1109 時 D 槽只剩 13 GB，估計 12 月中旬就滿（學長 1114 答 K-2 ①）。

### AF-04 搬到 C 槽

- robocopy 的結束碼 `0`～`7` 都是成功（`1`＝有複製檔），`8` 以上是有檔沒複製到 → **停**；舊的完全沒動，照舊在 D 槽做也可以（學長決定；那就跳過改名，`$new` 用 D 槽的 `API_Fetch` 路徑，AF-06 的 `status_file` 也寫 D 槽）
- 兩行的檔數或位元組不一樣：**停**，不改名，回報
- 改名出現紅字（存取被拒、檔案正在使用中）：關掉開在那個資料夾的檔案總管與記事本再試；還是不行就停
- 為什麼改名不刪：學長的其他東西可能還指著舊路徑，改名之後一用就會發現；刪不刪學長決定
- 搬的是整個 `API_Fetch`（`IDH_interface`、`Hb_API_Fetch`、`hd-hospital-fetch`），`hb` 雖然不做，資料一起搬。學長的 `hb_online_v2.py` 與它的資料都在 `Hb_API_Fetch` 裡，跟著搬過去、不改內容；它的 `output_dir` 是相對路徑，學長之後在 C 槽的 `Hb_API_Fetch` 裡跑就好（AF-12 跟學長講路徑改了時一起講）。AF-03 最後一行有印出排程就不能直接搬

### AF-05 換 v0.3.0

- 印出 `0.1.0`：複製沒成功，從第一行再做一次
- 找不到 zip：看「下載」裡的實際檔名（例如 `hd-hospital-fetch-0.3.0 (1).zip`），改 `$z` 那一段
- 院內網路連不上 GitHub：**停**，這一趟只做到 AF-04（v0.1.0 沒有抓取時段，不裝排程）
- Edge 擋下載：在下載清單選「…」→「保留」
- 為什麼只換一個檔：v0.3.0 只改了 `fetch_dialysis.py`（加抓取時段、狀態檔多一欄 `non_numeric_id_rows`），其他檔與 v0.1.0 相同

### AF-06 改設定三處

| 不對的情形 | 怎麼做 |
|---|---|
| 紅字「無效的 JSON」 | 多半是少了逗號，或反斜線只寫一個。回記事本：每個 `\` 寫成 `\\`、`fetch_hours` 前一行結尾有逗號 |
| `fetch_hours` 是空的 | 那一行沒存到，重開記事本看 |
| `output_dir` 還是 D 槽 | 貼上前沒先選起原本的值；重做 |

- 為什麼 `status_file` 要放進 `<指定資料夾>`：本系統讀檔時只掛那一個資料夾（唯讀），狀態檔在外面就看不到「抓取腳本最近一輪」
- 為什麼 07:00～23:00：學長 1114 答 F-6 ①，夜間不打院方 API
- 🧪 改成 `00:00-24:00` 只為了半夜也能演練；院內一律 `07:00-23:00`

### AF-07 寫檔前兩個檢查

| 不對的情形 | 怎麼做 |
|---|---|
| 第一個 `True` 而且標題有「系統管理員」 | 關掉重開一般的，再檢查一次 |
| 第一個 `True`，標題沒有「系統管理員」 | 這台關了 UAC，一般視窗也是最高權限，照樣往下 |
| 第二行紅字「存取被拒」 | 一般權限寫不進腳本資料夾。**停**，回報 |
| 第三行紅字「找不到」 | 這個月還沒有月份檔，正常；AF-09 會建 |
| 修改時間在幾分鐘內 | 有別的程式在寫當月檔。**停**，跟學長確認是誰（學長 1114 答 K-1：月份檔是從正式 IDH 主機搬來的，這台不該有人寫） |

想看最後幾行又不印病人資料：

```powershell
Get-Content -LiteralPath $m -Tail 6 -Encoding UTF8 | ForEach-Object { if ($_ -like 'Date:*') { $_ } else { '（{0} 字）' -f $_.Length } }
```

每段之間夾一行 `（0 字）` 是舊檔的寫法，不影響，記下來（AF-12）。

### AF-08 預演

- 多印「病歷號不是純數字的 N 列（照樣保留）」：不是錯，記下 N，不記病歷號
- 其他訊息：查第 3 節；查不出來就**停**

### AF-09 跑一輪

- 結束碼不是 `0`、`result` 不是 `ok`、第二個不是 `True`、主控台印出姓名或病歷號：**停**
- 第二輪寫了幾百列（整天）：`state\` 沒跟著搬或被刪了。**停**，回報；記下多寫了一次整天

### AF-10 裝排程

| 不對的情形 | 怎麼做 |
|---|---|
| 紅字有「執行原則」或「無法載入」 | 院方群組原則擋 PowerShell 腳本。**停**，學長決定 |
| `已經有一個叫 hd-hospital-fetch 的工作` | 有人裝過。**停**，跟學長確認；確定要換才加 `-Force` |
| `執行：` 指到 D 槽 | 不在 `$sf` 裡打的。`cd -LiteralPath $sf`、加 `-Force` 重裝 |

- 排程「只在使用者登入時執行」、用目前的帳號：主機重開機後要有人登入才會跑（跟本系統的 Docker Desktop 一樣）
- 用 `.exe` 版的話：`install-task.ps1 -Exe .\fetch_dialysis_w.exe`（1109 用的是 `.py`）

### AF-11 看三輪

| `LastTaskResult` | 意思 |
|---|---|
| `0` | 那一輪成功（含時段外） |
| `1` | 那一輪失敗，看狀態檔的 `reason`，對照第 3 節 |
| `267009` | 正在跑 |
| `267011` | 還沒跑過，`LastRunTime` 會是 `1999/11/30`；過了 `NextRunTime` 再看（1116 模擬實測：裝完約 2 分鐘才跑第一輪） |

- 過了 5 分鐘 `LastRunTime` 都沒變，或連續兩輪 `failed`：**停**，查第 3 節
- 狀態檔停在 22:5x 那一輪：23:00 後不抓，正常

### AF-12 記錄（手機上記，回來寫進私人 repo 的 `deploy/records/MMDD-主題/`）

- 做到哪一步、每一步的「成功」對不對、各步的時間
- AF-03 的 C 槽可用空間；AF-04 的檔數與位元組、舊資料夾改成什麼名字、學長說何時刪
- AF-05 的 `--version`；AF-08、AF-09 的回應列數；狀態檔的 `non_numeric_id_rows`（不是 0 就記數字）
- AF-11 三輪的時間與 `written_rows`
- 每個斷點學長怎麼決定；InPrivate 視窗用哪個帳號登入、幾點關掉
- **不記**：院方回應的內容、病人的姓名與病歷號

## 3. 出錯訊息總表

| 畫面上看到 | 意思 | 怎麼做 |
|---|---|---|
| `設定錯誤 找不到設定檔` | 不在 `$sf` 裡 | `cd -LiteralPath $sf` 再試 |
| `設定錯誤 設定檔不是合法的 JSON` | `config.json` 寫壞了 | 回 AF-06 |
| `設定錯誤 endpoint 要是 http 或 https 開頭` | 位址被改壞 | 對照 `values.md`（`http://` 開頭到 `.php`，不加 `?date=`） |
| `設定錯誤 fetch_hours 的格式是 "HH:MM-HH:MM"…`、`…開始要早於結束（不跨午夜）`、`…時刻要在 00:00～24:00 之間` | AF-06 加的那一行寫錯 | 改成 `"fetch_hours": "07:00-23:00"`（半形冒號與減號） |
| `失敗 重試 3 次仍失敗；最後一次：連線失敗：…` | 連不到院方 API | 用瀏覽器開 `<院方位址>?date=<今天，YYYY-MM-DD>` 看得到資料嗎；看不到就**停**。🧪 模擬院方 API 沒開，請開發端開 |
| `失敗 重試 3 次仍失敗；最後一次：HTTP 404` 或其他數字 | 院方回錯誤 | 位址的路徑抄錯；對了還是錯就**停** |
| `失敗 重試 3 次仍失敗；最後一次：逾時（>30 秒）` | 院方太慢 | 再試一次；連續逾時就**停** |
| `失敗 回應裡找不到 JSON 內容`、`回應的 JSON 無法解析`、`回應裡沒有 data_list 陣列` | 院方回的不是透析清單（維護頁、登入頁） | **停** |
| `失敗 當月的留底檔不是 UTF-8，先用 transcode_history.py 轉檔` | 當月檔是舊寫法 | 第 5 節第 3 步轉碼；轉不了就**停** |
| `跳過 上一輪還沒結束` | 另一輪正在跑 | 正常，等一下 |
| `時段外 只在 07:00-23:00 抓，這一輪不打院方 API` | 時段外，沒打 API、沒寫檔，結束碼 `0` | 正常 |
| `成功 … 病歷號不是純數字的 N 列（照樣保留）` | 有病歷號帶英文字母的列 | 不是錯，記下 N |
| `py` 說找不到指令 | 沒有 Python launcher | 換成 `python`；兩個都沒有就**停**（學長決定裝 Python 或用 `.exe`） |
| Windows 跳出「Windows 已保護您的電腦」 | `.exe` 第一次執行 | 有做 `Unblock-File` 就不會出現；出現了按「其他資訊」→「仍要執行」，雜湊對過才可以 |

## 4. 中途收工（AF-10 排程還沒裝就得走）

1. 確認沒留下會自己跑的東西：`Get-ScheduledTask -TaskName hd-hospital-fetch -ErrorAction SilentlyContinue` 沒印東西；「下載」裡沒有 zip
2. 做過 AF-04：C 槽那份與 D 槽改了名的舊資料夾都留著，跟學長說一聲；沒有排程就不會自己跑
3. 關掉 PowerShell 與瀏覽器，確認 InPrivate 視窗已關、一般視窗沒登入 GitHub；🏥 **不重開機**
4. 問學長下次哪個時段可以接（從 AF-08 起，含看三輪約 10 分鐘）
5. 照 AF-12 記：做到哪一步、學長的決定
6. **本系統不換版**（第二十三冊不做）

## 5. 主機不是 1109 的樣子時

AF-03 第四行是 `False`，核對路徑後確定 D 槽沒有腳本或沒有 `config.json`。這一節是從零放一次，約多 30 分鐘；學長同意才做。

1. **確認指定資料夾沒在雲端同步**：用檔案總管開 `IDH_interface`，檔案旁不能有雲朵或綠色勾勾；網址列最左邊的「開始備份」**不要按**（1109 現場那是 Windows 邀請備份桌面，表示沒在同步）。再貼 `(Get-Item -LiteralPath $dir).Attributes; Get-ChildItem -LiteralPath $dir -File | Select-Object -First 3 Name, Attributes`，出現 `ReparsePoint`、`Offline`、`Pinned`、`RecallOnDataAccess` 任何一個就**停**
2. **放腳本**：照 AF-05 下載 v0.3.0 的 zip（先不刪），然後 `Expand-Archive -LiteralPath $z -DestinationPath $new`、`Rename-Item (Join-Path $new 'hd-hospital-fetch-0.3.0') 'hd-hospital-fetch'`、`cd -LiteralPath $sf`、`Get-ChildItem -Recurse | Unblock-File`、`Copy-Item config.example.json config.json`，最後 `Remove-Item -LiteralPath $z`
3. **轉碼（只有歷史 txt 不是 UTF-8 才需要）**：`py transcode_history.py $dir` 預演（不寫檔；全部檔讀進記憶體，約每 1 GB 一分鐘，需要約合計 4.5 倍的可用記憶體）。全部是 `utf-8`（「要轉 0 個」）就跳過；有 `cp950` 才 `py transcode_history.py $dir --apply`，把最後一行「還原：…」抄下來。`混合`、`無法判斷`、「解析不出 JSON 的行」都**停**，學長決定
4. **填設定**：`notepad config.json`，`"endpoint"` 填 `values.md` 的院方位址（到 `.php` 為止），`"output_dir"`、`"status_file"`、`"fetch_hours"` 照 AF-06（範例檔已有 `fetch_hours`）
5. 接著從 AF-07 做下去

## 6. 一頁速查

```powershell
cd -LiteralPath C:\API_Fetch\hd-hospital-fetch
py fetch_dialysis.py --version
py fetch_dialysis.py --dry-run
py fetch_dialysis.py --once
$LASTEXITCODE
Get-Content -Encoding UTF8 C:\API_Fetch\IDH_interface\fetch-status.json
powershell -ExecutionPolicy Bypass -File .\install-task.ps1
Get-ScheduledTaskInfo -TaskName hd-hospital-fetch
powershell -ExecutionPolicy Bypass -File .\uninstall-task.ps1
```

`$LASTEXITCODE`：`0` 成功、`1` 失敗、`2` 設定錯。🧪 路徑的 `C:\API_Fetch` 換成 `C:\hd-sim-fetch\API_Fetch`。

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 第二十一冊 · 抓取腳本上線（簡易版）](21-api-quick.md)　[← 回部署手冊總覽](index.md)
