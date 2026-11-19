# 從零部署本系統（第 3 份，V-06～V-11）

上層文件：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》

> **狀態：現行（常備參考）。** 改寫自第十五冊（1117）；編號 `V-xx`（沿用第十五冊），每一步下面註明對應的 `N-xx` 與 `W-xx`／`Y-xx`／`Z-xx`。1118 照步驟順序拆成七份，這是第 3 份；🧪／🏥／📍 標記的意思見第 1 份 0.2 節。

## 摘要

- V-06 Windows 與 Docker 兩側都要連得出去；建置之前先 `docker pull` 兩個基底映像（1001 三次查不到 Docker Hub 的網域）
- V-07 三個埠 `13000`、`18080`、`18081` 沒人用；🏥 被佔用就停手回報資訊室
- V-08 填 `.env` 之前先定主機位址；1029 起一律用固定 IP，定了不要再換（平板的伺服器憑證簽這個名字）
- V-09 根目錄 🏥 `C:\hd\hd-tablet-care`、🧪 `C:\hd-sim`，設好「開工三行」
- V-10 產生本系統 repo 的部署金鑰與 SSH 設定檔；V-11 從 GitHub clone 並切到 tag

______________________________________________________________________

## 2. 主機這一層（續）

### V-06 確認連得出去，並先下載兩個基底映像

對應：N-06、W-06

建置時要從網路下載東西。先確認這些網站都連得到，免得建到一半才失敗。這一步分兩段：**Windows 連得到**，以及 **Docker 自己下載得到**。

**第一段：Windows 這一側**

```
Test-NetConnection github.com -Port 22
Test-NetConnection github.com -Port 443
Test-NetConnection registry-1.docker.io -Port 443
Test-NetConnection auth.docker.io -Port 443
Test-NetConnection production.cloudflare.docker.com -Port 443
Test-NetConnection production.cloudfront.docker.com -Port 443
Test-NetConnection deb.debian.org -Port 80
Test-NetConnection registry.npmjs.org -Port 443
Test-NetConnection binaries.prisma.sh -Port 443
Test-NetConnection dl.google.com -Port 443
Test-NetConnection services.gradle.org -Port 443
Test-NetConnection maven.google.com -Port 443
```

最後三條是外殼的建置（V-21）要用的。每個網域誰要用，見《[從零部署本系統之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》W-06。

**第二段：Docker 這一側**——把 V-14、V-21 要用的兩個基底映像先下載下來：

```
docker pull node:20-bookworm-slim
docker pull eclipse-temurin:17-jdk-jammy
```

`Test-NetConnection` 是 Windows 去查名稱、去連線；`docker pull` 是 **Docker Desktop 自己**去查、去下載，兩條路不一定同時通。 1001 就是 Windows 那一側沒測、Docker 那一側在 N-11 與 N-20 **三次查不到 Docker Hub 的網域**。這兩條先跑過，之後的建置不會半途卡在這裡，而且已下載的映像檔會直接沿用、建置也比較快。

**怎麼知道成功了**：第一段每一條最後都是 `TcpTestSucceeded : True`；第二段兩條最後都是 `Status: Downloaded newer image for …` 或 `Status: Image is up to date for …`。

**可能怎麼壞**

| 症狀                                                                                                         | 處置                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 22 是 `False`、443 是 `True`                                                                                 | 之後的部署金鑰改走 443，做法在 V-10 的出錯表                                                                                                                                                                                                                                                                         |
| 第一段出現 `Name resolution of … failed`（名稱查不到），其他都通                                             | 院內 DNS 查不到那個網域。試 `Resolve-DnsName <網域> -Server 8.8.8.8`，這樣查得到就是院內 DNS 的問題，請資訊室處理                                                                                                                                                                                                    |
| 第二段出現 `lookup <網域>: no such host`（網域是 `production.cloudfront.docker.com`、`auth.docker.io` 之類） | Docker 查不到 Docker Hub 的網域。依序：① 再打一次同一條；② `Resolve-DnsName <網域>`，Windows 查得到就重新啟動 Docker Desktop（工作列圖示按右鍵 → Restart）再打；③ Windows 也查不到，試 `Resolve-DnsName <網域> -Server 8.8.8.8`，這樣查得到就是院內 DNS 解析不了，請資訊室處理。**用了哪一個辦法才過，寫進演練紀錄** |
| 第二段的錯誤裡有一句 `Docker Desktop has no HTTPS proxy: connecting to … via direct connection`              | 這一句只是說明「沒有設代理、直接連」，**不是錯誤本身**；錯誤在同一段最後的 `no such host`                                                                                                                                                                                                                            |
| 經代理伺服器，全部 `False`                                                                                   | 改用 `curl.exe -I https://registry.npmjs.org` 測；Docker 要在 Settings → Resources → Proxies 設代理                                                                                                                                                                                                                  |
| 有幾個不通                                                                                                   | 請資訊室補齊再往下                                                                                                                                                                                                                                                                                                   |

> 📍 **1001**：第一段沒有記到結果；第二段當時還不是步驟。結果 Docker 在三個地方查不到名稱： N-11 用 `docker run node:20-bookworm-slim` 產生 `JWT_SECRET` 時，先是 `production.cloudfront.docker.com: no such host`、再打一次變成 `auth.docker.io: no such host`； N-20 建 `shell-builder` 時又是 `production.cloudfront.docker.com: no such host`，同一條指令再打一次就過了。所以是**時好時壞**，不是完全擋掉——上表的第 ① 項（再打一次）先做。 Docker Hub 的兩個下載站（`cloudflare`、`cloudfront`）會擇一使用，**兩個都要通**。
>
> 🧪 **模擬部署**：開發機通常全部通，照做一次確認即可。

______________________________________________________________________

### V-07 確認三個連接埠沒人用

對應：N-07、W-07

**做什麼**

```
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 13000,18080,18081 | Select-Object LocalPort, OwningProcess
```

**怎麼知道成功了**：**什麼都沒印出來**，代表三個埠都沒人在用。

**可能怎麼壞**：印出了某個埠 → 有別的程式在用它。🏥 實際部署：**先停手回報資訊室**，這三個埠是他們確認過的，不要自己換；🧪 模擬部署：自己換一個沒人用的。 **不要用 `-p` 之類的方式把埠對到別處**，埠只寫在 `.env` 裡。

> 📍 **1001**：三個埠都沒人用，服務啟動沒有撞埠。**院內主機上本系統的服務還在跑的話，這三個埠會印出來，那是我們自己的。** 1029 也確認與同機另一個專案沒有衝突。
>
> 🧪 **模擬部署**：三個埠記下來，V-12 填 `.env` 時要用。

______________________________________________________________________

## 3. 決定主機位址

### V-08 決定主機位址：護理站與平板用什麼連這台主機

對應：第十四冊沒有這一步（1007 新增），W-03 的位址一題

`.env` 有三項要寫主機位址（`HD_PUBLIC_API_URL`、`CORS_ORIGINS`、`MDM_KIOSK_BASE_URL`），三項**寫同一個值**。這個值這一份與 `.env` 的兩份一律寫成 `<主機>`。**它要在填 `.env` 之前定下來**，而且定了之後不要再換：平板的伺服器憑證就簽這個名字。

> ⚠️ **第十四冊之一的範例 `hd-server` 只是範例，不是要你填的值。** 1001 現場就問過「`hd-server` 要照寫嗎」。不要照抄任何範例（`deploy\hospital.env.example` 的註解裡到 `v0.5.0` 都還寫著 `hd-server`）。
>
> **1029 起的結論：主機位址一律用固定 IP。** 名稱在院內不一定查得到（1001 用名稱登不進去，1029 換成 IP 之後護理站直接登得進去，《[第三次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-3-1029/index.md)》）。下面的「名稱」只在資訊室明確保證護理站與平板都查得到時才考慮。

**做什麼**

1. 在主機上看有哪些可以選：

```
hostname
ipconfig /all
```

| 看什麼                                                              | 怎麼判斷                                                                                                                                                                            |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hostname`                                                          | 這台的電腦名稱。**只有院內 DNS 登記過這個名稱，別台機器才查得到**                                                                                                                   |
| `ipconfig /all` 實體網卡（「乙太網路」或「Wi-Fi」）的 **IPv4 位址** | 候選的 IP。`vEthernet (WSL)`、`vEthernet (Default Switch)` 或 `172.` 開頭的是虛擬網卡，**不要選**                                                                                   |
| 同一段的「DHCP 已啟用」                                             | `是` 表示這個 IP 可能會變。要用 IP，就要請資訊室把它固定下來。**1007 答覆院內主機的 IP 是固定的**（1029 看到 DHCP 否）；資訊室若是用 DHCP 保留固定的，這裡照樣顯示 `是`，不代表會變 |
| 「主要 DNS 尾碼」                                                   | 有的話，名稱有兩種寫法（例如 `<名稱>` 與 `<名稱>.<尾碼>`）。**只能選一種**，`CORS_ORIGINS` 要和護理站網址列上的寫法一字不差                                                         |

1. **到護理站的電腦**上確認查得到（用名稱的話）：

```
Resolve-DnsName <名稱>
```

查得到、而且對到主機那個 IP 才算。用 IP 的話跳過這一條。

1. 與資訊室確認：**平板的 Wi-Fi 網段也連得到同一個名稱或 IP**。平板常常查不到 Windows 的電腦名稱（院內 DNS 沒登記的話），**拿不準就用資訊室固定下來的 IP**。

**怎麼知道成功了**：一個值，資訊室點過頭；護理站查得到（用名稱時）。演練紀錄寫「`<主機>` 用的是**名稱／IP**，由＿＿確認」——**值本身不寫進演練紀錄以外的任何文件**（院內的值只進私人 repo 的 `deploy/records/`）。

**真正的驗證在後面**：V-17 在護理站登入成功、V-25 平板開得到下載頁，這個值才算對。

**可能怎麼壞**

| 症狀                                                  | 處置                                                   |
| ----------------------------------------------------- | ------------------------------------------------------ |
| 護理站 `Resolve-DnsName` 說 `DNS name does not exist` | 這個名稱院內查不到。改用固定 IP，或請資訊室在 DNS 登記 |
| 資訊室說 IP 不能固定                                  | 用名稱，並請資訊室確認平板的網段查得到它               |
| 名稱與 IP 都不確定                                    | **停在這一步**。這個值填錯，之後每一台平板都要重新佈建 |

> 📍 **1001**：現場打了 `hostname`，自己決定了一個值，沒有資訊室的書面答案。當天沒有記是名稱還是 IP，1005 補記：**是名稱**（有沒有帶 DNS 尾碼未記）。1029 照《[護理站登不進去與主機位址之一：換主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login-switch-ip/index.md)》換成 IP。

已經部署好之後才要從名稱換成 IP（或換 IP），照《[護理站登不進去與主機位址之一：換主機位址](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-login-switch-ip/index.md)》的 T-xx。

> 🧪 **模擬部署**：`<主機>` 是開發機 **Wi-Fi 那張網卡的 IPv4 位址**（《[`.env` 怎麼填之一：開發機演練](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-env-simulation/index.md)》0.3 節），例如 `192.0.2.23`。手機要連同一個 Wi-Fi；同一輪模擬部署之內不要換 Wi-Fi。

______________________________________________________________________

## 4. 取得程式碼

### V-09 建立資料夾，並設好「開工三行」

對應：N-08、W-08

**做什麼**

```
$root = "C:\hd\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
$cfg  = "$root\config\.env"
New-Item -ItemType Directory -Force "$root\config", "$root\backups" | Out-Null
Get-ChildItem $root
$cfg
```

前兩行設定兩個變數，之後一直會用到：`$root` 是根目錄，`$cfg` 是 V-12 要建立的 `.env` 的位置。之後的 `docker compose` 指令都寫成 `--env-file $cfg`，而且都在 `$root\repo` 底下打。

**怎麼知道成功了**：列出 `backups`、`config` 兩個資料夾，最後一行印出 `C:\hd\hd-tablet-care\config\.env`（🧪 模擬部署是 `C:\hd-sim\config\.env`）。 `repo` 現在還沒有是對的，下一步 clone 才會產生；`.env` 也還沒有，V-12 才會建立；`export` 不必先建，第一次取出資料時自動建立。

**不可以放的地方**：OneDrive 之類的雲端同步資料夾、網路磁碟機、RAM 磁碟（院內主機有一顆 E 槽是 RAM 磁碟，《[第一次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-1-0922/index.md)》3.2 節）、 `C:\Users\<帳號>\` 底下的桌面／文件／下載。

> 📍 **1001**：根目錄是 `C:\hd\hd-tablet-care`。第十四冊寫的是 `D:\hd-tablet-care`，但院內主機的 D 槽 0922 時只剩約 4.6%（《[第一次進院紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/record-1-0922/index.md)》3.2 節）， C 槽空間充足、Docker 的虛擬磁碟也在 C 槽。**院方同不同意這個位置還沒有書面答覆**（V-02 第 5 題；1029 仍沒問到）。
>
> ⚠️ **開工三行**：PowerShell 關掉再開，`$root`、`$cfg` 就不見了。**之後每開一個新的 PowerShell 視窗，先輸入下面這三行**（第三行要等 V-11 clone 完才有那個資料夾）。看到 `couldn't find env file`，十次有九次是忘了這三行。

```
$root = "C:\hd\hd-tablet-care"          # 🧪 模擬部署改成 C:\hd-sim
$cfg  = "$root\config\.env"
cd $root\repo
```

______________________________________________________________________

### V-10 產生本系統 repo 的部署金鑰

對應：N-09、W-09

這把金鑰讓這台機器可以從 GitHub **讀**本系統的程式碼，別的什麼都不能做。

**做什麼**

1. 產生金鑰。三行照抄，不用改任何字：

```
New-Item -ItemType Directory -Force $HOME\.ssh
ssh-keygen -t ed25519 -C "hd-tablet-care@$(hostname)" -f $HOME\.ssh\hd-tablet-care -N '""'
Get-Content $HOME\.ssh\hd-tablet-care.pub
```

第一行是先建好 `.ssh` 資料夾：沒用過 SSH 的新帳號沒有這個資料夾，`ssh-keygen` 不會自己建。資料夾已經在的話，這一行什麼都不會動。 `$(hostname)` 會自動換成這台機器的名字，只當註記用，讓管理者在 GitHub 上認得這把金鑰是哪台機器的。

1. 把印出來的那**一整行**（`ssh-ed25519 AAAA… hd-tablet-care@…`）交給 repo 管理者。管理者到 GitHub 的 `hd-tablet-care` repo → **Settings → Deploy keys → Add deploy key** 貼上，**不要勾 Allow write access**。
1. 開 SSH 的設定檔。兩行照抄：

```
if (-not (Test-Path $HOME\.ssh\config)) { New-Item -ItemType File $HOME\.ssh\config }
notepad $HOME\.ssh\config
```

第一行是先建好沒有副檔名的空檔：直接讓記事本建新檔，它會自作主張存成 `config.txt`，ssh 就讀不到。在檔案最後加上這一段，存檔關閉：

```
Host github-hd-tablet-care
    HostName github.com
    User git
    IdentityFile ~/.ssh/hd-tablet-care
    IdentitiesOnly yes
```

**怎麼知道成功了**

```
ssh -T github-hd-tablet-care
```

第一次會問 `Are you sure you want to continue connecting (yes/no)?`，核對顯示的指紋是 GitHub 公布的那一組再打 `yes`。最後看到 `Hi 94sh09sh19sh/hd-tablet-care! You've successfully authenticated, but GitHub does not provide shell access.`

**可能怎麼壞**

| 症狀                                                                                                     | 處置                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Permission denied (publickey)`                                                                          | 公鑰還沒登記，或登記到別的 repo 去了                                                                                                                                 |
| `ssh-keygen` 找不到                                                                                      | Windows 的 OpenSSH Client 選用功能沒裝。🏥 問資訊室；🧪 到「設定 → 系統 → 選用功能」加裝                                                                             |
| `Saving key ... failed: No such file or directory`，接著 `Get-Content` 說 `.pub` 不存在                  | 漏打了建立 `.ssh` 資料夾那一行。補打後重跑 `ssh-keygen`                                                                                                              |
| 22 埠不通（V-06）                                                                                        | 設定檔那一段的 `HostName` 改成 `ssh.github.com`，並加一行 `Port 443`                                                                                                 |
| `Could not resolve hostname github-hd-tablet-care:` 後面接一串亂碼（那是 big5 的「無法辨別這台主機。」） | ssh 沒讀到設定檔，幾乎都是記事本存成了 `config.txt`。`Get-ChildItem $HOME\.ssh` 看得到 `config.txt` 就打 `Rename-Item $HOME\.ssh\config.txt config`，再重跑 `ssh -T` |

> 🧪 **模擬部署**：開發機上**另產生一把**，不要拿你平常推程式碼的那把 SSH 金鑰頂替——那樣走的就不是院內那條路。登記時標題寫「模擬部署（開發機）」，之後可以一直留著重複使用。開發機的 `$HOME\.ssh\config` 裡已經有別的段落的話，加在最後面即可。

______________________________________________________________________

### V-11 clone 程式碼，切到 tag

對應：N-10、W-10

**做什麼**（`<tag>` 換成 V-03 確認過的那一個，現在是 `v0.5.0`）

```
git clone git@github-hd-tablet-care:94sh09sh19sh/hd-tablet-care.git $root\repo
cd $root\repo
git checkout <tag>
git describe --tags
```

**怎麼知道成功了**：最後一行印出的**正好是**那個 tag，後面沒有 `-3-g1a2b3c4` 這種尾巴。

**可能怎麼壞**

| 症狀                                                                      | 處置                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 一大段 `You are in 'detached HEAD' state…`                                | **正常**。部署本來就不在分支上                                                                                                                                                                                                                                                                           |
| `error: pathspec '<tag>' did not match`                                   | tag 沒推上去，回 V-03                                                                                                                                                                                                                                                                                    |
| `destination path … already exists`                                       | 那個資料夾已經有東西。🏥 **院內主機上這是 1001 clone 的那一份**，回 0.5 節，不要刪；🧪 上一輪沒撤除乾淨，照第 10.2 節撤除                                                                                                                                                                                |
| V-10 的 `ssh -T` 成功，`git clone` 卻出現 `Connection reset by … port 22` | 網路把連線切斷，不是金鑰的問題。`Test-Path $root\repo` 是 `True` 就先刪掉這次 clone 殘留的資料夾，再重跑；還是被切，就把 V-10 設定檔那一段改走 443，重跑 `ssh -T` 再 clone（見《[從零部署本系統之一](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-detail/index.md)》W-06） |

> 📍 **1001**：`HEAD is now at 9992721 docs: 週報 0930 定版`，`git describe --tags` 印出 `v0.3.0`。
>
> 🧪 **模擬部署**：一定要從 GitHub **全新 clone** 到 `C:\hd-sim\repo`，不要複製你的工作目錄，也不要在工作目錄裡做。

______________________________________________________________________

上一份：《[從零部署本系統（第 2 份，V-01～V-05）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-2/index.md)》｜下一份：《[從零部署本系統（第 4 份，V-12～V-17）](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-4/index.md)》｜第一份（索引）：《[從零部署本系統](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install/index.md)》｜[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版 | 日期       | 異動                                                                             |
| ---- | ---------- | -------------------------------------------------------------------------------- |
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《從零部署本系統》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
