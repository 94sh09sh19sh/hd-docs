# 文件維護作業指示（agent 用）

2026-10-26 起，給 AI agent 的維護規則改成專案 repo 裡的 skill `.claude/skills/hd-docs/`（不上站）：一份每次都讀的核心，加上按任務分開的幾份，只在做那件事時才讀。原因與省下的量見《[文件架構與 token 成本](https://94sh09sh19sh.github.io/hd-docs/1028/weekly/doc-architecture/index.md)》；人用的說明仍是 [HOWTO.md](https://94sh09sh19sh.github.io/hd-docs/1028/weekly/HOWTO/index.md)。

本頁只留舊章節的對照，讓別份文件裡寫的「AGENT.md「某某」」還找得到去處：

| 舊章節                                                                          | 現在在哪（`.claude/skills/hd-docs/` 底下）                                                                                                                         |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 前提、git、其他硬性規則（公開界線、相對連結、README、權杖、底線檔案、既成紀錄） | `SKILL.md`「每次都適用」「收尾順序」                                                                                                                               |
| 其他硬性規則第一條（迭代做完的文件收尾）                                        | `references/iteration-wrapup.md`                                                                                                                                   |
| 改完文件，回頭檢查這兩份指南                                                    | `references/format-and-site.md`「維護指南要不要改」                                                                                                                |
| md 格式                                                                         | `references/format-and-site.md`「md 格式」                                                                                                                         |
| 目錄結構                                                                        | 拿掉；文件清單的真本是 `docs-site/mkdocs.yml` 的 `nav` 與《[其他文件總表](https://94sh09sh19sh.github.io/hd-docs/1028/notes/index.md)》，`npm run docs:check` 比對 |
| 目錄職責                                                                        | `references/new-doc.md`「目錄職責」                                                                                                                                |
| 定版規則、版本歷程的適用範圍、還沒有第一次定版的新文件                          | `references/weekly-and-freeze.md`                                                                                                                                  |
| 週中改文件、週中可以先開週報草稿、新增一篇週報                                  | `references/weekly-and-freeze.md`；首頁的修訂中標記改由 `npm run docs:gen` 產生                                                                                    |
| 新增其他文件、`notes/` 底下的文件、大段條列收進子文件                           | `references/new-doc.md`                                                                                                                                            |
| 測試手冊的分冊（含項次字母）                                                    | `references/testing.md`                                                                                                                                            |
| 部署手冊的分冊                                                                  | `references/deployment.md`                                                                                                                                         |
| 改架構圖、舊站（HackMD）                                                        | `references/format-and-site.md`                                                                                                                                    |
| 首頁硬性上限                                                                    | `references/homepage.md`                                                                                                                                           |
| 驗收                                                                            | `npm run docs:check`；手動排查指令在 `references/format-and-site.md` 文末                                                                                          |

______________________________________________________________________

[← 回進度首頁](https://94sh09sh19sh.github.io/hd-docs/1028/index.md)
