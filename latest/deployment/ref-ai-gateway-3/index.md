# AI 閘道（第 3 份，Z-11～Z-24）

上層文件：[《AI 閘道》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway/index.md)

> **狀態：現行**（常備參考）。改寫來源見[第 1 份](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway/index.md)開頭。編號：`Z-xx`，沿用原編號。
>
> ⚠️ **實驗室的位址、SSH 埠、帳號與密碼，一律不寫進 repo、不寫進這本手冊、不寫進週報**（DEP-42）。本份用 `<角括號>` 標出要換成實際值的地方；實際值只存在你自己電腦上、專案目錄以外的那一份筆記（Z-01）。文件站是公開的。

## 摘要

- 實測（第 3 節）：Z-11 端對端驗收與繁中品質紀錄、Z-12 換模型換方法、Z-13 用畫面看一次（選做）
- 收尾（第 4 節）：Z-14 實驗室上不留東西、Z-15 repo 裡沒有實驗室的連線資訊
- 院內：放 `config.yaml`、建置啟動、之後每次 `up` 帶 `--profile ai`、Q-07 有答案才接正式 GPU API、把 AI 整個關掉（Z-20～Z-24）
- 換模型、換端點只改 `config.yaml`（存檔即生效）與 `.env` 的 `LLM_PROVIDER`，不改程式、不重建後端（FR-S13、DEP-17）
- 閘道停掉時主線照常（DEP-24）
- AI 閘道特有的疑難排解在第 6 節；Z-01～Z-10 在[第 1 份](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway/index.md)與[第 2 份](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway-2/index.md)

______________________________________________________________________

## 3. 實測

### Z-11 端對端驗收與品質紀錄（開發機）

```
cd <專案目錄>
npm run verify:iteration13:api -- --gateway http://127.0.0.1:18000/v1 --report $HOME\hd-lab\ai-lab-trial-<日期>.md
```

腳本自己建一個暫存資料庫、另起一個 `LLM_PROVIDER=lab` 的後端（不碰開發用的資料庫），依序驗： AI 總開關開得起來（健康檢查經閘道通過）、合成病人的衛教產生成功且 `ai_invocations` 記下實驗室上的實際模型、「看似真實」的病人被擋下且完全沒有送出；再把四項 AI 功能各跑一次，輸出與耗時寫進報告。

**第一次會很慢**：模型要載入，可能一兩分鐘（規範第 7 項），腳本的逾時已放寬到五分鐘以上。

**怎麼知道成功了**：結尾 `全部通過`（驗收 3、4、5 那幾行是 `·`，表示在別處驗）；報告檔裡四項都有輸出。

報告要人讀：每一項的「品質」欄照這四點判讀後填——**繁體中文是否通順、有沒有簡體字或中國大陸用語、有沒有捏造提示裡沒有的事、格式是否照提示**。結論與耗時抄進《[部署演練紀錄](https://94sh09sh19sh.github.io/hd-docs/latest/notes/deployment-drills/index.md)》10.4；**報告檔本身留在專案目錄外**。

| 症狀                        | 處置                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| `AI 總開關` 那一步 HTTP 409 | 健康檢查沒過。`curl.exe http://127.0.0.1:18000/health` 看是閘道、`config.yaml` 還是轉送的問題 |
| 背景工作 `推論伺服器逾時`   | 第一次載入太久，或別人在用大型模型。等幾分鐘重跑；一直如此就換小一點的模型（Z-12）            |
| 輸出夾雜簡體字              | 照實記錄，這正是要蒐集的結果。可換模型比較                                                    |

______________________________________________________________________

### Z-12 換模型、換方法（驗收 3、4）

**換模型**——實驗室改 `config.yaml` 的 `model` 為 Z-04 挑的備用模型，存檔。開發機：

```
npm run verify:iteration13:api -- --gateway http://127.0.0.1:18000/v1 --expect-model <備用模型>
```

**換方法**——`config.yaml` 改成方法二（langchain-openai，OpenAI 相容介面）：

```
provider: openai
base_url: http://host.docker.internal:11434/v1     # 結尾多一段 /v1
```

存檔，再跑一次（不帶 `--expect-model` 也可以）。

**怎麼知道成功了**：兩次都 `全部通過`；第一次的「呼叫紀錄的模型」是備用模型。**全程沒有重建映像檔、沒有重新啟動閘道、後端每次都是腳本新起的同一份程式**——換的只有 `config.yaml`。

______________________________________________________________________

### Z-13 用畫面看一次（開發機，選做）

開發機的 `.env`：

```
LLM_PROVIDER=lab
LLM_ENDPOINT=http://127.0.0.1:18000/v1
LLM_MODEL_ID=
LLM_TIMEOUT_SECONDS=300
```

`npm run dev`，護理端「系統管理」：供應者「實驗室 API」、資料離開院內標成「院外：僅得送合成資料」、模型識別字是 `config.yaml` 那一個、健康檢查通過。開 AI 總開關，替一位病歷號 `HD-TEST-` 開頭的病人產生衛教。**看完把 `.env` 改回 `LLM_PROVIDER=mock`。**

______________________________________________________________________

## 4. 收尾（驗收 6、7）

### Z-14 實驗室上不留東西

測試期間閘道可以留著。**確定不用了**：

```
docker rm -f <個人前綴>-hd-ai-gateway
docker rmi <個人前綴>-hd-ai-gateway:i13
docker ps -a --format '{{.Names}}' | grep <個人前綴>     # 沒有輸出
docker images | grep <個人前綴>                           # 沒有輸出
ls -la ~                                                  # 沒有本專案的檔案
```

個人資料夾留不留照實驗室的規矩；`config.yaml` 裡只有實驗室自己的位址與模型名稱。

**怎麼知道成功了**：本專案的東西只剩個人資料夾底下那一份（或整個刪掉）。這是驗收 7，結果寫進[迭代 13 分冊](https://94sh09sh19sh.github.io/hd-docs/latest/testing/iteration-13/index.md) §13.6。

開發機：關掉 Z-10 的轉送視窗，`.env` 改回 `mock`。

______________________________________________________________________

### Z-15 repo 裡沒有實驗室的連線資訊（開發機）

```
npm run verify:iteration13 -- --secrets $HOME\hd-lab\lab.env
```

腳本逐字比對 `lab.env` 裡每一個值：工作目錄的每個檔案、git 歷史的每一次改動、每一則提交訊息。**值不會印出來**。要連密碼一起驗，暫時在 `lab.env` 加一行 `LAB_PASSWORD=…`，跑完刪掉。

**怎麼知道成功了**：每一個名稱都是 `✓ …檔案、歷史、提交訊息都找不到`。

| 症狀                 | 處置                                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------ |
| 某個值出現在某個檔案 | 改掉，**再確認它沒被提交過**。已經提交或推上 GitHub 的，要當成外洩處理：換密碼、請學長姐評估要不要換位址或埠 |

______________________________________________________________________

## 5. 院內主機

首波 AI 功能預設關閉（DEP-29），閘道可以根本不起。Z-20～Z-22 在本系統起來之後做一次，讓閘道就位、確認它明確回報「設定尚未填好」（🏥 院內 1001／1029 已做過，第 0.2 節）；Z-23 等 Q-07（正式 GPU API）有答案才做。這一段與[《從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-6/index.md) V-29、V-30 是同一件事。

指令都在主機的 PowerShell、`$root\repo` 底下下，每個新視窗先輸入這三行：

```
$root = "C:\hd\hd-tablet-care"          # 🧪 開發機演練改成 C:\hd-sim
$cfg  = "$root\config\.env"
cd $root\repo
```

（0927 原文寫的是 `D:\hd-tablet-care`；1001 起院內主機的根目錄是 `C:\hd\hd-tablet-care`。）

### Z-20 放院內那一份 `config.yaml`

先看有沒有：`Test-Path $root\config\ai-gateway\config.yaml` 是 `True` 就是做過了（🏥 院內主機已經有），**不要再複製一次蓋掉它**。沒有才做：

```
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
```

範本的 `provider` 預設 `openai`（正式 GPU API 多半提供 OpenAI 相容介面；若是 Ollama 改 `ollama`），`base_url` 與 `model` 刻意留空：留空時閘道照樣啟動，但每個請求都回「閘道設定有誤」，後端的健康檢查不通過，AI 總開關就開不起來——不會半套設定就開始跑。**不要填實驗室的位址**——院內主機連得出去，填了就是把資料往院外送。`base_url` 只准是院內位址（FR-S07；`check:egress` 會掃範本）。

compose 把設定目錄（`HD_CONFIG_DIR`）唯讀掛進閘道的 `/config`，閘道讀 `/config/ai-gateway/config.yaml`。

### Z-21 建置與啟動閘道

```
docker compose --env-file $cfg --profile ai build ai-gateway
docker compose --env-file $cfg --profile ai up -d ai-gateway
docker compose --env-file $cfg exec -T api node -e "fetch('http://ai-gateway:8000/health').then(async r=>console.log(r.status, await r.text()))"
```

**怎麼知道成功了**：建置最後印出 `全部通過`；最後一條印出

```
503 {"status":"error","config":"error","detail":"base_url 尚未填寫（推論端點的位址）"}
```

**這就是正確的狀態**：閘道在、`api` 經私有網路連得到它、它清楚說出還缺什麼。

> 📍 **1029 院內**：J-20 沿用 1001 的設定檔，最後一條印出 503 `base_url 尚未填寫`；建置 29.2 秒（主機上留有 1001 建置的快取）。

| 症狀                                                       | 處置                                                                                                                                                        |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fetch failed`                                             | 閘道沒起來。`docker compose --env-file $cfg --profile ai logs ai-gateway`                                                                                   |
| `找不到設定檔`                                             | Z-20 的路徑不對：必須是設定目錄底下的 `ai-gateway\config.yaml`                                                                                              |
| `docker compose ps` 看到 `ai-gateway` 有 `0.0.0.0:…->8000` | 有人在 compose 加了 `ports`。拿掉——閘道不對外（部署規範 5.3），`npm run check:container` 會擋                                                               |
| 建置時 `no such host`                                      | 查不到 Docker Hub 或套件來源（DNS），處置同[《從零部署本系統》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-fresh-install-3/index.md) V-06 |

### Z-22 之後每一次 `up` 都帶 `--profile ai`

閘道起過之後，換版時（[《本系統換版與退回》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-upgrade/index.md)）`build` 與 `up -d` 都要加 `--profile ai`，閘道才會跟著換成新版映像檔。沒帶的話，閘道停在舊版，但**主線不受影響**（DEP-24）。

> 📍 **1116 院內**：換到 `v0.5.0` 時刻意沒帶（兩版之間閘道沒改、AI 關著），閘道仍是 `v0.4.0`，正常。之後哪一版的閘道有改，換版那一步就要帶。

### Z-23 接上正式 GPU API（Q-07 有答案之後）

1. `$root\config\ai-gateway\config.yaml`：填 `provider`、`base_url`、`model`（要金鑰時填 `api_key`；這個檔在主機的設定目錄，不在 repo，DEP-13）。院內範本的 `timeout_seconds: 120`、`health_timeout_seconds: 3`。存檔即生效，閘道不必重新啟動。
1. 確認：Z-21 的最後一行改成 `200 {"status":"ok",…}`。
1. `$cfg` 的 AI 那一段（`LLM_MODEL_ID` 接閘道時**留空**：模型只由 `config.yaml` 決定；`LLM_TIMEOUT_SECONDS` 要比 `timeout_seconds` 大）：

```
LLM_PROVIDER=onprem
LLM_ENDPOINT=http://ai-gateway:8000/v1
LLM_MODEL_ID=
LLM_TIMEOUT_SECONDS=150
```

1. `docker compose --env-file $cfg up -d api`（只換環境變數，**不重建映像檔**）。
1. 護理端「系統管理」：供應者「院內地端推論」、健康檢查通過，才照 DEP-29 的條件開 AI 總開關。「允許真實病人資料」是另一個開關，另有條件，**不在這一步開**。

**這就是 FR-S13 的驗收**：由實驗室換成正式 GPU API，改的只有 `config.yaml` 與 `.env` 的 `LLM_PROVIDER`，程式一行未動。

### Z-24 把 AI 整個關掉

護理端關 AI 總開關，然後：

```
docker compose --env-file $cfg --profile ai stop ai-gateway
```

主線完全不受影響（DEP-24，本機實測過，見《部署演練紀錄》第 10 節）。

______________________________________________________________________

## 6. 疑難排解（AI 閘道特有的）

| 症狀                                                      | 原因                                                                           | 處置                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| 護理端「健康檢查」寫 `無法連線至推論伺服器`               | 後端連不到**閘道**（開發機：轉送斷了；院內：閘道沒起）                         | 開發機重開 Z-10；院內 Z-21                                           |
| 健康檢查寫 `推論伺服器回應 HTTP 503`                      | 閘道在，但它後面不通或設定有誤                                                 | 開 `<閘道>/health` 看 `detail`                                       |
| 健康檢查寫 `端點上找不到設定的模型`                       | 後端的 `LLM_MODEL_ID` 填了東西，與 `config.yaml` 不同                          | `LLM_MODEL_ID` 留空                                                  |
| 換了 `config.yaml`，呼叫紀錄的模型沒變                    | 改到另一份檔案（實驗室：不是掛進容器的那個資料夾；院內：不是設定目錄底下那份） | `docker inspect <容器> --format '{{json .Mounts}}'` 看實際掛的是哪裡 |
| 院內後端起不來：`正式環境設定下不得使用 LLM_PROVIDER=lab` | 有人把開發機的設定抄過來了                                                     | 這是 DEP-40 在擋。改成 `onprem` 或 `mock`                            |
| 輸出前面有一段思考過程                                    | 模型把思考放在 `<think>` 以外的格式                                            | `config.yaml` 加 `reasoning: false`（方法一），或換模型              |

現場其他症狀見[《現場疑難排解》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-troubleshooting/index.md)。

______________________________________________________________________

上一份：[《AI 閘道（第 2 份，Z-03～Z-10）》](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/ref-ai-gateway-2/index.md)・[部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
| ---- | ---- | ---- |
|      |      |      |

[← 回部署手冊目錄](https://94sh09sh19sh.github.io/hd-docs/latest/deployment/index.md)
