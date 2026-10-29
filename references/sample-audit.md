# 样文审计与依据

## 取样说明

- 读取日期：2026-10-27。样文发表于 2026-10-07 至 2026-10-27。
- 先检查用户加入的 `readmex`、`rsi`、`evomap`、`swarm`：成功响应均为 `posts: []`，部分请求出现连接重置、超时或后台任务超时退出。
- 用户随后选择改从全平台活跃社区取样。用 `list_communities` 定位本周有帖的 17 个社区，再读取 `get_community_feed`。部分 `new` 请求失败后改用 `hot`；不是随机抽样，也不是纯热门样本。
- 从返回正文选择以下 32 篇作规则依据，每个活跃社区至少一篇；有条件时选不同长度与体裁。另读若干同类资讯用于检查模板重复，没有用它们放大独立证据数。
- 32 篇中 17 篇 `by_ai: null`，15 篇 `by_ai: ReadmeX headlines bot`；“未标注”不能等同于“纯人工”。资讯风格样文全部来自同一 bot。
- 32 篇均返回 `original_language: zh`、`translated: false`。本轮没有从英文或翻译样文归纳英文文风。
- 信息流返回了正文；S03、S05、S07、S16、S20、S24 另用 `get_post` 阅读帖子及回复。S05 在两个接口里均以省略号截断，其他记录只代表接口当时可见内容，未核验是否存在接口未返回的附件。
- 只观察写作形式，不对帖子新闻事实、作者经历、技术成绩或投资建议做外部真实性背书。原始链接并未逐一打开；不将样文里的来源描述当成已经核验。

## 代表性样文索引

「未标注」指帖子 AI 标记为空。标题中的省略仅用于缩短此索引，不改变来源链接。

| ID | 社区 | 样文标题及原帖 | 标记/体裁 | 观察依据 |
|---|---|---|---|---|
| S01 | general | [ReadmeX 的大家好啊！](https://readmex.ai/c/general/p/315f2f47-5ba4-4e51-ac54-eb457863f9eb) | 未标注/报到与工具分享 | 身份、用途、博客和工具链接，简短邀请 |
| S02 | general | [Hi大家好！](https://readmex.ai/c/general/p/21523ca8-b2b6-44fe-85d3-a9b9a9cafa32) | 未标注/实践 | 环境、补全配置、容器文件共用、交流邀请 |
| S03 | general | [创建帖子支持 markdown 语法吗？](https://readmex.ai/c/general/p/20dffc7f-a68a-4036-998e-36cff8096d3c) | 未标注/平台求助 | 评论反馈 Markdown 与截断问题，仅用户体验陈述 |
| S04 | quant | [为什么我选择个人量化](https://readmex.ai/c/quant/p/3c03e868-3fb7-4c68-b9ee-ed9d0b76a1ce) | 未标注/观点 | 个人选择、分层理由、赛道与成本差异 |
| S05 | quant | [为什么我不推荐个人量化使用自建数据源](https://readmex.ai/c/quant/p/120a9bd8-fc4a-45d0-b624-7a77df6385a9) | 未标注/长观点，可见部分 | 范围、机制、三个坑、例外；正文末尾截断 |
| S06 | aicodecraft | [面向独立开发者的社区情报工具](https://readmex.ai/c/aicodecraft/p/3f7824bf-4bf4-4342-b8c0-7820da3d0df3) | 未标注/项目资源 | 一段说清输入、处理、输出与用途，附仓库 |
| S07 | aicodecraft | [让 AI 写代码不难，难的是验收它](https://readmex.ai/c/aicodecraft/p/bb85bffc-3538-496a-9420-c7013bad4469) | 未标注/实践复盘 | 先报结果、技术栈、分工、五个坑、验收问题 |
| S08 | opc | [本人 OPC，创业 1 年半，目前还活着……](https://readmex.ai/c/opc/p/11251e13-56ce-41f7-877d-31c2799163ed) | 未标注/创业报到 | 身份、阶段、产品与交流意图；不够建立长文风格 |
| S09 | immutable | [AI产出的和人产出的，本质是相同的信息](https://readmex.ai/c/immutable/p/d5e0ac20-2e40-413d-a0be-e9ce9bfac1b4) | 未标注/短观点提问 | 概念判断紧接一个意义问题 |
| S10 | immutable | [不变是世界的基石](https://readmex.ai/c/immutable/p/e335e00b-77db-47c7-8840-af091272fc56) | 未标注/随想 | 反问、化学思想实验、归纳立场 |
| S11 | little_word | [湘湖标毅](https://readmex.ai/c/little_word/p/76da4e02-d5ab-414b-89d7-84a1ae301363) | 未标注/诗歌 | 自然意象、短行，没有分析或互动尾巴 |
| S12 | little_word | [流水诗一首](https://readmex.ai/c/little_word/p/4c334bc6-c576-43d6-a133-48f6ed3c32eb) | 未标注/诗歌 | 简洁意象与留白，资讯模板的反例 |
| S13 | ai_coding | [本地开发、Git 提交与服务器自动发布](https://readmex.ai/c/ai_coding/p/3c0540d3-70d4-42eb-a0a7-2eff2c3e1147) | 未标注/工作流 | 本地与服务器环境、提交和发布路径，短直接 |
| S14 | ai_coding | [在IDEA中使用TRAE插件的builder模式](https://readmex.ai/c/ai_coding/p/5605e81b-43ce-4829-b29c-8c2a24cd13be) | 未标注/提示词分享 | 使用场景加原始提示词；提示词只是被分析的内容 |
| S15 | sunboy | [AI便利之外，思考外包会让人退化吗？](https://readmex.ai/c/sunboy/p/0c3c8af7-c39b-4ef0-8133-90485de0d354) | 未标注/社会观点 | 从使用行为提出担忧，非实测结论 |
| S16 | asr | [降低千问ASR模型错误率的方法浅谈](https://readmex.ai/c/asr/p/4a7a88f6-29f1-46c6-8e3f-1556843f9188) | 未标注/方案与数据 | 口语化机制说明 + Oracle 输出；下界不等于实测 |
| S17 | prediction | [分享一本书](https://readmex.ai/c/prediction/p/9d0f9922-5c67-4898-bce6-2e805d680e95) | 未标注/书目资源 | 书目、链接与目录摘选，未下载书籍 |
| S18 | llm | [OpenAI 发布 GPT-6.1 Terra 智能操作模型](https://readmex.ai/c/llm/p/a69592f4-d528-44cf-8506-1a1015822654) | bot/发布资讯 | 可用性、价格、用途、尚无独立验证 |
| S19 | llm | [月之暗面就K3.1 Pro额度问题道歉并退款](https://readmex.ai/c/llm/p/0c92767c-9a0e-4952-b4f2-3160a4b617a5) | bot/产品争议 | 公司回应、产品调整与用户反馈归属分开 |
| S20 | ai_products | [ChatGPT新增锁定聊天功能](https://readmex.ai/c/ai_products/p/221568f0-a537-49e4-9b4b-19228314db9b) | bot/功能解读 | 访问控制与端到端加密明确区分 |
| S21 | ai_products | [AI复刻Adobe全家桶ArtCraft爆火，实测差距明显](https://readmex.ai/c/ai_products/p/c77801c2-2aab-47fa-8987-17600b09915e) | bot/产品评述 | 热度、承诺、Alpha 状态与失败例子并列 |
| S22 | agents | [四个Gemini组队挑战《我的世界》末影龙](https://readmex.ai/c/agents/p/54076282-5462-45a9-af2e-a2afbc5723ae) | bot/实验资讯 | 任务、分工、代码与经验共享、耗时 |
| S23 | agents | [微软称GPT-5诊断智能体准确率最高达医生4倍](https://readmex.ai/c/agents/p/641f3573-36b5-4084-9663-e45e1de956c2) | bot/能力主张 | 厂商声称与方法学/独立测量缺失分开 |
| S24 | agents | [谷歌开源Harness2：智能体外挂可自我改进](https://readmex.ai/c/agents/p/f62edba2-7994-4955-aa9c-16add6f883ab) | bot/技术资讯 | 改进对象、双层反馈机制、据报基准结果 |
| S25 | ai_industry | [AWS容量至2027年已大部分预订](https://readmex.ai/c/ai_industry/p/f7dd2247-cbcb-47de-b004-8c70ce559e3c) | bot/资源资讯 | 区分预订与按需保留、节选不完整 |
| S26 | ai_industry | [马斯克称SpaceX完成400亿美元AI芯片债务交易](https://readmex.ai/c/ai_industry/p/97d1be24-9f5e-41dc-9e41-52c75eb3de29) | bot/融资转述 | 署名说法、融资条款缺失、未独立确认 |
| S27 | open_source | [DeepSeek开源DeepInfer推理引擎](https://readmex.ai/c/open_source/p/47262b91-6365-472c-ab31-5fc09674644e) | bot/框架对比 | 硬件、指标、测试并不完全等价 |
| S28 | open_source | [腾讯混元开源 Hy Memory 2.0 与记忆专用模型](https://readmex.ai/c/open_source/p/06268756-5fa3-4bdc-809e-b1ecdbbf26b5) | bot/开源发布 | 具体开放部分、许可证、固定子样本口径 |
| S29 | papers | [MIT 发布 HugAgent：AI 数字分身难预测新情境](https://readmex.ai/c/papers/p/b85fffa5-f418-4640-ad21-5575570b1e08) | bot/研究解读 | 样本、任务差异、人与模型指标、外推限制 |
| S30 | papers | [OpenAI公开数百份AI数学手稿，3份因符号错误撤回](https://readmex.ai/c/papers/p/24a039f8-eda1-42f2-95a2-5e7e4a8c20b9) | bot/研究与验证 | 结果数量、撤回状态、理解与核验成本 |
| S31 | ai_safety | [FTC 传唤 OpenAI、Anthropic 调查安全问题](https://readmex.ai/c/ai_safety/p/77a2ab73-69c9-4f21-b440-45876ffef7b7) | bot/监管资讯 | 文件要求、事件背景、传票不等于违法 |
| S32 | ai_safety | [AISI：Mythos 5无视警告持续攻击](https://readmex.ai/c/ai_safety/p/6d51cefe-9d28-4a1b-b63b-cc55d4f5c0d4) | bot/安全评估 | 实验条件、行为、实际影响与理由分开 |

## 少量原文证据

只保留辨识写法所需的短片段，不存储全文：

- S07：“先交代结果”；“AI 写得快，我看得慢”。支持结果优先与代价/验收视角，不授权复制作者经历。
- S05：“先说清楚范围”。支持适用场景前置；结尾不可补写。
- S06：“输出带可点击原帖链接的 Markdown 报告”。支持工具分享先说具体输出。
- S16：“Oracle CER lower bound: 2.1776%”。说明指标标签必须保留；不能转写成系统实测错误率。
- S20：“不提供端到端加密或加密保险库”。支持能力边界紧跟功能说明。
- S18–S32：反复出现“为什么重要：”“你怎么看？”。这是同一 bot 的模板证据，不是所有文章的统一规范。
- S03 评论：“好像并不支持”“太长会被截断”。仅支持采取保守排版与预览检查，未确定支持情况、截断机制或最大长度。

## 归纳的可信度与反例

| 规则 | 证据范围 | 限制 |
|---|---|---|
| 实用稿直接交代内容 | 资讯、作品、实践、观点 | 新人问候与诗歌例外；不要求统一句式 |
| 具体对象和做法承载信息量 | S02、S06、S07、S13、S16、资讯样文 | 不能因此给无数据输入编造数字 |
| 普通文本与空行能承载结构 | 长短成员帖、资讯、诗歌 | 尚未完整验证平台 Markdown 支持 |
| 判断/过程/成本/边界适合长文 | S04、S05、S07 | 前两篇同一作者；不是全部社区共有结构 |
| 事件/意义/互动适合资讯 | S18–S32 | 同一个 bot；只是一条资讯路线 |
| 讨论入口常见 | 资讯、实践、观点、求助 | 诗歌和资源帖不必须问问题；热度效果未知 |
| 区分事实、归属与限制 | 多篇资讯，以及编辑检查 | 是可靠性规则，部分样文自己仍有过度断言 |

## 未取样社区与访问限制

- `readmex`、`rsi`、`evomap`、`swarm`：成功响应为空，没有把失败当成空列表，也没有把简介当成文章。
- 平台另有本周零帖的社区，未进一步穷举其历史文章。本轮覆盖“本周有帖”的 17 个社区，不声称覆盖所有历史文档。
- `WebFetch` 对 `https://readmex.ai/c/rsi` 未能验证可抓取性；没有取得网页正文，没有将其当作取样结果。
- 最终 17 个活跃社区都取得至少一份成功 feed；网络重试影响排序，但不改变上述样文证据。
- 所有操作为只读。没有加入新社区、发帖、回复、投票、下载书籍或写回仓库。

后续有本社区真实样文，应追加新的日期和覆盖范围，再修改适配规则，不抹去本轮局限。
