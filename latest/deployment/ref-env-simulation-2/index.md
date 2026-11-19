# `.env` 怎麼填之二：開發機演練（第 2～5 節）

上層文件：《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)》　接在《[`.env` 怎麼填之一：開發機演練（第 0～1 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation/index.md)》之後

> **狀態：現行（常備參考）。** 🧪 開發機演練（模擬部署）那一份 `.env`。1117 由第十五冊之二改寫，節號沿用（這一份是第 2～5 節）；沒有步驟編號。第 0～1 節（開始之前、逐項填）在之一；🏥 院內的填法看《[`.env` 怎麼填](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env/index.md)》。

## 摘要

- 第 2 節：已接上模擬讀檔（1.9 的 A）的整份樣子，只有 tag、三個位址裡的 IP、`JWT_SECRET` 要換
- 第 3 節：與院內同樣的三條核對，再逐項看 `HD_SHELL_SIGNING=dev`、`HD_SIMULATION_DEPLOYMENT=yes`
- 第 4 節：開發機的 IP 變了：同一輪內三個位址一起改、重建、重跑 `shell-builder`、手機重新佈建；做完的那一輪不必管
- 第 5 節：與院內的差異總表，🧪 那一欄的值都不可以出現在院內的 `.env`（三個埠例外）
- 不要把模擬部署的 `.env` 複製到院內再改

## 2. 填好的樣子

只有四處要換成你自己的：`HD_IMAGE_TAG`、三個位址裡的 IP（同一個）、`JWT_SECRET`。其餘照抄即可。下面是\*\*已接上模擬讀檔（1.9 的 A）\*\*的樣子；V-12 剛填時，`COMPOSE_FILE` 那一行先維持範本的註解：

```
HD_IMAGE_TAG=v0.5.0

HD_BACKUP_DIR=C:\hd-sim\backups
HD_CONFIG_DIR=C:\hd-sim\config
HD_EXPORT_DIR=C:\hd-sim\export

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://192.0.2.23:13000
CORS_ORIGINS=http://192.0.2.23:18080
MDM_KIOSK_BASE_URL=https://192.0.2.23:18081

HD_SHELL_SRC_DIR=C:\hd-sim\hd-kiosk-shell
HD_SHELL_SIGNING=dev
KIOSK_SHELL_MIN_VERSION=

JWT_SECRET=<這一輪產生的那一串>
JWT_EXPIRES_IN=8h

SUPER_ADMIN_WORK_ID=sim-admin
SUPER_ADMIN_INITIAL_PASSWORD=Sim-Init-2026
SUPER_ADMIN_DISPLAY_NAME=模擬部署管理員

BACKUP_DAILY_AT=03:00
DB_DISK_MIN_FREE_MB=1024

LLM_PROVIDER=mock
LLM_ENDPOINT=
LLM_API_KEY=
LLM_MODEL_ID=
LLM_TIMEOUT_SECONDS=150
LLM_HEALTH_TIMEOUT_SECONDS=5

HD_DIALYSIS_LIST_DIR=
HD_LAB_DIR=
COMPOSE_FILE=docker-compose.yml;docker-compose.hospital-files-sim.yml
HOSPITAL_LAB_FIELD_MAP=

HOSPITAL_API_BASE_URL=
HD_SIMULATION_DEPLOYMENT=yes

BINDING_MAX_HOURS=6
BINDING_EXPIRY_SWEEP_SECONDS=60
SYMPTOM_TREND_WINDOW_DAYS=30
SYMPTOM_TREND_REPORT_LIMIT=10
DEVICE_ONLINE_THRESHOLD_SECONDS=90
REALTIME_HEARTBEAT_SECONDS=20
```

______________________________________________________________________

## 3. 填完之後核對

與院內用同樣的三條（上層第 3 節）：

```
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^[^#].*(<|>|hd-server|localhost)'
Select-String -Path $cfg -Pattern '^(HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL)='
```

前兩條什麼都沒印出來才算過（第二條只看不是 `#` 開頭的行）；第三條印出三行，IP 都相同。第一條印出 `failed to read …\.env: line N: …` 就是 0.1 節那一行斷掉的註解還在。再用眼睛核對：

- `HD_IMAGE_TAG` 與 `git describe --tags` 相同
- 三個目錄都在 `C:\hd-sim\` 底下
- 三個埠是 `13000`、`18080`、`18081`（或你 V-07 換過的），而且與位址裡的埠對得上
- 三個位址都是 **Wi-Fi 那張網卡的 IP**，一字不差；`MDM_KIOSK_BASE_URL` 是 **`https://`**
- **`HD_SHELL_SIGNING=dev`**
- `LLM_PROVIDER=mock`
- **`HD_SIMULATION_DEPLOYMENT=yes`**；院方資料那六行是 1.9 表上同一欄的樣子（A：`COMPOSE_FILE` 帶 `docker-compose.hospital-files-sim.yml`、`HOSPITAL_API_BASE_URL` 空白；C：`HOSPITAL_API_BASE_URL` 指向 `hospital-api-sim`）
- `HD_LAB_DIR` 空白，`COMPOSE_FILE` 裡沒有 `docker-compose.lab-files.yml`
- **沒有** `HIGH_RISK_WRITTEN_CONFIRMATION` 這一行（1010 迭代 18.1 起拿掉）
- 整份沒有任何一個值加了引號

______________________________________________________________________

## 4. 開發機的 IP 變了

換了 Wi-Fi、隔天重新連線，IP 都可能變。症狀是護理端登入 `Failed to fetch`、手機開不到下載頁，或外殼一片空白。

| 情況                 | 做什麼                                                                                                                                                                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 還在同一輪模擬部署中 | 三個位址的 IP 一起改 → `docker compose --env-file $cfg build` → `up -d`（`HD_PUBLIC_API_URL` 寫在網頁檔案裡，要重建）→ 重跑 `shell-builder`（V-22，它發現位址變了會重簽伺服器憑證）→ `restart patient-web`（V-24）→ 手機上的 App「清除資料」，重新註冊、佈建 |
| 這一輪已經做完       | 不必管，V-32 撤除就好。下一輪重新查 IP 再填                                                                                                                                                                                                                  |

這一段在院內**不該發生**：院內的位址擇一之後就不再換（V-08）。模擬部署碰到一次，正好體會為什麼——改一個 IP，要重建網頁、重簽憑證、每一台平板重新佈建。

______________________________________________________________________

## 5. 與院內的差異總表（🧪／🏥）

帶進院之前再看一次這張表：**🧪 那一欄的每一個值，都不可以出現在院內那份 `.env` 裡**——只有三個埠例外，兩邊剛好相同；空白的幾項兩邊也相同。

| 變數                                                                  | 🏥 院內正式主機                                                                       | 🧪 開發機演練                                                                   |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `HD_BACKUP_DIR`、`HD_CONFIG_DIR`、`HD_EXPORT_DIR`、`HD_SHELL_SRC_DIR` | `C:\hd\hd-tablet-care\…`（1001 起院內實際用的；`HD_EXPORT_DIR` 1027 起才有）          | `C:\hd-sim\…`                                                                   |
| 三個埠                                                                | `13000`、`18080`、`18081`（0930 資訊室確認）                                          | 相同（例外）                                                                    |
| 三個位址的主機                                                        | V-08 定的院內固定 IP（1029 起）                                                       | 開發機的 Wi-Fi IP                                                               |
| `HD_SHELL_SIGNING`                                                    | **`hospital`**                                                                        | **`dev`**                                                                       |
| `HD_DIALYSIS_LIST_DIR`（1111）                                        | 從零部署時空白；啟用讀檔後 `C:\API_Fetch\IDH_interface`（1116 起院內現況）            | 空白（1.9 的 A）；練院內那種路徑時 `C:\hd-sim\…`（B）                           |
| `HD_LAB_DIR`、`HOSPITAL_LAB_FIELD_MAP`（1111）                        | 空白（`hb` 先不讀）                                                                   | 空白                                                                            |
| `COMPOSE_FILE`（1111）                                                | 從零部署時維持註解；啟用讀檔後 `docker-compose.yml;docker-compose.dialysis-files.yml` | `docker-compose.yml;docker-compose.hospital-files-sim.yml`（A）；B 與院內同一種 |
| `HOSPITAL_API_BASE_URL`（1005）                                       | **一律空白**（1110 起不打院方 API；1005～1109 是「只探測、探測過報備過才填」）        | 空白（A、B）；舊做法 C 是 `http://hospital-api-sim:8090/dialysislist.php`       |
| `HD_SIMULATION_DEPLOYMENT`（1005）                                    | **永遠空白**                                                                          | **`yes`**                                                                       |
| ~~`HIGH_RISK_WRITTEN_CONFIRMATION`（1010）~~                          | 18.1 起不在設定檔：書面確認拿到後在系統管理登記                                       | 18.1 起不在設定檔：**永遠不登記**                                               |
| `JWT_SECRET`                                                          | 院內當場產生                                                                          | 每一輪各自產生                                                                  |
| `SUPER_ADMIN_*`                                                       | 護理長給的工號與名字、臨時密碼                                                        | `sim-admin` 之類的虛構值                                                        |
| 其他                                                                  | 相同                                                                                  | 相同                                                                            |

兩邊**形狀相同**的地方也值得記住：三個位址都是「同一個別人連得到的主機」，護理端都用 `http://<主機>:18080` 開，都不用 `localhost`；讀檔都是唯讀掛一個資料夾、都用讀檔檢查驗。

> ⚠️ **不要把模擬部署的 `.env` 複製到院內再改。** 從院內主機上的範本重新複製、照上層一項一項填（院內主機上已經有一份就照上層第 6 節核對）。抄過去最常漏改的是 `HD_SHELL_SIGNING`，而它一旦讓院內主機產生了開發用金鑰，就要撤掉資料卷重來；其次是 `HD_SIMULATION_DEPLOYMENT=yes`，留著它院內就擋不住模擬資料。

______________________________________________________________________

______________________________________________________________________

上一份：《[`.env` 怎麼填之一：開發機演練（第 0～1 節）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版                                                                                 | 日期       | 異動                                                                                            |
| ------------------------------------------------------------------------------------ | ---------- | ----------------------------------------------------------------------------------------------- |
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-env-simulation-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《`.env` 怎麼填之一：開發機演練》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
