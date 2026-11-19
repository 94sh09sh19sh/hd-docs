# 第二次進院（1001）· 從零部署本系統（第 2 份，N-19～N-31）

上層文件：[《第二次進院（1001）· 從零部署本系統》](visit-2-system.md)

> 狀態：**已照做 1001，凍結**（結果見[《第二次進院紀錄（1001，部分成功）》](record-2-1001.md)）；1117 由舊的第十四冊改寫；編號 `N-xx`，每一步的細節在[《之四》](visit-2-system-detail-4.md)、[《之五》](visit-2-system-detail-5.md)

## 摘要

- 接第 1 份的 N-18：第 7 節外殼 App 與平板 N-19～N-27、第 8 節 AI 閘道 N-28～N-29、第 9 節 🏥 收尾、第 10 節 🧪 只在開發機做的 N-30～N-31
- 整趟 🏥／🧪 不同的地方在第 1 份開頭那張表；所有文件的清單也在第 1 份
- 1001 做到 N-23；N-24～N-27 平板那幾步沒做
- 完整指令與出錯處置：N-19～N-27 在《之四》，N-28～N-31 與收尾在《之五》
- 每一步只寫做什麼、怎樣算成功；「成功」那一格沒看到就是沒成功，不要往下

## 7. 外殼 App 與平板

### N-19 外殼 repo 的部署金鑰與 clone

**做什麼**：另產生 `hd-kiosk-shell` 金鑰、登記到外殼 repo、`.ssh\config` 加 `Host github-hd-kiosk-shell`；`ssh -T` 後 clone 到 `$root\hd-kiosk-shell`（不切 tag）。

**成功**：`ssh -T github-hd-kiosk-shell` 印出 `Hi 94sh09sh19sh/hd-kiosk-shell!…`；`git -C $root\hd-kiosk-shell tag` 列得出 N-03 那一版（連舊版一起列出是對的）。

🧪 與 N-09 相同，開發機上另產生一把、標題註明模擬部署。

### N-20 建 `shell-builder` 的映像檔

**做什麼**：`docker compose --env-file $cfg --profile shell build shell-builder`（第一次下載約 1.5 GB）。

**成功**：最後幾行有「✓ 外殼 v0.x.x（…，契約第 1 版）已準備好，相依已下載」。

### N-21 建 APK（第一次會產生金鑰）

**做什麼**：`docker compose --env-file $cfg --profile shell run --rm shell-builder`，跑兩次。

**成功**：第一次印出「這一次新產生：…」、APK 檔名與三個 SHA-256（抄下來）；第二次印出「金鑰全部沿用，這一次沒有產生任何新的金鑰」，簽章憑證的 SHA-256 與第一次相同。

🧪 第一次那行寫「APK 簽章金鑰（開發用）」，是對的。

### N-22 備份金鑰，並核對還原得回來

**做什麼**：`shell-builder keys-backup`，再 `shell-builder keys-verify`。

**成功**：第一條印出「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」；第二條每一項都 ✓，最後「還原得回來」。

### N-23 讓病人端改走 HTTPS

**做什麼**：`docker compose --env-file $cfg restart patient-web`，再看 `logs patient-web --tail 5`。

**成功**：最後一次啟動的日誌有「（HTTPS；HTTP 只留外殼下載頁）」；`http://localhost:18081/shell/` 看得到下載頁；`http://localhost:18081/` 轉到 `https://` 並跳出憑證警告是對的。

### N-24 平板連得到主機

**做什麼**：平板連上平常要用的 Wi-Fi，瀏覽器開 `http://<平板要連的位址>:18081/shell/`。

**成功**：看得到下載頁。

🧪 手機和開發機連同一個 Wi-Fi，位址是開發機的區網 IP；開不到的處置在詳細版。

### N-25 在護理端註冊平板

**做什麼**：護理端 → 新增裝置 → 註冊新平板；畫面上的 QR code 與網址只顯示一次，先不要關。

**成功**：畫面上的網址以 `https://` 開頭。

### N-26 平板的系統設定並安裝 App

**做什麼**：設裝置 PIN、關「新增使用者」；開螢幕固定並勾「解除固定前要求 PIN」；從下載頁下載並安裝 App。

**成功**：平板上多了「透析照護平板」。

### N-27 第一次開啟並釘住

**做什麼**：掃 N-25 的 QR code → 儲存並啟動 → 確定固定；解除一次、再釘回去。

**成功**：平板是病人端的等待畫面、沒有憑證警告、離不開；護理端「固定狀態」是固定中（解除時變已跳出）、「外殼版本」正常。把序號與床號的對應記下來。

🧪 用開發用的 Android 手機；做完把 App 解除安裝。

## 8. AI 閘道：讓它就位

### N-28 放 AI 閘道的設定檔

**做什麼**：建 `$root\config\ai-gateway`，把 `services\ai-gateway\config.hospital.example.yaml` 複製成 `config.yaml`。

**成功**：設定檔在 `$root\config\ai-gateway\config.yaml`，`base_url` 與 `model` 保持空白（不填任何位址）。

### N-29 建置並啟動閘道

**做什麼**：`--profile ai build ai-gateway`、`--profile ai up -d ai-gateway`，再從 `api` 容器打閘道的 health。

**成功**：建置最後印出 `全部通過`；health 印出 `503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}`。

## 9. 收尾

### 🏥 冒煙測試與交接（沒有編號）

**做什麼**：在護理站的電腦走一次主線（虛構資料）、開總覽螢幕、現場教學、寫交接文件、當天晚上補演練紀錄。

**成功**：交接文件第一行寫「首波試用、不是全單位上線」，十個項次都有內容（清單在詳細版）。

## 10. 只在開發機做（🧪）

### N-30 跑三支驗收

**做什麼**：在平常開發的工作目錄打 `npm run verify:iteration11`、`12`、`13`，都加 `-- --live --env-file C:\hd-sim\config\.env`；再各走一次更新（W-19）與退回（W-20）。

**成功**：三支都全部 ✓；結果填進演練紀錄。

### N-31 撤除

**做什麼**：`down` 全部 profile、刪兩個資料卷與 `hd-tablet-care*` 映像檔、刪 `C:\hd-sim`、刪 N-24 加過的防火牆規則、手機上的 App 解除安裝。

**成功**：`docker volume ls` 與 `docker images` 看不到 `hd-tablet-care` 開頭的東西；`C:\hd-sim` 不存在。

🏥 撤除只准在開發機做。

上一份：[《第二次進院（1001）· 從零部署本系統》](visit-2-system.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第二次進院（1001）· 從零部署本系統》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
