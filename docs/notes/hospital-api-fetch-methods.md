# 院方 API 的四種抓取方式

版本：v0.1　文件狀態：草案（2026-11-08 開立）　適用讀者：FDE 工程團隊、使用者本人

子文件：《[之一：1107 學長答覆後的現況與應對](hospital-api-fetch-methods-status.md)》（介接方式要改、週一進院前後要做什麼）、《[之二：1108 給學長的問題清單](hospital-api-fetch-methods-questions.md)》、《[之四：下一次進院的工作規劃（兩支都跑起來）](hospital-api-fetch-methods-next-visit-plan.md)》

---

## 摘要

- 讀院方透析清單 API 的程式目前有四份：學長 Google Drive 共享的 `API_script` 版、成大版、斗六版、本系統（迭代 15）
- 前三份都是 IDH 系統的 `scripts/fetch_API.py`，對院方送出的請求一樣（`GET ?date=今天`），差在**什麼時候抓、失敗怎麼辦、抓完存在哪**
- 成大版與 `API_script` 版**只在有人開著儀表板時才抓**；斗六版改成 `django-crontab` 每 5 分鐘，但仍要整個 Django 專案在；本系統是後端自己排程、預設每 3 分鐘
- 三份 Python 都把**原始回應附加到文字檔留底**（含全中心姓名、病歷號的明文）：`API_script` 版一個檔一直長，成大、斗六版每月一個 `YYYY-MM.txt`；本系統不寫檔
- `API_script` 版的留底「`Date:` 與資料在同一行」，成大版的 `refetch_from_txt.py` 會把整行跳過——若歷史 txt 有它寫的，重建時會少資料（第 3 節）
- 三份 Python 寫檔都沒指定編碼，在 Windows 上預設是 big5（cp950），姓名有罕用字時整次抓取丟失（第 4 節）
- 本系統的介接是照這三份重寫的，不是改寫；與 `fetch_API.py` 的逐項差異在第 1、2.4 節
- 1107 學長要求改成「主機上的獨立腳本抓、存成檔，本系統改讀檔」，怎麼做寫在子文件

## 0. 四種方式從哪來

| # | 方式 | 來源 | 狀態 |
|---|---|---|---|
| 1 | `API_script` 版 | 學長以連結與使用者的帳號共享 Google Drive 資料夾，1108 時只有三個檔：`fetch_API.py`、`hb_online_v2.py`、`API raw data address.docx`（1108 晚上學長再放上 `hb` 用的 `collector_common.py`、`config.json`）；已全部下載到 repo 外的 `old_API_ref/API_script/`（另有使用者自己存的 `link.txt`，只記連結） | 1107 學長說：**應該是舊版本，可能上傳錯了**（子文件第 2 節） |
| 2 | 成大版 | 采綾學姊給的 IDH 系統 repo，`RyanJ` 分支，clone 在 `ref_project/成大醫院IDH系統_RyanJ/` | 學長說主機上裝的「都是成大 IDH」 |
| 3 | 斗六版 | 使用者先前取得的斗六分院 IDH 系統，`ref_project/斗六分院IDH系統的code/` | 斗六那一台主機，與本院區無關；學長說「斗六搬過來也要改」 |
| 4 | 本系統 | `apps/api/src/modules/hospital-sync/`（迭代 15，TypeScript） | 院內主機 `v0.4.0`，位址空白、**沒在打**；只有 1029 探測打過一次 |

不算在內的：`hb_online_v2.py` 是照病人逐一查檢驗資料的另一支收集程式，打的是另一支 API、不是透析清單（1109 補齊程式後確認），見《[同院 IDH 系統參考調查之一](idh-reference-survey-api-script.md)》第 4 節。

三份 Python 都**只讀**；`ref_project/`、`old_API_ref/` 都在專案 repo 外，不 commit。

## 1. 總表

| 比較 | ① `API_script` 版 | ② 成大版 | ③ 斗六版 | ④ 本系統 |
|---|---|---|---|---|
| 端點 | 成大那一台 `dialysislist.php` | 同 ① | 斗六那一台 | 同 ①，位址放設定目錄的 `.env`（DEP-46） |
| 位址從哪來 | 寫死在程式 | 寫死 | 寫死 | 環境變數 `HOSPITAL_API_BASE_URL`，空白就不抓 |
| 查詢 | `?date=今天` | 同左 | 同左；另有 `?case_number=&start_date=&end_date=` 查一位病人 45 天 | `?date=今天` |
| 「今天」怎麼算 | `datetime.now()`，跟機器時區 | 同左 | 同左 | 固定 +08:00（容器預設 UTC，照機器算會在早上 8 點前抓到前一天） |
| 什麼時候抓 | 由 IDH 系統呼叫，同 ② | 儀表板頁面被開啟、且分鐘數是 3 的倍數；或床位全空時 | `django-crontab` 每 5 分鐘（`*/5 * * * *`） | 後端啟動 5 秒後第一次，之後依營運參數，預設 3 分鐘，護理站可調 |
| 要什麼才跑得起來 | Django 專案＋有人開頁面 | 同左 | Django 專案＋系統的 crontab（`manage.py crontab add`） | 本系統的 `api` 容器 |
| 逾時 | 沒有 | 沒有 | 30 秒 | 30 秒 |
| 重試 | 沒有 | 沒有 | 3 次，間隔 5 秒 | 失敗後再試 3 次，間隔 1、2、3 秒 |
| 同時只跑一次 | 沒有 | 沒有 | 有一把執行緒鎖（但跨行程擋不住，第 2.3 節） | 有，排程與「立即同步」撞在一起時共用同一次 |
| 去掉開頭 `<meta>` | `strip(...)` 逐字元刪 | 同左 | 同左 | 從第一個 `{` 開始解析 |
| 非 2xx | `raise_for_status()` 丟例外 | 同左，由 `corn_job` 接住 | 算一次失敗、重試 | 記失敗原因，不丟例外 |
| 2xx 但不是 200 | `data_list` 沒設定，`UnboundLocalError` | 補了 `else: data_list = []` | 同 ② | 視為成功讀回應 |
| 抓到空資料 | 照樣轉 CSV，`temp.csv` 蓋成空的 | 不轉 CSV，`temp.csv` 留著上一次 | 照樣轉 CSV，蓋成空的 | 寫一筆抓取紀錄，沒有透析就沒有東西要同步 |
| 欄數檢查 | 沒有，照位置套 51 個欄名 | 同左 | 同左 | 每一列都要 51 欄，不對就把那一次透析整次退回 |
| 床位數字開頭的列 | 整列丟掉 | 同左 | 同左 | 全部保留（1029 探測：601 列裡 172 列會被前三份丟掉） |
| 病歷號不是純數字 | 整列丟掉 | 同左 | 同左 | 照 `[A-Za-z0-9-]{4,32}` 檢查，不合格的整次透析退回並寫原因 |
| 去識別化 | 沒有 | 沒有 | `temp.csv` 的病歷號與姓名用固定金鑰加密（115/01/14 加的）；留底 txt 仍是明文 | 不寫檔；位址與病歷號不進任何紀錄 |
| 原始回應留底 | 全部附加到 `data_list_sucess.txt` | 每月一個 `YYYY-MM.txt` | 同 ② | 不留原文，只存回應的 SHA-256 與抓取紀錄 |
| 留底寫在哪 | 執行時的目前目錄 | 同左（Django 專案根目錄） | 同左 | — |
| 主控台輸出 | `save sucesssfully` | 網址、參數、狀態碼，**還有整包原始回應** | 每次嘗試、筆數 | 只寫「怎麼了」，不帶位址也不帶值 |
| 抓完之後 | 拆三份 CSV → SQLite，給預警模型 | 同左 | 同左；另把 45 天歷史附加到 `all_patients_history.csv` | 病人主檔、床位、療程、下機判定（結束體重出現）、四種數值；生命徵象只收有配平板的病人 |
| 測試工具 | 沒有 | `test_api.py`：5 秒逾時，印回應前 100 字 | 沒有 | `hospital-api-probe`：只印結構，不印值、不寫檔、不碰資料庫；模擬院方 API 另有標頭可辨識 |

## 2. 各方式的細節

### 2.1 ① `API_script` 版

```
IDH 系統 views.py 的 corn_job()
   └─ fetchData() → getNowDate() → getAPIResponse()
        GET ?date=今天 → strip <meta> → json.loads → data_list
        附加到 data_list_sucess.txt：「Date: YYYY-MM-DD HH:MM」緊接原始 JSON，再換行
   └─ convertCSV() → 套 51 欄名 → 丟兩種列 → interface/data/temp.csv
```

- 留底的時間戳 `getNowDatee()` 只到分鐘，**後面沒換行**，時間戳與 JSON 在同一行
- 回應是 2xx 但不是 200 時，`data_list` 從沒被設定，回傳時丟 `UnboundLocalError`
- 留著舊的 `# print(data_list)`、`json.dump` 註解；`reorder()` 讀寫路徑前後不一致，沒有人呼叫
- 判斷：留底最簡陋、沒有防呆，**比成大版早**；學長 1107 也說雲端那份應該是舊的

### 2.2 ② 成大版（`RyanJ` 分支）

```
有人開儀表板（area == "dashboard"）且 分鐘 % 3 == 0 ──┐
床位全部是空的（啟動後第一次）──────────────────────┴─ corn_job()
   └─ fetchData()   GET ?date=今天 → 附加到 YYYY-MM.txt
                    「Date: YYYY-MM-DD HH:MM:SS」一行、原始 JSON 一行
                    data 為空就不轉 CSV
   └─ splitCSV()    病人、透析、紀錄三份 CSV
   └─ saveData()    transaction 內寫進 SQLite
```

- **沒有真正的排程**：沒人開頁面就不抓；同一分鐘內每開一次儀表板就再抓一次
- `corn_job` 用 `try` 包住，連線逾時只寫進 log、網站照跑；但 `requests.get` 沒有逾時，院方一慢整個頁面卡住
- 除錯輸出把整包原始回應印到主控台（含全中心的姓名、病歷號）
- `refetch_from_txt.py`：讀目前目錄所有 `YYYY-MM.txt`，跳過空行與 `Date:` 開頭的行，其餘每行 `strip` 後解析，再走 `convertCSV` → `splitCSV` → `saveData` 補回資料庫
- `test_api.py`：打一次固定日期、5 秒逾時，只印狀態碼與前 100 字
- git log 最新幾筆是「清掉大檔」「把資料庫與敏感檔移出追蹤」，資料保護問題見《[同院 IDH 系統參考調查](idh-reference-survey.md)》第 8 節

### 2.3 ③ 斗六版

```
系統 crontab（*/5 * * * *）→ manage.py crontab run → interface.views.corn_job()
   └─ 執行緒鎖：上一次沒跑完就跳過
   └─ fetchData()   最多 3 次、每次 30 秒逾時、間隔 5 秒 → 附加到 YYYY-MM.txt（格式同 ②）
                    convertCSV 前把病歷號與姓名加密
   └─ splitCSV() → saveData()   三步各自 try，一步失敗下一步照做
```

- 儀表板觸發的那兩行已註解掉（標 `[TEST]`），只靠 crontab
- `django-crontab` 是把工作寫進作業系統的 crontab，**要 Linux／Unix 的 cron**；Windows 主機上不能直接用（推論，斗六主機的系統未確認）
- 每次 crontab 叫起來是一個新行程，`threading.Lock` 只在同一個行程裡有效，**擋不住兩次排程重疊**（推論，從程式結構判斷）
- 加密只做在 `temp.csv`；**留底的 `YYYY-MM.txt` 寫的是加密前的原始回應**，仍是明文
- 金鑰檔 `secret.key` 不存在就自動產生一把；固定 IV（16 個 `0`），同一個值每次加密結果相同，才能拿來串接
- 第二種查詢 `fetch_history_stats()`：解密病歷號 → 查該病人前 45 天 → 明文附加到 `all_patients_history.csv` → 算統計值；它把兩組血壓欄位對調了（上層調查第 5 節第 1 點，成大版才對）
- 抓到空資料仍照樣 `convertCSV`，`temp.csv` 會被蓋成空的

### 2.4 ④ 本系統（迭代 15）

```
後端啟動 → 5 秒後 run() → 之後每 N 分鐘（營運參數，預設 3）
   └─ fetchDialysisList()      ?date=院內今天（+08:00），30 秒逾時，失敗再試 3 次
   └─ 模擬院方 API 的標頭 ＋ 正式環境 → 整次作廢（DEP-46）
   └─ parseHospitalApiBody()   從第一個 { 開始
   └─ validateRows()           每列 51 欄；依（病歷號、透析開始時間）分成一次一次的透析
   └─ apply()                  病人主檔 → 床位 → 每次透析：療程、換床、下機、四種數值、生命徵象
   └─ 抓取紀錄＋狀態變了才寫稽核（開始失敗、恢復、拒收）
```

- 檔案：`hospital-api.client.ts`（HTTP）、`hospital-api.format.ts`（解析與驗證，不碰資料庫，探測工具共用）、`hospital-api.adapter.ts`（數值範圍檢查）、`hospital-sync.service.ts`（排程與同步）
- 全有或全無的單位是「一位病人的一次透析」；一位出錯，其他病人照常
- 數字用十進位字串處理、不經浮點數；空字串是缺值，`0` 照實保留、顯示時才擋
- 三條界線：護理師改過的不改回去、判斷不了就不猜、只讀不寫院方
- **不留原始回應**：本系統只要「現在的狀態」，歷史資料不靠這裡（這也是 1107 學長要求改的原因之一，見子文件）

## 3. 三種留底檔的格式

之後若改成「腳本存檔、本系統讀檔」，讀的就是這些檔，所以格式要先對清楚。

| 方式 | 檔名 | 一次抓取寫成 | `refetch_from_txt.py` 讀得回來嗎 |
|---|---|---|---|
| ① `API_script` 版 | `data_list_sucess.txt`（一個檔一直長） | `Date: 2026-11-07 14:03{"data_list":[...]}` 換行——**時間戳與 JSON 同一行** | **讀不回來**：整行以 `Date:` 開頭，被當成時間戳跳過 |
| ② 成大版 | `YYYY-MM.txt`（每月一個） | `Date: 2026-11-07 14:03:00` 換行，`{"data_list":[...]}` 換行 | 讀得回來 |
| ③ 斗六版 | 同 ② | 同 ② | 讀得回來 |

- 每一次都是**當天到目前為止的全部列**，不是增量：同一份資料一天裡會重複附加很多次，檔案大小約是「每次回應大小 × 抓取次數」
- 1029 探測時一次是 601 列；檔案一個月會長到多大、主機磁碟夠不夠，要從主機上現有的歷史 txt 實際量
- 1107 學長說**歷史 txt 已搬到指定位置**（Word 檔寫的 `API_Fetch\IDH_interface`）；是哪一種格式寫的、有沒有混到 ①，還不知道（子文件第 3 節）

## 4. 三份 Python 共同的坑

| 坑 | 說明 | 影響 |
|---|---|---|
| 寫檔沒指定編碼 | `open(file_name, 'a')`：Windows 上 Python 預設用系統編碼頁（繁中 Windows 是 cp950），Python 3.15 起才預設 UTF-8（推論，未在主機上驗證） | 姓名有 cp950 沒有的字時寫檔失敗；寫檔在同一個 `try` 裡，**整次抓取的結果變成空清單**；用 UTF-8 讀 cp950 寫的檔會亂碼，`refetch_from_txt.py` 用 `errors='ignore'` 讀，亂掉也不會出錯 |
| `strip('<meta charset="UTF-8" />')` | 是刪頭尾出現在這組字元裡的「字」，不是刪這段字串 | 現在剛好能用；回應開頭格式一改就壞 |
| 時區 | `datetime.now()` 跟著機器 | Windows 主機設 +08 沒問題；放進容器（預設 UTC）會在早上 8 點前抓到前一天 |
| 留底是明文 | 三份都把含姓名、病歷號、生日的原始回應寫進文字檔 | 放在哪個資料夾、誰讀得到、會不會被雲端同步，就是個資問題（子文件第 5 節） |
| 寫在目前目錄 | 留底檔與 `temp.csv` 的路徑都相對於執行位置 | 換個地方執行就寫到別處；成大版 `reorder()` 前後路徑不一致 |

## 5. 結論

| 問題 | 答案 |
|---|---|
| 四種對院方送出的請求一樣嗎 | **一樣**，都是同一支 `dialysislist.php` 的 `?date=今天`（斗六是另一台）。院方那一端看不出差別 |
| 差在哪 | 抓的時機、失敗處理、要不要留底、抓完給誰用 |
| 哪一份最適合拿來當獨立腳本的底 | 成大版的留底格式（`YYYY-MM.txt`，`refetch_from_txt.py` 讀得回來）＋斗六版的逾時與重試，**拿掉 Django**、指定編碼與輸出資料夾、不印原始回應；細節在子文件第 6 節 |
| 本系統的介接要不要丟掉 | 不用丟：解析與同步（`hospital-api.format.ts` 之後的部分）照用，換的只是「資料從 HTTP 來」改成「從檔案來」，見子文件第 7 節 |

## 6. 公開界線

- 院方 API 的院內位址、Google Drive 連結、主機上的完整路徑**不寫進本文件**；位址看程式或私人紀錄
- `ref_project/`、`old_API_ref/` 留在 repo 外，不 commit（專案 repo 的文件會同步到公開站）
- 留底 txt 有真實病人資料，本文件只寫格式，不放任何一行內容
- 位址、Drive 連結、原始檔的複本收在私人 repo 的 `deploy/records/1108-hospital-api/`（病人資料不收）

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回其他文件總表](index.md)　[← 回進度首頁](../index.md)
