# ReadmeX Writing

中文科技写作与编辑技能：从思路、笔记、链接和亲历材料形成有中心判断、递进叙事与可追溯来源的草稿。**不是ReadmeX官方规范，也不保证未经人工review即可发表。**

## 安装

```bash
git clone https://github.com/fanzhidongyzby/readmex-writing.git ~/.claude/skills/readmex-writing
```

已有同名目录时不要覆盖：先备份或使用现有Git仓库。Claude Code中使用 `/readmex-writing`，提供读者/社区、材料和交付目标。

## 默认与可选能力

- 默认：Markdown草稿；新写、访谈、复盘、编辑、发布前校对。
- 图文可选：可使用PNG/JPEG/WebP与可编辑源，通用检查不强制品牌。EvoMap风格可另安装[evomap-illustrator](https://github.com/fanzhidongyzby/evomap-illustrator)，PNG导出需rsvg-convert。
- 飞书review可选：需要用户自己的lark-cli、相应lark技能、登录及权限。包内没有私人文档、账号或默认知识库节点。
- 图片托管、公众号后台转存与社区发布需另行授权和实际工具；本包不承诺自动发布或账号操作。

Python工具需要Python3.9+，只用标准库。写作本身由所运行的助手完成，CLI不会调用付费模型。

## 本地个人配置

`.local/profile.json`被Git忽略，可设置 `default_output`、`illustration_profile`、`cover_size`、`max_heading_units`、`heading_numbering`、`require_svg_sources`等。当前用户要求高于本地偏好；事实、保密与授权边界不可被偏好覆盖。

私人目录/例稿可留本机，但不进入Git、正文或对外资源包。公共代码与远程同步，个人配置故意不跨用户同步。

## 检查工具

```bash
python3 -I scripts/test_validate_article.py
python3 -I scripts/check_release.py
python3 -I scripts/validate_article.py --article article.md --manifest manifest.json --profile generic --no-local
```

选择EvoMap视觉检查时用 `--profile evomap`。不提供profile可继承本地偏好。manifest支持 `reference_heading`、`required_figure_sections`、`image_profile`及明确的用户格式覆盖。

通用模式允许不带图或外部引用的原创草稿，允许不编号标题、不同来源标题和原图色彩。EvoMap模式保留白底、不透明、颜色比例、短标题、编号、封面及SVG源等约束。

RGB/RGBA8位PNG可实际解码检查；其他PNG、JPEG/WebP只做基础格式和尺寸检查，SVG做安全性检查。工具不会联网证明来源公开性，不判事实、论述质量、视觉布局或平台渲染。不同URL、粗体引言、代码围栏、嵌套括号与工作区资产边界有回归覆盖。

## 示例与评审

[完整输入](examples/insight-input.md)和[完整示例](examples/insight.md)是公开合成案例；[短稿示例](references/examples.md)涵盖不同体裁。它们只示范处理，不是事实来源或固定黄金模板。

[语义评审](evals/RUBRIC.md)列出跨主题及编辑权限场景。确定性测试通过不等于模型eval通过，发布前仍需人工review。

## Git同步与更新

此目录同时是技能安装目录和Git仓库。

```bash
python3 -I scripts/repo_sync.py status
python3 -I scripts/repo_sync.py pull
```

修改前先正常拉取，使用工作分支，运行测试及发布检查后提交。已提交且本地干净时同步：

```bash
python3 -I scripts/repo_sync.py push
```

工具只支持快进拉取与正常推送，不自动提交、强制推送、覆盖分叉或发布内容。`status`会核对本地HEAD与上游提交；手动修改本地代码后，在commit/push前不可能自动与远程一致。

安装推送前检查：`git config core.hooksPath .githooks`。hook只运行本地测试和公开包检查，不访问账号或付费模型。

## 许可与边界

原创代码、规范与示例采用MIT许可。第三方帖子摘录、论文、品牌名称、图片与字体仍保留各自权利，不因本仓库的许可获得再分发授权。不包含原VI、Logo、字体文件、私人稿件或账号配置。
