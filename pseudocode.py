# input file : R
# output code file : C

# Planing
def Planning(R):
    # 核心组件与摘要
    Overall_Plan(o) = LLM(R, prompt = "提取核心组件..." )
    # 设计类和函数接口
    Arch_Design(d) = LLM(R, o, prompt = "设计函数..." )
    # 确定逻辑
    Logic_Design(l) = LLM(R, o, d, prompt = "定义执行的顺序..." )
    # 提取超参数与配置
    Config(g) = LLM(R, o, d, prompt="提取超参数...")
    
    # 这里的Plan是一个静态的结构化对象
    P = {o, d, l, g}
    # 从Logic Design中解析出有序的文件列表
    File_List(F) = Parse_File_Order(l)
    return P, F

# Analysis
def Analysis(R, P, F):
    Analysis_Docs(A) = {}
    
    # 按顺序遍历文档列表
    for target_file in F:
        if target_file == "config.yaml":  # 配置文件不需要分析
                continue
        prompt = f"根据原始论文{R}和对应的Plan{P}，构建对于每个{target_file}的详细分析，注意遵循{P.d}规定的数据结构和{P.g}规定的超参数..."
        analysis_content = LLM(prompt, task = "Logic Analysis")
        A[target_file] = analysis_content
    return A

# coding
def Coding(R, P, F, A):
    codebase(C) = {} # 初始化代码库
    Context_History = "" 
    
    for target_file in F:

        # 准备上下文
        current_context = Context_History
        
        # 获取当前文件的analysis
        specific_instruction = A[target_file]
        prompt = f"论文{R},plan{P}，之前的代码{current_context}，当前的任务{target_file}，当前的任务分析{specific_instruction}，生成当前任务的代码，注意使用{P.g}规定的超参数..."
        code_content = LLM(prompt, task="Implementation")
        C[target_file] = code_content
        Context_History += f"\n## File: {target_file}\n{code_content}\n"
            
    return C
		
# Execution Flow
P,F = Planning(R)
A = Analysis(R, P, F)
Final_Code = Coding(R, P, F, A)