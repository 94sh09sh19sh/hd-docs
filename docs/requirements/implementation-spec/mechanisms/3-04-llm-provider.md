# 實作規格書 3.4 模型供應者介面層 `LlmProviderPort`（改寫）

上層文件：《[實作規格書](../../implementation-spec.md)》第 3 章

**取代 v1.0 的「AI Proxy Service 直接呼叫外部服務商」設計。**

```
LlmProviderPort（抽象介面）
├── MockLlmProvider      ← 預設。回傳固定範例，讓所有 AI 功能可先開發與測試
├── LabApiProvider       ← 過渡期。實驗室 API（院外），僅得送合成資料
└── OnPremiseProvider    ← 正式。院內 DGX Spark 上的推論端點（不由本專案部署，見 DEP-16）
```

介面至少涵蓋：`generate(prompt, options)`、健康檢查、可用模型清單。

**硬性規則**：

1. **任何呼叫語言模型之處，一律透過 `LlmProviderPort`。** 不得在業務邏輯中出現任何一家廠商的 SDK、端點或模型名稱。切換 provider 只能是設定變更。
2. **模型識別字串、端點、金鑰全部由設定提供**，`.env.example` 保留空值。院內推論服務的端點與可用模型未確認（Q-07）、實驗室的可用模型會變動（Q-08），因此**不在程式或文件中寫死任何模型名稱**。0926 起模型名稱只寫在 AI 閘道的 `config.yaml`（實驗室那一份不進 repo，repo 只放範本）。
3. **`LabApiProvider` 必須帶「合成資料檢查」**：當目前 provider 為 `LabApiProvider` 時，帶有真實病人資料標記的請求要被擋下並記錄（FR-S06）。這是程式強制，不是靠人的自律。
4. **去識別化在寫入資料庫之前完成**，不是查詢時才遮蔽（《資料庫使用規範》第 14 條）。
5. **AI 呼叫一律寫入 `ai_invocations`**：provider、模型、參數、耗時、是否觸發去識別化、成功或失敗。提示與輸出留存 12 個月，原始（未去識別化）提示不存。
6. **非即時功能走背景佇列。** 衛教生成、記錄草擬這類「可以等」的工作不得阻擋 HTTP 請求，也不得在資料庫交易中呼叫模型（會佔住 SQLite 唯一的寫入位置）。

**0926：介面之下多一層 AI 閘道**（FR-S13、部署規範第 5 章）。`LlmProviderPort` 不動，`LabApiProvider` 與 `OnPremiseProvider` 的 `LLM_ENDPOINT` 都指向**閘道**，不指向推論端點：

```
LlmProviderPort ── HttpLlmProvider ──▶ AI 閘道（services/ai-gateway，Python ＋ LangChain）
  ├── MockLlmProvider                      │ config.yaml：provider／base_url／model／參數
  ├── LabApiProvider   ─┐                  ├─▶ 實驗室 Ollama（過渡期，經 SSH 通道，只送合成資料）
  └── OnPremiseProvider ┘ 同一份 HTTP 實作 └─▶ 院內正式 GPU API（正式）
```

硬性規則再加四條：

7. **後端不得直接連推論端點**（DEP-41）。Ollama 的位址、模型名稱、LangChain 只准出現在閘道裡
8. **閘道照實驗室規範寫**：`config.yaml` 管 `provider`（`ollama` 或 `openai` 相容介面）、`base_url`、`model`、`temperature`、`num_ctx`；`llm_factory` 集中建立物件。**不提供任何管理模型的端點**（規範：只能呼叫、不能管理）
9. **換正式 GPU API 的驗收標準是「只改 `config.yaml` 與 `LLM_PROVIDER`」**。若做不到，改的是閘道，不是後端
10. **正式環境設定下 `LLM_PROVIDER=lab` 拒絕啟動**（DEP-40），與第 3 條的合成資料檢查並存

**閘道對後端的介面**：`/v1/chat/completions`、`/v1/models`（回傳 `config.yaml` 設定的模型，不列推論端點上的全部模型）、`/health`。後端的 `HttpLlmProvider` 沿用；0919 那句「院內伺服器規格與實驗室 API 端點格式確認前這只是暫定」到此定案——**格式由我們自己的閘道決定**，外面怎麼變都關在閘道裡。

**0927 補（迭代 13 實作時發現）**：`HttpLlmProvider` 原本把 `LLM_MODEL_ID` 當必填，還拿它核對模型清單，換模型就得同時改 `config.yaml` 與後端 `.env`，第 9 條做不到。改了一處：**接閘道時 `LLM_MODEL_ID` 留空**，請求不帶 `model`，由閘道決定並在回應裡回報實際模型，`ai_invocations` 記那一個。第 2 條「模型名稱只寫在 `config.yaml`」因此是程式強制，不只是慣例。

**1007 補（迭代 17.3）**：硬性規則再加一條：

11. **AI 生成的內容禁用簡體字與中國大陸用語**（含台灣不這樣寫的繁體字形）。由 `AiGatewayService` 統一把關：系統提示最後一律附上台灣用語的規則；輸出查到問題就記一筆失敗的呼叫紀錄、把「哪個詞改成什麼」附進提示請模型重寫，背景生成最多送 3 次、SOP 查詢最多 2 次，最後一次仍不合格也照樣交出。**前端不得出現這道把關的痕跡**：退回的那幾次照第 5 條記呼叫紀錄與稽核，但回給前端的清單不列、提示截掉重寫附註（`apps/api/src/common/zh-tw-retry.ts`）。字表在 `packages/shared/zh-tw/`，由 `npm run zh-tw:data` 產生資料檔。**不得另開一條繞過閘道的呼叫路徑**——第 1 條本來就這樣規定，這一條讓它多一個理由

**1123 補（院內推論端點的線索）**：同一台院內主機上另一套系統直接連院內的 Ollama（原生介面、沒有金鑰；《[同主機 RAG 系統參考調查](../../../notes/ai-endpoint-reference-survey.md)》）。閘道的 `provider: ollama` 就是這一種，**不改程式**：

- 院內那份 `config.yaml` 填 `provider: ollama`、`base_url`、`model`；Ollama 在同一台主機時 `base_url` 寫 `http://host.docker.internal:11434`（容器裡的 `127.0.0.1` 是容器自己），在別台就寫那台的院內位址（只進主機設定目錄與私人紀錄）
- 範本 `services/ai-gateway/config.hospital.example.yaml` 現在預設 `provider: openai`、位址與模型留空；**問到 Q-07 第 6、9 題（實際位址、模型）後再改範本**（1125：能共用，學長說那套系統目前沒在用、使用者被指定用同一個端點）（改範本是動 `services/`，照常先問使用者）
- 共用端點時：優先用對方已常駐的模型、不另外要模型（避免把對方的模型換出去）；背景佇列維持一次一件、不調高併發；逾時先照範本（閘道 120、後端 150 秒）實測，不夠兩個一起加大
- Ollama 不提供語音辨識；迭代 34 的辨識端點另計（4.34）

---

[← 回實作規格書](../../implementation-spec.md)　[← 回進度首頁](../../../index.md)
