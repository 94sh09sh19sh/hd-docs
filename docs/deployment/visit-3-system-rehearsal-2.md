# 第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之八：開發機才做的演練（I-06～I-12、照主文件做 J-04～J-30）

上層文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

> - 狀態：**已照做 1029（第一輪），凍結**。第一輪做到 J-30，I-13～I-15 沒做，判定 `v0.4.0` **還不能**帶進院（《[第三次進院紀錄（1029，部分成功）](record-3-1029.md)》O-02）；改寫來源（1117）：第十七冊；編號：`I-xx`（沿用第十七冊），中間照做的是主文件的 `J-xx`

開發機演練共三份（之七～之九），這一份是第 2～4 節（I-06～I-12、照主文件做 J-04～J-30）；讀之前（要準備的東西、時間、規矩）與第 1 節準備在《[…之七：開發機才做的演練（第 0 節、I-01～I-05）](visit-3-system-rehearsal.md)》。

## 摘要

- 這一份是第 2 節（I-06～I-12）與第 3、4 節
- 第 2 節在開發機上重做一次 1001 那天的部署：`v0.3.0`、主機位址用名稱、放行名單故意填錯，做完和院內主機一樣登不進去
- I-06 建資料夾與開工三行；I-07 clone、切到 `v0.3.0`；I-08 照 1001 的樣子填 `.env`（`CORS_ORIGINS` 故意填 `hd-server`）
- I-09 建資料卷、建置、建資料庫、啟動；I-10 外殼與 APK、金鑰備份、病人端改走 HTTPS；I-11 舊版 AI 閘道
- I-12 確認重現了 1001：親眼看到 `Failed to fetch`、放行檢查是空的
- 第 3、4 節翻開印好的詳細版，從 J-04 照做到 J-30；J-01～J-03、J-31～J-33 跳過，J-30 做完回到之九

---

## 2. 把開發機變成「1001 離院時的院內主機」

這一節在開發機上重做一次 1001 那天的部署：`v0.3.0`、位址用名稱、**放行名單填錯**。做完之後，開發機會和院內主機一樣：三個服務在跑、護理端登不進去。

### I-06 建資料夾、開工三行（＝V-09）

**做什麼**

```powershell
$root = "C:\hd-sim"
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
```

**怎麼知道成功了**：列出 `backups`、`config` 兩個資料夾。

> ⚠️ PowerShell 關掉再開，要重打 `$root`、`$cfg` 兩行，I-07 之後再加 `cd $root\repo`（就是主文件 J-04 的開工三行，只是根目錄換成 `C:\hd-sim`）。

---

### I-07 clone，切到 `v0.3.0`（＝V-11）

**做什麼**

```powershell
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git $root\repo
git clone git@github-hd-kiosk-shell:94sh09sh19sh/hd-kiosk-shell.git $root\hd-kiosk-shell
cd $root\repo
git checkout v0.3.0
git describe --tags
```

**怎麼知道成功了**：最後一行正好是 `v0.3.0`。一大段 `detached HEAD` 是正常的。

| 症狀 | 處置 |
|---|---|
| `destination path … already exists` | 上一輪沒撤除乾淨，回 I-03 |
| `Connection reset by … port 22` | 網路切斷連線。刪掉殘留的資料夾（`Remove-Item -Recurse -Force $root\repo`）再 clone 一次 |

---

### I-08 照 1001 的樣子填 `v0.3.0` 的 `.env`

**做什麼**

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

這是 `v0.3.0` 的範本，**沒有** `HD_EXPORT_DIR` 與院方 API 那兩行——院內那一份也沒有，J-16 才補。照下面填（`<名稱>` 換成 I-05 的電腦名稱，三處都是；`JWT_SECRET` 用下一段的指令產生）：

```
HD_IMAGE_TAG=v0.3.0

HD_BACKUP_DIR=C:\hd-sim\backups
HD_CONFIG_DIR=C:\hd-sim\config

HD_API_PORT=13000
HD_NURSE_PORT=18080
HD_PATIENT_PORT=18081

HD_PUBLIC_API_URL=http://<名稱>:13000
CORS_ORIGINS=http://hd-server:18080
MDM_KIOSK_BASE_URL=https://<名稱>:18081

HD_SHELL_SRC_DIR=C:\hd-sim\hd-kiosk-shell
HD_SHELL_SIGNING=dev
KIOSK_SHELL_MIN_VERSION=

JWT_SECRET=<這一輪產生的那一串>
JWT_EXPIRES_IN=8h

SUPER_ADMIN_WORK_ID=sim-admin
SUPER_ADMIN_INITIAL_PASSWORD=Sim-Init-2026
SUPER_ADMIN_DISPLAY_NAME=模擬部署管理員
```

其餘各行（備份時間、AI、營運參數）**維持範本的值**。`.env` 各格的意思見《[`.env` 怎麼填之一：開發機演練](ref-env-simulation.md)》。

產生 `JWT_SECRET`（與院內同一行 PowerShell，不用 Node.js）：

```powershell
$b = New-Object byte[] 48; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); [Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_')
```

> 💡 **`CORS_ORIGINS=http://hd-server:18080` 是故意填錯的**：照抄了舊範例的 `hd-server`，就是出發前推測 1001 最可能的原因（《[第二次進院紀錄（1001）之一：為什麼登不進去](record-2-1001-login.md)》的可能 A）。這一輪要親眼看到這個錯怎麼出現、J-09～J-14 怎麼把它修好。（1029 院內抄到的名單其實是對的，見紀錄 O-01；演練照樣用這個錯來練修法。）

> ⚠️ **`HD_SHELL_SIGNING` 一定是 `dev`**，院內才是 `hospital`。忘了改、已經跑過 `shell-builder` 的話，只能撤除重來（I-17）。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
Select-String -Path $cfg -Pattern '^(HD_IMAGE_TAG|HD_PUBLIC_API_URL|CORS_ORIGINS|MDM_KIOSK_BASE_URL|HD_SHELL_SIGNING)='
```

第一條什麼都沒印；第二條五行，與上面一致（`CORS_ORIGINS` 是 `hd-server`，其他兩個位址是 `<名稱>`）。

---

### I-09 建資料卷、建置、建資料庫、啟動（＝V-13～V-16）

**做什麼**（記下開始時間；第四條是一整行）

```powershell
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
docker compose --env-file $cfg build
docker compose --env-file $cfg run --rm --no-deps api node apps/api/scripts/prisma-cli.mjs migrate deploy --schema apps/api/prisma/schema.prisma
docker compose --env-file $cfg up -d
docker compose --env-file $cfg ps
curl.exe -s http://localhost:13000/api/health
```

**怎麼知道成功了**：建置最後 `Image hd-tablet-care:v0.3.0 Built`；建資料庫最後 `All migrations have been successfully applied.`；`ps` 三個服務 `Up`；health 是 `{"status":"ok",…}`。記下結束時間。

| 症狀 | 處置 |
|---|---|
| `no such host` | 再打一次 |
| `api` 一直 `Restarting` | `docker compose --env-file $cfg logs api --tail 30` 看是哪一條設定被拒 |

---

### I-10 外殼：建 `shell-builder`、建 APK、備份金鑰、病人端改走 HTTPS（＝V-21～V-24）

**做什麼**（記下開始時間；第一條第一次約 30 分鐘）

```powershell
docker compose --env-file $cfg --profile shell build shell-builder
docker compose --env-file $cfg --profile shell run --rm shell-builder
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-backup
docker compose --env-file $cfg restart patient-web
docker compose --env-file $cfg --profile shell run --rm shell-builder keys-info
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 第一條最後幾行 | 「✓ 外殼 v0.3.0（…，契約第 1 版）已準備好，相依已下載」 |
| 第二條 | 「這一次新產生：院內 CA 伺服器憑證（`<名稱>`） APK 簽章金鑰（開發用）」，接著 APK 檔名與三個 SHA-256 |
| 第三條 | 「已備份：備份目錄/keys/hd-keys-<時間>.tar.gz」——這一份就是模擬的「1001 那份金鑰備份」，**檔名抄下來** |
| `keys-info` | 「伺服器憑證」那一行是 `DNS:<名稱>` |

記下結束時間。

---

### I-11 AI 閘道（舊版）（＝V-29、V-30）

1001 有沒有做這一步沒記到。這裡**做**，因為這是比較難的情形：J-20 要把一個舊版閘道換成新版。

**做什麼**

```powershell
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
docker compose --env-file $cfg --profile ai build ai-gateway
docker compose --env-file $cfg --profile ai up -d ai-gateway
docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
```

**怎麼知道成功了**：建置最後 `全部通過`；最後一條印出 `503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}`。

---

### I-12 確認重現了 1001

**做什麼**

1. 開發機的瀏覽器開 `http://<名稱>:18080`，用 `sim-admin` / `Sim-Init-2026` 登入。
2. 在 PowerShell 打放行檢查：

   ```powershell
   curl.exe -s -i -H "Origin: http://<名稱>:18080" http://<名稱>:13000/api/health | Select-String Access-Control-Allow-Origin
   ```

**怎麼知道成功了**：

| 看什麼 | 應該是 |
|---|---|
| 登入 | 登入鈕下面出現 **`Failed to fetch`** |
| 放行檢查 | **什麼都沒印** |

兩個都看到了，開發機就是「1001 離院時的院內主機」。**記下這一刻的時間**，然後**把 PowerShell 關掉**（院內到場時也是開一個新的視窗）。

| 症狀 | 處置 |
|---|---|
| 竟然登得進去 | `CORS_ORIGINS` 沒有照 I-08 填成 `hd-server`，或瀏覽器用了 `localhost` 以外的寫法剛好對上。回 I-08 檢查 |

---

## 3、4. 照主文件做 J-04～J-30

**從這裡開始，翻開印好的詳細版，從 J-04 一步一步照做到 J-30。** 每一步模擬部署要改的地方與要記下、要確認的東西，寫在那一步的 🧪：主文件是一行，詳細版的「🧪 開發機演練」是完整的；寫「照做」的，就是一字不差照打（`$root` 換成 `C:\hd-sim`）。

- J-01～J-03 跳過（J-01 就是 I-01；J-02 的問題清單照樣在出發前寄）
- J-08 之前，先照詳細版 J-08 的 🧪 開三條只對私人網路的防火牆規則、把 Wi-Fi 設成「私人」（I-17 撤除時刪規則）
- J-13 之後與 J-29 之後各多做一件（寫在那兩步的 🧪）
- J-31～J-33 跳過；J-30 做完回到第 5 節

---

上一份：《[…之七：開發機才做的演練（第 0 節、I-01～I-05）](visit-3-system-rehearsal.md)》；下一份：《[…之九：開發機才做的演練（I-13～I-17、附錄）](visit-3-system-rehearsal-3.md)》；主文件：《[第三次進院（1029）· 接手 v0.3.0、換成 IP、換版](visit-3-system.md)》

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第三次進院（1029）· 接手 v0.3.0、換成 IP、換版之七：開發機才做的演練》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
