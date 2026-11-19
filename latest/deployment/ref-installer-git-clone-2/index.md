# 安裝包路線之七：院方要求直接 git clone（G-09～G-14）

上層文件：[《安裝包路線（歷史）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)　接在[《安裝包路線之六：院方要求直接 git clone（G-01～G-08）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone/index.md)之後

> **狀態：歷史**（路線 0926 撤除），只當紀錄；出路二用到的 `npm run package:build`、`package:verify` 1117 時已不在 repo 裡。改寫來源見[之六](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone/index.md)開頭。編號：`G-xx`，沿用原編號。

## 摘要

- 出路二：書面例外、Node 與三個目錄、`npm ci`、`check:offline`、建置用 `.env` 只一行、建置並驗位址、五支盤點、建包驗收、關閉對外連線並確認、院方掃毒後接回 H-10（G-09～G-18）
- 第 4 節只有在 G-06 選了二時才做，等於把 P-02～P-09 搬到院內主機上重做一次，預留 60～120 分鐘
- G-09 取得書面例外；G-10 確認主機上的 Node.js，並分好三個目錄
- G-11 安裝相依套件；G-12 確認這份 `node_modules` 帶得走
- G-13 建置用的 `.env` 只填一行；G-14 建置並確認位址寫對了
- G-15～G-18（五支盤點、建包驗收、關閉對外連線、院方掃毒後接回 H-10）在[之八](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone-3/index.md)

______________________________________________________________________

## 4. 出路二：在主機上建置安裝包

**這一整節只有在 G-06 選了二時才做。** 它等於把 P-02～P-09（[《安裝包路線之一》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build/index.md)） 搬到院內主機上重做一次。 **預留 60～120 分鐘**，大部分花在 G-11 下載套件。

### G-09 取得書面例外

**做什麼**

請資訊室（或有權限核准的人）在紙上寫明並簽名：

| 事項                   | 內容                                                                                                                                                     |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 例外的條款             | DEP-11（在正式主機上建置）；以及今天這段對外連線                                                                                                         |
| 期間                   | 今天幾點到幾點                                                                                                                                           |
| 允許連線的來源         | G-05 第 3 題的白名單                                                                                                                                     |
| 關閉連線的人與確認方式 | G-05 第 4 題                                                                                                                                             |
| 以後的更新是否沿用     | 是／否（[第 5 節](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone-3/#5-%E4%B9%8B%E5%BE%8C%E7%9A%84%E6%9B%B4%E6%96%B0)） |

**怎麼知道成功了**

你手上有一張簽了名的紙。**口頭同意不算。**

**可能怎麼壞、怎麼處理**

| 症狀                             | 處置                                                                                                    |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 「不用那麼麻煩，我說可以就可以」 | 回出路一。這張紙保護的是對方：半年後有人問「為什麼這台主機上有 `npm install` 的痕跡」，答案就在這張紙上 |

> 回去之後，這次例外要寫進《[部署規範](https://94sh09sh19sh.github.io/hd-docs/latest/requirements/deployment-spec/index.md)》。 **手冊不能替規範開例外**，它只記錄現場發生了什麼。

______________________________________________________________________

### G-10 確認主機上的 Node.js，並分好三個目錄

**做什麼**

```
node -v
npm -v
```

然後決定三個目錄，**三個必須彼此分開**：

| 目錄                 | 放什麼                             | 建議                                                                                                             |
| -------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **建置目錄**         | clone 下來的原始碼、`node_modules` | 就是剛才 clone 的那個，路徑越短越好                                                                              |
| **安裝目錄的上一層** | 建出來的安裝包、`.env`             | 與 [H-09](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-3/index.md) 相同，例如 `C:\hd\` |
| **資料與備份目錄**   | 資料庫、備份                       | 與 [H-13](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-3/index.md) 相同，資訊室指定    |

**怎麼知道成功了**

`node -v` ≥ v20.11，三個目錄寫在筆記本上。

**可能怎麼壞、怎麼處理**

| 症狀                         | 處置                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **沒有 Node.js**             | 裝 Node.js 是另一件要走變更申請的事，而且要從 `nodejs.org` 下載（又一個要開的來源）。**多半今天做不完——回出路一** |
| 有 Node.js，但低於 v20.11    | 同上。**不要升級它**：那是別的專案裝的，升級可能弄壞人家                                                          |
| 有 Node.js 且版本夠          | 可以用，但要知道：**安裝包裡的 `runtime\node.exe` 就是從這一支複製的**。記下版本，它會寫進 `VERSION.json`         |
| 建置目錄在「文件」或桌面底下 | 搬到短路徑。兩萬多個檔案加上深層目錄，會撞到 Windows 的路徑長度限制                                               |

______________________________________________________________________

### G-11 安裝相依套件

**做什麼**（計時）

```
cd <建置目錄>
npm ci
```

**用 `npm ci` 不用 `npm install`**：前者只照 `package-lock.json` 裝，不會自行升級任何套件，裝出來的東西和開發機上驗收過的是同一份。

**怎麼知道成功了**

沒有 `ERR!`，最後一行是 `added <數字> packages`，而且 `node_modules\@prisma\engines\` 底下有引擎檔：

```
Get-ChildItem node_modules\@prisma\engines\ | Where-Object Name -Match "engine"
```

**可能怎麼壞、怎麼處理**

| 症狀                                                     | 原因                                                    | 處置                                                                                        |
| -------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `ECONNREFUSED`／`ETIMEDOUT`，網址是 `registry.npmjs.org` | 白名單沒有套件來源                                      | 抄下錯誤原文。請資訊室加，加不了就回出路一                                                  |
| `407 Proxy Authentication Required`                      | 代理要帳密                                              | **不要把任何人的帳密寫進 npm 設定。** 回出路一                                              |
| 裝完了，但 `engines` 底下沒有引擎檔                      | `binaries.prisma.sh` 不在白名單，安裝後腳本靜靜地失敗了 | G-12 一定會擋下來。請資訊室加白名單，然後 `Remove-Item -Recurse node_modules` 重跑 `npm ci` |
| `EPERM`／`EACCES`                                        | 防毒即時掃描、或還有 node 行程開著                      | 請資訊室暫時把**建置目錄**加進排除清單；不行就等掃描過去再重跑                              |
| 跑了 20 分鐘還沒完                                       | 代理限速                                                | 記下耗時。這是院方評估「以後更新方便」時該知道的數字                                        |

______________________________________________________________________

### G-12 確認這份 `node_modules` 帶得走

**做什麼**

```
npm run check:offline
```

**怎麼知道成功了**

六項全部通過，沒有「阻擋項」。這一步與 [P-03](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build/index.md) 相同。

**可能怎麼壞、怎麼處理**

見 [P-03](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build/index.md) 的表。最常見的是引擎沒下載到（G-11 第三列）。

______________________________________________________________________

### G-13 填建置用的 `.env`，只填一行

**做什麼**

```
Set-Content -Encoding utf8 -Path .\.env -Value "VITE_API_BASE_URL=http://<院內主機>:<API_PORT>"
```

**這個 `.env` 放在建置目錄**，只用來告訴建置兩個 PWA 該連哪個位址。它**不是**服務要讀的那一份——服務讀的在安裝目錄的上一層，接回 H-10（[《安裝包路線（歷史）》第 3 份](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-3/index.md)）時才建。

**怎麼知道成功了**

`Get-Content .\.env` 只有那一行，位址與 K-01（[《安裝包路線（歷史）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer/index.md)）決定的一致。

**可能怎麼壞、怎麼處理**

| 症狀                                  | 處置                                                                                                                                          |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 想把 `JWT_SECRET`、管理員密碼也寫進來 | **不要。** 建置不需要它們，而建置目錄是你離院時要刪掉或留給院方的東西                                                                         |
| 位址還沒決定                          | 回出路一。**這一行填錯，護理站就登不進去**（[X-19](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-troubleshooting-2/index.md)） |

> **這是出路二唯一比路線 B 好的地方**：位址是在現場、看著真正的主機填的，不會發生「開發機上建包時填錯位址，到院內才發現」的事。

______________________________________________________________________

### G-14 建置並確認位址寫對了

**做什麼**

```
npm run build
Select-String -Path apps\nurse-pwa\dist\assets\*.js -Pattern "<院內主機>" -List | Select-Object Filename
Select-String -Path apps\nurse-pwa\dist\assets\*.js -Pattern "localhost:3000" -List | Select-Object Filename
```

**怎麼知道成功了**

第一個 `Select-String` **找得到**，第二個**找不到**。`apps\patient-pwa\dist\` 底下有 `sw.js`。

**可能怎麼壞、怎麼處理**

| 症狀                        | 處置                                                                                                  |
| --------------------------- | ----------------------------------------------------------------------------------------------------- |
| 仍然找得到 `localhost:3000` | `.env` 不在建置目錄的最上層，或變數名稱打錯。改好再 `npm run build`                                   |
| TypeScript 錯誤             | 在開發機上建得起來、在這裡建不起來，多半是 Node 版本差太多。**不要現場改程式**，回出路一              |
| 其餘                        | 見 [P-04](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-build/index.md) 的表 |

______________________________________________________________________

上一份：[《安裝包路線之六：院方要求直接 git clone（G-01～G-08）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone/index.md)・下一份：[《安裝包路線之八：院方要求直接 git clone（G-15～G-18、第 5、6 節）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-installer-git-clone-3/index.md)・[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版 | 日期       | 異動                                                                                                     |
| ---- | ---------- | -------------------------------------------------------------------------------------------------------- |
| 1118 | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《安裝包路線之六：院方要求直接 git clone》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
