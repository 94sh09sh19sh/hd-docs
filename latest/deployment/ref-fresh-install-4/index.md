# 從零部署本系統（第 4 份，V-12～V-17）

上層文件：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》

> **狀態：現行（常備參考）。** 改寫自第十五冊（1117）；編號 `V-xx`（沿用第十五冊），每一步下面註明對應的 `N-xx` 與 `W-xx`／`Y-xx`／`Z-xx`。1118 照步驟順序拆成七份，這是第 4 份；🧪／🏥／📍 標記的意思見第 1 份 0.2 節。

## 摘要

- V-12 由範本填 `.env`；`v0.5.0` 的範本第 98 行是斷掉的註解，整份複製後要刪掉那一行
- 逐項填法照《`.env` 怎麼填》（🏥）與之一（🧪）；三個位址都寫 V-08 的 `<主機>`，讀檔四行先留空
- V-13 建兩個資料卷；V-14 建置映像（`.env` 的位址在這之前一定要對）；V-15 建資料庫（`v0.5.0` 遷移 33 個）；V-16 啟動
- V-17 分四段：後端活著、網頁寫死的後端位址與 CORS、主機上用 `<主機>` 登入、護理站的電腦登入；之後看一次系統管理
- 護理端不要用 `localhost` 開，登入一定 `Failed to fetch`（1001 卡在這一步）

______________________________________________________________________

## 5. 設定

### V-12 由範本填 `.env`

對應：N-11、W-11、Y-03

**做什麼**

```
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

> ⚠️ **`v0.5.0` 的範本有一行斷掉的註解**：第 98 行是沒有 `#` 開頭的「aw_txt 與 hb-status.json）」（迭代 32 寫範本時 `\r` 被當成換行），整份複製後 compose 會說 `failed to read …\.env: line 98: unexpected character …`。在記事本裡**刪掉那一行**（或在開頭加 `#`）再存檔。master 已修好（`8c12505`），`v0.5.0` 之後的 tag 沒有這一行。

**逐項怎麼填，照另外兩份**：

- 🏥 實際部署 → 《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)》
- 🧪 模擬部署 → 《[`.env` 怎麼填之一：開發機演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation/index.md)》

三個位址都寫 V-08 定下的 `<主機>`。外殼 App 那三項（`HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING`、`MDM_KIOSK_BASE_URL`）與 `HD_EXPORT_DIR` **現在就一起填好**，雖然外殼第 8 節才做、資料取出更晚——每一條 `docker compose` 指令都會檢查它們。讀檔的四行（`HD_DIALYSIS_LIST_DIR`、`HD_LAB_DIR`、`COMPOSE_FILE`、`HOSPITAL_LAB_FIELD_MAP`）這時**都先留空、`COMPOSE_FILE` 維持註解**，到 9.5 節才接。

`JWT_SECRET` 用 PowerShell 產生（`.env` 那兩份有那一行），**不要用 `docker run node:…`**：1001 用那條，兩次都因為 Docker 查不到 Docker Hub 的網域而失敗（V-06 方框）。範本的註解到 `v0.5.0` 還寫著那一條，不要照它。

**怎麼知道成功了**

```
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
```

第一條**什麼都沒印出來**；第二條印出三行，**三行的主機部分都是 V-08 定的那一個**，前兩行是 `http://`、第三行是 `https://`。

**可能怎麼壞**

| 症狀                                                                       | 處置                                                                                                                                           |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `required variable HD_… is missing a value: 請設定 …`                      | 冒號後面寫的就是還缺什麼，補上                                                                                                                 |
| `couldn't find env file`                                                   | `$cfg` 沒設（V-09 的開工三行），或路徑打錯                                                                                                     |
| `failed to read …\.env: line N: unexpected character … in variable name …` | `.env` 第 N 行不是註解也不是「名稱=值」，最常見是上面那一行斷掉的註解。`notepad $cfg` 刪掉第 N 行（或在開頭加 `#`），再打一次 `config --quiet` |
| 第二條看到 `hd-server`                                                     | 那是舊版的範例，**照抄了**。換成 V-08 的值                                                                                                     |
| 🏥 第二條看到 `localhost`                                                  | 護理站與平板連不到 `localhost`（那是它們自己）。換成 V-08 的值                                                                                 |

> ⚠️ **不要拿 repo 根目錄的 `.env.example` 來填。** 那一份是日常開發（`npm run dev`）用的，變數名稱不同。部署用的範本只有 `deploy\hospital.env.example` 這一份。
>
> 📍 **1001**：院內主機上已經有一份 `C:\hd\hd-tablet-care\config\.env`。在那台上**不要再複製範本蓋掉它**，照《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-2/index.md)》第 6 節核對。

______________________________________________________________________

### V-13 建立兩個資料卷

對應：N-12、W-12

**只在第一次部署時做。**

**做什麼**

```
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
docker volume ls
```

**怎麼知道成功了**：清單裡看得到這兩個名字。

> 🧪 **模擬部署**：做之前先 `docker volume ls` 看一眼，**清單裡不該已經有 `hd-tablet-care-` 開頭的**。有的話是上一輪留下來的，照第 10.2 節撤除再回來，否則就不是「從零」。

______________________________________________________________________

## 6. 建置與啟動

### V-14 建置映像檔

對應：N-13、W-13

**做什麼**（**先記下開始時間**）

```
docker compose --env-file $cfg build
```

第一次約十分鐘，畫面會一直捲動，是正常的（1029 院內換版時有快取，一分鐘內就建完）。

**怎麼知道成功了**：最後出現 `Image hd-tablet-care:<tag> Built`（現在是 `hd-tablet-care:v0.5.0`）；再打 `docker images hd-tablet-care` 看得到這個 tag。**記下結束時間**。

`HD_PUBLIC_API_URL` 就是在這一步寫進護理端網頁檔案的。**`.env` 的位址在這一步之前一定要是對的**，之後才改就要再 `build` 一次。

**可能怎麼壞**

| 症狀                                                                                  | 處置                                                      |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `failed to resolve source metadata for docker.io/library/node`，後面有 `no such host` | Docker 查不到 Docker Hub 的網域，照 V-06 第二段那一列處理 |
| `npm error code ETIMEDOUT` 或 `ECONNRESET`                                            | 網路不穩，再打一次同一條指令；已下載的部分會沿用          |
| `pull access denied for hd-tablet-care`                                               | 打成 `up` 了。先 `build`                                  |

> 📍 **1001**：建置成功，但耗時沒有記到。

______________________________________________________________________

### V-15 建立資料庫

對應：N-14、W-14

**做什麼**（一整行，不要斷開）

```
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
```

**怎麼知道成功了**：中間出現 `SQLite database hd.db created at file:/data/hd.db`（第一次才會有），接著逐一套用遷移（`v0.5.0` 共 33 個），最後一行 `All migrations have been successfully applied.`

**可能怎麼壞**：錯誤訊息裡提到 `binaries.prisma.sh` → 映像檔建壞了，回 V-14 重建。**不要為了讓它下載而開任何網路例外。**

______________________________________________________________________

### V-16 啟動

對應：N-15、W-15

**做什麼**

```
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
```

**怎麼知道成功了**：`api`、`nurse-web`、`patient-web` 三個的狀態都是 `Up`。 `ai-gateway`、`shell-builder`、`data-export`、`hospital-api-sim` **不在清單上是對的**，它們各在 `ai`、`shell`、`export`、`simulation` 設定檔裡，平時不跑。

**可能怎麼壞**

| 症狀                              | 處置                                                                                                                 |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `api` 一直是 `Restarting`         | 設定被後端拒絕。`docker compose --env-file $cfg logs api --tail 30` 最後幾行會寫是哪一條，照訊息改 `.env` 再 `up -d` |
| `address already in use`          | 埠被佔了，回 V-07                                                                                                    |
| `bind source path does not exist` | `HD_BACKUP_DIR` 或 `HD_CONFIG_DIR` 指的資料夾不存在，回 V-09                                                         |

______________________________________________________________________

### V-17 確認它是對的，而且護理站登得進去

對應：N-16、W-16

這一步分四段，**照順序做**，第四段之後再看一次系統管理的設定。1001 卡在這一步：登入 `Failed to fetch`，原因是第二段的 CORS 不放行（《[第二次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001/index.md)》M-01；分析在《[第二次進院紀錄（1001）之一：為什麼登不進去](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-2-1001-login/index.md)》）。

**第一段：後端活著**（在主機上打）

```
curl.exe -s http://localhost:13000/api/health
[Console]::OutputEncoding = [Text.Encoding]::UTF8; docker compose --env-file $cfg logs api --tail 30
```

`13000` 是 `.env` 的 `HD_API_PORT`，**🏥 實際部署與 🧪 模擬部署都是 `13000`**。第一條用 `localhost`，是在主機自己身上問、不經過網路與防火牆：這一條不通，問題在服務本身；這一條通、後面不通，問題在位址或網路。第二條前面的 `[Console]::OutputEncoding …` 讓日誌的中文不變亂碼。

| 看什麼                        | 應該是                                                      |
| ----------------------------- | ----------------------------------------------------------- |
| health                        | `{"status":"ok",…}` 開頭                                    |
| 日誌「已連線至 SQLite」那一行 | 有 `synchronous=FULL`                                       |
| 日誌「版本標記」那一行        | 後面寫著 `（正式環境設定）`——模擬部署也是這樣，**這是對的** |
| 日誌「伺服器時區」            | `Asia/Taipei`，而且時間是現在                               |

**第二段：網頁裡寫死的後端位址、後端的 CORS 都是對的**（在主機上打，不必開瀏覽器）

先看網頁會連哪裡：

```
Select-String -Path $cfg -Pattern '^HD_PUBLIC_API_URL='
docker compose --env-file $cfg exec nurse-web grep -rhoE 'https?://[A-Za-z0-9.-]+:[0-9]+' apps/nurse-pwa/dist/assets
```

第二條印出的是**護理端網頁實際會去連的後端位址**（V-14 建置時寫進去的）。**兩條印出的位址要一模一樣**，例如都是 `http://<主機>:13000`。不一樣的話，是先 `build`、之後才改了 `.env` 的位址。再建置一次：

```
docker compose --env-file $cfg build
docker compose --env-file $cfg up -d
```

再看後端放不放行護理端（`<主機>` 換成 V-08 的值）：

```
Select-String -Path $cfg -Pattern '^CORS_ORIGINS='
curl.exe -s -i -H "Origin: http://<主機>:18080" http://<主機>:13000/api/health | Select-String Access-Control-Allow-Origin
```

第一條要是 `CORS_ORIGINS=http://<主機>:18080`；第二條要印出 `Access-Control-Allow-Origin: http://<主機>:18080`。

第二條**什麼都沒印出來**，就是後端不放行護理端的來源，登入一定 `Failed to fetch`——**1001 就是這個結果**。把第一條的值改對（或值是對的、只是改完還沒套用），然後 `docker compose --env-file $cfg up -d`，再打一次第二條。 `.env` 只在容器建立時讀一次，改完不 `up -d`，後端還在用舊的名單。視窗太窄時那一行可能只看得到後半段（例如 `…rol-Allow-Origin`），看得到 `Allow-Origin` 就是有放行。

**第三段：在主機上用正確的網址登入**

主機的瀏覽器開 **`http://<主機>:18080`**——**不要用 `localhost`**。

> ⚠️ 🏥 實際部署用 `http://localhost:18080` 開，頁面出得來，**登入一定失敗**（`Failed to fetch`）：網址列的來源是 `localhost`， `CORS_ORIGINS` 寫的是 `<主機>`，後端不放行。這不是壞掉，是設計如此。1001 現場就先用 `localhost` 開過。

用 `.env` 的 `SUPER_ADMIN_WORK_ID` 與 `SUPER_ADMIN_INITIAL_PASSWORD` 登入，**被要求改密碼**。

**第四段：在護理站的電腦上登入**

在**護理站的電腦**開同一個網址 `http://<主機>:18080`，登入成功。**這一段才算數**：主機連自己不經過防火牆，在主機上登得進去，不代表護理站也登得進去。🏥 護理站那台要 Windows 密碼、會休眠，請護理師輸入。

**第四段之後：系統管理看一次**（`v0.5.0` 空資料庫的預設值，1116 模擬實測）

1. 系統管理 → 功能開關：**全部關掉**。從零建置後有兩項預設是開的——「本次透析」面板、現有功能的小幅遊戲化——**這兩項也關**（DEP-29：面板等讀檔接上、對真實資料驗過才開；遊戲化等長者、社工、護理部看過才開）。其他開關若是開的，關掉並記下是哪一個，回來告訴開發端
1. 系統管理 → 營運參數與選項清單：「院方床位轉床號的方式」是 `0`（不是就改回 `0`）；「院方資料未更新提示的起始時刻」`8`、「結束時刻」`23`（迭代 32.1 的預設，不必改）；「院方資料同步」卡寫「還沒有設定院方資料的來源……」
1. 床位清單是空的，**是對的**：1005 迭代 15 起空資料庫不再預設 15 床（院內主機的 `01`～`15` 是 1001 用舊版建庫時留下的）；床位在 9.5 節接上讀檔後由院方資料自動加進來，不接讀檔就由護理長在系統管理建

**怎麼知道成功了**：四段都過，系統管理三項都對。

**可能怎麼壞**

| 症狀                                     | 處置                                                                                                                                                                                          |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 頁面開得了，按登入出現 `Failed to fetch` | 照《[護理站登不進去與主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login/index.md)》逐步查                                                                           |
| 頁面開得了，出現 `工作ID 或密碼錯誤`     | 有連到後端，帳號或密碼不對。第一個帳號**只在資料庫還沒有任何使用者時建立**，事後改 `.env` 不會改到已建立的帳號                                                                                |
| 沒有帳號可以登入                         | `SUPER_ADMIN_*` 沒填。補上再 `up -d`，**資料庫不必重建**                                                                                                                                      |
| 護理站的電腦開不到頁面，主機自己開得到   | 防火牆或網段，找資訊室（Q-27）。**不要自己關防火牆**                                                                                                                                          |
| 護理站的電腦連頁面都說找不到主機         | `<主機>` 是名稱而護理站查不到，回 V-08；決定改用 IP 就照《[護理站登不進去與主機位址之一：換主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login-switch-ip/index.md)》 |
| 日誌的「伺服器時區」不是 `Asia/Taipei`   | 後端會拒絕啟動。不要自己改主機時區，找資訊室                                                                                                                                                  |

> 改完密碼之後，🏥 實際部署要把新密碼交給院方指定的人保管（護理長自己改掉管理者密碼，開發端從此不知道），`.env` 裡的初始密碼可以清空（清空後 `up -d`）。
>
> 📍 **1001**：第一段 health 正常；登入出現 `Failed to fetch`。現場查到「放不放行護理端」那一條**印出空的**——後端不放行護理端的來源，離院時未解。1029 換成 IP 之後護理站 15:34 登得進去。
>
> 🧪 **模擬部署**：`<主機>` 是開發機的區網 IP，開 `http://<開發機區網 IP>:18080`。登入成功之後，**故意用 `http://localhost:18080` 再開一次、按登入**，親眼看一次 `Failed to fetch` 長什麼樣——這就是院內用錯網址時會看到的。看完關掉，回到用區網 IP 開的那一頁。第四段改成用手機的瀏覽器開同一個網址（要連同一個 Wi-Fi；手機沒有 Ctrl＋F5，改成關掉分頁重開）；開不到時照 V-25 方框處理防火牆。

______________________________________________________________________

上一份：《[從零部署本系統（第 3 份，V-06～V-11）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-3/index.md)》｜下一份：《[從零部署本系統（第 5 份，V-18～V-24）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-5/index.md)》｜第一份（索引）：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
