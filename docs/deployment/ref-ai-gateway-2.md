# AI 閘道（第 2 份，Z-03～Z-10）

上層文件：[《AI 閘道》](ref-ai-gateway.md)

> **狀態：現行**（常備參考）。改寫來源見[第 1 份](ref-ai-gateway.md)開頭。編號：`Z-xx`，沿用原編號。

> ⚠️ **實驗室的位址、SSH 埠、帳號與密碼，一律不寫進 repo、不寫進這本手冊、不寫進週報**（DEP-42）。本份用 `<角括號>` 標出要換成實際值的地方；實際值只存在你自己電腦上、專案目錄以外的那一份筆記（Z-01）。文件站是公開的。

## 摘要

- 第 2 節實驗室這一層（Z-03～Z-10）：過渡期在實驗室的 GPU 伺服器上起閘道，只准合成資料；實驗室的值一律用 `<角括號>`（DEP-42）
- Z-03 建個人資料夾、Z-04 `ollama list` 查可用模型，兩步都在**容器外**
- Z-05 從開發機把閘道程式碼放進個人資料夾、Z-06 在個人資料夾裡建映像檔或替代做法
- Z-07 起個人容器（只綁 `127.0.0.1`）、Z-08 在容器內以 `curl` 找到 Ollama
- Z-09 填 `config.yaml`、Z-10 開發機上 SSH 本機轉送
- Z-01～Z-02 在第 1 份；實測、收尾與院內（Z-11～Z-24）在[第 3 份](ref-ai-gateway-3.md)

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

上一份：[《AI 閘道》](ref-ai-gateway.md)・下一份：[《AI 閘道（第 3 份，Z-11～Z-24）》](ref-ai-gateway-3.md)・[部署手冊目錄](index.md)

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|
| [1118](https://94sh09sh19sh.github.io/hd-docs/1118/deployment/ref-ai-gateway-2/) | 2026-11-18 | 首次定版。1118 照每份約 300 行的上限由《AI 閘道》拆出，內容與步驟編號不動 |

[← 回部署手冊目錄](index.md)
