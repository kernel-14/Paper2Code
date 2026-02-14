from openai import OpenAI
import json
import os
from tqdm import tqdm
import sys
import copy
from utils import extract_planning, content_to_json, extract_code_from_content, print_response, print_log_cost, load_accumulated_cost, save_accumulated_cost, read_python_files
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--paper_name',type=str)
parser.add_argument('--gpt_version',type=str, default="o3-mini")
parser.add_argument('--paper_format',type=str, default="JSON", choices=["JSON", "LaTeX"])
parser.add_argument('--pdf_json_path', type=str) # json format
parser.add_argument('--pdf_latex_path', type=str) # latex format
parser.add_argument('--output_dir',type=str, default="")
parser.add_argument('--output_repo_dir',type=str, default="")

args    = parser.parse_args()
# 支持自定义 API 基础 URL
client_kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
api_base = os.environ.get("OPENAI_API_BASE")
if api_base:
    # 确保 URL 格式正确，添加 /v1 后缀（如果还没有）
    if not api_base.endswith('/v1'):
        api_base = api_base.rstrip('/') + '/v1'
    client_kwargs["base_url"] = api_base
    print(f"[INFO] 使用自定义 API 基础 URL: {api_base}", file=sys.stderr)
else:
    print(f"[INFO] 使用官方 OpenAI API", file=sys.stderr)

client = OpenAI(**client_kwargs)

paper_name = args.paper_name
gpt_version = args.gpt_version
paper_format = args.paper_format
pdf_json_path = args.pdf_json_path
pdf_latex_path = args.pdf_latex_path
output_dir = args.output_dir
output_repo_dir = args.output_repo_dir

if paper_format == "JSON":
    with open(f'{pdf_json_path}') as f:
        paper_content = json.load(f)
elif paper_format == "LaTeX":
    with open(f'{pdf_latex_path}') as f:
        paper_content = f.read()
else:
    print(f"[ERROR] Invalid paper format. Please select either 'JSON' or 'LaTeX.")
    sys.exit(0)

with open(f'{output_dir}/planning_config.yaml') as f: 
    config_yaml = f.read()

context_lst = extract_planning(f'{output_dir}/planning_trajectories.json')
# 0: overview, 1: detailed, 2: PRD
# file_list = content_to_json(context_lst[1])
task_list = content_to_json(context_lst[2])

todo_file_lst = task_list['Task list']
done_file_lst = ['config.yaml']
done_file_dict = {}

code_msg = [
    {"role": "system", "content": f"""You are an expert researcher and software engineer with a deep understanding of experimental design and reproducibility in scientific research.
You will receive configuration file named "config.yaml", and implmented code repository. 
Your task is to write a Bash script that can run the given repository from scratch. The script should create and activate the required environment, install all dependencies, and include the commands needed to execute the main file or entry point. Make sure the script is self-contained and can be executed without any manual setup.
     
Write code with triple quoto."""}]

def get_write_msg(todo_file_name, done_file_lst): 
    code_files = ""
    for done_file in done_file_lst:
        if done_file.endswith(".yaml"): continue
        code_files += f"""
```python
{done_file_dict[done_file]}
```

"""

    write_msg=[
{'role': 'user', "content": f"""# Context

## Configuration file
```yaml
{config_yaml}
```
-----

## Code Files
{code_files}

-----

# Format example
## Code: {todo_file_name}
```python
## {todo_file_name}
...
```

-----

# Instruction
Based on the code files, follow "Format example", write the code. 

We have {done_file_lst}.
Next, you must write only the "{todo_file_name}".

## Code: {todo_file_name}"""}]
    return write_msg


def api_call(msg):
    if "o3-mini" in gpt_version or "o4-mini" in gpt_version:
        completion = client.chat.completions.create(
            model=gpt_version, 
            reasoning_effort="high",
            messages=msg
        )
    else:
        completion = client.chat.completions.create(
            model=gpt_version, 
            messages=msg
        )
    return completion


def convert_completion_to_json(completion):
    """处理不同API端点返回的响应格式"""
    import sys
    
    # 检查是否已经是dict
    if isinstance(completion, dict):
        return completion
    
    # 检查是否是字符串
    if isinstance(completion, str):
        # 尝试解析JSON
        try:
            return json.loads(completion)
        except json.JSONDecodeError as e:
            print(f"[DEBUG] 字符串解析失败: {e}", file=sys.stderr)
            print(f"[DEBUG] 返回值内容: {completion[:500]}", file=sys.stderr)
            raise
    
    # 检查是否是对象
    try:
        # 尝试调用 model_dump_json()
        if hasattr(completion, 'model_dump_json'):
            return json.loads(completion.model_dump_json())
        # 尝试调用 model_dump()
        elif hasattr(completion, 'model_dump'):
            return completion.model_dump()
        # 尝试调用 dict()
        elif hasattr(completion, '__dict__'):
            return vars(completion)
        else:
            # 最后的尝试：直接转换为JSON字符串
            print(f"[DEBUG] 未知对象类型: {type(completion)}", file=sys.stderr)
            print(f"[DEBUG] 对象内容: {str(completion)[:500]}", file=sys.stderr)
            raise TypeError(f"无法转换类型 {type(completion)} 到 JSON")
    except Exception as e:
        print(f"[DEBUG] 对象转换失败: {e}", file=sys.stderr)
        raise
    

artifact_output_dir=f'{output_dir}/coding_artifacts'
os.makedirs(artifact_output_dir, exist_ok=True)

python_dict = read_python_files(output_repo_dir)

for todo_idx, todo_file_name in enumerate(tqdm(todo_file_lst)):
    if todo_file_name == "config.yaml":
        continue
    
    done_file_dict[todo_file_name] = python_dict[todo_file_name]
    done_file_lst.append(todo_file_name)


total_accumulated_cost = load_accumulated_cost(f"{output_dir}/accumulated_cost.json")
for todo_idx, todo_file_name in enumerate(["reproduce.sh"]):
    responses = []
    trajectories = copy.deepcopy(code_msg)

    current_stage = f"[CODING] {todo_file_name}"
    print(current_stage)

    if todo_file_name == "config.yaml":
        continue

    instruction_msg = get_write_msg(todo_file_name, done_file_lst)
    trajectories.extend(instruction_msg)

    completion = api_call(trajectories)
    # print(completion.choices[0].message)
    
    # response
    completion_json = convert_completion_to_json(completion)
    responses.append(completion_json)

    # trajectories
    message = completion.choices[0].message
    trajectories.append({'role': message.role, 'content': message.content})

    done_file_lst.append(todo_file_name)

    # save
    # save_dir_name = f"{paper_name}_repo"
    os.makedirs(f'{output_repo_dir}', exist_ok=True)
    save_todo_file_name = todo_file_name.replace("/", "_")


    # print and logging
    print_response(completion_json)
    temp_total_accumulated_cost = print_log_cost(completion_json, gpt_version, current_stage, output_dir, total_accumulated_cost)
    total_accumulated_cost = temp_total_accumulated_cost

    # save artifacts
    with open(f'{artifact_output_dir}/{save_todo_file_name}_coding.txt', 'w', encoding='utf-8') as f:
        f.write(completion_json['choices'][0]['message']['content'])


    # extract code save 
    code = extract_code_from_content(message.content)
    if len(code) == 0:
        code = message.content 

    done_file_dict[todo_file_name] = code
    if save_todo_file_name != todo_file_name:
        todo_file_dir = '/'.join(todo_file_name.split("/")[:-1])
        os.makedirs(f"{output_repo_dir}/{todo_file_dir}", exist_ok=True)

    with open(f"{output_repo_dir}/{todo_file_name}", 'w', encoding='utf-8') as f:
        f.write(code)

save_accumulated_cost(f"{output_dir}/accumulated_cost.json", total_accumulated_cost)
