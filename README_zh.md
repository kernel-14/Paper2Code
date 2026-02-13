# 📄 Paper2Code: 从机器学习科学论文自动生成代码

![PaperCoder 概览](./assets/papercoder_overview.png)

📄 [在 arXiv 上阅读论文](https://arxiv.org/abs/2504.17192)

**PaperCoder** 是一个多智能体 LLM 系统，可以将论文转变为代码库。
它遵循三阶段管道：规划、分析和代码生成，每个阶段由专门的智能体处理。
我们的方法在 Paper2Code 和 PaperBench 上都优于强基线，并生成忠实、高质量的实现。

---

## 🗺️ 目录

- [⚡ 快速开始](#-快速开始)
- [📚 详细设置说明](#-详细设置说明)
- [📦 Paper2Code 基准数据集](#-paper2code-基准数据集)
- [📊 由 PaperCoder 生成的代码库的模型评估](#-由-papercoder-生成的代码库的模型评估)

---

## ⚡ 快速开始
- 注意：以下命令运行示例论文 ([Attention Is All You Need](https://arxiv.org/abs/1706.03762))。  

### 使用 OpenAI API
- 💵 使用 o3-mini 的预计成本：$0.50–$0.70

```bash
pip install openai

export OPENAI_API_KEY="<OPENAI_API_KEY>"

cd scripts
bash run.sh
```

### 使用开源模型和 vLLM
- 如果您在安装 vLLM 时遇到任何问题，请参考 [官方 vLLM 仓库](https://github.com/vllm-project/vllm)。
- 默认模型是 `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`。

```bash
pip install vllm

cd scripts
bash run_llm.sh
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

## 📚 详细设置说明

### 🛠️ 环境配置

- 💡 要使用 `o3-mini` 版本，请确保安装了最新的 `openai` 包。
- 📦 只安装您需要的内容：
  - 对于 OpenAI API：`openai`
  - 对于开源模型：`vllm`
      - 如果您在安装 vLLM 时遇到任何问题，请参考 [官方 vLLM 仓库](https://github.com/vllm-project/vllm)。


```bash
pip install openai 
pip install vllm 
```

- 或者，如果您愿意，可以使用 `pip` 安装所有依赖：

```bash
pip install -r requirements.txt
```

### 📄 （可选）将 PDF 转换为 JSON
以下过程描述如何将论文 PDF 转换为 JSON 格式。
如果您有权访问 LaTeX 源代码并计划与 PaperCoder 一起使用，您可以跳过此步骤并跳转到 [🚀 运行 PaperCoder](#-运行-papercoder)。
注意：在我们的实验中，我们将所有论文 PDF 转换为 JSON 格式。

1. 克隆 `s2orc-doc2json` 仓库，将您的 PDF 文件转换为结构化 JSON 格式。
   （有关详细配置，请参考 [官方仓库](https://github.com/allenai/s2orc-doc2json)。）

```bash
git clone https://github.com/allenai/s2orc-doc2json.git
```

2. 运行 PDF 处理服务。

```bash
cd ./s2orc-doc2json/grobid-0.7.3
./gradlew run
```

3. 将您的 PDF 转换为 JSON 格式。

```bash
mkdir -p ./s2orc-doc2json/output_dir/paper_coder
python ./s2orc-doc2json/doc2json/grobid2json/process_pdf.py \
    -i ${PDF_PATH} \
    -t ./s2orc-doc2json/temp_dir/ \
    -o ./s2orc-doc2json/output_dir/paper_coder
```

### 🚀 运行 PaperCoder
- 注意：以下命令运行示例论文 ([Attention Is All You Need](https://arxiv.org/abs/1706.03762))。
  如果您想在自己的论文上运行 PaperCoder，请相应地修改环境变量。

#### 使用 OpenAI API
- 💵 使用 o3-mini 的预计成本：$0.50–$0.70


```bash
# 使用论文的基于 PDF 的 JSON 格式
export OPENAI_API_KEY="<OPENAI_API_KEY>"

cd scripts
bash run.sh
```

```bash
# 使用论文的 LaTeX 源代码
export OPENAI_API_KEY="<OPENAI_API_KEY>"

cd scripts
bash run_latex.sh
```


#### 使用开源模型和 vLLM
- 默认模型是 `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`。

```bash
# 使用论文的基于 PDF 的 JSON 格式
cd scripts
bash run_llm.sh
```

```bash
# 使用论文的 LaTeX 源代码
cd scripts
bash run_latex_llm.sh
```

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
🌟 评估总结 🌟
📄 论文名称：Transformer
🧪 评估类型：ref_based
📁 目标代码库目录：../outputs/Transformer_repo
📊 评估结果：
        📈 分数：4.5000
        ✅ 有效：8/8
========================================
🌟 使用总结 🌟
[评估] Transformer - ref_based
🛠️ 模型：o3-mini
📥 输入令牌：44318（成本：$0.04874980）
📦 缓存输入令牌：0（成本：$0.00000000）
📤 输出令牌：26310（成本：$0.11576400）
💵 当前总成本：$0.16451380
🪙 截至目前累计总成本：$0.16451380
============================================
```
