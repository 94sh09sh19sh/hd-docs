# 第二次進院（1001）· 從零部署本系統之五：詳細版（N-28～N-31、日常、停手條件、編號對照）

上層文件：[《第二次進院（1001）· 從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system/index.md)

> 狀態：**已照做 1001，凍結**（結果見[《第二次進院紀錄（1001，部分成功）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)）；1117 由舊的第十四冊改寫；編號與主文件相同（`N-xx`），每一步開頭的「對應」是沿用的原步驟（`W-xx`、`Y-xx`、`Z-xx` 在哪一份，見[《之一》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail/index.md)開頭）

## 摘要

- 第 8 節 AI 閘道 N-28～N-29：首波 AI 功能是關的（DEP-29），只讓閘道就位、確認它回報設定還沒填，不接任何模型
- 第 9 節收尾：9.1 🏥 冒煙測試與交接（交接文件十個項次）；9.2 🧪 N-30 三支驗收與更新、回退，N-31 撤除
- 第 10 節之後的日常：換版、退回、停服務、換外殼、接 GPU API 各照哪一份常備參考
- 第 11 節什麼時候當場停手，以及停手時做的三件事
- 附錄：本冊 `N-xx` 與原冊 `W-xx`、`Y-xx`、`Z-xx` 的步驟編號對照
- N-27 以前在《之四》；兩個 1001 現場寫的附錄在《之六》

## 8. AI 閘道：讓它就位

首波 AI 功能是關的（DEP-29）。這一節只讓閘道就位、確認它清楚回報「設定還沒填」，**不接任何模型**。

### N-28 放 AI 閘道的設定檔

對應：Z-20

**做什麼**

```
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
```

範本的 `base_url` 與 `model` 刻意留空，**保持空白**。**絕對不要填實驗室的位址**——那是把資料往院外送。

______________________________________________________________________

### N-29 建置並啟動閘道

對應：Z-21、Z-22

**做什麼**

```
docker compose --env-file $cfg --profile ai build ai-gateway
docker compose --env-file $cfg --profile ai up -d ai-gateway
docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
```

**怎麼知道成功了**：建置最後印出 `全部通過`；最後一條印出

```
503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}
```

**503 在這裡是正確的**：閘道在、後端連得到它、它清楚說出還缺什麼。

| 症狀           | 處置                                                                      |
| -------------- | ------------------------------------------------------------------------- |
| `fetch failed` | 閘道沒起來，`docker compose --env-file $cfg --profile ai logs ai-gateway` |
| `找不到設定檔` | N-28 的路徑不對，必須是 `config\ai-gateway\config.yaml`                   |

> ⚠️ 閘道起過之後，**日後更新時 `build` 與 `up -d` 都要加 `--profile ai`**，閘道才會跟著換新版。接上正式 GPU API 是 Q-07 有答案之後的事，見[《AI 閘道》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway-3/index.md) Z-23。

______________________________________________________________________

## 9. 收尾

### 9.1 🏥 冒煙測試與交接

| 步驟     | 做什麼                                                                                                                                            | 詳細在[《第一次進院（0922）· 部署本系統之一：進院當天詳細版》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite/index.md) |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 冒煙測試 | 在護理站的電腦走一次主線：登入 → 建病人 → 建排班 → 指派平板 → 解除綁定 → 稽核查得到。**測試資料用虛構的**，交接時說明哪幾筆是測試資料、誰負責清掉 | H-16                                                                                                                                                    |
| 總覽螢幕 | 在指定位置開啟護理端總覽，確認不會休眠                                                                                                            | H-18                                                                                                                                                    |
| 現場教學 | 護理長、值班護理師、資訊室各教一次，**講完當場讓對方自己做一次**                                                                                  | H-20                                                                                                                                                    |
| 交接文件 | 見下表                                                                                                                                            | H-21                                                                                                                                                    |
| 當天晚上 | 把演練紀錄補完                                                                                                                                    | H-24                                                                                                                                                    |

交接文件至少要有（第一行寫「**首波試用、不是全單位上線**」）：

| 項次     | 內容                                                                              |
| -------- | --------------------------------------------------------------------------------- |
| 位置     | `$root` 底下四個資料夾各放什麼；兩個資料卷的名字                                  |
| 版本     | 部署的 tag；外殼版本                                                              |
| 連接埠   | 三個埠與登記狀況                                                                  |
| 帳號     | 初始管理員的工作 ID（**密碼由院方自行保管**）                                     |
| 啟停     | `docker compose --env-file <設定目錄>\.env stop`／`up -d`，在 `repo` 資料夾底下打 |
| 備份     | 每日幾點、落在哪、誰送往另一台機器                                                |
| 外殼     | N-21 的三個 SHA-256；金鑰備份的檔名                                               |
| 信任邊界 | 能登入這台主機的人一律可信任（DEP-38）；日後帳號政策改變要重新評估                |
| 已知限制 | AI 關閉、N-18 若沒過的實況、尚未佈建的平板                                        |
| 聯絡方式 | 出事找誰                                                                          |

### 9.2 🧪 驗收，然後撤除乾淨

#### N-30 跑三支驗收

對應：容器路線原冊第 7 節（[《從零部署本系統之一：容器路線的原冊》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)）、[《平板與外殼 App》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)的開發機驗收

**這一步是驗收，不是部署步驟**，也是整輪裡唯一准用 Node.js 的地方。在**平常開發的工作目錄**（不是 `C:\hd-sim\repo`）打：

```
npm run verify:iteration11 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration12 -- --live --env-file C:\hd-sim\config\.env
npm run verify:iteration13 -- --live --env-file C:\hd-sim\config\.env
```

**怎麼知道成功了**：三支都全部 ✓。第一支會執行 `down -v` 再 `up -d`，驗證「資料卷不會被 `-v` 刪掉」，**這是刻意的**。

然後依容器路線原冊第 7 節，再各走一次**更新**（W-19，打一個測試 tag）與**回退**（W-20），做法在[《本系統換版與退回》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)。每一步的結果填進《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》。

#### N-31 撤除

對應：容器路線原冊第 8 節（[《備份、還原與關服務》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)）

模擬部署做完**一定要撤除**，下一輪才又是從零；也免得開發機上一直有三個服務佔著埠。

```
cd C:\hd-sim\repo
docker compose --env-file C:\hd-sim\config\.env --profile ai --profile shell down
docker volume rm hd-tablet-care-data hd-tablet-care-keys
docker images "hd-tablet-care*"
```

最後一條列出的映像檔，逐一 `docker rmi <名稱>:<tag>` 刪掉。接著：

```
cd C:\
Remove-Item -Recurse -Force C:\hd-sim
Remove-NetFirewallRule -DisplayName "hd-sim patient 18081"
```

（最後一條只有 N-24 真的加過防火牆規則時才需要，要用系統管理員身分打。）手機上的「透析照護平板」解除安裝。部署金鑰與 `$HOME\.ssh\config` 那兩段**可以留著**，下一輪繼續用。

**怎麼知道成功了**：`docker volume ls` 與 `docker images` 都看不到 `hd-tablet-care` 開頭的東西；`C:\hd-sim` 不存在。

> ⚠️ **撤除只准在模擬部署做。** 🏥 實際部署的撤除會刪掉整個透析中心的紀錄，要院方書面同意，照[《備份、還原與關服務》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)。

______________________________________________________________________

## 10. 之後的日常

1117 起這些做法都在常備參考：

| 要做什麼                     | 照哪裡                                                                                                                                                                                                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 換新版（更新）               | [《本系統換版與退回》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md) W-19。排在非透析時段，更新後第一個班次要有人在                                                                                                                                       |
| 新版有問題，退回上一版       | 《本系統換版與退回》W-20。**更新後寫進去的資料會一起消失**，要在累積新資料之前決定                                                                                                                                                                                                         |
| 暫停或停用服務               | [《備份、還原與關服務》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)                                                                                                                                                                            |
| 換外殼版本、調高最低可用版本 | [《平板與外殼 App》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet-2/index.md) Y-14、Y-15                                                                                                                                                                            |
| 每年核對金鑰備份             | 《平板與外殼 App》                                                                                                                                                                                                                                                                         |
| 接上正式 GPU API             | [《AI 閘道》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway-3/index.md) Z-23                                                                                                                                                                                     |
| 出錯了，這本沒寫到           | [《從零部署本系統之一：容器路線的原冊》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)的出錯處置、《平板與外殼 App》、《AI 閘道》、[《現場疑難排解》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-troubleshooting/index.md) |

______________________________________________________________________

## 11. 什麼時候當場停手

下列任一種出現，**停手、記錄、擇日**。硬幹的代價比重來高得多（詳見[《進院通則》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-visit-rules/index.md)）：

- 有人說「把網路開一下就好了」「手動開個容器比較快」「把整顆磁碟掛進去」
- 資料庫只能放在雲端同步資料夾或人人讀得到的共用資料夾
- 防毒排除當天加不了，有人說「先跑跑看」
- N-21 出現「這個金鑰資料卷是『dev』用的」
- 冒煙測試沒過，但已經到了下班時間

停手時做三件事：`docker compose --env-file $cfg stop` 把服務停掉、把現況寫進演練紀錄、當場講清楚下一次需要什麼。

______________________________________________________________________

## 附錄：步驟編號對照

| 本冊 | 原冊             |     | 本冊 | 原冊                                                |
| ---- | ---------------- | --- | ---- | --------------------------------------------------- |
| N-01 | 《進院通則》     |     | N-17 | W-17                                                |
| N-02 | W-03             |     | N-18 | W-18                                                |
| N-03 | W-01、W-02、Y-01 |     | N-19 | Y-02                                                |
| N-04 | W-04             |     | N-20 | Y-04                                                |
| N-05 | W-05             |     | N-21 | Y-05                                                |
| N-06 | W-06             |     | N-22 | Y-06                                                |
| N-07 | W-07             |     | N-23 | Y-07                                                |
| N-08 | W-08             |     | N-24 | Y-08                                                |
| N-09 | W-09             |     | N-25 | Y-09                                                |
| N-10 | W-10             |     | N-26 | Y-10、Y-11                                          |
| N-11 | W-11、Y-03       |     | N-27 | Y-12、Y-13                                          |
| N-12 | W-12             |     | N-28 | Z-20                                                |
| N-13 | W-13             |     | N-29 | Z-21、Z-22                                          |
| N-14 | W-14             |     | N-30 | 容器路線原冊第 7 節、《平板與外殼 App》的開發機驗收 |
| N-15 | W-15             |     | N-31 | 容器路線原冊第 8 節                                 |
| N-16 | W-16             |     |      |                                                     |

`W-xx` 在《從零部署本系統之一、之二：容器路線的原冊》、`Y-xx` 在《平板與外殼 App》、`Z-xx` 在《AI 閘道》。在演練紀錄裡寫「卡在 N-21」或「卡在 Y-05」都可以，兩者指的是同一件事。

______________________________________________________________________

上一份：[《第二次進院（1001）· 從零部署本系統之四：詳細版（N-19～N-27）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail-4/index.md)｜下一份：[《第二次進院（1001）· 從零部署本系統之六：詳細版（附錄：查防毒排除清單、登不進去）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-2-system-detail-6/index.md)

## 版本歷程

| 定版 | 日期       | 異動                                                                                                             |
| ---- | ---------- | ---------------------------------------------------------------------------------------------------------------- |
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第二次進院（1001）· 從零部署本系統之一：詳細版》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
