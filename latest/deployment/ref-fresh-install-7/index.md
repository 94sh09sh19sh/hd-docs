# 從零部署本系統（第 7 份，V-31～V-32、收尾與附錄）

上層文件：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》

> **狀態：現行（常備參考）。** 改寫自第十五冊（1117）；編號 `V-xx`（沿用第十五冊），每一步下面註明對應的 `N-xx` 與 `W-xx`／`Y-xx`／`Z-xx`。1118 照步驟順序拆成七份，這是第 7 份；🧪／🏥／📍 標記的意思見第 1 份 0.2 節。

## 摘要

- 10.1 🏥 實際部署：冒煙測試與交接，交接文件至少要寫哪些
- 10.2 🧪 模擬部署：V-31 跑三支驗收（含 `v0.5.0` 的已知誤判），V-32 撤除乾淨
- 第 11 節 之後的日常：換版、退回、關服務、外殼、AI 閘道、讀檔、取資料、登不進去各照哪一份
- 第 12 節 什麼時候當場停手，停手時做的三件事
- 附錄：步驟編號對照（V／N／W／Y／Z）

______________________________________________________________________

## 10. 收尾

### 10.1 實際部署：冒煙測試與交接

🏥 只在院內做。

| 步驟     | 做什麼                                                                                                                                                                                                                         | 詳細在                                                                                                                                                                                                                                                                                            |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 冒煙測試 | 在護理站的電腦走一次主線：登入 → 建病人 → 建排班 → 指派平板 → 解除綁定 → 稽核查得到。**測試資料用虛構的**，交接時說明哪幾筆是測試資料、誰負責清掉。已啟用讀檔的主機不輸入任何真實病人資料、不開任何功能開關，改照 SY-13 那張表 | 《[第一次進院（0922）· 部署本系統之三：進院當天詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite-3/index.md)》H-16；《[第五次進院（1116）任務二 · 本系統換版上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-2/index.md)》SY-13 |
| 總覽螢幕 | 在指定位置開啟護理端總覽，確認不會休眠（會休眠就請資訊室調電源設定）                                                                                                                                                           | H-18                                                                                                                                                                                                                                                                                              |
| 現場教學 | 護理長、值班護理師、資訊室各教一次，**講完當場讓對方自己做一次**                                                                                                                                                               | H-20                                                                                                                                                                                                                                                                                              |
| 交接文件 | 見下表；1116 起的交接紙範本在《[院內主機現況與未完成事項之一：交接紙](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status-handover/index.md)》                                                                 | H-21                                                                                                                                                                                                                                                                                              |
| 當天晚上 | 把演練紀錄補完；**每一步的時間都要有**；院內的值只寫進私人 repo 的 `deploy/records/<MMDD-主題>/`                                                                                                                               | H-24                                                                                                                                                                                                                                                                                              |

交接文件至少要有（第一行寫「**首波試用、不是全單位上線**」）：

| 項次     | 內容                                                                                                                                                                                                               |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 位置     | `C:\hd\hd-tablet-care` 底下各資料夾放什麼（`repo`、`hd-kiosk-shell`、`config`、`backups`、`export`）；兩個資料卷的名字；讀檔的話抓取腳本的留底資料夾                                                               |
| 版本     | 部署的 tag；外殼版本                                                                                                                                                                                               |
| 連接埠   | 三個埠與登記狀況                                                                                                                                                                                                   |
| 位址     | 護理站開哪個網址（`http://<主機>:18080`）；**不要用 `localhost` 開**，會登不進去                                                                                                                                   |
| 帳號     | 初始管理員的工作 ID（**密碼由院方自行保管**）                                                                                                                                                                      |
| 啟停     | `docker compose --env-file <設定目錄>\.env stop`／`up -d`，在 `repo` 資料夾底下打                                                                                                                                  |
| 備份     | 每日幾點、落在哪、誰送往另一台機器                                                                                                                                                                                 |
| 外殼     | V-22 的三個 SHA-256；金鑰備份的檔名                                                                                                                                                                                |
| 防毒     | 排除清單加了沒有、誰加的；沒加就照抄可能的現象（V-05）                                                                                                                                                             |
| 斷電之後 | V-19 的結果與從開機到紅框消失幾分鐘；沒驗寫「未驗」                                                                                                                                                                |
| 信任邊界 | 能登入這台主機的人一律可信任（DEP-38）；日後帳號政策改變要重新評估                                                                                                                                                 |
| 資料取出 | 研究與後續計畫要取資料時照《[取出資料](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-data-export/index.md)》在主機上做；沒有院方核准不得執行（DEP-47）。取出紀錄在護理端「系統管理 → 資料取出紀錄」 |
| 已知限制 | AI 關閉、V-19 若沒過的實況、尚未佈建的平板、1001 現場裝的 Git 是否走過變更流程、Docker 查 Docker Hub 網域時好時壞（日後更新會再遇到）                                                                              |
| 聯絡方式 | 出事找誰                                                                                                                                                                                                           |

### 10.2 🧪 模擬部署：驗收，然後撤除乾淨

#### V-31 跑三支驗收

對應：N-30、《[從零部署本系統之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail-2/index.md)》第 7 節、《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-2/index.md)》（舊第十二冊第 7 節）

**這一步是驗收，不是部署步驟**，也是整輪裡唯一准用 Node.js 的地方。在**平常開發的工作目錄**（不是 `C:\hd-sim\repo`）打，先切到要測的 tag，驗完切回來：

```
git switch --detach <tag>
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
git switch master
```

**怎麼知道成功了**：三支都全部 ✓。第一支會執行 `down -v` 再 `up -d`，驗證「資料卷不會被 `-v` 刪掉」，**這是刻意的**。

`v0.5.0` 的已知誤判（1116 模擬，記進紀錄、算過）：第一支在讀檔還開著時，「繫結掛載的目的地只有 /backups 與 /config」會 ✗（停用讀檔後重跑就過）；第三支「apps/、packages/ 與 compose 裡沒有 LangChain、Ollama」會 ✗，命中的是驗收腳本 `apps/api/scripts/verify-iteration13.ts` 自己的假端點，master 已修，下一個 tag 起不會出現；驗收 6 印出紅色 `ERROR` 是後端照預期拒絕啟動時印的，看上面兩個 ✓ 就算過。某一項 ✗ 而不是這幾種：抄原文，判斷是驗收腳本跟不上新版還是新版真的有問題，**兩種都要打新 tag 重新演練**。

然後依《[從零部署本系統之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail-2/index.md)》第 7 節，再各走一次**更新**（W-19，打一個測試 tag）與**回退**（W-20），做法在《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》。每一步的結果填進《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》。

#### V-32 撤除

對應：N-31

模擬部署做完**一定要撤除**，下一輪才又是從零；也免得開發機上一直有三個服務佔著埠。

```
cd C:\hd-sim\repo
docker compose --env-file C:\hd-sim\config\.env --profile ai --profile shell --profile simulation down
docker volume rm hd-tablet-care-data hd-tablet-care-keys
docker volume ls --filter name=hd-tablet-care
docker images "hd-tablet-care*"
```

第四條若還列出 `hd-tablet-care-hospital-sim-files`（模擬讀檔用的，不是 external），`docker volume rm hd-tablet-care-hospital-sim-files`。最後一條列出的映像檔，逐一 `docker rmi <名稱>:<tag>` 刪掉。接著：

```
cd C:\
Remove-Item -Recurse -Force C:\hd-sim
Get-NetFirewallRule -DisplayName "hd-sim *" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
```

（最後一條只有 V-25 真的加過防火牆規則時才會刪到東西，要用系統管理員身分打。）手機上的「透析照護平板」解除安裝。部署金鑰與 `$HOME\.ssh\config` 那兩段**可以留著**，下一輪繼續用。 V-06 下載的兩個基底映像也可以留著。

**怎麼知道成功了**：`docker volume ls` 與 `docker images` 都看不到 `hd-tablet-care` 開頭的東西；`C:\hd-sim` 不存在。

> ⚠️ **撤除只准在模擬部署做。** 🏥 實際部署的撤除會刪掉整個透析中心的紀錄，要院方書面同意，照《[備份、還原與關服務](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)》。

______________________________________________________________________

## 11. 之後的日常

| 要做什麼                                                     | 照哪裡                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 院內主機現在是什麼狀態、還有什麼沒做                         | 《[院內主機現況與未完成事項](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status/index.md)》                                                                                                                                                                                                                                                                                                                                  |
| 換新版（更新）                                               | 《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》W-19。排在非透析時段，更新後第一個班次要有人在（首波開始用之前的例外見那一份）。**更新前先照 V-06 第二段下載一次基底映像**                                                                                                                                                                                                               |
| 新版有問題，退回上一版                                       | 《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade-2/index.md)》W-20。**更新後寫進去的資料會一起消失**，要在累積新資料之前決定                                                                                                                                                                                                                                                                         |
| 暫停或停用服務                                               | 《[備份、還原與關服務](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)》                                                                                                                                                                                                                                                                                                                               |
| 換外殼版本、調高最低可用版本、平板重新佈建、每年核對金鑰備份 | 《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-2/index.md)》Y-14、Y-15                                                                                                                                                                                                                                                                                                                                |
| 接上正式 GPU API                                             | 《[AI 閘道](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway-3/index.md)》Z-23                                                                                                                                                                                                                                                                                                                                         |
| 院方資料：讀檔的啟用、檢查、停用                             | 《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》；抓取腳本那一側照《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script/index.md)》。接上之後，舊版建庫留下的 `01`～`15` 預設床位（只有 1001 建的院內資料庫有）由護理長在「系統管理 → 床位清單」拿掉                                                                        |
| 研究與後續計畫要取資料                                       | 《[取出資料](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-data-export/index.md)》                                                                                                                                                                                                                                                                                                                                             |
| 護理站登不進去、主機位址要換                                 | 《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》                                                                                                                                                                                                                                                                                                                                   |
| 出錯了，這本沒寫到                                           | 《[從零部署本系統之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail-2/index.md)》第 9 節、《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》、《[AI 閘道](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway/index.md)》、《[現場疑難排解](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-troubleshooting/index.md)》 |

______________________________________________________________________

## 12. 什麼時候當場停手

下列任一種出現，**停手、記錄、擇日**。硬幹的代價比重來高得多（詳見《[進院通則](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)》）：

- 有人說「把網路開一下就好了」「手動開個容器比較快」「把整顆磁碟掛進去」
- 資料庫只能放在雲端同步資料夾或人人讀得到的共用資料夾
- ~~防毒排除當天加不了，有人說「先跑跑看」~~（1116 改：防毒排除不擋，加不了寫進交接文件，V-05）
- V-08 的主機位址沒有人能確認
- V-22 出現「這個金鑰資料卷是『dev』用的」
- 讀檔檢查出現「唯讀：否」，或 🏥 出現「模擬標記檔：有」
- 冒煙測試沒過，但已經到了下班時間

停手時做三件事：`docker compose --env-file $cfg stop` 把服務停掉、把現況寫進演練紀錄、當場講清楚下一次需要什麼。

> 📍 **1001** 離院時服務沒有停，留著在跑（《[第二次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001-2/index.md)》M-09）。登入不通，沒有人能用，所以風險不大；但從 1007 起，**登入沒通就離院時，照上面把服務停掉**，下一次來再 `up -d`。

______________________________________________________________________

## 附錄：步驟編號對照

| 本冊     | 第十四冊     | 原冊             |     | 本冊 | 第十四冊 | 原冊                                 |
| -------- | ------------ | ---------------- | --- | ---- | -------- | ------------------------------------ |
| V-01     | N-01         | 舊總覽第 3 節    |     | V-17 | N-16     | W-16                                 |
| V-02     | N-02         | W-03             |     | V-18 | N-17     | W-17                                 |
| V-03     | N-03         | W-01、W-02、Y-01 |     | V-19 | N-18     | W-18                                 |
| V-04     | N-04         | W-04             |     | V-20 | N-19     | Y-02                                 |
| V-05     | N-05         | W-05             |     | V-21 | N-20     | Y-04                                 |
| V-06     | N-06         | W-06             |     | V-22 | N-21     | Y-05                                 |
| V-07     | N-07         | W-07             |     | V-23 | N-22     | Y-06                                 |
| **V-08** | **（新增）** | W-03 的位址一題  |     | V-24 | N-23     | Y-07                                 |
| V-09     | N-08         | W-08             |     | V-25 | N-24     | Y-08                                 |
| V-10     | N-09         | W-09             |     | V-26 | N-25     | Y-09                                 |
| V-11     | N-10         | W-10             |     | V-27 | N-26     | Y-10、Y-11                           |
| V-12     | N-11         | W-11、Y-03       |     | V-28 | N-27     | Y-12、Y-13                           |
| V-13     | N-12         | W-12             |     | V-29 | N-28     | Z-20                                 |
| V-14     | N-13         | W-13             |     | V-30 | N-29     | Z-21、Z-22                           |
| V-15     | N-14         | W-14             |     | V-31 | N-30     | 舊第十一冊第 7 節、舊第十二冊第 7 節 |
| V-16     | N-15         | W-15             |     | V-32 | N-31     | 舊第十一冊第 8 節                    |

V-30a 沒有對應的 N、W 編號（1005 新增）。從 V-09 起，本冊的編號比第十四冊多一號（V-08 是新增的）。演練紀錄裡寫「卡在 V-22」或「卡在 N-21」或「卡在 Y-05」，指的是同一件事。`N-xx` 在《[第二次進院（1001）· 從零部署本系統之一：詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail/index.md)》，`W-xx` 在《[從零部署本系統之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》（W-01～W-07）與《[之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail-2/index.md)》（W-08～W-18），`Y-xx` 在《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》，`Z-xx` 在《[AI 閘道](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway/index.md)》。

舊冊的附錄「護理端頁面開得起來卻登不進去」（先認清用哪個網址開、第 1～4 步）移到《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》。

______________________________________________________________________

上一份：《[從零部署本系統（第 6 份，V-25～V-30a）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-6/index.md)》｜第一份（索引）：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版                                                                                | 日期       | 異動                                                                             |
| ----------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-fresh-install-7/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《從零部署本系統》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
