#!/usr/bin/env python3
"""
Paper2Code 运行脚本 (Windows PowerShell 兼容版本)
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def run_command(cmd, description="", env=None):
    """运行命令并处理错误"""
    if description:
        print(f"\n------- {description} -------")
    
    print(f"执行: {' '.join(cmd)}")
    try:
        # 继承当前环境变量，并合并新的环境变量
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        result = subprocess.run(cmd, check=True, env=cmd_env)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"错误: 命令执行失败 (返回码: {e.returncode})")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


def load_api_key(api_key_arg=None):
    """
    加载API_KEY (优先级: 命令行参数 > .env文件 > 环境变量)
    """
    # 1. 优先使用命令行参数传入的API_KEY
    if api_key_arg:
        print("✓ 使用命令行参数提供的 API_KEY")
        return api_key_arg
    
    # 2. 加载 .env 文件
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        if load_dotenv is None:
            print("⚠ 找到 .env 文件，但 python-dotenv 未安装。")
            print("  请运行: pip install python-dotenv")
        else:
            load_dotenv(env_file)
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                print(f"✓ 从 .env 文件加载 API_KEY: {env_file}")
                return api_key
    
    # 3. 使用环境变量
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print("✓ 使用环境变量中的 API_KEY")
        return api_key
    
    # 都没找到
    print("错误: 找不到 OPENAI_API_KEY")
    print("请通过以下方式之一提供 API_KEY:")
    print("  1. 命令行参数: python run.py --api-key YOUR_KEY")
    print("  2. .env 文件: 在项目根目录创建 .env，内容为 OPENAI_API_KEY=YOUR_KEY")
    print("  3. 环境变量: $env:OPENAI_API_KEY = 'YOUR_KEY'")
    sys.exit(1)


def load_api_base_url(base_url_arg=None):
    """
    加载API基础URL (优先级: 命令行参数 > .env文件 > 官方API)
    """
    # 1. 优先使用命令行参数传入的URL
    if base_url_arg:
        print(f"✓ 使用命令行参数提供的 API 基础 URL: {base_url_arg}")
        return base_url_arg
    
    # 2. 从 .env 文件加载
    base_url = os.environ.get("OPENAI_API_BASE")
    if base_url:
        print(f"✓ 使用 .env 文件中的 API 基础 URL: {base_url}")
        return base_url
    
    # 3. 使用官方 OpenAI API
    return None


def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description="Paper2Code 运行脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py                                    # 从 .env 或环境变量加载 API_KEY
  python run.py --api-key sk-xxx                   # 使用命令行参数提供 API_KEY
  python run.py --api-base-url http://172.96.160.199:3000  # 使用自定义 API 基础 URL
  python run.py --api-key sk-xxx --api-base-url http://172.96.160.199:3000 --paper Transformer
        """
    )
    parser.add_argument("--api-key", type=str, help="OpenAI API 密钥")
    parser.add_argument("--api-base-url", type=str, help="OpenAI API 基础 URL (如: http://172.96.160.199:3000)")
    parser.add_argument("--paper", type=str, default="Transformer", help="论文名称 (默认: Transformer)")
    parser.add_argument("--gpt-version", type=str, default="o3-mini", help="GPT 模型版本 (默认: o3-mini)")
    
    args = parser.parse_args()
    
    # 加载 API_KEY
    api_key = load_api_key(args.api_key)
    os.environ["OPENAI_API_KEY"] = api_key
    
    # 加载 API 基础 URL
    api_base_url = load_api_base_url(args.api_base_url)
    if api_base_url:
        os.environ["OPENAI_API_BASE"] = api_base_url
    
    # 配置变量
    GPT_VERSION = args.gpt_version
    PAPER_NAME = args.paper
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 设置路径
    PDF_PATH = project_root / "examples" / "Transformer.pdf"
    PDF_JSON_PATH = project_root / "examples" / "Transformer.json"
    PDF_JSON_CLEANED_PATH = project_root / "examples" / "Transformer_cleaned.json"
    OUTPUT_DIR = project_root / "outputs" / "Transformer"
    OUTPUT_REPO_DIR = project_root / "outputs" / "Transformer_repo"
    
    # 代码目录
    codes_dir = project_root / "codes"
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPO_DIR.mkdir(parents=True, exist_ok=True)
    
    # 显示配置信息
    print("\n" + "="*50)
    print("Paper2Code 配置信息")
    print("="*50)
    print(f"论文名称: {PAPER_NAME}")
    print(f"GPT 版本: {GPT_VERSION}")
    print(f"JSON 输入: {PDF_JSON_CLEANED_PATH}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"API_KEY: {'已加载' if os.environ.get('OPENAI_API_KEY') else '未设置'}")
    if api_base_url:
        print(f"API 基础 URL: {api_base_url}")
    else:
        print(f"API 基础 URL: 官方 OpenAI API")
    print("="*50)
    
    print(f"\n开始处理: {PAPER_NAME}")
    
    # 准备所有命令需要的环境变量
    cmd_env = {
        "OPENAI_API_KEY": api_key,
    }
    if api_base_url:
        cmd_env["OPENAI_API_BASE"] = api_base_url
    
    # Step 1: Preprocess
    run_command([
        sys.executable,
        str(codes_dir / "0_pdf_process.py"),
        "--input_json_path", str(PDF_JSON_PATH),
        "--output_json_path", str(PDF_JSON_CLEANED_PATH)
    ], "Preprocess", env=cmd_env)
    
    # Step 2: Planning
    run_command([
        sys.executable,
        str(codes_dir / "1_planning.py"),
        "--paper_name", PAPER_NAME,
        "--gpt_version", GPT_VERSION,
        "--pdf_json_path", str(PDF_JSON_CLEANED_PATH),
        "--output_dir", str(OUTPUT_DIR)
    ], "PaperCoder - Planning", env=cmd_env)
    
    # Step 3: Extract Config
    run_command([
        sys.executable,
        str(codes_dir / "1.1_extract_config.py"),
        "--paper_name", PAPER_NAME,
        "--output_dir", str(OUTPUT_DIR)
    ], "PaperCoder - Extract Config", env=cmd_env)
    
    # Step 4: Copy config
    planning_config = OUTPUT_DIR / "planning_config.yaml"
    output_config = OUTPUT_REPO_DIR / "config.yaml"
    if planning_config.exists():
        shutil.copy2(planning_config, output_config)
        print(f"复制配置文件: {planning_config} -> {output_config}")
    else:
        print(f"警告: 配置文件不存在 {planning_config}")
    
    # Step 5: Analyzing
    run_command([
        sys.executable,
        str(codes_dir / "2_analyzing.py"),
        "--paper_name", PAPER_NAME,
        "--gpt_version", GPT_VERSION,
        "--pdf_json_path", str(PDF_JSON_CLEANED_PATH),
        "--output_dir", str(OUTPUT_DIR)
    ], "PaperCoder - Analyzing", env=cmd_env)
    
    # Step 6: Coding
    run_command([
        sys.executable,
        str(codes_dir / "3_coding.py"),
        "--paper_name", PAPER_NAME,
        "--gpt_version", GPT_VERSION,
        "--pdf_json_path", str(PDF_JSON_CLEANED_PATH),
        "--output_dir", str(OUTPUT_DIR),
        "--output_repo_dir", str(OUTPUT_REPO_DIR)
    ], "PaperCoder - Coding", env=cmd_env)
    
    print("\n✓ 所有步骤执行完成！")


if __name__ == "__main__":
    main()
