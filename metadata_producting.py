# -*- coding: utf-8 -*-

import json
import logging
import requests
import docx
from PyPDF2 import PdfReader
import time
import os
import win32com.client as win32
import jwt
import re
import math
import threading
from concurrent.futures import ThreadPoolExecutor
import pythoncom

# --- 1. 用户配置区域 ---

# 使用官方推荐的V3深度思考接口
API_URL = "https://jiutian.10086.cn/largemodel/api/v3/chat/completions"

# !!! 【必须操作】请在这里填写您的API_KEY !!!
API_KEY = "" 

# <--- MODIFIED: 根据您的截图，更新了更完整的文件列表 --->
INPUT_FILES = [
    # '政务系统问答数据集/origin_files/论⽂阅读.docx',
    # '政务系统问答数据集/origin_files/九天大模型应用平台用户使用手册.pdf',
    # '政务系统问答数据集/origin_files/幼儿早期阅读兴趣的激发策略_戴薇.pdf',
    # '政务系统问答数据集/origin_files/幼儿身长与体重标准表.pdf',
    # '政务系统问答数据集/origin_files/幼儿年龄与身高标准数值表.pdf',
    # '政务系统问答数据集/origin_files/婴幼儿营养喂养评估服务指南.docx',
    # '政务系统问答数据集/origin_files/婴儿健康用品资料.doc',
    # '政务系统问答数据集/origin_files/疫苗接种.pdf',
    # '政务系统问答数据集/origin_files/一.docx',
    # '政务系统问答数据集/origin_files/续表.pdf',
    # '政务系统问答数据集/origin_files/健康儿童行动提升计划.docx',
    # '政务系统问答数据集/origin_files/儿童心理.doc',
    # '政务系统问答数据集/origin_files/儿童听力.doc',
    # '政务系统问答数据集/origin_files/儿童视力2.doc',
    # '政务系统问答数据集/origin_files/儿童口腔.doc',
    # '政务系统问答数据集/origin_files/促进幼儿自主性与规则意识协调发展的教育策略_刘易.pdf',
    # '政务系统问答数据集/origin_files/出生缺陷综合防治方案的通知.docx',
    # '政务系统问答数据集/origin_files/1.婴幼儿亲子交流与玩耍咨询指导docx.docx',
    # '政务系统问答数据集/origin_files/8 9 10/10/推动个人养老金发展.docx',
    # '政务系统问答数据集/origin_files/8 9 10/10/人口总量有所下降 人口高质量发展取得成效.docx',
    # '政务系统问答数据集/origin_files/8 9 10/10/国务院办公厅关于加快完善生育支持政策体系推动建设生育友好型社会的若干措施.docx',
    # '政务系统问答数据集/origin_files/8 9 10/10/国务院办公厅关于促进.docx',
    # '政务系统问答数据集/origin_files/8 9 10/10/关于组织申报2024年中央财政支持普惠托育服务发展示范项目的通知.docx',
    # '政务系统问答数据集/origin_files/8 9 10/10/关于进一步完善和落实积极生育支持措施的指导意见.docx',
    # '政务系统问答数据集/origin_files/8 9 10/9/政府工作报告.docx',
    # '政务系统问答数据集/origin_files/8 9 10/9/卫生健康委 发展改革委 中央宣传部 教育部 民政部.docx',
    # '政务系统问答数据集/origin_files/8 9 10/9/国务院办公厅关于全面推进生育保险和.docx',
    # '政务系统问答数据集/origin_files/8 9 10/9/促进3岁以下婴幼儿照护服务发展  .docx',
    # '政务系统问答数据集/origin_files/8 9 10/9/2023年全国医疗保障事业发展统计公报.docx',
    # '政务系统问答数据集/origin_files/8 9 10/9/《关于进一步完善和落实积极生育支持措施的指导意见》解读问答.docx',
    # '政务系统问答数据集/origin_files/8 9 10/8/幼儿园管理条例.docx',
    # '政务系统问答数据集/origin_files/8 9 10/8/山东支持幼儿园为2至3岁幼儿提供更多优质托育服务.docx',
    # '政务系统问答数据集/origin_files/8 9 10/8/去年我国普惠性幼儿园达23.docx',
    # '政务系统问答数据集/origin_files/8 9 10/8/教育部办公厅 国家卫生健康委办公厅 国家疾控局综合司关于切实抓牢幼儿园和小学近视防控关键阶段防控工作的通知.docx',
    # '政务系统问答数据集/origin_files/8 9 10/8/坚决纠正幼儿园.docx'
    # '政务系统问答数据集/origin_files/第二批/公司登记管理实施办法.docx',
    # '政务系统问答数据集\origin_files\第二批\名称登记管理办法.docx',
    # '政务系统问答数据集\origin_files\第二批\企业服务授信额度.docx',
    # '政务系统问答数据集\origin_files\第二批\政务智能体企业服务 问答对.docx',
    # '政务系统问答数据集\origin_files\第二批\政务智能体企业服务 问答对.docx（旷).docx'
    '政务系统问答数据集\origin_files\未转换\1.docx',
    '政务系统问答数据集\origin_files\未转换\2.docx',
    '政务系统问答数据集\origin_files\未转换\3.docx',
    '政务系统问答数据集\origin_files\未转换\4.docx',
    '政务系统问答数据集\origin_files\未转换\5.docx',
    '政务系统问答数据集\origin_files\未转换\6.docx',
    '政务系统问答数据集\origin_files\未转换\7.docx',
    '政务系统问答数据集\origin_files\未转换\8.docx',
    '政务系统问答数据集\origin_files\未转换\9.docx',
    '政务系统问答数据集\origin_files\未转换\10.docx',
    '政务系统问答数据集\origin_files\未转换\企业4.docx',
    '政务系统问答数据集\origin_files\未转换\企业文件.docx',
]
OUTPUT_JSON_FILE = '政务系统问答数据集/generated_qa_dataset3.json'
LOG_FILE = '政务系统问答数据集/generation3.log'

# 每个文本块期望模型一次性生成多少个QA对
QA_PAIRS_PER_CHUNK = 10
# 每个文本块的大小（字符数）
CHUNK_SIZE = 2500
# 重叠大小，以保证上下文连续性
CHUNK_OVERLAP = 200
# 每生成多少个QA对就保存一次文件
SAVE_EVERY_N_PAIRS = 10
# <--- NEW: 新增失败重试配置 --->
MAX_RETRIES = 5 # 1次初次尝试 + 4次重试


# --- 辅助函数 (无需修改) ---

def generate_token(apikey: str, exp_seconds: int):
    """
    根据API Key生成有时效性的JWT Token.
    """
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("无效的API Key格式，请确保格式为 'id.secret'", e)
    payload = {
        "api_key": id,
        "exp": int(round(time.time())) + exp_seconds,
        "timestamp": int(round(time.time())),
    }
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "sign_type": "SIGN"},
    )

def setup_logging():
    """
    配置日志系统，方便追踪和调试.
    """
    logger = logging.getLogger('QAGenerator')
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - Thread %(thread)d - %(message)s')
    
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def chunk_text(text: str, chunk_size: int, chunk_overlap: int):
    """
    将文本按指定大小和重叠进行切分.
    """
    if not text:
        return []
    
    chunks = []
    start_index = 0
    while start_index < len(text):
        end_index = start_index + chunk_size
        chunks.append(text[start_index:end_index])
        
        next_start = start_index + chunk_size - chunk_overlap
        
        if next_start <= start_index:
            start_index += 1
        else:
            start_index = next_start
            
    return chunks

def convert_doc_to_docx(doc_path, logger):
    """
    在后台自动将.doc文件转换为.docx文件.
    """
    try:
        pythoncom.CoInitialize()
        doc_path_abs = os.path.abspath(doc_path)
        word_app = win32.Dispatch("Word.Application")
        word_app.Visible = False
        logger.info(f"正在后台使用Word转换文件: {doc_path_abs}")
        doc = word_app.Documents.Open(doc_path_abs)
        docx_path_abs = doc_path_abs + "x"
        doc.SaveAs(docx_path_abs, FileFormat=16)
        doc.Close()
        word_app.Quit()
        logger.info(f"文件成功转换为: {docx_path_abs}")
        return docx_path_abs
    except Exception as e:
        if 'word_app' in locals():
            word_app.Quit()
        logger.error(f"转换 {doc_path} 时发生错误: {e}")
        return None
    finally:
        pythoncom.CoUninitialize()


def read_doc_file(file_path, logger):
    """
    读取.docx文件的文本内容.
    """
    try:
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        logger.info(f"成功读取Word文件: {file_path}")
        return '\n'.join(full_text)
    except Exception as e:
        logger.error(f"读取Word文件 {file_path} 失败: {e}")
        return ""

def read_pdf_file(file_path, logger):
    """
    读取.pdf文件的文本内容.
    """
    try:
        reader = PdfReader(file_path)
        full_text = [page.extract_text() for page in reader.pages]
        logger.info(f"成功读取PDF文件: {file_path}")
        return '\n'.join(filter(None, full_text))
    except Exception as e:
        logger.error(f"读取PDF文件 {file_path} 失败: {e}")
        return ""

def load_knowledge_chunks(file_path, logger, chunk_size, chunk_overlap):
    """
    加载单个文件并使用重叠策略切分成文本块列表.
    """
    file_path = file_path.replace('\\', '/')
    file_ext = os.path.splitext(file_path)[1].lower()
    content = ""
    if file_ext == '.doc':
        new_docx_path = convert_doc_to_docx(file_path, logger)
        if new_docx_path:
            content = read_doc_file(new_docx_path, logger)
    elif file_ext == '.docx':
        content = read_doc_file(file_path, logger)
    elif file_ext == '.pdf':
        content = read_pdf_file(file_path, logger)
    
    if not content:
        logger.warning(f"文件内容为空或读取失败: {file_path}")
        return []

    all_chunks = chunk_text(content, chunk_size, chunk_overlap)
    
    logger.info(f"文件 {os.path.basename(file_path)} 已被切分成 {len(all_chunks)} 个重叠的文本块。")
    return all_chunks

# --- API调用模块 ---
# <--- MODIFIED: 增加了重试逻辑 --->
def call_llm_api(prompt_chunk, num_pairs, logger):
    """
    调用V3接口，处理单个文本块，并智能提取包含多个QA对的JSON数组.
    失败时会自动重试。
    """
    for attempt in range(MAX_RETRIES):
        try:
            jwt_token = generate_token(API_KEY, 3600)
            headers = {'Content-Type':"application/json", "Authorization":"Bearer " + jwt_token}
            
            system_prompt = (
                f"你是一个专业的AI助手，任务是根据用户提供的“背景知识文档片段”，生成 **{num_pairs}个** 高质量的“问题-回答”(QA)对。"
                "你的回答必须严格遵守以下规则：\n"
                "1. **完全基于背景知识**：所有回答都必须完全源于我提供的“背景知识文档片段”，禁止使用任何外部知识或进行推断。\n"
                "2. **场景化提问**：你需要创造性地模拟真实用户的提问场景，例如一个新手父母、一个办事群众等。\n"
                "3. **手把手式回答**：回答必须非常详细、清晰、分点叙述，就像一步一步教别人怎么做一样。\n"
                "4. **仅针对当前片段提问**：请只根据当前提供的文档片段生成问题，不要涉及片段之外的内容。\n"
                "5. **严格的JSON数组格式输出**：你的最终输出必须是一个包含多个JSON对象的JSON数组，格式为：[{\"question\": \"问题1\", \"answer\": \"答案1\"}, {\"question\": \"问题2\", \"answer\": \"答案2\"}]。\n"
                "6. **识别图表与流程**：如果文本片段中明显描述了一个流程图或引用了一张图片（例如，通过“图1”、“流程如下”等关键词），请为此创建一个独立的问答对。问题可以是“请描述一下[图表/流程]的内容？”，答案则需要根据上下文文字，详细地、分步骤地解释这个图表或流程。\n"
                "**重要：** 你的整个回复中，除了这个JSON数组，绝对不能包含任何其他文字、解释、注释、思考过程或任何形式的额外标记。你的回复必须以`[`开始，并以`]`结束。"
            )
            
            user_prompt = f"--- 背景知识文档片段如下 ---\n{prompt_chunk}"

            payload = {
                "model": "jiutian-think-v3",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }

            response = requests.post(API_URL, json=payload, headers=headers, stream=False, timeout=180)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('choices') and isinstance(result['choices'], list) and len(result['choices']) > 0:
                message = result['choices'][0].get('message')
                if message and 'content' in message:
                    content_str = message['content']
                else:
                    raise KeyError("在 choices[0] 中未找到 'message' 或 'content' 字段。")
            else:
                if 'message' in result:
                    raise Exception(f"API返回错误: code={result.get('code')}, message={result.get('message')}")
                else:
                    raise KeyError("响应JSON中未找到 'choices' 字段或其为空。")
            
            try:
                match = re.search(r'```json\s*([\s\S]*?)\s*```', content_str)
                if match:
                    json_part = match.group(1)
                else:
                    start_index = -1
                    if content_str.find('[') != -1:
                        start_index = content_str.find('[')
                    elif content_str.find('{') != -1:
                        start_index = content_str.find('{')

                    end_index = -1
                    if content_str.rfind(']') != -1:
                        end_index = content_str.rfind(']')
                    elif content_str.rfind('}') != -1:
                        end_index = content_str.rfind('}')

                    if start_index != -1 and end_index != -1 and end_index > start_index:
                        json_part = content_str[start_index:end_index+1]
                    else:
                        raise json.JSONDecodeError("响应中未找到有效的JSON结构。", content_str, 0)

                qa_pairs = json.loads(json_part)
                
                if isinstance(qa_pairs, dict):
                    qa_pairs = [qa_pairs]

                return qa_pairs # 成功，直接返回结果并退出循环

            except json.JSONDecodeError:
                logger.error(f"模型返回的不是有效的JSON格式，或无法从中提取JSON。收到的内容是: '{content_str}'")
                return None # 这种错误通常不可重试，直接返回失败

        except Exception as e:
            logger.warning(f"API调用或解析在第 {attempt + 1}/{MAX_RETRIES} 次尝试时失败: {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** (attempt + 1) # 指数退避: 2, 4, 8, 16 秒
                logger.info(f"将在 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logger.error(f"API调用在所有 {MAX_RETRIES} 次尝试后均失败。")
                if 'response' in locals():
                    logger.error(f"最后一次失败的原始返回内容: {response.text}")
    
    return None # 所有重试都失败后，返回None

def process_file(file_path, all_qa_pairs, lock, logger):
    """
    处理单个文件的完整流程：读取、分块、为每个块生成QA对、保存。
    """
    logger.info(f"========== 开始处理文件: {file_path} ==========")
    
    knowledge_chunks = load_knowledge_chunks(file_path, logger, CHUNK_SIZE, CHUNK_OVERLAP)
    if not knowledge_chunks:
        return

    for i, chunk in enumerate(knowledge_chunks):
        logger.info(f"--- 正在为文件 '{os.path.basename(file_path)}' 的第 {i + 1}/{len(knowledge_chunks)} 个文本块生成QA对 ---")
        
        qa_pairs_list = call_llm_api(chunk, QA_PAIRS_PER_CHUNK, logger)
        
        if qa_pairs_list and isinstance(qa_pairs_list, list):
            valid_pairs = [p for p in qa_pairs_list if isinstance(p, dict) and 'question' in p and 'answer' in p]
            if valid_pairs:
                with lock:
                    len_before = len(all_qa_pairs)
                    all_qa_pairs.extend(valid_pairs)
                    newly_added_count = len(valid_pairs)
                    
                    logger.info(f"成功生成并添加了 {newly_added_count} 个QA对。总数: {len(all_qa_pairs)}")
                    
                    if len(all_qa_pairs) // SAVE_EVERY_N_PAIRS > len_before // SAVE_EVERY_N_PAIRS:
                        try:
                            with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
                                json.dump(all_qa_pairs, f, ensure_ascii=False, indent=4)
                            logger.info(f"进度已保存，当前总计 {len(all_qa_pairs)} 个。")
                        except Exception as e:
                            logger.error(f"保存文件时出错: {e}")
            else:
                logger.warning(f"API返回了列表，但其中不包含有效的QA对。")
        else:
            logger.warning(f"为当前块生成QA对失败或返回格式不正确，跳过。")
            # 这里不再需要sleep，因为call_llm_api内部已经有重试和等待了

# --- 主逻辑 (并行处理) ---
def main():
    logger = setup_logging()
    if "请在这里填写" in API_KEY:
        logger.error("!!! 配置错误: 请在脚本顶部的'用户配置区域'填写您的API_Key。")
        return
    if "." not in API_KEY:
         logger.error("!!! 配置错误: 请确认您的API_KEY格式是否为 'id.secret'。")
         return

    output_dir = os.path.dirname(OUTPUT_JSON_FILE)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    all_qa_pairs = []
    try:
        with open(OUTPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            all_qa_pairs = json.load(f)
        logger.info(f"成功加载了 {len(all_qa_pairs)} 个已有的QA对。")
    except (FileNotFoundError, json.JSONDecodeError):
        logger.info("未找到旧数据集，将从零开始创建。")

    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(process_file, file_path, all_qa_pairs, lock, logger) for file_path in INPUT_FILES]
        
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"一个文件处理线程发生严重错误: {e}")

    # 最终保存一次，确保所有数据都写入
    try:
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_qa_pairs, f, ensure_ascii=False, indent=4)
        logger.info(f"--- 全部文件处理完毕！最终生成了 {len(all_qa_pairs)} 个QA对。---")
    except Exception as e:
        logger.error(f"最终保存文件时出错: {e}")


if __name__ == '__main__':
    main()






























