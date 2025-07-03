# -*- coding: utf-8 -*-

import json
import csv
import os
import logging

# --- 配置区域 ---
# 输入的JSON文件名
INPUT_JSON_FILE = '政务系统问答数据集/generated_qa_dataset3.json'
# 输出的CSV文件名
OUTPUT_CSV_FILE = '政务系统问答数据集/qa_dataset3.csv'

def convert_json_to_csv(json_file, csv_file, logger):
    """
    读取JSON文件，并将其内容写入CSV文件。
    """
    try:
        # 打开JSON文件并加载数据
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"成功读取JSON文件: {json_file}，包含 {len(data)} 条记录。")

        # 确保输出目录存在
        output_dir = os.path.dirname(csv_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 打开CSV文件进行写入
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            # 使用csv.writer来写入数据
            writer = csv.writer(f)

            # 写入表头 (Header)
            writer.writerow(['question', 'answer'])

            # 遍历JSON数据中的每一个问答对
            for item in data:
                question = item.get('question', '')
                answer = item.get('answer', '')

                # 特殊处理：如果答案是一个列表，则将其合并成一个字符串
                if isinstance(answer, list):
                    # 使用换行符将列表中的每个句子连接起来
                    answer = '\n'.join(answer)
                
                # 将问答对写入新的一行
                writer.writerow([question, answer])
        
        logger.info(f"成功将数据转换为CSV格式，并保存到文件: {csv_file}")
        return True

    except FileNotFoundError:
        logger.error(f"错误：找不到输入的JSON文件 '{json_file}'。请确认文件名和路径是否正确。")
        return False
    except json.JSONDecodeError:
        logger.error(f"错误：JSON文件 '{json_file}' 格式不正确，无法解析。")
        return False
    except Exception as e:
        logger.error(f"发生未知错误: {e}")
        return False

# --- 主逻辑 ---
if __name__ == '__main__':
    # 设置一个简单的日志记录器，以便在控制台看到输出信息
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger('Converter')
    
    # 执行转换
    convert_json_to_csv(INPUT_JSON_FILE, OUTPUT_CSV_FILE, logger)
