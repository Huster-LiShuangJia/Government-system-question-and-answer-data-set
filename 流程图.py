# -*- coding: utf-8 -*-

import os
from graphviz import Digraph

# --- 配置区域 ---
OUTPUT_FILENAME = '政务系统问答数据集\pipeline_flowchart'
OUTPUT_FORMAT = 'png'
# 确保Graphviz的可执行文件路径在系统环境变量中，或者在这里手动指定
# 例如: os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

def create_flowchart():
    """
    使用Graphviz库创建数据处理与生成流程图。
    """
    # 创建一个有向图 (Digraph)
    # graph_attr 设置全局图表属性，如字体
    # node_attr 设置全局节点默认属性
    # edge_attr 设置全局边（箭头）默认属性
    dot = Digraph('DataProcessingPipeline', comment='自动化QA数据集生成管道')
    dot.attr(rankdir='TD', splines='ortho', nodesep='0.8', ranksep='1.2')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Microsoft YaHei', fontsize='12')
    dot.attr('edge', fontname='Microsoft YaHei', fontsize='10')

    # --- 1. 定义不同模块的样式 ---
    style_input = {'fillcolor': '#fff1f2', 'color': '#ff8fab'}
    style_preprocess = {'fillcolor': '#fefce8', 'color': '#facc15'}
    style_parallel = {'fillcolor': '#eff6ff', 'color': '#60a5fa'}
    style_api = {'fillcolor': '#f0fdf4', 'color': '#4ade80'}
    style_output = {'fillcolor': '#f5f3ff', 'color': '#a78bfa'}
    style_final = {'fillcolor': '#ecfdf5', 'color': '#34d399', 'shape': 'cylinder'} # 最终产物用圆柱表示

    # --- 2. 创建各个子图（模块） ---

    # 数据输入模块
    with dot.subgraph(name='cluster_input') as c:
        c.attr(label='数据输入 (Data Input)', style='filled', color='#f8fafc', fontname='Microsoft YaHei Bold')
        c.node('pdf', '.pdf 文件', **style_input)
        c.node('word', '.doc / .docx 文件', **style_input)

    # 预处理与分块模块
    with dot.subgraph(name='cluster_preprocess') as c:
        c.attr(label='预处理与分块 (Preprocessing & Chunking)', style='filled', color='#f8fafc', fontname='Microsoft YaHei Bold')
        c.node('read', '文件读取模块\n(含.doc自动转换)', **style_preprocess)
        c.node('chunk', '智能文本分块\n(Overlapping Chunking)', **style_preprocess)
        c.node('chunks', '文本块列表\n[块1, 块2, ...]', shape='note', **style_preprocess)

    # 并行处理模块
    with dot.subgraph(name='cluster_parallel') as c:
        c.attr(label='并行处理 (Parallel Processing)', style='filled', color='#f8fafc', fontname='Microsoft YaHei Bold')
        c.node('pool', '线程池\n(最多32个并发线程)', shape='component', **style_parallel)
        c.node('task1', '文件1处理任务', **style_parallel)
        c.node('task2', '文件2处理任务', **style_parallel)
        c.node('task_n', '... 其他文件任务', **style_parallel)

    # 单任务处理流程模块
    with dot.subgraph(name='cluster_api') as c:
        c.attr(label='单任务处理流程 (API Interaction per Task)', style='filled', color='#f8fafc', fontname='Microsoft YaHei Bold')
        c.node('jwt', '1. 生成JWT动态令牌', **style_api)
        c.node('prompt', '2. 构建复杂Prompt指令', **style_api)
        c.node('call_api', '3. 调用九天V3 API', **style_api)
        c.node('retry', '失败自动重试\n(指数退避策略)', shape='diamond', **style_api)
        c.node('response', 'API原始响应\n(含思考过程)', shape='note', **style_api)
        c.node('extract', '4. 智能JSON提取', **style_api)
        c.node('qa_list', 'QA对列表 (JSON数组)', shape='note', **style_api)

    # 结果聚合与输出模块
    with dot.subgraph(name='cluster_output') as c:
        c.attr(label='结果聚合与输出 (Result Aggregation & Output)', style='filled', color='#f8fafc', fontname='Microsoft YaHei Bold')
        c.node('lock', '线程锁\n(确保写入安全)', shape='Mdiamond', **style_output)
        c.node('global_list', '全局QA列表 (内存中)', **style_output)
        c.node('save', '定时/批量保存', **style_output)
        c.node('json_out', 'generated_qa_dataset.json', **style_final)
        c.node('csv_script', 'CSV转换脚本', **style_output)
        c.node('csv_out', 'qa_dataset.csv', **style_final)

    # --- 3. 定义节点之间的连接关系 ---
    dot.edge('pdf', 'read')
    dot.edge('word', 'read')
    dot.edge('read', 'chunk')
    dot.edge('chunk', 'chunks')
    dot.edge('chunks', 'pool')
    
    dot.edge('pool', 'task1')
    dot.edge('pool', 'task2')
    dot.edge('pool', 'task_n')

    # 使用不可见的节点来辅助布局
    dot.node('dummy', style='invis', width='0', height='0')
    dot.edge('task1', 'dummy', style='invis')
    dot.edge('task2', 'dummy', style='invis')
    dot.edge('task_n', 'dummy', style='invis')
    dot.edge('dummy', 'jwt', style='invis')
    
    dot.edge('jwt', 'prompt')
    dot.edge('prompt', 'call_api')
    dot.edge('call_api', 'retry', label='超时/网络错误')
    dot.edge('retry', 'call_api', label='重试')
    dot.edge('call_api', 'response', label='成功')
    dot.edge('response', 'extract')
    dot.edge('extract', 'qa_list')
    
    dot.edge('qa_list', 'lock')
    dot.edge('lock', 'global_list')
    dot.edge('global_list', 'save')
    dot.edge('save', 'json_out')
    dot.edge('json_out', 'csv_script')
    dot.edge('csv_script', 'csv_out')

    # --- 4. 渲染并保存图表 ---
    try:
        # render方法会自动调用Graphviz程序来生成图片
        dot.render(OUTPUT_FILENAME, format=OUTPUT_FORMAT, cleanup=True, view=False)
        print(f"流程图已成功生成: {OUTPUT_FILENAME}.{OUTPUT_FORMAT}")
    except Exception as e:
        print(f"生成流程图失败: {e}")
        print("请确保您已正确安装Graphviz软件，并将其bin目录添加到了系统PATH环境变量中。")

if __name__ == '__main__':
    create_flowchart()
