# 图文与远程交付适配

写作内核不要求图床、飞书或指定绘图工具。只有用户选择相应输出时才启用此适配；未知工具先检查实际能力，不猜CLI参数或用户身份。

## 图与论述

先确认主线与每张图支持的论点，图与对应文字相邻。每个主要主题是否需要图由信息关系和用户要求决定；用户明确要求逐小节覆盖时，用manifest列出要求，不为了配额画装饰图。

封面不参与正文图号；正文图按出现顺序使用“图 x：具体描述”。图注解释对象、关系或结果，不把内部素材ID、来源文件名、页码或核验日志复制到正文。

自绘机制图只保留主对象、必要节点/边/状态标签。统计图按真实数据生成，无数据时不画增长曲线。原论文图、截图和照片保留其科学信息与原有色彩，不强制有可编辑SVG，也不宣称它们是自绘图。

## 视觉profile

通用profile检查文件格式、尺寸和SVG安全性，不要求白底、固定比例或特定颜色。

用户选择EvoMap自绘风格时，使用独立安装的evomap-illustrator或明确配置的绘图工具：白底不透明PNG、黑白灰主体、彩色面积小于10%、高对比文字和配对SVG。模板缺首选字体时用系统回退，交付说明实际替代。品牌Logo、VI原文件与字体文件不进入公开包。

## 封面默认规格

所有新制封面默认采用公众号主封面：**2.35:1，1200×511 实际像素**。这个默认不依赖社区、绘图工具、视觉profile或本地个人配置才生效；用户明确要求其他平台或尺寸时，使用其指定值并在manifest的`cover_size`记录。封面可选，不把纯文字稿强制改成图文；正文图按信息关系自行选择尺寸。

先在1200×511画布上重新布局，使用缩略图可读的大字与少量关键图形；正文架构图不能仅缩小后充当封面。逻辑画布乘scale才是最终PNG像素：默认画布配`--scale 1`得到1200×511，配2则得到2400×1022，后者即使比例相同也不满足默认交付尺寸。用户需要高分辨率源时可另存，不替代标准封面。

检查实际PNG/JPEG/WebP文件头的尺寸；有SVG时核对其画布；预览应使用真实宽高和等比显示。更换比例要重新布局，不压扁、放大拉伸或裁掉主要对象。当前尺寸已经符合时保持尺寸，只修复必要构图，不做无意义重采样。

## 资产manifest

```json
{
  "image_profile": "generic",
  "reference_heading": "参考资料",
  "figures": [
    {"title":"封面","section":"cover","path":"images/cover.png"},
    {"number":1,"title":"任务状态","description":"任务状态跨重试保留","section":"1.1","path":"images/state.png","svg":"images/state.svg"}
  ]
}
```

`path`可用历史兼容键`png`；SVG可选，`require_svg_sources`可显式要求。路径必须在manifest工作区内，不允许绝对路径、目录跳转或符号链接逃逸。Markdown图片目标与path一致；需要外链交付时可用`render_url`，但仍提供本地资产用于格式检查。

首项若为封面，`section="cover"`且number省略；其余number按正文图顺序递增。EvoMap profile还要求alt为“图 x：description”、本地文件如`01-任务状态.png/.svg`同名配对。通用profile不强制原始照片或第三方素材改名。

可覆盖：`cover_size`、`max_heading_units`、`heading_numbering`、`require_cover`、`require_subheadings`、`require_introduction`、`require_references`、`required_figure_sections`、`require_svg_sources`。未要求逐节配图时，通用profile不强制所有小节有图；EvoMap默认覆盖主要业务主题。

```bash
python3 -I scripts/validate_article.py --article article.md --manifest manifest.json --profile generic --no-local
python3 -I scripts/validate_article.py --article article.md --manifest manifest.json --profile evomap --no-local
```

省略profile时可继承本地profile；公开测试使用`--no-local`，避免个人配置影响CI。PNG在支持的RGB/RGBA8位格式下做实际解码；其他PNG类型和JPEG/WebP只做基础格式/尺寸检查，不冒称完整像素或视觉校验。SVG禁止脚本、事件处理和外部资源。

## 图片托管与HTML

本地制作不等于允许对外托管。上传前确认服务、素材范围和必要可见性；私有信息派生图也继承保密边界。不擅自关联无关旧聊天、issue或其他成员任务，不把正文一起上传到仅获图片授权的服务。

HTML里使用经匿名预检的HTTPS图片URL，确认HTTP成功、真实图片媒体类型、非空内容及与原图一致。不要把API下载页面、PDF、需要登录的地址或应用令牌当图片src。

签名链接只在有效期内可用。公众号导入后确认微信完成转存，不能把临时链接称作永久图床；刷新应使用已有图片元数据，不重复上传或创建新任务。浏览器预览与复制检查不等于微信后台已经保存或发布。

## 飞书与社区

飞书需用户自己的lark-cli、对应技能、登录和权限。先fetch最新稿；新版本新建，原地更新才改指定文档。XML业务标题自动编号，来源标题不编号。局部修改使用当前块ID与revision；列表包装器可能没有原生ID，应定位实际列表项，不能假定容器可直接更新。

父节点、收件人和发送身份来自当前请求或经当前用户明确要求取用的本地偏好。验证目标与实际parent_node_token，不把作者私人节点写成公共默认。

每次写回后检查受影响内容与未修改资源。人工并发微调出现时以最新稿为准，不能恢复旧快照。发本人review前核实收件人，文档、图片与附件实际结果分别核验；临时草稿只删除已查看且归本任务的目录，保留用户成果。

ReadmeX的Markdown、图片上传和长度限制以当次接口及授权测试为准；正文字符串能容纳Markdown不代表页面一定渲染。飞书review、图片托管、社区发布和群发是不同授权，不自动扩大范围。
