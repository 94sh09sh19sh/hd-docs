# 迭代 28 手動測試 — 蒐集資料的完整取出

> 《[完整手動測試手冊](https://94sh09sh19sh.github.io/hd-docs/1028/testing/manual-test-guide/index.md)》的分冊之一，對應《實作規格書》4.28 節。共用的環境準備、啟動與疑難排解都在主手冊，這一冊只寫迭代 28 的部分。設計與理由在《[蒐集資料的完整取出](https://94sh09sh19sh.github.io/hd-docs/1028/notes/data-extraction-plan/index.md)》，院內的步驟在部署手冊[第十六冊](https://94sh09sh19sh.github.io/hd-docs/1028/deployment/16-data-export/index.md)。

## 摘要

這一冊驗五件事（項次 `al1`～`al24`，自動化另跑 `npm run verify:iteration28` 與 `npm run verify:iteration28:api`）：

- 三種範圍（全部、某幾類、某幾張）與 `--list`；範圍沒給、打錯、合用錯了都擋，打錯列出最接近的
- 兩個等級：完整級是原值、憑證清空；假名化級找不到姓名與病歷號、自由文字不出、代號接得起來、金鑰不在輸出包
- 從備份取出、匯出目錄的位置檢查、沒打 yes 不寫檔案
- 取出紀錄進稽核軌跡與系統管理「資料取出紀錄」頁，頁面上沒有取出按鈕
- 一位沒做過的人照第十六冊、不用任何 AI，完成一次部分取出與一次第二條路

| 標記            | 意思                                                                                                                                                                                         |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🛠 **開發機**    | `npm run data:export -- …`（先 `npm run build:shared`）；`.env` 要有 `BACKUP_DIR` 與 `HD_EXPORT_DIR`（專案目錄外、與備份目錄分開）。迭代 28 有一個遷移（`npm run prisma:deploy -w @hd/api`） |
| 🐳 **模擬部署** | 部署規範 DEP-22 那一輪：`docker compose --env-file <設定目錄>\.env --profile export run --rm data-export …`                                                                                  |
| 🖥 **護理端**    | 以系統管理者登入專業版                                                                                                                                                                       |

## 這一冊有什麼

| 節    | 內容                       | 在哪裡做 | 對應               |
| ----- | -------------------------- | -------- | ------------------ |
| §28.1 | `--list` 與三種範圍        | 🛠        | 驗收第 1、2 條     |
| §28.2 | 兩個等級與上一層           | 🛠        | 驗收第 3、4 條     |
| §28.3 | 從備份取出、位置檢查、確認 | 🛠        | 驗收第 5 條        |
| §28.4 | 容器裡跑：沒有網路         | 🐳       | 驗收第 6 條        |
| §28.5 | 取出紀錄與系統管理頁       | 🛠 🖥      | 驗收第 8 條        |
| §28.6 | 沒做過的人照手冊做         | 🐳       | 驗收第 9 條        |
| §28.7 | 自動化驗收                 | 🛠        | 驗收第 6、7、10 條 |

**前置**：開發資料庫是合成資料（`HD-TEST-` 開頭的病歷號）。`HD_EXPORT_DIR` 例如 `C:\claude_code_space\lab_project\hd-export`，**不要放在專案目錄、暫存目錄、桌面或文件底下**（會被擋，見 `al14`）。

______________________________________________________________________

## §28.1 `--list` 與三種範圍

- `al1` **［終端機］** 🛠 `npm run data:export -- --list`。 → 十二類依序列出（病人與療程…帳號），每一類底下每張表一列：英文表名、中文名稱、幾筆、最早與最晚日期；最後一句「--list 不寫任何檔案，不算一次取出」。匯出目錄裡沒有多出任何東西。
- `al2` **［終端機］** `npm run data:export -- --all --level full --purpose 驗收 --approval 驗收-001 --operator 測試者`。 → 先印摘要（等級完整、當下的資料庫、寫到哪個資料夾、共 98 張表、預估大小、用途、核准文號、經手人），停在「確認無誤請輸入 yes」；打 `yes`。 → 「取出完成。」，資料夾 `hd-export-<日期時間>-full`。
- `al3` **［檔案總管］** 開 `al2` 的資料夾。 → 有 `讀我.txt`、`data.sqlite`、`tables`（98 個 CSV）、`manifest.json`、`schema.prisma`、`data-dictionary.md`、`SHA256SUMS.txt`；`讀我.txt` 最後一段的筆數與 `al1` 一致。
- `al4` **［終端機］** `--category 病人自述 --level pseudonymized …`（用途等三個照 `al2`）。 → 只有病人自述那 8 張表的 CSV。
- `al5` **［終端機］** `--category 臨床數值 --tables help_requests --level pseudonymized …`。 → 臨床數值 5 張＋`help_requests`，共 6 張（聯集）。
- `al6` **［終端機］** 依序試：什麼範圍都不給；`--tables help_requets`；`--category 病人自訴`；`--all --tables patients`；拿掉 `--approval`；拿掉 `--level`。 → 每一次都停在「沒有取出：…」，打錯的兩次列出最接近的 `help_requests`、`病人自述`；匯出目錄裡沒有多出任何東西。

## §28.2 兩個等級與上一層

- `al7` **［試算表］** 開 `al3` 的 `tables\nurses.csv`。 → 中文不是亂碼；`password_hash` 那一欄**欄名在、內容全空**；工作識別碼與姓名是原值。時間欄寫成 `…T13:25:00.000+08:00`。
- `al8` **［SQLite 檢視工具］** 開 `al3` 的 `data.sqlite`，看 `nurses.password_hash`、`devices.api_key_hash`、`nurse_sessions.token_id`。 → 全空；`nurse_sessions` 有不只一列時仍開得起來（那一欄的唯一索引已拿掉，`manifest.json` 的 `sqliteNote` 有寫）。
- `al9` **［檔案總管］** 在 `al4` 的資料夾裡搜尋任何一位病人的病歷號（`HD-TEST-`）與姓名。 → 找不到。`help_requests.csv` 沒有 `message`、`resolution_note` 兩欄；`patient_id` 是 `ps-` 開頭的代號，與 `symptom_reports.csv` 同一位病人的代號相同。
- `al10` **［檔案總管］** 看匯出目錄。 → `假名化對照\<al4 的資料夾名>\` 底下有 `金鑰.txt` 與 `對照表.csv`；**`al4` 的資料夾裡沒有**任何金鑰或對照表；假名化級沒有 `data.sqlite`。
- `al11` **［終端機］** `--tables help_requests --with-parents --level pseudonymized …`。 → 多了病人、療程、平板、綁定、護理師幾張；`patients.csv` 的病歷號與姓名是代號、沒有 `note` 欄；`nurses.csv` 的密碼雜湊是空的；沒有再往上帶（沒有 `nurse_sessions`）。
- `al12` **［檔案總管］** 開 `al4` 的 `manifest.json`。 → `referencedButNotExported` 列出病人、療程等「指向了但沒取」的表；每張表的每一欄有 `class`（匯出分類）與 `treatment`（處理方式）。

## §28.3 從備份取出、位置檢查、確認

- `al13` **［終端機］** 護理端系統管理「資料庫與備份」按「立即備份」，記下檔名；`--from-backup <檔名> --tables patients --level full …`。 → 成功；`manifest.json` 的 `source` 是那一份備份。把備份旁邊的 `.sha256` 檔改掉一個字再跑一次。 → 「雜湊…對不上，不取」。改回來。
- `al14` **［終端機］** 把 `.env` 的 `HD_EXPORT_DIR` 依序改成：專案目錄底下、`\\某台主機\分享`、`…\OneDrive\export`、備份目錄底下，各跑一次 `al2`。 → 分別被擋（專案目錄、網路路徑、雲端同步、與備份目錄重疊），沒有建出任何資料夾。改回來。
- `al15` **［終端機］** 跑 `al2`，摘要出來後打 `no`。 → 「已取消，沒有寫任何檔案」。
- `al16` **［終端機］** 後端停著（不 `npm run dev`）跑一次 `al4`。 → 照樣成功——取出不需要後端。

## §28.4 容器裡跑：沒有網路

- `al17` **［PowerShell］** 🐳 照第十六冊 U-02、U-03 跑一次 `--list` 與一次 `--category 病人自述 --level pseudonymized`。 → 與 §28.1 相同的結果，輸出在 `HD_EXPORT_DIR` 底下。
- `al18` **［PowerShell］** 🐳 `docker compose --env-file <設定目錄>\.env --profile export run --rm --entrypoint sh data-export -c "cat /proc/net/route; ls /keys"`。 → 路由表只有表頭（沒有任何網路介面）；`/keys` 不存在（沒有掛金鑰資料卷）。
- `al19` **［PowerShell］** 🐳 `docker compose --env-file <設定目錄>\.env up -d` 之後 `docker compose ps`。 → 沒有 `data-export`（預設的 `up` 不帶它）。

## §28.5 取出紀錄與系統管理頁

- `al20` **［護理端］** 🖥 重新啟動後端（或等一小時），系統管理 → **資料取出紀錄**。 → 前面每一次取出各一列（時間、完成或中止、等級、範圍與取了哪些表的**中文名稱**、用途、核准文號、經手人、筆數）；被擋與取消的不在。畫面上**沒有任何按鈕**，也看不到英文表名。
- `al21` **［護理端］** 稽核軌跡（先選用途）找「研究與後續計畫的資料取出」。 → 每一次一筆，說明寫了等級、範圍、經手人、核准文號、用途；中止的那一筆結果是失敗。
- `al22` **［護理端］** 再重新啟動一次後端，回到資料取出紀錄。 → 筆數不變（收過的不會再收一次）。

## §28.6 沒做過的人照手冊做

- `al23` **［人］** 🐳 請一位沒做過的人，只拿第十六冊、**不用任何 AI**，在模擬部署上完成一次 `--tables` 的部分取出（U-01～U-05、U-08）。 → 做得完；卡住的地方記下是哪一步、哪一句看不懂，回頭改手冊。
- `al24` **［人］** 🐳 同一位照第十六冊 U-09（第二條路）：驗最新一份備份的雜湊、複製到匯出目錄、用 SQLite 檢視工具開。 → 做得完，看得到病人與求助的資料；知道這時要另外手寫一筆紀錄。

## §28.7 自動化驗收

`npm run verify:iteration28`（不需要後端，也不需要 Prisma）：check:export 全綠且擋新表與新欄、十二類都有表、compose 的 `data-export` 沒有網路與金鑰、後端沒有取出端點、頁面沒有按鈕、取出指令沒有網路模組、`--help` 的步驟、手冊。`npm run verify:iteration28:api`（要 Prisma，不需要後端）：在 repo 旁邊建全新的資料庫與合成資料，真的跑八組取出與擋下的情況，再讓後端的收紀錄服務收一次。`verify:acceptance` 與全部回歸照樣通過。

## 版本歷程

| 定版 | 日期       | 異動                                                                    |
| ---- | ---------- | ----------------------------------------------------------------------- |
| 1028 | 2026-10-28 | 首次定版。蒐集資料的完整取出（al1～al24）；1028 在容器裡實跑 al17～al22 |

[← 回完整手動測試手冊](https://94sh09sh19sh.github.io/hd-docs/1028/testing/manual-test-guide/index.md)
