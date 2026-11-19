# 第二次進院（1001）· 從零部署本系統之十：收掉 0922 留下的東西（L-04～L-07、開發機練習）

上層文件：[《第二次進院（1001）· 從零部署本系統》](visit-2-system.md)

> 狀態：**凍結**（隨第二次進院；1029 確認容器已不在，其餘見[《之九》](visit-2-system-cleanup.md)「最新狀況」）；1117 由舊的第十四冊之三改寫；編號 `L-xx`，是[《第一次進院紀錄（0922，失敗）》](record-1-0922-2.md) F-10 的新手版

## 摘要

- 接《之九》的 L-03：第 2 節收掉，L-04 收掉容器、L-05 刪掉主機 C 槽上那一份 clone、L-06 `python` 映像檔問過再決定
- 第 3 節收完之後：L-07 確認收乾淨了、順便查 3000 埠，以及演練紀錄這一段應該有的
- 第 4 節什麼時候當場停手
- 附錄：🧪 在開發機上先練一次，練完收尾
- 三條鐵則與最新狀況在《之九》

## 2. 收掉

### L-04 收掉容器

對應：F-10 ③

**做什麼**

```powershell
docker stop dialysis_system_v0
docker rm dialysis_system_v0
docker ps -a --filter name=dialysis_system_v0
```

`stop` 是停下來，`rm` 是刪掉這個容器。

**怎麼知道成功了**：前兩行各印出一次 `dialysis_system_v0`；第三行**只剩標題那一列**。

`docker rm` 只刪容器本身——容器裡的 shell 歷史、Git 設定、只在容器裡的那份 clone 都跟著沒了——**不會動到主機 C 槽上的任何檔案**。這是對的：C 槽上那一份，下一步在主機上刪。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `You cannot remove a running container` | 第一行沒成功。再打一次 `docker stop`，等它印出名字再 `rm` |
| `docker stop` 超過一分鐘沒回來 | 按 Ctrl+C，改打 `docker kill dialysis_system_v0`，再 `rm` |
| `No such container` | 已經刪掉了。看第三行確認就好 |

---

### L-05 刪掉主機 C 槽上那一份 clone

對應：F-10 ④

**只有 L-03 判斷「在主機的 C 槽」（或 L-01 方框在 C 槽找到）時才做。** 其他情形跳到 L-06。

**做什麼**

1. 把 L-03 換算好的路徑存進一個變數，之後就不必重打（例子是 `C:\hd-tablet-care`，換成你抄下來的）：

   ```powershell
   $old = "C:\hd-tablet-care"
   ```

2. 在主機上認一次，確定它是本系統、不是別人的：

   ```powershell
   Get-ChildItem $old
   Select-String -Path "$old\.git\config" -Pattern "url"
   ```

   | 看什麼 | 應該是 |
   |---|---|
   | 第一行 | 本系統的檔案：`apps`、`docs`、`packages`、`package.json`、`README.md`… |
   | 第二行 | `url = …` 那一行裡有 `hd-tablet-care` |

3. 把這兩段輸出給資訊室的同仁看，說明：「這是 0922 我們留下的原始碼，要刪掉。」**對方同意了**才往下。

4. 用檔案總管刪（會先進資源回收筒，刪錯還救得回來）：

   ```powershell
   explorer.exe (Split-Path $old)
   ```

   這一行會開啟它的上一層資料夾。在那個資料夾上**按右鍵 → 刪除**。

5. 回 PowerShell 確認：

   ```powershell
   Test-Path $old
   ```

6. 資訊室確認沒刪錯之後，開**資源回收筒**，對**那一項**按右鍵 → 刪除。**不要按「清理資源回收筒」**：那會連同這台主機上其他人丟進去的東西一起清掉。

**怎麼知道成功了**：第 5 步印出 `False`；資源回收筒裡沒有那一項。

> ⚠️ **不要改用 `Remove-Item -Recurse -Force`。** 那是直接永久刪除，路徑打錯一個字就救不回來，而這台主機上還有別人的專案。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 第 2 步說找不到路徑 | 路徑換算錯了。回頭對一次 L-03 抄下來的位置；容器已經刪了查不回來的話，用 L-01 方框那一條在主機上找 |
| 第 2 步列出來的不像本系統，或 `url` 裡沒有 `hd-tablet-care` | **停手，不要刪。** 路徑換錯了，刪下去的會是別人的東西 |
| 刪的時候跳出「太大，無法放入資源回收筒，要永久刪除嗎？」 | 再核對一次第 2 步的輸出，確定是本系統，再按「是」 |
| 「檔案正在使用中」 | 有程式開著裡面的檔案。把其他檔案總管視窗、編輯器關掉再刪；還是不行，回 L-04 確認容器真的刪掉了 |
| 資訊室不同意刪 | 不刪。演練紀錄寫「保留，資訊室＿＿決定」，照樣往下 |

---

### L-06 `python` 映像檔：問過再決定

對應：F-10 ⑤

**做什麼**：先看，不刪。

```powershell
docker image ls python
docker ps -a --filter ancestor=python
```

第一行列出主機上所有 `python` 開頭的映像檔；第二行列出還有哪些容器是用它開的。

**怎麼判斷**

| 看到 | 意思 |
|---|---|
| 第一行只有一列，`TAG` 是 `latest`；第二行只有標題列 | 很可能只有 0922 那次用過。**問資訊室**：「這個 `python:latest` 是我們上次拉的，你們另一個專案有沒有在用？」 |
| 第一行有好幾列（例如還有 `3.11-slim`） | 其他那幾列是別人的，**不要碰**；`latest` 那一列一樣先問 |
| 第二行有容器 | 有人正在用它開的容器，**不刪**，演練紀錄記下容器名字即可 |

資訊室說可以刪，才打：

```powershell
docker image rm python:latest
```

**怎麼知道成功了**：印出一串 `Untagged: …`、`Deleted: sha256:…`；再打一次 `docker image ls python`，`latest` 那一列不見了。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `conflict: unable to remove repository reference … container … is using its referenced image` | 還有別的容器在用它。**不要加 `-f` 硬刪**，保留下來 |
| 資訊室不確定 | 保留。它只佔一點磁碟空間，不影響本系統。演練紀錄寫「保留，待資訊室確認」 |

---

## 3. 收完之後

### L-07 確認收乾淨了，順便查 3000 埠

對應：F-09

**做什麼**

```powershell
docker ps -a --format "{{.Names}}  {{.Image}}  {{.Status}}"
Get-NetTCPConnection -State Listen -LocalPort 3000, 9000 -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess
```

**怎麼知道成功了**

| 看什麼 | 應該是 |
|---|---|
| 第一行 | 沒有 `dialysis_system_v0`。其他列是另一個專案的，**抄下名字即可，不要動** |
| 第二行，3000 那一列 | 兩種都算對，照實寫進演練紀錄：**消失了** → 當初佔著 3000 的就是我們那個容器；**還在** → 是別人的，往下查是誰 |

3000 還在的話，查是誰佔的（`<OwningProcess>` 換成上一行印出的數字）：

```powershell
Get-Process -Id <OwningProcess> | Select-Object Id, ProcessName, Path
docker ps --format "{{.Names}}  {{.Ports}}"
```

行程是 `com.docker.backend` 或 `wslrelay` 的話，那是 Docker 在轉送某個容器的埠，第二行會看到是哪一個。把結果告訴資訊室，**請他們登記這個埠是誰的**。

> ⚠️ **不論 3000 空出來與否，本系統都不用 3000，也不用 9000。** 本系統用的是資訊室 0930 確認的 `13000`、`18080`、`18081`，在 N-07 確認沒人在用。

### 演練紀錄這一段應該有的

| 步驟 | 要寫的 |
|---|---|
| L-01 | 容器當時的狀態（Up／Exited／已不在） |
| L-02 | 三行輸出原文 |
| L-03 | clone 的位置、`log -1` 那一行、有沒有權杖殘留（只寫有無） |
| L-04 | 容器已刪 |
| L-05 | 主機上那一份已刪／只在容器裡／未找到／資訊室決定保留 |
| L-06 | `python:latest` 已刪／保留（誰決定的） |
| L-07 | 3000 埠空出來了，或被誰佔著 |

**七格都有答案，這一冊就做完了**——「保留」「未找到」也是答案。接著回 N-04。

---

## 4. 什麼時候當場停手

下列任一種出現，**停手、記錄、不要硬收**：

- L-03 的 `ls /app` 裡**沒有** `Windows`、`Users`（掛進去的不是 C 槽，收法不同）
- 要刪的資料夾、映像檔，看起來不像本系統的
- 有人說「整個 `prune` 一下比較快」「加個 `-f` 就刪得掉了」
- 資訊室的同仁不在場，卻要刪主機上的檔案

**L-04（收容器）沒完成，就不要開始部署**：那個容器掛著整顆 C 槽，留著它部署，等於主機上一直開著一扇沒人看的門。L-05、L-06 因資訊室決定保留而沒刪，不擋部署，寫進交接文件的「已知限制」即可。

---

## 附錄：在開發機上先練一次

🧪 **這一段只在開發機上做。** 它搭一個無害的替身，讓你在進院前把 L-01～L-07 的指令親手打過一次。

替身和 0922 那個容器同名、同映像檔，但**只掛一個空資料夾、不對應任何埠**。

> ⚠️ **練習時絕對不要照《第一次進院紀錄（0922，失敗）》1.1 節那一行原樣打**：那一行會把你開發機的整顆 C 槽掛進去。

**搭替身**

```powershell
New-Item -ItemType Directory -Force C:\hd-drill | Out-Null
docker run -dit --name dialysis_system_v0 -v C:\hd-drill:/app python
docker exec dialysis_system_v0 git init -q /app/hd-tablet-care
docker exec dialysis_system_v0 git -C /app/hd-tablet-care remote add origin https://FAKE-TOKEN@github.com/94sh09sh19sh/hd-tablet-care.git
docker exec dialysis_system_v0 git -C /app/hd-tablet-care -c user.name=drill -c user.email=drill@example.invalid commit -q --allow-empty -m drill
```

第二行第一次會下載 `python` 映像檔（約 1 GB），要等幾分鐘。`FAKE-TOKEN` 是假的，只是模擬權杖殘留長什麼樣子。

**然後照 L-01 起往下做，與院內不同的地方：**

| 步驟 | 練習時 |
|---|---|
| L-02 | `Source` 會是 `C:\hd-drill` 或它的換算寫法；第三行是 `{}`（替身沒有對應埠） |
| L-03 第 1 步 | `ls /app` 只會看到 `hd-tablet-care`，**看不到 `Windows` 是對的**（替身只掛了 `C:\hd-drill`），照樣往第 2 步 |
| L-03 換算路徑 | `/app` 換成 `C:\hd-drill`：`/app/hd-tablet-care` ＝ `C:\hd-drill\hd-tablet-care` |
| L-05 | 第 2 步只會看到 `.git`（替身沒有程式碼），`url` 裡有 `hd-tablet-care` 即可；第 3 步不必問人 |
| L-06 | 開發機上沒有別的東西在用 `python:latest` 的話，直接刪 |
| L-07 | 第二行跳過 |

**練完收尾**

```powershell
Remove-Item C:\hd-drill
docker ps -a --filter name=dialysis_system_v0
```

第一行把空下來的 `C:\hd-drill` 刪掉（裡面還有東西時 PowerShell 會問你，那表示 L-05 沒做完）；第二行只剩標題列就收乾淨了。

上一份：[《第二次進院（1001）· 從零部署本系統之九：收掉 0922 留下的東西（L-01～L-03）》](visit-2-system-cleanup.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/visit-2-system-cleanup-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《第二次進院（1001）· 從零部署本系統之九：收掉 0922 留下的東西》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
