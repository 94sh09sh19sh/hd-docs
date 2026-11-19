# 第五次進院（1116）任務二 · 本系統換版上線之一：詳細版（讀之前、SY-01～SY-07）

上層文件：《[第五次進院（1116）任務二 · 本系統換版上線](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system/index.md)》　1116 照做的結果：《[第五次進院紀錄（1116，讀檔上線、平板與交接待補）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-5-1116/index.md)》

> **狀態：已照做 1116，凍結。** 院內主機現在的樣子與沒做完的步驟看《[院內主機現況與未完成事項](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status/index.md)》。
>
> **從哪幾份舊冊改寫（1117）**：第二十四冊（本系統換版上線詳細版）第 1、2 節；第二十冊（第五次進院新手版，`GO-xx`）有而第二十三、二十四冊沒有的內容，逐節比對後併進同一個編號（對照在《[之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-detail-2/index.md)》第 3 節）；第十七冊第 0.6 節的開發機起點（第 1.6 節）。第二十四冊的附錄改到別份：交接紙→《[院內主機現況與未完成事項之一：交接紙](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status-handover/index.md)》、停用讀檔之後已寫進主機的資料→《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》、護理端登不進去→《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》、平板重新佈建→《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》。1118 拆成兩份：這一份是第 1 節與第 2 節的 SY-01～SY-07，SY-08 起與第 3 節在《[之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-detail-2/index.md)》。
>
> **編號**：沿用上層的 `SY-xx`、`SY-M1`～`SY-M4`；舊第二十冊的 `GO-xx` 只在第 3 節對照。
>
> **照上層做，畫面跟「成功」不一樣時翻這一份同一個編號。** 這裡寫：什麼時候停手、時間怎麼排、要帶的東西、每一步的出錯處置與為什麼。
>
> 指令與訊息綁在根目錄的 `docker-compose.yml`、`docker-compose.dialysis-files.yml`、`docker-compose.hospital-files-sim.yml`、`deploy/hospital.env.example`、`apps/api/scripts/db-update.mjs`、`apps/api/scripts/restore-backup.ts`、`apps/api/src/hospital-api-probe.ts` 上（1117 對過 master）。規則的真本是《[部署規範](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/deployment-spec/index.md)》。
>
> **公開範圍**：一律用代稱（上層第 0.2 節）。院內主機名稱、IP、帳號、`.env` 的值、照片只進私人 repo 的 `deploy/records/`。

## 摘要

- 第 1 節：這一趟要做到什麼、三種結果、什麼時候當場停手、時間怎麼排、要帶的東西、🧪 1116 那一輪開發機的起點
- 第 2 節前半：SY-01～SY-07 每一步的出錯處置與為什麼；舊第二十冊多寫的依據（A-xx、DEP、第 11 章條號）併在同一個編號
- SY-08～SY-15、SY-M1～SY-M4 與第 3 節 `GO-xx` 對照在《[之二](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-detail-2/index.md)》
- 停用讀檔、退回、登不進去、平板重新佈建、交接紙都不在這一份，各自連到常備參考
- 開發機與正式主機的差別都標在上層；這一份只在處置不同時標 🏥／🧪
- 1116 實際照做的結果與發現不寫在這裡，見《第五次進院紀錄》

## 1. 讀之前

### 1.1 這一趟要做到什麼

| 優先 | 目標                                                                                                                                           | 做到就是                                                     |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1    | 透析清單抓取腳本在院內每 3 分鐘自己跑（第一階段，《[任務一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-api/index.md)》） | AF-11 三輪都成功                                             |
| 2    | 本系統換到 `<新 tag>`                                                                                                                          | 護理站登得進去、版本是 `<新 tag>`                            |
| 3    | 啟用讀檔、首波上線                                                                                                                             | 第一輪同步的病人、床號、療程對得上；平板在指定的床上走完一次 |
| 4    | 交接                                                                                                                                           | 交接紙交給護理長與資訊室，講一次、讓對方做一次               |

首波＝1 台暫用平板 `TB-00`、1 床、護理長指定的少數護理師；功能開關全部維持關閉（「本次透析」面板 SY-12 才開）。這一張表是 1111 開會定的「三件事同一趟做」，前一件沒成就不做後一件（《[上線準備清單](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-prep/index.md)》第 0.3 節）。

### 1.2 三種結果

| 結果     | 條件                                                                                                                   |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| **A 級** | 第一階段成功、換版成功、啟用讀檔第一輪對得上、平板走完一次、交接完成                                                   |
| **B 級** | 第一階段或換版成功，但停在 SY-09 之前或之後某一步（病人告知沒答案，床號對不上）。防毒排除沒加不算（1116 改，見 SY-03） |
| **C 級** | 第一階段沒成功：本系統不動，維持 `v0.4.0`                                                                              |

### 1.3 什麼時候當場停手

| 情形                                                   | 處理                                                                                                                                   | 結果       |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| 《任務一》沒做成                                       | 本系統不換版                                                                                                                           | C 級       |
| 換版後 `api` 起不來、主線壞掉，現場解不開              | 照《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》退回 `v0.4.0`，抓取腳本照跑     | B 級       |
| 病人告知沒答案                                         | 不啟用讀檔，做到 SY-08                                                                                                                 | B 級       |
| 防毒排除當天加不了                                     | **照樣往下**；交接紙寫誰、什麼時候加，以及 SY-03 那四種現象                                                                            | 不影響等級 |
| 第一輪床號或療程不對                                   | 照《[讀檔：啟用、檢查、停用](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-dialysis-files/index.md)》停用讀檔，記下實況 | B 級       |
| 平板到不了位、Wi-Fi 不通                               | 護理端照用、病人端不開；求助照舊用床邊呼叫鈴                                                                                           | B 級       |
| 離下班不到 45 分鐘                                     | 停在目前這一步，直接做 SY-14、SY-15                                                                                                    | —          |
| 有人說「把網路開一下」「手動開個容器把整顆磁碟掛進去」 | 不做                                                                                                                                   | —          |

停手時做三件事：服務維持在一個說得清楚的狀態（`v0.4.0` 或 `<新 tag>`、讀檔開或關）、把現況寫進紀錄、當場講清楚下一次需要什麼。

舊第二十冊另有兩列，1116 已不適用：①抓取腳本搬 C 槽（舊第十九冊 B-14a）搬不成就照舊在 D 槽做、讀檔的資料夾跟著用 D 槽——1116 搬成了，D 槽舊資料夾也已被學長刪掉；②防毒排除沒加就不啟用讀檔、做到 SY-08——1116 改成不擋（SY-03）。

### 1.4 時間怎麼排（🏥，第一階段之後）

| 段落                              | 大約時間                                |
| --------------------------------- | --------------------------------------- |
| SY-02、SY-03 看現況、防毒         | 30 分鐘                                 |
| SY-04～SY-06 換版、確認、備份還原 | 45～60 分鐘（主機有快取，建置一分鐘內） |
| SY-07 重新開機                    | 20 分鐘（院方准才做）                   |
| SY-08 密碼移交、建帳號            | 20 分鐘                                 |
| SY-09～SY-11 啟用讀檔、第一輪     | 30 分鐘                                 |
| SY-12 平板                        | 45 分鐘                                 |
| SY-13～SY-15 冒煙測試、交接、離院 | 60 分鐘                                 |

合計約 4～5 小時，是順利的版本。湊不到同一個時段：第一天做到 SY-07，SY-08 起另約。🧪 演練約 3～4 小時（SY-M2 約 30 分鐘）。

舊第二十冊把第一階段算在一起：看現況 15 分鐘、抓取腳本 60～90 分鐘（搬檔幾分鐘、看三輪約 10 分鐘）、防毒 15 分鐘，合計約 5～6 小時。1116 實際兩個任務合計約 2 小時（14:15 到院、16:20 離開），沒做 SY-07、SY-08、SY-14。

### 1.5 要帶的東西（🏥）

- 上層與這一份的紙本、演練紀錄空白表、《[交接紙](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status-handover/index.md)》；《任務一》與它的詳細版開在主機的瀏覽器上，不印
- 平板 `TB-00`、充電器（拔電續航沒測過，療程全程先插電）
- 管理者密碼、平板 PIN：親手移交，**不寫在紙上**
- 手機：GitHub 兩步驟驗證（《任務一》從 GitHub 下載抓取腳本 v0.3.0 要用）、私人 repo 的 `values.md`（`deploy/records/1108-hospital-api/`）與現場筆記

### 1.6 🧪 1116 那一輪開發機的起點（紀錄，之後不照做）

開發機重現院內主機、演練完撤除是開發端的事，不寫進進院冊（1116 定）；下面只記 1116 那一輪怎麼準備，之後的演練以《[院內主機現況與未完成事項](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-status/index.md)》的現況為起點另外準備。

- 原訂照舊第二十冊演練（第十七冊第 0.6 節），同一天改照第二十一冊（現在的《任務一》）與第二十三冊（現在的上層）的 🧪 做（《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》11.2）
- 重現的是 **1029 離院時**的主機：院內主機已經是 `v0.4.0`、位址已是 IP、登得進去。`v0.5.0` 1116 已打（commit `8575505`）；《[開發機才做的演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal/index.md)》第 1、6 節（I-01～I-05 準備、I-17 撤除）照舊，其餘照下表改；旁邊放印好的手冊

| 原本               | 1116 這一輪改成                                                                                                                                                                                                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| I-06               | 照做；多建一個 `C:\hd-sim\export`                                                                                                                                                                                                                                                                              |
| I-07               | `git checkout v0.4.0`（不是 `v0.3.0`）                                                                                                                                                                                                                                                                         |
| I-08               | 用 `v0.4.0` 的範本；`HD_IMAGE_TAG=v0.4.0`；三個位址**直接用 `<IP>` 而且填對**：`HD_PUBLIC_API_URL=http://<IP>:13000`、`CORS_ORIGINS=http://<IP>:18080`、`MDM_KIOSK_BASE_URL=https://<IP>:18081`；加 `HD_EXPORT_DIR=C:\hd-sim\export`；`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 留空。**不故意填錯** |
| I-09～I-11         | 照做（建出來的是 `v0.4.0`；伺服器憑證是 `IP Address:<IP>`）                                                                                                                                                                                                                                                    |
| I-12               | 改成確認重現了 1029：手機開 `http://<IP>:18080` **登得進去**；`docker ps` 是 `v0.4.0`。時間夠的話照《[平板與外殼 App](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-tablet/index.md)》把手機或暫用平板佈建起來，SY-12 才有東西看                                                                |
| 第十七冊第 3、4 節 | 改照上層 SY-02～SY-09、SY-12、SY-13 做；第一階段跳過（抓取腳本另照《任務一》的 🧪 驗）；SY-03 只看排除清單、不加；SY-07 Quit Docker Desktop 再開；SY-09～SY-11 用 SY-10 B1、B2                                                                                                                                 |
| I-13               | 改成 SY-10 B1、SY-10 B2、SY-M1 三步（讀檔模式；測試分冊 `ap17`）。第十七冊第 0.6 節原寫 B1 之後「床位圖出現模擬甲～模擬癸」；1116 實測簡易版列的是模擬甲、模擬乙……（沒有模擬辛，它是故意放的壞資料），床號要看「床位清單」卡（SY-11）                                                                          |
| I-14               | ＝SY-M2，`<新 tag>` 是 `v0.5.0`                                                                                                                                                                                                                                                                                |
| I-15               | ＝SY-M3：退回 `v0.4.0`，含把讀檔那兩行改回去；手機登得進去、版本是 `v0.4.0` 才算過                                                                                                                                                                                                                             |
| I-16               | ＝SY-M4                                                                                                                                                                                                                                                                                                        |

- 1116 那一輪的開發機：沒連 Wi-Fi，走旅行路由器的有線網路，`<IP>` 用那一張、網路設定檔改成「私人」；平板用使用者自己的 Android 手機佈建，不動 1029 那台暫用平板（它裝的是院內金鑰簽的外殼）；撤除後網路改回「公用」（演練紀錄 11.2）
- 第十七冊第 0.6 節原估的時間：準備 30 分鐘、重現 60～90 分鐘、手冊那一段 90～120 分鐘、驗收 60～75 分鐘、撤除 15 分鐘，合計約 4.5～5.5 小時

## 2. 各步驟

### SY-01 確認 tag、答案、人與時段

- 沒有照上層 🧪 整輪演練過、判定通過的 tag **不准帶**（舊編號 O-02；《[開發機才做的演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-rehearsal/index.md)》I-01、I-16）
- 演練中發現程式要修：修好、跑過驗收、**打下一個 tag**（例如 `v0.5.1`）重新演練。推上去的 tag 不移動、不刪掉重打（院內與紀錄都靠 tag 名字對版本）
- 「到時候看看」當成沒約到
- 答案的清單是《[上線準備清單](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-prep/index.md)》第 1 節 A-01～A-11；它的附錄（《部署規範》第 11 章 26 條）標 ✗ 的，帶著問題去
- `v0.5.0` 的 commit 是 `8575505`（`git rev-parse v0.5.0` 印的 `0ef8663…` 是附註 tag 物件本身，不是 commit；要對 commit 用 `git rev-parse v0.5.0^{commit}`）

### SY-02 看現況

| 症狀                                             | 處置                                                                                           |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| `git describe` 不是 `v0.4.0`，或 repo 有改動     | 有人動過。**停手**，問資訊室                                                                   |
| 有服務不是 `Up`                                  | `docker compose --env-file $cfg logs <服務> --tail 30` 抄下來，打電話給開發端                  |
| `failed to connect to the docker API at npipe:…` | Docker Desktop 沒開。開始選單開啟，等左下角變綠                                                |
| `backups\keys` 是空的                            | 金鑰備份不見了。記下來，SY-12 平板若要重新佈建會受影響，打電話給開發端                         |
| Docker Desktop 的設定是灰的                      | 院方鎖住了，記下來，不要繞過                                                                   |
| 使用統計取消勾選後按的是 **Apply & restart**     | Docker 會重新啟動，服務中斷約一分鐘後自己回來；沒回來就 `docker compose --env-file $cfg up -d` |

順便抄下 Docker Desktop 另外三項（SY-07、交接要用）：General → Start Docker Desktop when you sign in（應該勾，沒勾先不改、交資訊室）；Software updates（只看不改；找不到就是市集裝的）；Resources → Advanced → Disk image location（SY-03 要用的路徑）。

為什麼要看這幾樣（舊第二十冊）：

- `Up` 的時間比 1029 到今天短，代表中間重新開機過，就是舊 J-25（重新開機後服務會不會自己回來）想要的答案（《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之五：詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-5/index.md)》）
- `backups\keys`：補抄 1029 的金鑰備份檔名（1029 沒抄）
- C 槽剩多少：SY-13 議定磁碟門檻用
- 使用統計：1029 不記得按的是哪個 Apply，這次確認真的關了

### SY-03 防毒排除

想知道防毒有沒有在跑（系統管理員身分）：

```
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName, @{n='hex';e={'{0:X6}' -f $_.productState}}
```

`hex` 中間兩碼 `10` 或 `11` 是正在運作，`00`、`01` 是裝了沒在跑。1001 是 `061100`（Defender 正在運作）。1029 看排除清單是空的。

| 症狀                                          | 處置                                                                                                            |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `Must be an administrator to view exclusions` | 不是系統管理員身分，重開一個（開始 → 打 `powershell` → `Ctrl+Shift+Enter`）                                     |
| `Invalid namespace`                           | 這台是 Windows Server，改打 `Get-MpComputerStatus`，看 `AMRunningMode`、`AntivirusEnabled`                      |
| 資訊室當天加不了                              | **照樣往下，讀檔照開**（1116 改）；不加也能跑，出現下表的現象再加。交接紙「防毒」那一列寫「未加」，現象照抄下表 |

**為什麼 1116 起不擋讀檔**（舊第二十冊寫的是「加不了就不啟用讀檔」、交接紙寫「沒加之前不得輸入真實病人資料」，1116 改掉）：

- 資料庫放在 Docker 的具名資料卷裡，實體是 Docker 資料夾裡的一個虛擬磁碟檔（`ext4.vhdx`）。Defender 的即時掃描只看得到這一整個檔，看不到裡面的 `hd.db`、`-wal`、`-shm`。所以舊冊（《[第一次進院（0922）· 部署本系統之二：進院當天詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-1-system-onsite-2/index.md)》H-14、《[現場疑難排解](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-troubleshooting/index.md)》X-14）講的「SQLite 被掃描鎖住、間歇性 `database is locked`」，在容器路線不會因為防毒發生
- 這是照架構推的，**沒有在開著即時掃描的主機上實測過**
- Defender 看得到的是主機上本系統的資料夾：`config`、`backups`、`export`、第一階段的 `C:\API_Fetch\IDH_interface`，以及換版時的 `repo`

**沒排除時可能看到的現象**（交接紙照抄）：

| 在哪                         | 會看到                                                                                                              | 傷不傷資料                               | 怎麼確認                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Docker 資料夾                | 整體變慢，資訊室排的全機掃描時段特別明顯；開機後 Docker Desktop 比平常久才起來                                      | 不傷                                     | 問資訊室全機掃描排在幾點，對時間                                                                                                        |
| `backups`                    | 「系統管理 → 資料庫與備份」的備份歷程出現失敗，「最近一次成功備份」不是今天；極少數是備份檔被判成可疑、被隔離而不見 | 資料庫不受影響，但那一天沒有可還原的備份 | Windows 安全性 → 病毒與威脅防護 → 保護歷程記錄，看有沒有那個檔                                                                          |
| `C:\API_Fetch\IDH_interface` | 抓取腳本寫檔時被佔用，「系統管理 → 院方資料同步」卡停在舊時間                                                       | 不會寫壞，只是沒更新                     | 抓取腳本那邊的紀錄（《[院方 API 抓取腳本的維運](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fetch-script/index.md)》） |
| `repo`（換版時）             | `git checkout` 或建置偶爾說檔案被佔用                                                                               | 不傷                                     | 重打一次就過                                                                                                                            |

**出現任何一種**：請資訊室把 Docker 資料夾加進排除清單；是備份那一列，再加 `backups`。只排這兩個資料夾，不排整顆磁碟、不排 `node.exe`。看到 `database is locked` 不要先怪防毒：先看是不是換版、還原或資料取出的一次性容器還在跑（`docker compose --env-file $cfg ps -a`）。

### SY-04 換版

| 症狀                                                                       | 處置                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Permission denied (publickey)`                                            | 部署金鑰被拿掉了。`ssh -T github-hd-tablet-care` 看一下，打電話給開發端                                                                                                                                              |
| `error: pathspec '<新 tag>' did not match`                                 | tag 沒推上去或打錯字                                                                                                                                                                                                 |
| `git describe` 後面有尾巴（例如 `-3-gabc123`）                             | 不在 tag 上，重打 `git checkout <新 tag>`                                                                                                                                                                            |
| `no such host`（建置時）                                                   | 再打一次 → 工作列 Docker 圖示右鍵 Restart → 找資訊室看 DNS                                                                                                                                                           |
| 每個 `docker compose` 都說「請設定 HD\_…」                                 | `.env` 少了必填的那一行，照範本補                                                                                                                                                                                    |
| `failed to read …\.env: line N: unexpected character … in variable name …` | `.env` 第 N 行不是註解也不是「名稱=值」。最常見是整段複製了 `v0.5.0` 範本，帶進那一行斷掉的「aw_txt 與 hb-status.json）」（1116 模擬實測）。`notepad $cfg` 刪掉第 N 行（或在開頭加 `#`），再打 `config --quiet` 確認 |
| `更新中止：後端服務還在執行`                                               | 再打一次 `stop api`。**不要加 `--allow-running`**                                                                                                                                                                    |
| 其他任何「中止」                                                           | 資料庫沒被動到。整段抄下來，`HD_IMAGE_TAG` 改回 `v0.4.0`、`git checkout v0.4.0`、`docker compose --env-file $cfg up -d`，打電話給開發端                                                                              |

- 3 個遷移（迭代 30.4 連點成畫、32 院方資料讀檔、32.1 未更新提示時段）都只做加法；外殼不換版，APK 不必重建、平板不必重裝
- `.env` 的四行先留空，是因為讀檔要等 SY-09 四條都過才開；`COMPOSE_FILE` 那一行維持註解
- **為什麼只貼四行**：`v0.5.0` 範本那一段的第 97～98 行把 `hospital_dataset\raw_txt` 斷成兩行，第 98 行變成一行沒有 `#` 的「aw_txt 與 hb-status.json）」，整段貼進來 compose 就讀不到 `.env`（1116 模擬實測）。master 的範本已修好（commit `8c12505`），`v0.5.0` 照帶；下一個 tag 起整段複製也不會壞，但這一趟照只貼四行
- 🏥 主機的 `.env` 沒有「院方透析清單 API」那一段時，`HOSPITAL_API_BASE_URL`、`HD_SIMULATION_DEPLOYMENT` 不用補：compose 讀不到時當空白，正是院內要的
- `db-update.mjs` 會先做一份更新前備份（印在 `[3] 更新前備份（規範 18.1 第 1 關）` 底下），檔名與 SHA-256 是退回時唯一的依據，一定要抄
- 換版的通用做法（舊 W-19）與這一步的舊出處（舊 J-15～J-18）在《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》與《[第三次進院（1029）之四：詳細版](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-3-system-detail-4/index.md)》

### SY-05 啟動確認

| 症狀                                         | 處置                                                                                                                                                                                |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api` 一直 `Restarting`                      | `docker compose --env-file $cfg logs api --tail 30` 抄最後幾行。看不懂就照《[本系統換版與退回](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)》退回 |
| 放行檢查什麼都沒印                           | 照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》                                                                       |
| 護理站 `Failed to fetch`                     | Ctrl＋F5；仍不行照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》                                                       |
| 護理站 `工作ID 或密碼錯誤`                   | 有連到後端，帳號或密碼不對；換版不會改密碼                                                                                                                                          |
| 「本次透析」面板、現有功能的小幅遊戲化是開的 | 這兩項是程式的預設值（從零建置或換版後都是開的），正常；照上層 SY-05 第 3 項關掉                                                                                                    |
| 其他功能開關是開的                           | 關掉，記下是哪一個，回來告訴開發端                                                                                                                                                  |
| 「院方床位轉床號的方式」不是 `0`             | 改回 `0`，記下原本是多少                                                                                                                                                            |
| 日誌的「伺服器時區」不是 `Asia/Taipei`       | 後端會拒絕啟動。不要自己改主機時區，找資訊室                                                                                                                                        |

- 「版本更新紀錄」的版本欄 `0.1.0 → 0.1.0` 是 `package.json` 的號碼，不是 tag，正常
- `ai-gateway` 仍是 `v0.4.0`：兩版之間閘道沒改、AI 關著，SY-04 不建它
- 日誌那幾項對的是《部署規範》第 11 章第 3、7 條
- 提示時段：「院方資料未更新提示的起始時刻」`8`、「結束時刻」`23` 是迭代 32.1 的預設；舊第二十冊寫成看「院方資料同步」卡上的「「未更新」提示時段：8 時到 23 時」，但那一行要到 SY-10 接上資料夾後才出現（1116 模擬實測），所以改看營運參數表
- 功能開關為什麼兩項也要關（DEP-29、第 11 章第 18 條）：「本次透析」面板等 SY-11 對真實資料驗過才開（SY-12 第 4 項）；遊戲化等長者、社工、護理部看過才開。舊第二十冊寫「全部是關的」，1116 模擬才發現兩項預設是開的。要逐項看的清單在《[上線準備清單](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-prep/index.md)》第 7 節

### SY-06 備份還原

- **一律用 PowerShell**：Git Bash 會把 `/backups/…` 改寫成 Windows 路徑，還原就找不到檔
- 印出 `還原中止：SHA-256 與備份歷程上的紀錄不符，備份檔可能已損毀或被更動`：雜湊抄錯，重抄 `.sha256` 那一份；還是不符就打電話給開發端
- 刪測試檔那一條印「No such file」：前一條沒寫出測試檔，看前一條的錯誤原文
- 為什麼要送往另一台機器：備份只放在同一台主機，主機壞了就一起沒了（DEP-06、第 11 章第 8 條）；由誰送、多久送是資訊室的事（上線準備清單 A-05），寫進交接紙
- 備份與還原的通用做法在《[備份、還原與關服務](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-backup-shutdown/index.md)》

### SY-07 重新開機

- 為什麼：`restart: unless-stopped` 只管 Docker 起來之後；Docker Desktop 要有人登入 Windows 才會啟動。院方的答覆是斷電後由護理長到主機重新登入，不設自動登入，這一步就是在模擬護理長
- 要院方准（上線準備清單 A-04）；院方不准就跳過，《部署規範》第 11 章第 10 條不算通過，寫進交接紙的已知限制
- 三分鐘後服務沒回來：記下 Docker Desktop 有沒有隨登入起來、SY-02 抄的「Start Docker Desktop when you sign in」有沒有勾；手動開 Docker Desktop、等變綠、`docker compose --env-file $cfg up -d`。**不要改院方的登入或開機設定**，寫進交接紙的已知限制，交資訊室決定
- 順便看第一階段的排程：`Get-ScheduledTaskInfo -TaskName hd-hospital-fetch` 的 `LastRunTime` 有往前跳（排程也是登入後才跑）
- 🧪 開發機驗不出「沒人登入」的情形，所以只 Quit Docker Desktop；量到的分鐘數只當參考
- 🧪 按了之後護理端沒閃紅框、`docker ps` 的 `Up` 時間沒有歸零：按到的是視窗的關閉鈕，不是通知區圖示的 Quit。重做一次
- **1116 模擬實測：Quit 之後再開，服務沒有自己回來**（`docker ps -a` 全是 `Exited`）。Docker Desktop 在 Quit 時先逐一停掉容器、引擎再關（引擎只花 12 毫秒），容器被當成「手動停止」，`restart: unless-stopped` 就不會再啟動它。院內真的重新開機時會不會一樣還沒驗過；出現了就照上面手動 `up -d`、記下來，交開發端判斷要不要把 compose 的 `restart` 改成 `always`。1117 master 的 `docker-compose.yml` 仍是 `unless-stopped`，等院內重新開機實測後再定

SY-08 起：《[之二：詳細版（SY-08～SY-15、SY-M1～SY-M4、舊第二十冊對照）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/visit-5-system-detail-2/index.md)》

## 版本歷程

| 定版                                                                                  | 日期       | 異動                                                                                                                                            |
| ------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-5-system-detail/) | 2026-11-18 | 首次定版。1117 部署手冊整套重寫時由舊冊改寫而成（舊冊號見目錄最後的對照），步驟編號不變；1118 照每份約 300 行的上限拆檔，後段移到同一套的下一份 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
