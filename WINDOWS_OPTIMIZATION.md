# Paper2Code Windows 优化版本

这是官方 [PaperCoder](https://github.com/going-doer/Paper2Code) 的 **Windows 本地部署优化版本**。

## 📊 版本对比

| 功能 | 原始版本 | 本优化版本 |
|------|--------|----------|
| **Windows 支持** | Bash 脚本 (需要 Git Bash) | Python 脚本 (PowerShell 原生支持) |
| **API 密钥管理** | 仅支持环境变量 | `.env` 文件 + 命令行参数 + 环境变量 |
| **自定义 API 端点** | ❌ 不支持 | ✅ 完整支持 (支持兼容 OpenAI 的 API) |
| **编码处理** | ❌ GBK 问题 | ✅ 完全 UTF-8 支持 |
| **Debug 信息** | 基础输出 | ✅ 详细的日志和诊断输出 |
| **跨平台** | Linux/Mac 优先 | Windows + Linux + Mac |

## 🎯 主要改进

### 1. 原生 PowerShell 支持
- **原始**: 需要 Git Bash (`bash run.sh`)
- **改进**: 直接使用 Python 脚本 (`python run.py`)
  ```powershell
  cd scripts
  python run.py
  ```

### 2. 灵活的配置管理
- **`.env` 文件**, 在项目根目录创建:
  ```
  OPENAI_API_KEY=sk-your-key
  OPENAI_API_BASE=http://your-api:3000  # 可选
  ```
- **命令行参数** (优先级最高):
  ```powershell
  python run.py --api-key sk-xxx --api-base-url http://api:3000
  ```
- **环境变量** (最低优先级)

### 3. 自定义 API 服务支持
支持任何 OpenAI 兼容的 API 服务：
```powershell
# 使用自定义 API 端点
python run.py --api-base-url http://172.96.160.199:3000

# 自动处理 URL 格式
# http://api:3000 → http://api:3000/v1
```

### 4. 完全的 UTF-8 编码支持
- **原始**: Windows 下会出现 GBK 编码错误
- **改进**: 所有文件操作都使用 UTF-8 编码
  ```python
  # 修复前
  with open(file, 'w') as f:  # 默认使用 GBK
  
  # 修复后
  with open(file, 'w', encoding='utf-8') as f:
  ```

### 5. 增强的调试输出
```
[INFO] 使用自定义 API 基础 URL: http://172.96.160.199:3000/v1
[DEBUG] 字符串解析失败: ...
[DEBUG] 返回值内容: ...
```

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install openai python-dotenv

# 2. 创建 .env 文件 (在项目根目录)
OPENAI_API_KEY=sk-your-key

# 3. 运行
cd scripts
python run.py
```

**进阶用法:**
```powershell
# 指定自定义 API 端点
python run.py --api-base-url http://api.example.com:3000

# 指定论文和模型
python run.py --paper MyPaper --gpt-version gpt-4o

# 直接提供 API_KEY
python run.py --api-key sk-xxx
```

## 📋 命令行参数

```
python run.py [OPTIONS]

OPTIONS:
  --api-key str              OpenAI API 密钥
  --api-base-url str         API 基础 URL (如: http://api.com:3000)
  --paper str                论文名称 (默认: Transformer)
  --gpt-version str          GPT 模型版本 (默认: o3-mini)
  -h, --help                 显示帮助信息
```

## 🔄 同步官方更新

本版本定期同步官方优化。核心算法完全相同，仅增加 Windows 适配性。

- **官方仓库**: https://github.com/going-doer/Paper2Code
- **论文**: [PaperCoder: Autonomous Program Synthesis for Research Articles](https://arxiv.org/abs/2504.17192)

## 📝 修改日志

### v1.0 (2025-02-14)
- ✅ 添加 Python 脚本入口 (`scripts/run.py`)
- ✅ 支持 `.env` 文件配置
- ✅ 添加自定义 API 端点支持
- ✅ 修复 Windows UTF-8 编码问题
- ✅ 改进所有 OpenAI 客户端初始化
- ✅ 添加详细的调试日志

## ❓ 常见问题

**Q: 能在 Linux/Mac 上使用吗?**
A: 可以。本版本完全兼容所有平台，改进对 Windows 的支持但不影响其他平台。

**Q: 与官方版本有什么区别?**
A: 仅在 Windows 兼容性和配置管理上有改进，核心 PaperCoder 算法完全相同。

**Q: 如何使用自定义 API?**
A: 编辑 `.env` 文件添加 `OPENAI_API_BASE=http://your-api:3000`，或使用命令行参数 `--api-base-url`。

**Q: 出现编码错误怎么办?**
A: 本版本已修复所有编码问题，确保 Python 环境编码正确：
```powershell
python -c "import sys; print(sys.stdout.encoding)"
```
应该输出 `utf-8`。

## 📄 許可证

本项目沿用官方仓库的许可证。详见 [LICENSE](LICENSE)。
