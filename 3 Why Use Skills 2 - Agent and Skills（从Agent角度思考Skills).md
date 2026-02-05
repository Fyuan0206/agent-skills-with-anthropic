# 3.Why Use Skills 2 - Agent and Skills（从Agent角度思考Skills）

# Agent and Skills - 从Agent角度思考Skills

# 1 Why Agent + Skills?

![alt text](./images/3.1.png)

- 结合过去对 Agents 的理解 | How we used to think about agents
    - 编码 Agent | Coding Agent
    - 研究 Agent | Research Agent
    - 营销 Agent | Marketing Agent
    - 金融 Agent | Finance Agent
    - 通用型 Agent：代码是通用接口 | General-Purpose Agent: Code is the universal interface

# 2 Skills作为Agent的武器

我们可以把Skills作为Agent的武器，从Agent的功能思考Skill的方向

## 2.1 简单脚手架

- **bash**：命令行执行能力
- **filesystem**：文件系统操作能力

## 2.2 稳定可靠所需

要稳定可靠地完成工作，还需要：
- **上下文（Context）**：理解任务背景和环境
- **领域专业知识（Domain Expertise）**：特定领域的专业知识和经验

![alt text](./images/3.2.png)

# 3 从Agent功能思考Skill方向

| Agent类型 | 核心能力 | 对应Skill方向 |
| --- | --- | --- |
| 编码 Agent | 代码理解、生成、调试 | 代码规范、框架文档、调试流程 |
| 研究 Agent | 信息检索、分析、综合 | 搜索策略、资料筛选、论文分析 |
| 营销 Agent | 内容创作、数据分析 | 品牌规范、营销模板、指标分析 |
| 金融 Agent | 数据处理、风险评估 | 财务规则、合规要求、风险模型 |

# 4 总结

Skills 是 Agent 能力的扩展载体。通过将专业知识、工作流程和可重复操作封装为 Skills，Agent 能够：

![alt text](./images/3.3.png)

1. **突破原生限制**：获得代码执行之外的专业能力
2. **保证输出一致性**：通过标准化流程确保结果稳定
3. **提升效率**：避免每次重复描述相同的需求和上下文

从 Agent 的角度思考 Skills，本质上是思考：**Agent需要什么样的”武器”来完成特定任务？**

![alt text](./images/3.4.png)

下一节将会讲一讲我们如何精准的使用Skills。