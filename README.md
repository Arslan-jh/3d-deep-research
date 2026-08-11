# 3D Deep Research

**用可追溯证据链，把开放问题转化为可验证、可交付的深度研究报告。**

3D Deep Research 是一个单一 Skill。它通过来源账本、Claim 账本、反向证据检索、证据门控、三维分析和严格渲染校验，把开放问题转化为结构化的 Markdown、HTML 与 PDF 研究报告。

> 从来源到判断，从时间线到机制层。

## 为什么需要这个 Skill

普通研究流程往往停在“搜索—汇总”。这个 Skill 让判断路径本身可以被检查：

- **来源可追溯**：记录出处类型、证据作用、独立性、日期和限制。
- **Claim 可追溯**：每个承重判断都绑定 Source ID、反向材料、置信度、资料缺口和反证条件。
- **证据门控**：事实、因果、机制、市场判断和未来判断使用不同的最低证据门槛。
- **机制级分析**：把时间路径、关键力场和内部机制连成解释链，而不是平铺摘要。
- **交付可验证**：在交付前检查结构、引用、渲染、PDF 文本和视觉完整性。

## 3D 三轴方法

| 维度 | 要回答的问题 | 典型产物 |
|---|---|---|
| **X——时间线** | 研究对象如何走到今天？ | 4–7 个改变路径的转折点 |
| **Y——关键力场** | 哪些力量推动、限制或改变了路径？ | 2–4 个关键截面 |
| **Z——底层机制** | 关键参与者和系统为什么这样行动？ | 2–5 个机制及替代解释 |

三轴必须交汇为一个新的、可证伪的机制判断。这里的 `3D` 指“时间线 × 力量 × 机制”，不是三维图形、建模、渲染或 CAD Skill。

## 完整流程

```text
研究问题
  → 研究契约
  → 检索地图：事实 / 因果 / 反向证据
  → 来源账本 + Claim 账本
  → 证据门控
  → X/Y/Z 三轴分析与交汇
  → 基准路径、情景矩阵或领先指标
  → 报告装配
  → 严格校验与浏览器/PDF 渲染
  → Markdown / HTML / PDF 交付
```

证据不足时，流程会交付“已确认部分 + 资料缺口 + 下一步验证路径”，不会用听起来合理的内容补齐证据空白。

## 适用场景

- 公司、产品、技术、概念、人物、事件和行业研究。
- 竞品分析、尽职调查、市场与生态研究。
- 技术选型、政策或监管背景研究。
- 历史路径重建和机制级解释。
- 带有不确定性、反向证据和领先指标的决策报告。

## 安装

仓库根目录就是单一 Skill，同时附带示例报告和发布说明。

### Codex

```bash
git clone https://github.com/Arslan-jh/3d-deep-research.git
mkdir -p ~/.codex/skills/3d-deep-research
cp -R 3d-deep-research/. ~/.codex/skills/3d-deep-research/
```

然后使用 `$3d-deep-research`，或直接提出深度研究、证据综合、竞品分析或研究报告请求。

### Windows PowerShell

```powershell
git clone https://github.com/Arslan-jh/3d-deep-research.git
New-Item -ItemType Directory -Force $env:USERPROFILE\.codex\skills\3d-deep-research | Out-Null
Copy-Item -Recurse .\3d-deep-research\* $env:USERPROFILE\.codex\skills\3d-deep-research
```

仓库根目录可以复制到其他 Agent Skills 兼容运行时，但应先确认目标运行时的安装路径。

## 示例

- [工作流示例报告](examples/3d-deep-research-workflow/report.md)
- [HTML 报告](examples/3d-deep-research-workflow/report.html)
- [PDF 报告](examples/3d-deep-research-workflow/report.pdf)

示例请求：

```text
深度研究一家科技公司的竞争位置、发展路径和未来风险。

从时间线、市场力量和底层机制三个维度比较两个产品。

生成一份包含反向证据、资料缺口和领先指标的行业研究报告。
```

## 质量门槛

交付前检查：

1. 只有一个 H1，且六个一级章节按顺序出现。
2. 正文中的 Source ID 都能解析到来源账本。
3. 存在 Claim 证据矩阵。
4. 没有模板占位符或未渲染 Mermaid。
5. HTML/PDF 能成功生成，且 PDF 文本可提取。
6. 视觉产物没有缺字、裁切、重叠或难以阅读的过密区域。

```bash
python scripts/validate_report.py report.md --strict
python scripts/render_report.py report.md output.pdf --engine auto
```

## 仓库结构

```text
3d-deep-research/
├── SKILL.md
├── agents/openai.yaml
├── assets/
├── references/
├── scripts/
├── schema.json
├── README.md
├── LICENSE
├── examples/
```

## 能力边界

这个 Skill 提供研究方法和交付流程，不保证所有来源都正确，不替代领域专家，也不把结构校验等同于外部事实已经被证明。公开信息缺口、冲突证据、访问失败和不确定预测都会在报告中保留。

## License

MIT，见 [LICENSE](LICENSE)。
