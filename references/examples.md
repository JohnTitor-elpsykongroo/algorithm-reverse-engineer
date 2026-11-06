# 调用示例

替换路径和可选 ref 即可，不要求填满所有参数。

## 远程仓库

```text
$algorithm-reverse-engineer
分析 https://github.com/karpathy/micrograd.git，范围为 demo.ipynb 训练路径
及其实际核心计算。固定取得的 commit，中文输出到 ./analysis/micrograd。
完成工程分析、算法抽象和反向核验；仅运行微型验证。
```

## 本地仓库

```text
$algorithm-reverse-engineer
分析 D:\Research\solver 当前工作树，入口 run.py，配置 configs/demo.json。
保留未提交修改，记录配置覆盖，输出到 D:\Research\reports\solver。
重建完整算法与伪代码并回查实现；其他独立算法只列清单。
```

## 基于已有工程报告继续

```text
$algorithm-reverse-engineer
仓库 D:\Research\matcher，已有报告 D:\Research\reports\01-engineering.md。
先核对版本、配置和关键证据，复用可靠内容并补查，继续算法抽象与反向核验，
输出到 D:\Research\reports\matcher-final。
```

## 边界判断示例

- 配置把 A 改为 B，README 仍说 A：还原覆盖顺序，当前基线写 B，A 单列文档或未启用路径。
- 同时存在 fast/reference 实现：查分派条件，不能由存在判断执行。
- 名为 normalize 却仅做截断：写真实关系，不能补成单位范数归一化。
- 缺少可选依赖触发后端切换：记录实际语义及未验证分支，不假定等价。
- 只有接口与权重：给已知契约、观察及不可见边界，交付部分结果。
