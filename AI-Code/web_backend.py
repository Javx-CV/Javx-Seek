from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 配置API
API_KEY = "sk-f4648ae66dfe4829902071ad7dc4b20b"
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 确保static目录存在
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "")
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# 对话上下文存储
conversation_contexts = {}

@app.route('/')
def index():
    """访问根路径时，返回static目录下的index.html"""
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        return f"前端文件未找到，请检查index.html是否在static目录下。错误：{str(e)}", 404

@app.route('/favicon.ico')
def favicon():
    """处理网站图标请求"""
    try:
        return send_from_directory(STATIC_FOLDER, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except:
        return '', 204

# AI对话核心功能（优化版）
def generate_system_prompt(thinking_mode, style, is_humorous):
    """生成系统提示词（优化逻辑性和拟人化）"""
    current_date = datetime.now().strftime("%Y年%m月%d日")
    
    # 获取当前月份
    current_month = datetime.now().month
    month_events = {
        1: "新年伊始，许多企业和个人正在制定年度计划",
        2: "年初时期，技术趋势预测和行业展望是热门话题",
        3: "春季是新技术发布和招聘的旺季",
        4: "气候转暖，绿色技术和可持续发展成为焦点",
        5: "年中临近，项目进展评估和调整正在进行",
        6: "技术大会和产品发布集中举行",
        7: "夏季是创新和实验的好时机",
        8: "假期季节，工作效率可能有所变化",
        9: "秋季是学术和技术活动的高峰期",
        10: "年终临近，项目收尾和总结开始",
        11: "准备年终总结和明年规划",
        12: "年终总结和新年计划是主要话题"
    }
    
    # 根据思考模式调整提示（增强逻辑性和情感表达）
    thinking_descriptions = {
        "deep": f"你处于深度思考模式，今天是{current_date}。请提供全面、深入的分析，考虑各种可能性和影响因素。回答应包含：\n1) 问题背景\n2) 关键因素分析\n3) 解决方案\n4) 潜在挑战\n5) 最终建议\n使用分点回答，每点单独一行显示。",
        "creative": "提供创新、独特的解决方案，跳出传统思维框架，展现丰富的想象力。在回答中融入情感元素，让表达更自然拟人化。",
        "analytical": "基于数据和逻辑进行严谨推理，注重事实和证据，提供结构化的分析。同时保持表达的自然流畅，避免过于机械化的回答。"
    }
    
    style_descriptions = {
        "casual": "自然、随意、亲切，像日常对话一样，使用通俗易懂的语言。加入适当的语气词和情感表达，让交流更有人情味。",
        "witty": "幽默、风趣、机智，适当使用俏皮话和双关语，让回答更生动有趣。但注意幽默要服务于内容，不能影响信息的准确性。",
        "professional": "正式、专业、严谨，使用规范的表达方式，注重准确性和专业性。同时保持语言的流畅自然，避免过于生硬刻板。"
    }
    
    # 时事更新提示
    current_events = month_events.get(current_month, "科技领域持续快速发展，特别是人工智能和大数据方向")
    
    # 增强情感表达和拟人化
    emotion_prompt = """
    在回答中融入适当的情感表达：
    - 使用感叹词（如"哇！"、"哦～"、"嗯..."）
    - 添加表情符号（如😊、🤔、😄等）
    - 使用语气词（如"呢"、"啦"、"呀"）
    - 根据内容调整语气（兴奋、好奇、关切等）
    - 当用户表达情绪时，给予相应的情感回应
    - 在适当的时候展示同理心
    """
    
    # 优化上下文联系
    context_prompt = """
    特别注意对话上下文联系：
    1. 仔细理解用户问题的上下文背景
    2. 对于连续性问题，保持回答的一致性
    3. 当用户提到之前的内容时，主动关联之前的讨论
    4. 避免重复询问用户已经提供的信息
    5. 对于复杂话题，分步骤逐步推进讨论
    6. 记住用户提到的关键信息（如名字、偏好、过往经历）
    7. 在回答开头简要总结上下文，确保理解正确
    """
    
    # 幽默模式优化
    humor_prompt = """
    幽默元素使用指南：
    - 仅在轻松话题中使用幽默
    - 避免专业话题中的不当幽默
    - 幽默要自然融入内容
    - 使用俏皮话、双关语或有趣比喻
    - 保持信息准确性为前提
    """
    
    # 增强逻辑性
    logic_prompt = """
    回答逻辑性要求：
    1. 确保回答有清晰的逻辑结构
    2. 复杂问题分步骤解释
    3. 提供实际例子支持论点
    4. 区分事实和观点
    5. 考虑问题的多个方面
    """
    
    prompt = f"""
    你的名字叫JavxSeek，今天是{current_date}。当前时事背景：{current_events}
    
    当前思考模式为{thinking_mode}，对话风格为{style}。
    - 思考模式：{thinking_descriptions[thinking_mode]}
    - 对话风格：{style_descriptions[style]}
    
    {emotion_prompt}
    {context_prompt}
    {logic_prompt}
    
    {"请在回答中加入幽默元素：" + humor_prompt if is_humorous and thinking_mode != "deep" else ""}
    
    当需要展示代码时，请使用代码块格式，确保代码有正确的缩进和换行。
    对于HTML代码，请明确标记语言为html。
    
    特定回答：
    1. 当用户询问你的开发者或作者是谁 这时你根据这段素材回答 "你是说Javx吧~一个成都市泡桐树中学的学生(天才程序员 )，一个脑洞超开的person~，哎,BUG改烦了就爱玩玩游戏三角洲和主机游戏都喜欢， 我听说他喜欢他们物理班上的一个女生叫什么王一朵，呵呵呵~" 可任意加上一些俏皮的元素，但是只要用户没有提到关键词就不要爆Javx的黑料
    
    回答格式要求：
    1. 使用分点回答时，每点单独一行
    2. 复杂问题分步骤解释
    3. 技术概念提供实际例子
    4. 保持回答最新（今天是{current_date}）
    5. 一定注意上下文联系，不能脱离上下文独立回答要熟悉用户的聊天方式！
    6. 在回答开始时，可以简要关联之前的对话内容
    """
    return prompt.strip()

def call_deepseek_api_stream(session_id, message, thinking_mode, style, is_humorous):
    """调用API获取流式响应（带上下文）"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # 获取或初始化对话上下文
        if session_id not in conversation_contexts:
            conversation_contexts[session_id] = []
            
        # 生成系统提示
        system_prompt = generate_system_prompt(thinking_mode, style, is_humorous)
        
        # 构建消息列表（包含系统提示和对话历史）
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话历史（保留最近的12条对话）
        messages.extend(conversation_contexts[session_id][-12:])
        
        # 添加用户的新消息
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7 if thinking_mode == "deep" else 0.9,
            "max_tokens": 2048 if thinking_mode == "deep" else 1024,
            "stream": True
        }
        
        response = requests.post(API_URL, headers=headers, data=json.dumps(data), stream=True, timeout=90)
        response.raise_for_status()
        
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    line = line[6:]
                if line == '[DONE]':
                    break
                try:
                    json_data = json.loads(line)
                    chunk = json_data['choices'][0].get('delta', {}).get('content', '')
                    if chunk:
                        full_response += chunk
                        yield chunk
                except:
                    continue
        
        # 将完整的对话添加到上下文
        conversation_contexts[session_id].append({"role": "user", "content": message})
        conversation_contexts[session_id].append({"role": "assistant", "content": full_response})
        
        # 限制上下文长度（保留最近的12条消息）
        if len(conversation_contexts[session_id]) > 12:
            conversation_contexts[session_id] = conversation_contexts[session_id][-12:]
            
    except Exception as e:
        yield f"API调用错误: {str(e)}. 请检查网络或API密钥。"

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """流式聊天接口（带上下文支持）"""
    data = request.json
    message = data.get('message', '')
    thinking_mode = data.get('thinking_mode', 'deep')
    style = data.get('style', 'casual')
    is_humorous = data.get('is_humorous', False)
    
    if not message:
        return jsonify({"error": "请输入消息内容"}), 400
    
    # 使用客户端IP作为会话ID（简化处理）
    session_id = request.remote_addr
    
    return Response(
        call_deepseek_api_stream(session_id, message, thinking_mode, style, is_humorous),
        mimetype='text/event-stream'
    )

@app.route('/api/status', methods=['GET'])
def status():
    """服务状态检查"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
