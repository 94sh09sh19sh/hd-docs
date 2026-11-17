# 第二次進院（1001）· 從零部署本系統之二：詳細版（N-08～N-12）

上層文件：[《第二次進院（1001）· 從零部署本系統》](visit-2-system.md)

> 狀態：**已照做 1001，凍結**（結果見[《第二次進院紀錄（1001，部分成功）》](record-2-1001.md)）；1117 由舊的第十四冊改寫；編號與主文件相同（`N-xx`），每一步開頭的「對應」是沿用的原步驟（`W-xx`、`Y-xx`、`Z-xx` 在哪一份，見[《之一》](visit-2-system-detail.md)開頭）

## 摘要

- 第 3 節取得程式碼 N-08～N-10：決定根目錄並設好開工三行、產生本系統 repo 的部署金鑰並設 `.ssh\config`、clone 並切到 tag
- 第 4 節設定 N-11～N-12：由範本建 `.env`（逐項填法在《之七》）、建兩個資料卷
- 每一步寫完整指令、怎麼知道成功了、可能怎麼壞（例如 22 埠被切斷時改走 443）
- 🏥 根目錄 1001 實際放在 C 槽（紀錄 M-03）；🧪 用 `C:\hd-sim`，一定從 GitHub 全新 clone
- N-07 以前在《之一》，N-13 起在《之三》

## 3. 取得程式碼

### N-08 建立資料夾，並設好「開工三行」

對應：W-08

**做什麼**

先決定根目錄。🏥 用 `D:\hd-tablet-care`（1001 實際用了 `C:\hd\hd-tablet-care`，紀錄 M-03）；🧪 用 `C:\hd-sim`。

```powershell
$root = "D:\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
$cfg
```

前兩行設定兩個變數，本冊之後一直會用到：`$root` 是根目錄，`$cfg` 是 N-11 要建立的 `.env` 的位置。本冊之後的 `docker compose` 指令都寫成 `--env-file $cfg`，而且都在 `$root\repo` 底下打。

**怎麼知道成功了**：列出 `backups`、`config` 兩個資料夾，最後一行印出 `D:\hd-tablet-care\config\.env`（🧪 是 `C:\hd-sim\config\.env`）。`repo` 現在還沒有是對的，下一步 clone 才會產生；`.env` 也還沒有，N-11 才會建立。

**不可以放的地方**：OneDrive 之類的雲端同步資料夾、網路磁碟機、RAM 磁碟、`C:\Users\<帳號>\` 底下的桌面／文件／下載。

> ⚠️ **開工三行**：PowerShell 關掉再開，`$root`、`$cfg` 就不見了。**之後每開一個新的 PowerShell 視窗，先打這三行**（第三行要等 N-10 clone 完才有那個資料夾）。看到 `couldn't find env file`，十次有九次是忘了打這三行。

```powershell
$root = "D:\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
$cfg  = "$root\config\.env"
cd $root\repo
```

---

### N-09 產生本系統 repo 的部署金鑰

對應：W-09

這把金鑰讓這台機器可以從 GitHub **讀**本系統的程式碼，別的什麼都不能做。

**做什麼**

1. 產生金鑰。三行照抄，不用改任何字：

   ```powershell
   New-Item -ItemType Directory -Force $HOME\.ssh
   ssh-keygen -t ed25519 -C "hd-tablet-care@$(hostname)" -f $HOME\.ssh\hd-tablet-care -N '""'
   Get-Content $HOME\.ssh\hd-tablet-care.pub
   ```

   第一行是先建好 `.ssh` 資料夾：沒用過 SSH 的新帳號沒有這個資料夾，`ssh-keygen` 不會自己建。資料夾已經在的話，這一行什麼都不會動。`$(hostname)` 會自動換成這台機器的名字（想先看是什麼，單獨打 `hostname`），只當註記用，讓管理者在 GitHub 上認得這把金鑰是哪台機器的。

2. 把印出來的那**一整行**（`ssh-ed25519 AAAA… hd-tablet-care@…`）交給 repo 管理者。管理者到 GitHub 的 `hd-tablet-care` repo → **Settings → Deploy keys → Add deploy key** 貼上，**不要勾 Allow write access**。
3. 開 SSH 的設定檔。兩行照抄：

   ```powershell
   if (-not (Test-Path $HOME\.ssh\config)) { New-Item -ItemType File $HOME\.ssh\config }
   notepad $HOME\.ssh\config
   ```

   第一行是先建好沒有副檔名的空檔：直接讓記事本建新檔，它會自作主張存成 `config.txt`，ssh 就讀不到。檔案已經在的話，這一行什麼都不會動，原本的內容不會被清掉。在檔案最後加上這一段，存檔關閉：

   ```
   Host github-hd-tablet-care
       HostName github.com
       User git
       IdentityFile ~/.ssh/hd-tablet-care
       IdentitiesOnly yes
   ```

**怎麼知道成功了**

```powershell
ssh -T github-hd-tablet-care
```

第一次會問 `Are you sure you want to continue connecting (yes/no)?`，核對顯示的指紋是 GitHub 公布的那一組再打 `yes`。最後看到 `Hi 94sh09sh19sh/hd-tablet-care! You've successfully authenticated, but GitHub does not provide shell access.`

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `Permission denied (publickey)` | 公鑰還沒登記，或登記到別的 repo 去了 |
| `ssh-keygen` 找不到 | Windows 的 OpenSSH Client 選用功能沒裝。🏥 問資訊室；🧪 到「設定 → 系統 → 選用功能」加裝 |
| `Saving key ... failed: No such file or directory`，接著 `Get-Content` 說 `.pub` 不存在 | 漏打了建立 `.ssh` 資料夾那一行。補打後重跑 `ssh-keygen` |
| 22 埠不通（N-06） | 設定檔那一段的 `HostName` 改成 `ssh.github.com`，並加一行 `Port 443` |
| `Could not resolve hostname github-hd-tablet-care:` 後面接一串亂碼（那是 big5 的「無法辨別這台主機。」） | ssh 沒讀到設定檔，幾乎都是記事本存成了 `config.txt`（漏打第 3 步第一行）。`Get-ChildItem $HOME\.ssh` 看得到 `config.txt` 就打 `Rename-Item $HOME\.ssh\config.txt config`，再重跑 `ssh -T` |

🧪 開發機上**另產生一把**，不要拿你平常推程式碼的那把 SSH 金鑰頂替——那樣走的就不是院內那條路。登記時標題寫「模擬部署（開發機）」，之後可以一直留著重複使用。開發機的 `$HOME\.ssh\config` 裡如果已經有別的段落，加在最後面即可，不要動原本的。

---

### N-10 clone 程式碼，切到 tag

對應：W-10

**做什麼**（`<tag>` 換成 N-03 確認過的那一個，例如 `v0.2.0`）

```powershell
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git $root\repo
cd $root\repo
git checkout <tag>
git describe --tags
```

**怎麼知道成功了**：最後一行印出的**正好是**那個 tag，後面沒有 `-3-g1a2b3c4` 這種尾巴。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| 一大段 `You are in 'detached HEAD' state…` | **正常**。部署本來就不在分支上 |
| `error: pathspec '<tag>' did not match` | tag 沒推上去，回 N-03 |
| `destination path … already exists` | 那個資料夾已經有東西。🏥 先弄清楚是誰放的，**不要直接刪**；🧪 上一輪沒撤除乾淨，照 N-31 撤除 |
| N-09 的 `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷，不是金鑰的問題。`Test-Path $root\repo` 是 `True` 就先刪掉這次 clone 殘留的資料夾，再重跑 clone；還是被切，就把 N-09 設定檔那一段的 `HostName` 改成 `ssh.github.com`、加一行 `Port 443`，重跑 `ssh -T` 再 clone（見[《從零部署本系統之一：容器路線的原冊》](ref-fresh-install-detail.md)） |

🧪 一定要從 GitHub **全新 clone** 到 `C:\hd-sim\repo`，不要複製你的工作目錄，也不要在工作目錄裡做。

---

## 4. 設定

### N-11 由範本填 `.env`

對應：W-11、Y-03

**做什麼**

```powershell
Copy-Item $root\repo\deploy\hospital.env.example $cfg
notepad $cfg
```

**逐項怎麼填，照[《之七》](visit-2-system-env.md)**：🏥 與 🧪 每一項分開寫。

外殼 App 那三項（`HD_SHELL_SRC_DIR`、`HD_SHELL_SIGNING`、`MDM_KIOSK_BASE_URL`）**現在就一起填好**，雖然外殼第 7 節才做——每一條 `docker compose` 指令都會檢查它們。

**怎麼知道成功了**

```powershell
docker compose --env-file $cfg config --quiet
```

**什麼都沒印出來**就是對的。

**可能怎麼壞**

| 症狀 | 處置 |
|---|---|
| `required variable HD_… is missing a value: 請設定 …` | 冒號後面寫的就是還缺什麼，補上 |
| `couldn't find env file` | `$cfg` 沒設（N-08 的開工三行），或路徑打錯 |

> ⚠️ **不要拿 repo 根目錄的 `.env.example` 來填。** 那一份是日常開發（`npm run dev`）用的，變數名稱不同。部署用的範本只有 `deploy\hospital.env.example` 這一份。

---

### N-12 建立兩個資料卷

對應：W-12

**只在第一次部署時做。**

**做什麼**

```powershell
docker volume create hd-tablet-care-data
docker volume create hd-tablet-care-keys
docker volume ls
```

**怎麼知道成功了**：清單裡看得到這兩個名字。

🧪 做之前先 `docker volume ls` 看一眼，**清單裡不該已經有 `hd-tablet-care-` 開頭的**。有的話是上一輪留下來的，照 N-31 撤除再回來，否則就不是「從零」。

---

上一份：[《第二次進院（1001）· 從零部署本系統之一：詳細版（讀之前、N-01～N-07）》](visit-2-system-detail.md)｜下一份：[《第二次進院（1001）· 從零部署本系統之三：詳細版（N-13～N-18）》](visit-2-system-detail-3.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
