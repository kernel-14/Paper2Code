froked from https://github.com/going-doer/Paper2Code

# 📄 Paper2Code: 从机器学习科学论文自动生成代码

![PaperCoder 概览](./assets/papercoder_overview.png)

📄 [在 arXiv 上阅读论文](https://arxiv.org/abs/2504.17192)

> 🔧 **本仓库是官方版本的 Windows 优化版本** - 专为 Windows 本地部署和 PowerShell 使用优化

**PaperCoder** 是一个多智能体 LLM 系统，可以将论文转变为代码库。
它遵循三阶段管道：规划、分析和代码生成，每个阶段由专门的智能体处理。
我们的方法在 Paper2Code 和 PaperBench 上都优于强基线，并生成忠实、高质量的实现。

---

## 🗺️ 目录

- [📄 Paper2Code: 从机器学习科学论文自动生成代码](#-paper2code-从机器学习科学论文自动生成代码)
  - [🗺️ 目录](#️-目录)
  - [⚡ 快速开始](#-快速开始)
    - [🎯 Windows PowerShell 原生支持版本](#-windows-powershell-原生支持版本)
    - [使用 OpenAI API](#使用-openai-api)
    - [输出文件夹结构（仅包含重要文件）](#输出文件夹结构仅包含重要文件)
  - [📝 版本说明](#-版本说明)
    - [🔧 Windows 优化版本](#-windows-优化版本)
  - [📦 Paper2Code 基准数据集](#-paper2code-基准数据集)
  - [📊 由 PaperCoder 生成的代码库的模型评估](#-由-papercoder-生成的代码库的模型评估)
    - [🛠️ 环境配置](#️-环境配置)
    - [📝 无参考评估](#-无参考评估)
    - [📝 基于参考的评估](#-基于参考的评估)
    - [📄 输出示例](#-输出示例)

---

## ⚡ 快速开始
- 注意：以下命令运行示例论文 ([Attention Is All You Need](https://arxiv.org/abs/1706.03762))。  

### 🎯 Windows PowerShell 原生支持版本
本版本针对 **Windows 本地部署** 做了优化改进，相比原版本主要改进：

✨ **核心改进：**
- ✅ 原生支持 Windows PowerShell 执行（无需 Git Bash）
- ✅ Python 脚本入口 (`scripts/run.py`) - 替代 Bash 脚本
- ✅ 完整的 UTF-8 编码支持 - 解决 Windows GBK 编码问题
- ✅ `.env` 文件管理 API_KEY 和自定义 API 端点
- ✅ 支持自定义 OpenAI 兼容 API 服务 (base_url 配置)
- ✅ 详细的调试日志输出

📋 **环境配置：**

创建 `.env` 文件在项目根目录：
```
OPENAI_API_KEY=sk-your-api-key
OPENAI_API_BASE=http://your-api.com:3000  # 可选，用于自定义API端点
```

### 使用 OpenAI API
- 💵 使用 o3-mini 的预计成本：$0.50–$0.70

```bash
pip install openai python-dotenv

cd scripts
python run.py
```

**高级用法 (可选参数)：**
```bash
# 自定义 API 端点
python run.py --api-base-url http://your-api.com:3000

# 指定不同的论文和模型
python run.py --paper MyPaper --gpt-version gpt-4o

# 直接提供 API_KEY (不使用 .env)
python run.py --api-key sk-your-key
```


### 输出文件夹结构（仅包含重要文件）
```bash
outputs
├── Transformer
│   ├── analyzing_artifacts
│   ├── coding_artifacts
│   └── planning_artifacts
└── Transformer_repo # 最终输出代码库
```

---

## 📝 版本说明

### 🔧 Windows 优化版本

本仓库是官方 [PaperCoder](https://github.com/going-doer/Paper2Code) 的 **Windows 本地部署优化版本**。

**主要改进：**
- ✅ 原生 PowerShell 支持（无需 Git Bash）
- ✅ `.env` 文件和命令行参数管理 API_KEY
- ✅ 支持自定义 OpenAI 兼容 API 服务
- ✅ 完全 UTF-8 编码支持（修复 Windows GBK 问题）
- ✅ 详细的调试日志输出

**详细对比及使用指南**: 📖 [查看 WINDOWS_OPTIMIZATION.md](WINDOWS_OPTIMIZATION.md)

---

## 📦 Paper2Code 基准数据集
- Huggingface 数据集：[paper2code](https://huggingface.co/datasets/iaminju/paper2code)
  
- 您可以在 [data/paper2code](https://github.com/going-doer/Paper2Code/tree/main/data/paper2code) 中找到 Paper2Code 基准数据集的描述。
- 有关详细信息，请参考 [论文](https://arxiv.org/abs/2504.17192) 中第 4.1 节"Paper2Code 基准"。


---

## 📊 由 PaperCoder 生成的代码库的模型评估

- 我们使用基于模型的方法来评估代码库质量，支持基于参考和无参考两种设置。
  模型评估关键实现组件，分配严重程度级别，并使用 **o3-mini-high** 生成在 8 个样本之间平均的 1-5 的正确性分数。

- 有关详细信息，请参考论文中第 4.3.1 节（*Paper2Code 基准*）。
- **注意：** 以下示例评估示例代码库（**Transformer_repo**）。
  如果您想评估不同的代码库，请修改相关的路径和参数。

### 🛠️ 环境配置
```bash
pip install tiktoken
export OPENAI_API_KEY="<OPENAI_API_KEY>"
```


### 📝 无参考评估
- `target_repo_dir` 是生成的代码库。

```bash
cd codes/
python eval.py \
    --paper_name Transformer \
    --pdf_json_path ../examples/Transformer_cleaned.json \
    --data_dir ../data \
    --output_dir ../outputs/Transformer \
    --target_repo_dir ../outputs/Transformer_repo \
    --eval_result_dir ../results \
    --eval_type ref_free \
    --generated_n 8 \
    --papercoder
```

### 📝 基于参考的评估
- `target_repo_dir` 是生成的代码库。
- `gold_repo_dir` 应指向官方代码库（例如，作者发布的代码）。

```bash
cd codes/
python eval.py \
    --paper_name Transformer \
    --pdf_json_path ../examples/Transformer_cleaned.json \
    --data_dir ../data \
    --output_dir ../outputs/Transformer \
    --target_repo_dir ../outputs/Transformer_repo \
    --gold_repo_dir ../examples/Transformer_gold_repo \
    --eval_result_dir ../results \
    --eval_type ref_based \
    --generated_n 8 \
    --papercoder
```


### 📄 输出示例
```bash
========================================
🌟 Evaluation Summary 🌟
📄 Paper name: Transformer
🧪 Evaluation type: ref_based
📁 Target repo directory: ../outputs/Transformer_repo
📊 Evaluation result:
        📈 Score: 4.5000
        ✅ Valid: 8/8
========================================
🌟 Usage Summary 🌟
[Evaluation] Transformer - ref_based
🛠️ Model: o3-mini
📥 Input tokens: 44318 (Cost: $0.04874980)
📦 Cached input tokens: 0 (Cost: $0.00000000)
📤 Output tokens: 26310 (Cost: $0.11576400)
💵 Current total cost: $0.16451380
🪙 Accumulated total cost so far: $0.16451380
```
