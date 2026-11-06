# Algorithm Reverse Engineer

[English](README.md) | **简体中文**

一个可复用的 Codex Skill：深入追踪算法项目的真实实现，重建独立于编程语言的计算流程，再通过源码证据反向核验。

目标是建立准确的算法基线：解释选定实现实际计算了什么，让相关领域研究人员能够理解，并在证据充分时独立实现行为基本等价的版本。

## 能做什么

接收 Git 远程仓库地址或本地仓库路径，连续完成：

1. **固定分析对象**：记录 commit、本地修改、入口、生效配置、依赖和可访问资源。
2. **追踪工程实现**：沿执行链和数据流深入包装层、动态派发、核心计算及后处理。
3. **重建算法流程**：按计算意义组织表示、公式、阶段与完整伪代码。
4. **反向核验**：将结论映射回源码，寻找反例，在条件允许时执行小型验证。

适用于数值方法、机器学习、计算机视觉、图形学、几何处理、优化、搜索及混合流程，不绑定语言、框架或 Git 托管服务。函数调用图不能代替算法解释。

## 快速使用

入口是 [SKILL.md](SKILL.md)。将它的本地路径和分析请求一起交给 Codex；如果当前环境已能按名称发现该技能，可使用 `$algorithm-reverse-engineer` 调用。

支持以下输入：

| 输入 | 是否必需 |
|---|---|
| Git 远程地址或本地仓库路径 | 必需 |
| 分支、标签或 commit | 可选 |
| 目标算法、模块、入口、命令、配置或使用场景 | 可选 |
| 输出目录 | 可选，建议放在被分析仓库之外 |
| 已有工程分析报告 | 可选，复用前核对证据 |

报告默认使用**中文**，也可明确要求英文。仓库 README 默认展示英文，不改变技能的报告语言。

### 分析远程仓库

```text
$algorithm-reverse-engineer
分析 https://github.com/karpathy/micrograd.git。
范围：demo.ipynb 的训练路径及其实际核心计算。
固定并记录取得的 commit，中文输出到 ../reports/micrograd。
完成工程分析、算法抽象和反向核验；仅使用微型输入验证。
```

### 分析本地工作树

```text
$algorithm-reverse-engineer
分析 ./solver，入口 run.py，配置 configs/demo.json。
保留未提交修改，确认配置覆盖后的实际值。
重建数学描述和完整伪代码，再回查实现。
中文输出到 ../reports/solver。
```

### 基于已有报告继续

```text
$algorithm-reverse-engineer
仓库：./matcher
已有报告：../reports/matcher/01-engineering.md
核对版本、配置和关键证据，复用可靠结论并补查缺口，
继续算法抽象与反向核验，中文输出到 ../reports/matcher-final。
```

## 输出内容

默认生成三份互相引用的 Markdown 报告，使实现证据与可独立阅读的算法说明各有侧重：

| 报告 | 内容 |
|---|---|
| `01-engineering.md` | 来源与版本、范围、配置、执行路径、数据契约、证据索引和未解决问题 |
| `02-algorithm.md` | 问题定义、核心思想、必要流程图、阶段分解、数学描述、完整伪代码、设计决策和最小复现要求 |
| `03-verification.md` | 反向检查、实际测试结果、反例、验证边界和清理状态 |

最后检查两件事：删除仓库特有的类名、函数名和文件名后，说明是否仍具体可理解；从零实现时，是否仍需猜测关键细节。

## 证据与边界

- 区分源码事实、实际运行、文档陈述、分析推断和未解决问题。
- 保留影响结果的机制，包括配置覆盖、精度、顺序、随机性、状态复用、阈值、停止条件和输出映射。
- 区分独立数学检查、抽取原函数、兼容适配模型与完整项目运行。
- 源码、依赖、权重或动态行为不可见时，明确记录缺口；静态一致性不是正确性证明。
- 保留本地修改，分析其他版本时使用隔离副本。默认不开展完整训练、大数据下载、代码重构、算法改进或大规模文献调研。

## 验证经验

已对九个项目中的选定路径进行试用，各例运行覆盖程度不同：

| 案例 | 验证范围 |
|---|---|
| micrograd、FuzzyWuzzy | 小型运行与差分对照，包含配置覆盖和未调用备用实现等误判场景 |
| scikit-image Canny、scikit-learn KMeans | 核心数值和离散输出对照；Canny 保留尚未解决的像素差异 |
| tinyrenderer、PyTorch MNIST 示例 | 渲染流程静态分析及移植检查；MNIST 仍属于部分静态分析 |
| Annotated Transformer | 独立数学检查和抽取的 PyTorch 原定义，包括微型前向与一次优化更新 |
| PointNet | 显式适配 TensorFlow 接口后执行原模块，验证小型训练步与状态变化 |
| Darknet YOLOv3-tiny | 抽取原生 C 运算与配置检查；后续 DLL 重新加载被 Windows 应用控制阻止 |

这些是限定范围的试用，不代表完整还原全部仓库、完成完整训练或证明普遍等价。本地验证报告和测试环境不纳入 Git。

## 仓库结构

```text
SKILL.md             核心流程、证据规则与完成条件
agents/openai.yaml   技能显示元数据
references/          按需加载的参考指令
assets/              三份报告模板
scripts/             可选的确定性证据工具
```

辅助工具只需要 **Python 3.8+ 和 Git**，不依赖机器学习框架；运行目标项目所需的依赖另行确定。

在技能目录下运行，并将输出放在目标仓库之外：

```sh
python scripts/repo_snapshot.py /path/to/repository --output /path/to/reports/snapshot.json
python scripts/check_evidence.py --repo /path/to/repository --evidence /path/to/reports/evidence.json
```

快照工具记录 Git 身份与本地修改；引用工具检查 commit、路径、行号和文件哈希，不能判断代码是否在语义上支持某个结论。格式与限制见 [证据与核验说明](references/verification.md)。
