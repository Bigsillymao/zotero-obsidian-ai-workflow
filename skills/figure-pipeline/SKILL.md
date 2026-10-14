---
name: figure-pipeline
description: 科研出图与图件归档流水线：数据 → 择优出图（Origin/origin-plot MCP 或 Python 绘图库，按好用与效果选）→ 导出 PNG/PDF/TIF → 三处归档（资料包原位 / 项目目录\图\类型\ / vault 项目\附件\）→ 试验页嵌入 + index/log/git。当用户要求画图、出图、制备论文插图、归档或同步图件时使用。
---

# 出图与归档流水线

## 红线

- **工具择优（2026-10-14 起）**：绘图工具不限——Origin（origin-plot 技能与 MCP：`origin_plot` / `origin_export` / `origin_run_labtalk` / `origin_status` / `origin_doctor` / `origin_quit`，含模板路线）或 **Python 绘图库（matplotlib 等）** 都可以，**以“好用 + 出图质量好”为准**；不得再以“必须 Origin”为由拒绝其他工具
- **三处归档，缺一不可**，且出图当次完成

## 流程

1. **数据准备**：整理成 CSV（首行表头 = 轴标题与图例名，一个表头省掉一堆参数）；来源是 Excel 的数据**核校对原表**（数值红线）
2. **出图**：按选定工具执行——Origin 走 `origin_plot(data_path=..., export_path=...)`；Python 绘图库直接写脚本出图（注意中文字体）。默认三格式导出
   - `.png`（预览与 vault 嵌入）、`.pdf`（矢量，论文插图）、`.tif`（印刷）
3. **核对**：`Read` 导出的 PNG **亲自看图**（老版本 Origin 的 Execute 返回值不可信），不对就修再导
4. **归档三处**（同一文件名，逐处拷贝；各路径取值见 `LOCAL-CONFIG.md`）：
   - ① **项目资料包原位**：`<资料包根>\<项目资料>\01_原始数据\<试验>\`（论文取用与复核的主副本；目录约定可自定）
   - ② **项目目录**：`<项目目录>\<项目名>\图\<类型>\`
     —— 根目录**只放数据文件与文档**，图一律进 `图\`，且按类型分子目录（类型 = 你的试验/分析类别，如按方法、按章节划分）
   - ③ **vault**：`<vault>\项目\<项目名>\附件\`（当次拷入，不是可选项）
   - （表格等非图件交付物：进项目目录根 + vault `附件\`，不进 `图\`）
5. **vault 嵌入**：对应试验子页用 `![[文件名.png]]` 嵌入 + 图注（批次、方法、绘图工具、其他格式位置）；同步 `index.md` 摘要 + `log.md` 追加一行 + git 提交（命令见 vault-ops）
6. **收尾**：若用 Origin，全部导出并核对后调 `origin_quit`（走进程终止；导出文件不受影响，内存项目会丢——务必确认图都已在磁盘）。
   ⚠ **例外**：该图还需要用户手动补样式时**先别关**，等用户改完并导出；若用 Python 绘图库出图则无此步

## 模板路线（样式进阶，推荐）

COM 覆盖不到的外观（逐曲线样式、网格线、图例框等）最稳的做法是**用 Origin 模板定义样式**，而不是每次手调：

1. 从 [OriginLab Graph Gallery](https://www.originlab.com/www/products/GraphGallery.aspx) 检索并下载模板工程
   （可装社区 Skill `origin-template` 自动化：`download_origin_templates.ps1 -SearchTerms "<关键词>" -OutputDir "<模板库>"`；来源示例 [GG-pro-viki/Origin](https://github.com/GG-pro-viki/Origin)——个人学习用途、无开源许可，自用可以，勿转发进公开仓库）
2. 在 Origin 里打开模板 `.opj`/`.opju`，把中意的样式存为模板并套用到你的数据
3. ⚠ **版本兼容**：低编号老模板多为 `.opj`（Origin 2017 可开，已实测成功渲染）；**`.opju` 需 Origin 2018+**
4. ⚠ 脚本化打开工程（LabTalk `doc -o`）时，若当前项目有未保存修改会弹保存确认对话框卡死 COM——自动化打开前先处理未保存项目

## 版本差异（Origin）

- 出图能力以 **origin-plot 技能 + origin MCP** 为准（含安装与排障说明）
- 本流水线的「能/不能脚本化」清单实测于 **Origin 2017（9.4.x）**：
  - 能：数据导入、图型、对数轴、轴范围、刻度、中文轴标题与图例、导出 PNG/TIF/JPG/EPS/EMF/PDF、LabTalk 分析（拟合/积分/统计）
  - 不能（2017）：自动退出、逐曲线颜色/线宽/标记形状、加粗、网格线、图例框与位置；`save` 会弹模态框卡住 COM（要 `.opj` 请用户在 GUI 另存）
- **2021 及更新版本上部分限制可能已解除**——请在你自己版本上用 `origin_status` / `origin_doctor` 实测，不要照搬 2017 的结论
- 未安装 origin-plot MCP 时：可先在 Origin GUI 手工出图，本仓库的「三处归档 + 嵌入」流程照常可用

## 收尾清单

- [ ] 三种格式已导出并 `Read` 核对
- [ ] 三处归档完成（资料包 / 项目目录类型子目录 / vault 附件）
- [ ] vault 试验页嵌入 + 图注
- [ ] index.md / log.md / git 提交
- [ ] `origin_quit`（或按例外保留给用户补样式）
