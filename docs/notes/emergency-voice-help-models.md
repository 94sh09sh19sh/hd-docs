# 緊急求助的語音說明之一：開源專案與模型的選型

版本：v0.3　文件狀態：規劃中（2026-10-25 開立；1026 依使用者對選型規則的答覆再修；1026 鏡頭的選型另寫在之三）　適用讀者：FDE 工程團隊、資訊室

上層文件：《[緊急求助的語音說明：根本判斷與設計](emergency-voice-help.md)》第 5 節

> 1026 上層文件依使用者指出的前提重寫：語音不再用於派遣、改用於護理紀錄，轉寫改成批次。同日使用者答覆上層第 9 節前三題：非 GitHub 專案也可以用（第 1 節判準）、語氣要做要留（SenseVoice 回到系統裡，只存不顯示）。同日院方也建議配合鏡頭：鏡頭的專案照本文件第 1 節同一套條件查，寫在《[之三：鏡頭能做到哪些事](emergency-voice-help-camera.md)》第 1、2 節；採用的 ONNX Runtime 跟本文件第 2 節是同一個專案（鏡頭用它的網頁版、在平板上跑）。

---

## 摘要

- 篩選條件：直接選用的 GitHub 專案要 MIT 授權、超過 1000 顆星（使用者 1025）；間接相依不算（1026「照建議」）；加上 DEP-14 零院外連線、能在院內離線跑、聽得懂華語與台語（第 1 節）
- **1026 放寬**：非 GitHub 的專案與權重也可以用，條件是授權可用、院內硬體跑得動、公信力與安全性至少等同千星專案；開發端把它拆成五條可查核的判準（第 1.2 節）
- 採用八個 GitHub 專案，全部 MIT、千星以上：whisper.cpp（辨識引擎）、faster-whisper 與 CTranslate2（備選引擎與權重轉換）、Silero VAD 與 ONNX Runtime（切句）、SenseVoice 與 FunASR（語氣與聲音事件，只存不顯示）、OpenAI Whisper（模型格式的源頭）（第 2 節）
- 星數與授權是 2026-10-25 以 GitHub API 逐一查的；權重的下載數、按讚、格式是 1026 以 Hugging Face API 查的，不是憑印象
- 權重判定：Breeze-ASR-26／25 合格；SenseVoiceSmall 合格，但檔案是 PyTorch pickle，要隔離轉檔；emotion2vec+ 程式 repo 的授權沒釐清，維持備選（第 4 節）
- 排除的 GitHub 專案大多是 Apache-2.0（sherpa-onnx、WeNet、Qwen3-ASR、FireRedASR…），雲端服務違反 DEP-14（第 3 節）
- 台語是最大的不確定：Breeze-ASR-26 公開成績只有 30 句政府公告、字元錯誤率約 30%，沒有長者、病中、透析室雜音的資料，一定要自己測；語氣模型沒用台語訓練過（第 5 節）
- DGX Spark 是 ARM 加 GB10，whisper.cpp 要自己以 CUDA 編譯；院內 Windows 主機沒有 GPU，批次轉寫與語氣在 CPU 上跑，速度待實測（第 6 節）

## 1. 篩選條件

### 1.1 條件總表

| # | 條件 | 來源 |
|---|---|---|
| 1 | 直接選用的 GitHub 專案：MIT 授權、超過 1000 顆星；間接相依（PyTorch、NumPy 這類）不算 | 使用者 1025；1026「照建議」 |
| 2 | 非 GitHub 的專案與模型權重也可以用：授權可用、醫院硬體規格夠用、公信力與安全性至少等同 GitHub 千星專案（判準見 1.2） | 使用者 1026 |
| 3 | 執行期零院外連線，模型與程式全部在院內 | DEP-14 |
| 4 | 聽得懂華語、台語與兩者混用 | 院方 1025 |
| 5 | 除了文字，還要拿得到語氣與聲音事件（1026 使用者：要做、要留，不上護理紀錄） | 院方 1025；使用者 1026 |
| 6 | 能在 DGX Spark（aarch64、GB10）或院內 Windows 主機的 CPU 上跑 | Q-07、部署規範第 2 章 |
| 7 | 還在維護（近半年有推送）、沒有封存；權重是定版的檔案，改看發布者與檔案有沒有固定版本 | 開發端 |

星數、授權、最後推送時間都是 2026-10-25 以 `gh api repos/<名稱>` 查的；授權以 GitHub 判讀的 SPDX 為準，判讀不出來的另外開啟 LICENSE 檔看。

條件 1 照舊只認 MIT，所以第 3 節排除的 Apache-2.0 GitHub 專案維持排除；同樣是 Apache-2.0 的 Breeze 權重能用，是因為它走條件 2。日後若要把 GitHub 專案也放寬成「授權可用」，第一個回頭看的是 sherpa-onnx。

### 1.2 「等同千星」的判準（非 GitHub 專案與權重）

使用者只定了「公信力與安全性至少等同 GitHub 千星專案」，下表是開發端拆出來的查核方式；門檻是起始值，使用者覺得太鬆或太嚴再調。

| 面向 | 判準 | 為什麼 |
|---|---|---|
| 發布者 | 可查核的機構（公司或學研單位），有公開論文或技術報告 | 千星專案的公信力多半來自「有人負責、做法公開」；匿名上傳的權重不收 |
| 社群檢驗 | Hugging Face 按讚 50 以上，或近 30 天下載 5,000 次以上；程式另放在 GitHub 的，那個 repo 本身也要千星以上 | 表示有足夠多的人實際用過、出問題會被回報 |
| 安全 | 權重格式載入時不會執行程式（safetensors、GGUF、ONNX）；只有 PyTorch pickle（`.pt`、`.bin`、`.pkl`）的，在隔離的開發機以 `torch.load(weights_only=True)` 載入、轉成前述格式、記雜湊，系統只用轉好的；固定 Hugging Face 的 commit；不用第三方轉好的版本 | pickle 檔載入時可以執行任意程式，是權重最主要的安全風險；千星的程式專案有人審程式碼，權重沒有，只能從格式上擋 |
| 授權 | 明文允許院內使用（不限非商用、不禁醫療用途）；要求署名或保留名稱的照辦 | 使用者 1026「授權要可用」 |
| 硬體 | 院內 Windows 主機（i7-14700、64 GB、沒有 GPU，Q-27）的 CPU 跑得動批次；要即時的，等 DGX Spark（Q-07，尚未架設） | 使用者 1026「醫院硬體規格要夠用」；平板不跑模型（第 6 節） |

## 2. 採用的專案

| 專案 | 在本系統做什麼 | 授權 | 星數 | 最後推送 |
|---|---|---|---|---|
| [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | **辨識引擎（主）**：`whisper-server` 提供 HTTP `/inference`，內建 Silero VAD 選項；CPU、CUDA 都能編 | MIT | 54,654 | 2026-10-19 |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 辨識引擎（備選）：Python、速度快，但 DGX Spark 上要自己編 CTranslate2（第 6 節） | MIT | 26,125 | 2026-10-25 |
| [OpenNMT/CTranslate2](https://github.com/OpenNMT/CTranslate2) | faster-whisper 的底層；`ct2-transformers-converter` 把官方權重轉成它的格式 | MIT | 4,719 | 2026-10-25 |
| [openai/whisper](https://github.com/openai/whisper) | 模型架構與格式的源頭（Breeze 兩個模型都是它的微調）；不直接拿來跑，PyTorch 原版太慢 | MIT | 111,237 | 2026-08-31 |
| [snakers4/silero-vad](https://github.com/snakers4/silero-vad) | **切句**：判斷哪一段是人在說話，沒說話的不送辨識（防幻覺的第一道） | MIT | 10,522 | 2026-10-22 |
| [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) | Silero VAD 在語音閘道裡的執行環境（CPU） | MIT | 22,167 | 2026-10-25 |
| [QwenAudio/SenseVoice](https://github.com/QwenAudio/SenseVoice) | **語氣與聲音事件**：一次推論同時給語言、情緒 7 類、事件 8 類（原 FunAudioLLM/SenseVoice，已搬家）。1026 起語氣要做要留：每一句都跑、結果存進資料庫，第一版不顯示（上層第 3.4 節）；文字以 Breeze 為準 | MIT | 9,587 | 2026-09-30 |
| [modelscope/FunASR](https://github.com/modelscope/FunASR) | SenseVoice 的執行框架；也有 llama.cpp／GGUF 的免 Python 版本 | MIT | 20,812 | 2026-10-22 |

**只借作法、不進系統的**（同樣 MIT、千星以上；1026 起床邊對話改成批次轉寫，串流的作法只剩「其他」的按住說話用得到）：

| 專案 | 星數 | 借什麼 | 為什麼不直接用 |
|---|---|---|---|
| [ufal/whisper_streaming](https://github.com/ufal/whisper_streaming) | 3,676 | 串流辨識的「兩次結果一致才定稿」（LocalAgreement） | 自帶協定與前端程式，跟本系統的裝置 Token、SSE 對不上 |
| [collabora/WhisperLive](https://github.com/collabora/WhisperLive) | 4,332 | 即時辨識服務的切段與佇列 | 同上，而且自開 WebSocket |
| [KoljaB/RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) | 10,205 | VAD 加辨識的串接順序 | 設計給桌面麥克風，不是平板經 HTTPS 送來的音訊 |

**符合條件、但這一版不用的**：

- [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio)（MIT、10,702）：說話者分離。分得出「鄰床的人在說話」，但要建每個人的聲音特徵，等於聲紋，隱私代價大過好處，不做；代價是床邊對話的語氣分不出是病人還是護理師的（上層第 3.4 節）
- [ddlBoJack/emotion2vec](https://github.com/ddlBoJack/emotion2vec)（1,207 顆星）：語氣辨識 9 類，可當 SenseVoice 的備選。**README 寫 MIT，但 repo 裡沒有 LICENSE 檔，GitHub 判讀不出授權**——不符條件 1；1026 放寬的條件 2 也要「授權可用」，所以要用之前仍要先請作者補或以書面確認

## 3. 排除的專案與服務

條件 1 的 MIT 規則 1026 沒有改，下表照舊。

| 專案或服務 | 授權／星數 | 排除理由 |
|---|---|---|
| [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | Apache-2.0／15,503 | 不是 MIT |
| [wenet-e2e/wenet](https://github.com/wenet-e2e/wenet) | Apache-2.0／5,251 | 不是 MIT |
| [QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) | Apache-2.0／3,767 | 不是 MIT |
| [QwenAudio/Fun-ASR](https://github.com/QwenAudio/Fun-ASR) | Apache-2.0／1,585 | 不是 MIT |
| [FireRedTeam/FireRedASR](https://github.com/FireRedTeam/FireRedASR) | Apache-2.0／2,009 | 不是 MIT |
| [DataoceanAI/Dolphin](https://github.com/DataoceanAI/Dolphin) | Apache-2.0／797 | 不是 MIT、不到千星 |
| [m-bain/whisperX](https://github.com/m-bain/whisperX) | BSD-2-Clause／24,836 | 不是 MIT |
| [huggingface/transformers](https://github.com/huggingface/transformers) | Apache-2.0／168,138 | 不是 MIT。Breeze 官方範例用它；改走 whisper.cpp 就不需要 |
| [librosa/librosa](https://github.com/librosa/librosa) | ISC／8,710 | 不是 MIT。音量、語速、停頓改成自寫程式算（上層第 3.4 節） |
| [ricky0123/vad](https://github.com/ricky0123/vad) | 判讀不出／2,071 | 瀏覽器端 VAD；授權判讀不出，而且切句放在伺服器端就不需要 |
| [mozilla/DeepSpeech](https://github.com/mozilla/DeepSpeech) | MPL-2.0／26,775 | 不是 MIT、已封存 |
| Google、雅婷、Gemini 等雲端語音辨識 | — | DEP-14：執行期零院外連線 |
| Android 內建語音辨識、瀏覽器 Web Speech API | — | 走雲端，而且不支援台語 |

## 4. 模型權重

權重放在 Hugging Face，**不是 GitHub 專案**，照第 1.2 節的判準逐份查。下載數是 Hugging Face 統計的近 30 天數字，與按讚、格式都是 2026-10-26 以 Hugging Face API 查的。

| 權重 | 授權 | 發布者與論文 | 按讚／近 30 天下載 | 格式 | 判定 |
|---|---|---|---|---|---|
| [MediaTek-Research/Breeze-ASR-26](https://huggingface.co/MediaTek-Research/Breeze-ASR-26) | Apache-2.0 | 聯發科創新基地、陽明交大；[arXiv 2603.19259](https://arxiv.org/abs/2603.19259) | 93／37,022 | safetensors | **合格** |
| [MediaTek-Research/Breeze-ASR-25](https://huggingface.co/MediaTek-Research/Breeze-ASR-25) | Apache-2.0 | 聯發科創新基地；[arXiv 2506.11130](https://arxiv.org/abs/2506.11130) | 155／22,978 | safetensors（repo 另有訓練狀態的 `.pkl` 與 `.pt`，不下載） | **合格** |
| [FunAudioLLM/SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall) | [FunASR 模型授權 1.1](https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE) | 阿里巴巴通義實驗室；FunAudioLLM 技術報告 | 501／22,257 | `model.pt`（pickle） | **合格，要隔離轉檔**（第 1.2 節安全一列） |
| Silero VAD 模型 | MIT | 跟程式同一個 GitHub repo | — | ONNX | 走條件 1，合格 |
| [emotion2vec/emotion2vec_plus_large](https://huggingface.co/emotion2vec/emotion2vec_plus_large)（備選） | 模型卡寫 FunASR 模型授權；程式 repo 沒有 LICENSE 檔 | 上海交大等；[arXiv 2312.15185](https://arxiv.org/abs/2312.15185) | 81／4,527 | `model.pt`（pickle） | **暫不用**：授權沒釐清（第 2 節） |

| 權重 | 用途 | 重點 |
|---|---|---|
| Breeze-ASR-26 | **台語與台華混用** | whisper-large-v2 微調，約 1 萬小時**合成**台語（含台華混用）；輸出**華文字**，不是台文正字 |
| Breeze-ASR-25 | **台灣華語**（與英文混用） | whisper-large-v2 微調；CommonVoice16 台灣華語詞錯誤率 7.97（原版 9.84）；不含台語 |
| SenseVoiceSmall | **語氣與聲音事件** | 約 2.3 億參數；維護者書面澄清可商用；要註明出處、保留模型名稱。語言只有華、粵、英、日、韓，**沒有台語** |
| Silero VAD | 切句 | 約 2 MB |

- **權重轉換自己做**：從官方權重以 whisper.cpp 的轉換腳本（或 `ct2-transformers-converter`）轉，記下雜湊值。Hugging Face 上已有十幾份別人轉好的 Breeze-ASR-26（GGML、CTranslate2、量化版），來源無法查核，一律不用
- **SenseVoiceSmall 的轉檔**：只有 pickle 格式，在沒有連網、不放院內資料的開發機以 `weights_only=True` 載入，轉成 ONNX 或 GGUF（FunASR 有 GGUF 版本的路），記雜湊；院內只放轉好的檔案
- SenseVoice 的情緒 7 類：開心、難過、生氣、中性、害怕、厭惡、驚訝；事件 8 類：背景音樂、說話、掌聲、笑聲、哭聲、打噴嚏、呼吸聲、咳嗽。**它是用華語等五種語言訓練的，台語長者的語氣認不認得準，沒有人測過**——這是語氣第一版只存不顯示的主因（上層第 3.4 節）

## 5. 台語辨識的難處

- **Whisper 本身不認得台語**：原版沒有台語的語言代號，聽到台語多半硬寫成華語或亂寫
- **Breeze-ASR-26 以華文字輸出**：台文正字寫法不統一、護理師也讀華文，輸出華文字對護理站反而好用；代價是台語特有的詞會被「翻」成華語，意思可能偏掉
- **公開成績很薄**：30 句行政院公告（台華對照），字元錯誤率 30.13%，雅婷 32.11%、Gemini 3 Flash 32.52%、Breeze-ASR-25 49.99%——前三名差距不到 2.4 個百分點、樣本只有 30 句，看不出誰真的比較好
- **沒測過的情境正好是我們的情境**：訓練資料全是合成語音；論文沒有長者、病中無力的聲音、透析機與鄰床的雜音，也沒有醫療用語
- **混用的處理**：Breeze-ASR-26 的訓練資料含台華混用；純華語交給 Breeze-ASR-25 可能比較準。上層文件第 5 節的「兩個模型並跑、取有把握的那個」只是假設，要用上層文件第 6 節的語料驗證，不行就只留 Breeze-ASR-26
- **語氣也一樣**：SenseVoice 聽台語時，語言標籤會判錯，情緒標籤準不準要用上層第 6 節的語料分台語、華語各算一次
- **Whisper 會幻覺**：在靜音與雜音上會生出不存在的句子（常見的是影片字幕那類「謝謝收看」）。醫療情境最怕這個，防法寫在上層文件第 5 節

## 6. 在哪裡跑

| 地方 | 跑得動嗎 | 要注意 |
|---|---|---|
| **院內 DGX Spark**（建議） | 跑得動。統一記憶體 128 GB，兩個 large-v2 加 SenseVoice 都放得下 | aarch64＋GB10（計算能力 12.1）。whisper.cpp 的官方 CUDA 映像只有 x86，要在那台上以 `-DGGML_CUDA=1` 自己編；faster-whisper 在 arm64 上沒有官方 GPU 版 CTranslate2，有人回報裝了也只會用 CPU、要自己編（[speaches #620](https://github.com/speaches-ai/speaches/issues/620)）。端點本身要有人架、有人顧（Q-07，**本院區尚未架設**） |
| 院內 Windows 主機 CPU（i7-14700、64 GB） | 量化版應跑得動，**速度待實測**；SenseVoiceSmall 只有 large-v2 的約七分之一大，語氣這一步的負擔小 | 主機跟別的專案共用（Q-27）；只建議在端點到之前、合成語料上試。1026 起床邊對話是批次、延遲目標是結案後 2 分鐘，CPU 比即時串流更有機會趕上；按住說話要幾秒內出來，仍要 GPU |
| 開發機 | 跑得動 | 驗證語料、效能量測、pickle 權重的隔離轉檔都在這裡先做 |
| 平板上 | 不考慮 | 4 GB 記憶體跑不動約 15 億參數的模型，而且會發燙、耗電 |

## 7. 參考資料

- [Breeze Taigi: Benchmarks and Models for Taiwanese Hokkien Speech Recognition and Synthesis](https://arxiv.org/abs/2603.19259)（陽明交大、聯發科創新基地，2026-02）
- [A Self-Refining Framework for Enhancing ASR Using TTS-Synthesized Data](https://arxiv.org/abs/2506.11130)（Breeze-ASR-25 的論文，文中稱 Twister）
- [Breeze-ASR-26 模型卡](https://huggingface.co/MediaTek-Research/Breeze-ASR-26)、[Breeze-ASR-25 模型卡](https://huggingface.co/MediaTek-Research/Breeze-ASR-25)
- [SenseVoice README 的授權說明](https://github.com/QwenAudio/SenseVoice#license)、[FunASR 模型授權](https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE)
- [emotion2vec 論文](https://arxiv.org/abs/2312.15185)
- [whisper.cpp server 的參數（含 VAD）](https://github.com/ggml-org/whisper.cpp/tree/master/examples/server)
- [CLiFT-ASR：低資源台語辨識的跨語言微調](https://arxiv.org/abs/2511.06860)（另一條路線：用 TAT-MOE 語料微調，whisper-small 主測試集字元錯誤率約 18.7%；TAT 語料不是開放授權）
- Hugging Face 模型 API：`https://huggingface.co/api/models/<名稱>`（下載數、按讚、檔案清單）

---

## 版本歷程

| 定版 | 日期 | 異動 |
|---|---|---|

[← 回上層文件](emergency-voice-help.md)　[← 回其他文件總表](index.md)　[← 回進度首頁](../index.md)
