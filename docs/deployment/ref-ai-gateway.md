# AI 閘道

> **狀態：現行**（常備參考）。
>
> 1117 從舊的《AI 閘道：實驗室實測與院內設定》全部改寫，並以 `services/ai-gateway/`（`config.example.yaml`、`config.hospital.example.yaml`、`gateway/`、`Dockerfile`）與 `docker-compose.yml` 的 `ai-gateway` 服務核對。
>
> 編號：`Z-xx`，沿用原編號（Z-01～Z-15 實驗室、Z-20～Z-24 院內）。

## 摘要

- 院內現況（1116）：閘道在院內主機上就位、**AI 關著**；`config.yaml` 的 `base_url`、`model` 刻意空白，健康檢查回 503「base_url 尚未填寫」是正確狀態；閘道映像檔是 `v0.4.0`（1029 建的），本系統換到 `v0.5.0` 時沒建它（第 0.2 節）
- 兩半：第 1～4 節是**過渡期**，在實驗室的 GPU 伺服器上起閘道、開發機經 SSH 接過去，以真的模型跑一次（只准合成資料），**還沒實測**（校外連不到，Q-08）；第 5 節是**院內**的 `ai-gateway` 服務
- 實驗室的位址、SSH 埠、帳號與密碼一律不寫進 repo、手冊與週報（DEP-42），只存在專案目錄外的一份筆記（Z-01）
- 實驗室：個人資料夾、`ollama list`（容器外）、建映像檔或替代做法、個人容器只綁 `127.0.0.1`、容器內 `curl` 找 Ollama、填 `config.yaml`、SSH 本機轉送、端對端驗收與繁中品質紀錄、換模型換方法、收尾（Z-01～Z-15）
- 院內：放 `config.yaml`、建置啟動、之後每次 `up` 帶 `--profile ai`、Q-07 有答案才接正式 GPU API、把 AI 整個關掉（Z-20～Z-24）
- 換模型、換端點只改 `config.yaml`（存檔即生效）與 `.env` 的 `LLM_PROVIDER`，不改程式、不重建後端（FR-S13、DEP-17）
- 閘道停掉時主線照常（DEP-24）

規則的真本是《[部署規範](../requirements/deployment-spec.md)》第 5 章（DEP-16、DEP-17、DEP-40～DEP-42）；閘道本身的說明在 repo 的 `services/ai-gateway/README.md`。這一份只寫手指要按什麼、每一步會怎麼壞。

> ⚠️ **實驗室的位址、SSH 埠、帳號與密碼，一律不寫進 repo、不寫進這本手冊、不寫進週報**（DEP-42）。本份用 `<角括號>` 標出要換成實際值的地方；實際值只存在你自己電腦上、專案目錄以外的那一份筆記（Z-01）。文件站是公開的。

---

## 0. 讀之前

### 0.1 這一份做什麼（實驗室那一半）

```
開發機                                         實驗室 GPU 伺服器
┌──────────────────────┐   SSH 本機轉送   ┌───────────────────────────────────────┐
│ 後端  LLM_PROVIDER=lab │ ───────────────▶ │ 個人容器：AI 閘道（只綁本機介面）       │
│ LLM_ENDPOINT=          │  127.0.0.1:18000 │   config.yaml 在個人資料夾             │
│  http://127.0.0.1:18000/v1                │         │ LangChain                   │
└──────────────────────┘                  │         ▼                             │
                                          │ Ollama（別人維護，只能呼叫、不能管理） │
                                          └───────────────────────────────────────┘
```

| 步驟 | 在哪裡做 | 產生什麼 |
|---|---|---|
| 記下連線資訊 | 開發機，專案目錄外 | 一份只有你看得到的筆記；也是驗收 6 的比對來源 |
| 個人資料夾、查可用模型 | 實驗室，**容器外** | `<指定路徑>/<個人資料夾>/hd-ai-gateway/`；選定的模型名稱 |
| 建映像檔、起個人容器 | 實驗室，個人資料夾裡 | 閘道容器，只綁實驗室伺服器的 `127.0.0.1` |
| 容器內 `curl` 確認連得到 Ollama、填 `config.yaml` | 實驗室，**容器內** | 閘道的 `/health` 通過 |
| SSH 本機轉送 | 開發機 | 開發機的 `127.0.0.1:18000` 接到閘道 |
| 端對端驗收與品質紀錄 | 開發機 | 驗收 1、2 在真模型上通過；四項 AI 功能的輸出、耗時報告 |
| 換模型、換方法 | 實驗室改 `config.yaml`、開發機重跑 | 驗收 3、4 |
| 收尾 | 實驗室 | 個人資料夾以外沒有本專案的東西（驗收 7） |

### 0.2 現況（1116）

| 哪一段 | 現況 |
|---|---|
| 🏥 院內主機的閘道 | 1001 起就在跑（1001 有沒有照 V-29、V-30 做沒記到，1029 盤點時本系統四個容器含 AI 閘道都是 `v0.3.0`）；1029 J-20 沿用 1001 的設定檔、建成 `v0.4.0`，健康檢查 503 `base_url 尚未填寫`；1116 本系統換到 `v0.5.0` 時**沒建閘道**（兩版之間閘道沒改、AI 關著），所以仍是 `v0.4.0`、`Up`，正常 |
| 🏥 院內 `config.yaml` | `$root\config\ai-gateway\config.yaml`，由 `config.hospital.example.yaml` 複製，`base_url`、`model` 空白 |
| 🏥 院內 `.env` | `LLM_PROVIDER=mock`（首波 AI 關閉，DEP-29） |
| 正式 GPU API | Q-07 還沒答覆；答覆前不做 Z-23 |
| 實驗室實測 | 第 1～4 節還沒做（校外連不到，Q-08）；結論要回填《[部署演練紀錄](../notes/deployment-drills.md)》10.4 |
| 開發機本機實測（0927） | 實驗室之前，整條路徑先在開發機上以**假的推論端點**走過一次：閘道映像檔、LangChain 兩種方法、改 `config.yaml` 換模型、閘道停掉時主線照常，全部通過；院內那一份閘道也在開發機的部署實測上起過一次（`verify:iteration13 --live`：建置、不開埠、`api` 連得到、明確回報設定尚未填好）。結果見《部署演練紀錄》第 10 節 |

### 0.3 實驗室規範與本份的對應（DEP-42）

| # | 規範 | 本份 |
|---|---|---|
| 1 | 以 SSH 連線；**以 Terminal 的 `ssh` 取代 VS Code 的遠端視窗**（本專案唯一的差異） | Z-02 |
| 2 | 在指定路徑建個人資料夾，資料與程式碼只放自己的資料夾，不得動用別人的 | Z-03、Z-05；**不改共用帳號的任何設定檔，含 `~/.ssh/`** |
| 3 | 建個人容器，所有工作與套件安裝都在容器內 | Z-06、Z-07 |
| 4 | 查可用模型在**容器外**；確認連線在**容器內**以 `curl` 測 | Z-04、Z-08 |
| 5 | 以 LangChain 呼叫，建議以 config 檔管理設定 | 閘道本身就是這樣寫的；`config.yaml` 在個人資料夾 |
| 6 | 只能呼叫模型，不可管理；要新模型聯絡學長姐 | 閘道沒有任何管理模型的端點 |
| 7 | 第一次回應慢是模型在載入；一直慢可能是別人在用大型模型 | Z-11 的逾時設得寬；結果照實記錄 |

---

## 1. 開發機這一層

### Z-01 在專案目錄外記下連線資訊

在**專案目錄以外**開一個資料夾（例如 `%USERPROFILE%\hd-lab\`），建一份 `lab.env`：

```
LAB_HOST=<實驗室伺服器的位址>
LAB_SSH_PORT=<SSH 埠>
LAB_USER=<帳號>
LAB_JUMP_HOST=<若要先登入另一台再轉連，那一台的位址；沒有就刪掉這行>
LAB_GATEWAY_PORT=<閘道在實驗室伺服器上要綁的埠，挑一個沒人用的>
```

**密碼不寫進這份檔**，每次連線手打。這份檔同時是驗收 6 的比對來源（Z-15）。

再在 `%USERPROFILE%\.ssh\config`（**開發機自己的**，不是實驗室的）加一段，之後所有指令都用 `hd-lab` 這個別名，實際位址不必再出現在任何指令裡：

```
Host hd-lab
    HostName <實驗室伺服器的位址>
    Port <SSH 埠>
    User <帳號>
    # 要先登入另一台再轉連時才加這一行
    ProxyJump <帳號>@<轉連用的那一台>:<埠>
```

**怎麼知道成功了**：`ssh -G hd-lab` 印出的 `hostname`、`port`、`user` 是對的。

| 症狀 | 處置 |
|---|---|
| `%USERPROFILE%\.ssh` 不存在 | `mkdir $HOME\.ssh`。0927 時開發機沒有任何 SSH 設定，這是第一份（外殼與本系統的部署金鑰在院內主機上，不在開發機） |

---

### Z-02 第一次連線

```powershell
ssh hd-lab
```

打密碼。第一次會問主機指紋，**請學長姐確認指紋**再回 `yes`。

**怎麼知道成功了**：出現實驗室伺服器的提示字元；`hostname`、`whoami` 是預期的主機與帳號。

| 症狀 | 處置 |
|---|---|
| `Connection timed out` | 不在校內網路。實驗室伺服器校外連不到（Q-08），先連校內網路或照實驗室的方式轉連（`ProxyJump`） |
| `Permission denied` | 帳號或密碼錯。**不要**為了省打密碼去改實驗室那邊的 `~/.ssh/authorized_keys`——那是共用帳號的設定檔（規範第 2 項） |

> 從這裡開始的「實驗室」步驟都在這個 SSH 視窗裡做；「開發機」步驟另開一個 PowerShell 視窗。

---

## 2. 實驗室這一層

### Z-03 建個人資料夾（實驗室，容器外）

```bash
cd <指定路徑>
mkdir -p <個人資料夾>/hd-ai-gateway
ls -ld <個人資料夾> <個人資料夾>/hd-ai-gateway
```

**怎麼知道成功了**：兩個目錄都在，擁有者是你的帳號。之後**本專案的每一個檔案都只放在這底下**。

| 症狀 | 處置 |
|---|---|
| `Permission denied` | 不是規範指定的那個路徑。問學長姐，不要在家目錄或別人的資料夾底下建 |

---

### Z-04 查可用模型（實驗室，**容器外**）

```bash
ollama list
```

**怎麼知道成功了**：列出模型名稱與大小。挑一個**繁體中文能力可能較好、大小與目前使用狀況相符**的，名稱**一字不差**抄到開發機那份筆記（含冒號後面的標籤）。另挑一個備用，Z-12 換模型時用。

| 症狀 | 處置 |
|---|---|
| `ollama: command not found` | 這一台的 Ollama 不在你的 `PATH`，或查詢方式不同。問學長姐怎麼查，**不要自己裝** |
| 想用的模型不在清單上 | 只能用清單上有的（規範第 6 項）；要新模型聯絡學長姐 |

---

### Z-05 把閘道程式碼放進個人資料夾（開發機）

**只傳閘道這一個目錄**，本系統的其他程式碼、資料庫、`.env` 一律不上實驗室：

```powershell
cd <專案目錄>\services\ai-gateway
scp -r gateway Dockerfile .dockerignore requirements.txt config.example.yaml hd-lab:<指定路徑>/<個人資料夾>/hd-ai-gateway/
```

`<專案目錄>` 是開發機上本 repo 的根目錄。

**怎麼知道成功了**：實驗室上 `ls <指定路徑>/<個人資料夾>/hd-ai-gateway` 看得到那五樣。

| 症狀 | 處置 |
|---|---|
| 開發機有 `config.yaml` 也跟著傳上去了 | 本機那份不該存在（它有 `.gitignore`，但檔案還是會在）。刪掉本機那份，實驗室的在 Z-07 另建 |

---

### Z-06 建映像檔（實驗室，個人資料夾裡）

```bash
cd <指定路徑>/<個人資料夾>/hd-ai-gateway
docker build -t <個人前綴>-hd-ai-gateway:i13 .
```

`<個人前綴>` 用你自己的代號，讓別人一眼看得出這是誰的映像檔與容器。

**怎麼知道成功了**：建置過程最後有一段自我測試（`gateway.selftest`），結尾印出 `全部通過`，接著 `naming to …<個人前綴>-hd-ai-gateway:i13`。 **這一步同時確認了 LangChain 等套件裝在映像檔裡、兩種方法都能用**，還沒碰到真的模型。

| 症狀 | 處置 |
|---|---|
| `permission denied while trying to connect to the Docker daemon` | 你的帳號沒有 Docker 權限。問學長姐個人容器要怎麼建——若規定一律從實驗室提供的映像檔開，走下面的「替代做法」 |
| 下載 Python 套件失敗 | 實驗室伺服器連不到套件來源。問學長姐有沒有鏡像站；**不要改共用的 pip 設定** |
| 自我測試有 `✗` | 套件版本不對或程式被改過。對照 repo 的那一版重傳（Z-05） |

**替代做法**（不准自己建映像檔時）：以實驗室指定的 Python 映像檔開個人容器，把個人資料夾掛進去，套件裝在容器裡：

```bash
docker run -it --name <個人前綴>-hd-ai-gateway \
  -p 127.0.0.1:<閘道埠>:8000 --add-host=host.docker.internal:host-gateway \
  -v <指定路徑>/<個人資料夾>/hd-ai-gateway:/work -w /work \
  -e AI_GATEWAY_CONFIG=/work/config.yaml -e LANGSMITH_TRACING=false \
  <實驗室指定的 Python 3.12 映像檔> bash
# 以下在容器裡
pip install -r requirements.txt
python -m gateway.selftest
python -m gateway          # 前景執行；要離開按 Ctrl+P Ctrl+Q（容器繼續跑）
```

走這條路時，**實驗室與院內就不是同一個映像檔**（DEP-16），在演練紀錄裡寫明。

---

### Z-07 起個人容器（實驗室）

先放一份還沒填好的設定檔——**閘道在設定檔有誤時照樣啟動**，只是每個請求都回「設定有誤」，填好存檔就生效（閘道每個請求都會檢查這個檔有沒有變）：

```bash
cd <指定路徑>/<個人資料夾>/hd-ai-gateway
cp config.example.yaml config.yaml
chmod 644 config.yaml      # 容器裡以一般使用者執行，要讀得到

docker run -d --name <個人前綴>-hd-ai-gateway \
  -p 127.0.0.1:<閘道埠>:8000 \
  --add-host=host.docker.internal:host-gateway \
  -v <指定路徑>/<個人資料夾>/hd-ai-gateway:/config/ai-gateway:ro \
  <個人前綴>-hd-ai-gateway:i13
docker logs <個人前綴>-hd-ai-gateway
```

**`-p 127.0.0.1:…` 那個 `127.0.0.1` 不能省**：省了就是對整個實驗室網路開放，別人的機器連得到你的閘道（DEP-42）。映像檔裡預設 `AI_GATEWAY_CONFIG=/config/ai-gateway/config.yaml`、綁 `0.0.0.0:8000`（容器裡），對外開不開由 `-p` 決定。

**怎麼知道成功了**：`docker logs` 有 `設定檔有誤，改好之前 AI 功能無法使用：base_url 尚未填寫（推論端點的位址）` 與 `Uvicorn running on http://0.0.0.0:8000`。

| 症狀 | 處置 |
|---|---|
| `port is already allocated` | `<閘道埠>` 被別人用了。換一個，開發機筆記同步改 |
| `找不到設定檔 /config/ai-gateway/config.yaml` | `-v` 的左邊不是你的個人資料夾那一層，或 `cp` 沒做 |
| `Permission denied` 讀不到 `config.yaml` | 少了 `chmod 644` |

---

### Z-08 容器內以 `curl` 找到 Ollama（實驗室，**容器內**）

```bash
docker exec <個人前綴>-hd-ai-gateway curl -s -m 5 http://host.docker.internal:11434/api/tags
```

（`11434` 是 Ollama 的預設埠；實驗室若另有指定，照指定的。）

**怎麼知道成功了**：印出一段 JSON，裡面有 Z-04 看到的那些模型名稱。**這個位址就是 `config.yaml` 的 `base_url`。**

| 症狀 | 處置 |
|---|---|
| `Could not resolve host` | 少了 `--add-host=host.docker.internal:host-gateway`。`docker rm -f` 後照 Z-07 重起 |
| `Connection refused` | Ollama 只聽實驗室伺服器自己的 `127.0.0.1`，一般網路的容器進不去。改用「host 網路」起容器（下方） |
| 逾時 | 問學長姐：容器裡要用哪個位址連 Ollama |

**host 網路的起法**（Ollama 只聽本機時）：容器直接用實驗室伺服器的網路，閘道自己只綁 `127.0.0.1`：

```bash
docker rm -f <個人前綴>-hd-ai-gateway
docker run -d --name <個人前綴>-hd-ai-gateway --network host \
  -e AI_GATEWAY_HOST=127.0.0.1 -e AI_GATEWAY_PORT=<閘道埠> \
  -v <指定路徑>/<個人資料夾>/hd-ai-gateway:/config/ai-gateway:ro \
  <個人前綴>-hd-ai-gateway:i13
docker exec <個人前綴>-hd-ai-gateway curl -s -m 5 http://127.0.0.1:11434/api/tags
```

這時 `base_url` 是 `http://127.0.0.1:11434`，後面各步驟裡閘道自己的位址是 `127.0.0.1:<閘道埠>`（不是 `:8000`）。

---

### Z-09 填 `config.yaml`（實驗室）

```bash
nano <指定路徑>/<個人資料夾>/hd-ai-gateway/config.yaml
```

| 欄位 | 填什麼 |
|---|---|
| `provider` | `ollama`（先用方法一，langchain-ollama） |
| `base_url` | Z-08 測通的那一個，例如 `http://host.docker.internal:11434` |
| `model` | Z-04 挑的那一個，一字不差（含冒號後面的標籤） |
| 其他 | 範本的預設即可（`temperature: 0.2`、`num_ctx: 8192`、`timeout_seconds: 240`、`health_timeout_seconds: 3`） |

範本的幾條規則（`config.example.yaml` 的註解）：後端的 `LLM_TIMEOUT_SECONDS` 要比 `timeout_seconds` 大（開發機建議 300），否則後端會先放棄；`health_timeout_seconds` 要比後端的 `LLM_HEALTH_TIMEOUT_SECONDS`（預設 5）小，否則看到的只是「閘道逾時」而不是真正的原因；推論端點要金鑰時才填 `api_key`（Ollama 不需要）。

存檔。**不必重新啟動容器。**

```bash
docker exec <個人前綴>-hd-ai-gateway curl -s 127.0.0.1:8000/health
```

**怎麼知道成功了**：`{"status":"ok","config":"ok","provider":"ollama","model":"<你填的模型>",…}`。

| 症狀 | 處置 |
|---|---|
| `"config":"error"` | 看 `detail` 那一句，照它說的改（例如 `model 尚未填寫（推論端點上可用的模型名稱）`） |
| `推論端點上找不到設定的模型「…」` | `model` 與 `ollama list` 不是一字不差（常見：少了 `:` 後面的標籤） |

---

### Z-10 SSH 本機轉送（開發機）

另開一個 PowerShell 視窗，**這個視窗在測試期間一直開著**：

```powershell
ssh -N -L 127.0.0.1:18000:127.0.0.1:<閘道埠> hd-lab
```

打完密碼後游標停住、沒有任何輸出，這是正常的。再開一個視窗：

```powershell
curl.exe -s http://127.0.0.1:18000/health
```

**怎麼知道成功了**：與 Z-09 同樣的一行 JSON，這次是在開發機上看到的。

| 症狀 | 處置 |
|---|---|
| `bind [127.0.0.1]:18000: Address already in use` | 開發機上 18000 被佔了。換一個（例如 18001），後面的位址一起換 |
| `connect failed: Connection refused` | 實驗室那邊閘道沒在跑，或 `<閘道埠>` 對不上。回 Z-07／Z-08 |
| 過一陣子就斷 | 閒置被踢。加 `-o ServerAliveInterval=30` |

---

## 3. 實測

### Z-11 端對端驗收與品質紀錄（開發機）

```powershell
cd <專案目錄>
npm run verify:iteration13:api -- --gateway http://127.0.0.1:18000/v1 --report $HOME\hd-lab\ai-lab-trial-<日期>.md
```

腳本自己建一個暫存資料庫、另起一個 `LLM_PROVIDER=lab` 的後端（不碰開發用的資料庫），依序驗： AI 總開關開得起來（健康檢查經閘道通過）、合成病人的衛教產生成功且 `ai_invocations` 記下實驗室上的實際模型、「看似真實」的病人被擋下且完全沒有送出；再把四項 AI 功能各跑一次，輸出與耗時寫進報告。

**第一次會很慢**：模型要載入，可能一兩分鐘（規範第 7 項），腳本的逾時已放寬到五分鐘以上。

**怎麼知道成功了**：結尾 `全部通過`（驗收 3、4、5 那幾行是 `·`，表示在別處驗）；報告檔裡四項都有輸出。

報告要人讀：每一項的「品質」欄照這四點判讀後填——**繁體中文是否通順、有沒有簡體字或中國大陸用語、有沒有捏造提示裡沒有的事、格式是否照提示**。結論與耗時抄進《[部署演練紀錄](../notes/deployment-drills.md)》10.4；**報告檔本身留在專案目錄外**。

| 症狀 | 處置 |
|---|---|
| `AI 總開關` 那一步 HTTP 409 | 健康檢查沒過。`curl.exe http://127.0.0.1:18000/health` 看是閘道、`config.yaml` 還是轉送的問題 |
| 背景工作 `推論伺服器逾時` | 第一次載入太久，或別人在用大型模型。等幾分鐘重跑；一直如此就換小一點的模型（Z-12） |
| 輸出夾雜簡體字 | 照實記錄，這正是要蒐集的結果。可換模型比較 |

---

### Z-12 換模型、換方法（驗收 3、4）

**換模型**——實驗室改 `config.yaml` 的 `model` 為 Z-04 挑的備用模型，存檔。開發機：

```powershell
npm run verify:iteration13:api -- --gateway http://127.0.0.1:18000/v1 --expect-model <備用模型>
```

**換方法**——`config.yaml` 改成方法二（langchain-openai，OpenAI 相容介面）：

```yaml
provider: openai
base_url: http://host.docker.internal:11434/v1     # 結尾多一段 /v1
```

存檔，再跑一次（不帶 `--expect-model` 也可以）。

**怎麼知道成功了**：兩次都 `全部通過`；第一次的「呼叫紀錄的模型」是備用模型。**全程沒有重建映像檔、沒有重新啟動閘道、後端每次都是腳本新起的同一份程式**——換的只有 `config.yaml`。

---

### Z-13 用畫面看一次（開發機，選做）

開發機的 `.env`：

```
LLM_PROVIDER=lab
LLM_ENDPOINT=http://127.0.0.1:18000/v1
LLM_MODEL_ID=
LLM_TIMEOUT_SECONDS=300
```

`npm run dev`，護理端「系統管理」：供應者「實驗室 API」、資料離開院內標成「院外：僅得送合成資料」、模型識別字是 `config.yaml` 那一個、健康檢查通過。開 AI 總開關，替一位病歷號 `HD-TEST-` 開頭的病人產生衛教。**看完把 `.env` 改回 `LLM_PROVIDER=mock`。**

---

## 4. 收尾（驗收 6、7）

### Z-14 實驗室上不留東西

測試期間閘道可以留著。**確定不用了**：

```bash
docker rm -f <個人前綴>-hd-ai-gateway
docker rmi <個人前綴>-hd-ai-gateway:i13
docker ps -a --format '{{.Names}}' | grep <個人前綴>     # 沒有輸出
docker images | grep <個人前綴>                           # 沒有輸出
ls -la ~                                                  # 沒有本專案的檔案
```

個人資料夾留不留照實驗室的規矩；`config.yaml` 裡只有實驗室自己的位址與模型名稱。

**怎麼知道成功了**：本專案的東西只剩個人資料夾底下那一份（或整個刪掉）。這是驗收 7，結果寫進[迭代 13 分冊](../testing/iteration-13.md) §13.6。

開發機：關掉 Z-10 的轉送視窗，`.env` 改回 `mock`。

---

### Z-15 repo 裡沒有實驗室的連線資訊（開發機）

```powershell
npm run verify:iteration13 -- --secrets $HOME\hd-lab\lab.env
```

腳本逐字比對 `lab.env` 裡每一個值：工作目錄的每個檔案、git 歷史的每一次改動、每一則提交訊息。**值不會印出來**。要連密碼一起驗，暫時在 `lab.env` 加一行 `LAB_PASSWORD=…`，跑完刪掉。

**怎麼知道成功了**：每一個名稱都是 `✓ …檔案、歷史、提交訊息都找不到`。

| 症狀 | 處置 |
|---|---|
| 某個值出現在某個檔案 | 改掉，**再確認它沒被提交過**。已經提交或推上 GitHub 的，要當成外洩處理：換密碼、請學長姐評估要不要換位址或埠 |

---

## 5. 院內主機

首波 AI 功能預設關閉（DEP-29），閘道可以根本不起。Z-20～Z-22 在本系統起來之後做一次，讓閘道就位、確認它明確回報「設定尚未填好」（🏥 院內 1001／1029 已做過，第 0.2 節）；Z-23 等 Q-07（正式 GPU API）有答案才做。這一段與[《從零部署本系統》](ref-fresh-install.md) V-29、V-30 是同一件事。

指令都在主機的 PowerShell、`$root\repo` 底下下，每個新視窗先輸入這三行：

```powershell
$root = "C:\hd\hd-tablet-care"          # 🧪 開發機演練改成 C:\hd-sim
$cfg  = "$root\config\.env"
cd $root\repo
```

（0927 原文寫的是 `D:\hd-tablet-care`；1001 起院內主機的根目錄是 `C:\hd\hd-tablet-care`。）

### Z-20 放院內那一份 `config.yaml`

先看有沒有：`Test-Path $root\config\ai-gateway\config.yaml` 是 `True` 就是做過了（🏥 院內主機已經有），**不要再複製一次蓋掉它**。沒有才做：

```powershell
New-Item -ItemType Directory -Force $root\config\ai-gateway | Out-Null
Copy-Item services\ai-gateway\config.hospital.example.yaml $root\config\ai-gateway\config.yaml
```

範本的 `provider` 預設 `openai`（正式 GPU API 多半提供 OpenAI 相容介面；若是 Ollama 改 `ollama`），`base_url` 與 `model` 刻意留空：留空時閘道照樣啟動，但每個請求都回「閘道設定有誤」，後端的健康檢查不通過，AI 總開關就開不起來——不會半套設定就開始跑。**不要填實驗室的位址**——院內主機連得出去，填了就是把資料往院外送。`base_url` 只准是院內位址（FR-S07；`check:egress` 會掃範本）。

compose 把設定目錄（`HD_CONFIG_DIR`）唯讀掛進閘道的 `/config`，閘道讀 `/config/ai-gateway/config.yaml`。

### Z-21 建置與啟動閘道

```powershell
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

| 症狀 | 處置 |
|---|---|
| `fetch failed` | 閘道沒起來。`docker compose --env-file $cfg --profile ai logs ai-gateway` |
| `找不到設定檔` | Z-20 的路徑不對：必須是設定目錄底下的 `ai-gateway\config.yaml` |
| `docker compose ps` 看到 `ai-gateway` 有 `0.0.0.0:…->8000` | 有人在 compose 加了 `ports`。拿掉——閘道不對外（部署規範 5.3），`npm run check:container` 會擋 |
| 建置時 `no such host` | 查不到 Docker Hub 或套件來源（DNS），處置同[《從零部署本系統》](ref-fresh-install.md) V-06 |

### Z-22 之後每一次 `up` 都帶 `--profile ai`

閘道起過之後，換版時（[《本系統換版與退回》](ref-upgrade.md)）`build` 與 `up -d` 都要加 `--profile ai`，閘道才會跟著換成新版映像檔。沒帶的話，閘道停在舊版，但**主線不受影響**（DEP-24）。

> 📍 **1116 院內**：換到 `v0.5.0` 時刻意沒帶（兩版之間閘道沒改、AI 關著），閘道仍是 `v0.4.0`，正常。之後哪一版的閘道有改，換版那一步就要帶。

### Z-23 接上正式 GPU API（Q-07 有答案之後）

1. `$root\config\ai-gateway\config.yaml`：填 `provider`、`base_url`、`model`（要金鑰時填 `api_key`；這個檔在主機的設定目錄，不在 repo，DEP-13）。院內範本的 `timeout_seconds: 120`、`health_timeout_seconds: 3`。存檔即生效，閘道不必重新啟動。
2. 確認：Z-21 的最後一行改成 `200 {"status":"ok",…}`。
3. `$cfg` 的 AI 那一段（`LLM_MODEL_ID` 接閘道時**留空**：模型只由 `config.yaml` 決定；`LLM_TIMEOUT_SECONDS` 要比 `timeout_seconds` 大）：

```
LLM_PROVIDER=onprem
LLM_ENDPOINT=http://ai-gateway:8000/v1
LLM_MODEL_ID=
LLM_TIMEOUT_SECONDS=150
```

4. `docker compose --env-file $cfg up -d api`（只換環境變數，**不重建映像檔**）。
5. 護理端「系統管理」：供應者「院內地端推論」、健康檢查通過，才照 DEP-29 的條件開 AI 總開關。「允許真實病人資料」是另一個開關，另有條件，**不在這一步開**。

**這就是 FR-S13 的驗收**：由實驗室換成正式 GPU API，改的只有 `config.yaml` 與 `.env` 的 `LLM_PROVIDER`，程式一行未動。

### Z-24 把 AI 整個關掉

護理端關 AI 總開關，然後：

```powershell
docker compose --env-file $cfg --profile ai stop ai-gateway
```

主線完全不受影響（DEP-24，本機實測過，見《部署演練紀錄》第 10 節）。

---

## 6. 疑難排解（AI 閘道特有的）

| 症狀 | 原因 | 處置 |
|---|---|---|
| 護理端「健康檢查」寫 `無法連線至推論伺服器` | 後端連不到**閘道**（開發機：轉送斷了；院內：閘道沒起） | 開發機重開 Z-10；院內 Z-21 |
| 健康檢查寫 `推論伺服器回應 HTTP 503` | 閘道在，但它後面不通或設定有誤 | 開 `<閘道>/health` 看 `detail` |
| 健康檢查寫 `端點上找不到設定的模型` | 後端的 `LLM_MODEL_ID` 填了東西，與 `config.yaml` 不同 | `LLM_MODEL_ID` 留空 |
| 換了 `config.yaml`，呼叫紀錄的模型沒變 | 改到另一份檔案（實驗室：不是掛進容器的那個資料夾；院內：不是設定目錄底下那份） | `docker inspect <容器> --format '{{json .Mounts}}'` 看實際掛的是哪裡 |
| 院內後端起不來：`正式環境設定下不得使用 LLM_PROVIDER=lab` | 有人把開發機的設定抄過來了 | 這是 DEP-40 在擋。改成 `onprem` 或 `mock` |
| 輸出前面有一段思考過程 | 模型把思考放在 `<think>` 以外的格式 | `config.yaml` 加 `reasoning: false`（方法一），或換模型 |

現場其他症狀見[《現場疑難排解》](ref-troubleshooting.md)。

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回部署手冊目錄](index.md)
