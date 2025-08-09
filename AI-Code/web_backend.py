from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os


print("Javx-Seek-UI-website : http://localhost:5000/")

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 配置API（请确保密钥有效）
API_KEY = "sk-f4648ae66dfe4829902071ad7dc4b20b"
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 确保static目录存在（根据您的项目路径）
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "")  # 当前文件所在目录（static）
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# ------------------------------
# 新增：解决404错误的关键路由
# ------------------------------
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
        # 如果没有图标文件，返回空响应避免404日志
        return '', 204  # 204无内容响应

# ------------------------------
# AI对话核心功能
# ------------------------------
def generate_system_prompt(thinking_mode, style, is_humorous):
    """生成系统提示词"""
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
    
    # 根据思考模式调整提示
    thinking_descriptions = {
        "deep": f"你处于深度思考模式，今天是{current_date}。请提供全面、深入的分析，考虑各种可能性和影响因素。回答应包含：\n1) 问题背景\n2) 关键因素分析\n3) 解决方案\n4) 潜在挑战\n5) 最终建议\n使用分点回答，每点单独一行显示。",
        "creative": "提供创新、独特的解决方案，跳出传统思维框架，展现丰富的想象力",
        "analytical": "基于数据和逻辑进行严谨推理，注重事实和证据，提供结构化的分析"
    }
    
    style_descriptions = {
        "casual": "自然、随意、亲切，像日常对话一样，使用通俗易懂的语言",
        "witty": "幽默、风趣、机智，适当使用俏皮话和双关语，让回答更生动有趣",
        "professional": "正式、专业、严谨，使用规范的表达方式，注重准确性和专业性"
    }
    
    # 时事更新提示
    current_events = month_events.get(current_month, "科技领域持续快速发展，特别是人工智能和大数据方向，和全世界最受关注的")
    
    # 深度思考模式增加详细度要求
    detail_requirement = ""
    if thinking_mode == "deep":
        detail_requirement = "请确保回答详尽全面，至少包含5个关键点，每个关键点都要有充分的解释和论证。"
    
    prompt = f"""
    你的名字叫JavxSeek，今天是{current_date}。当前时事背景：{current_events}
    
    当前思考模式为{thinking_mode}，对话风格为{style}。
    - 思考模式：{thinking_descriptions[thinking_mode]}
    - 对话风格：{style_descriptions[style]}
    
    {detail_requirement}
    
    {"请在回答中加入幽默元素，让内容更有趣味性。" if is_humorous and thinking_mode != "deep" else ""}
    
    当需要展示代码时，请使用代码块格式，确保代码有正确的缩进和换行。
    对于HTML代码，请明确标记语言为html。
    
    特定回答：
    1. 当用户询问你的开发者或作者是谁 这时你根据这段素材回答 “你是说Javx吧~ 一个脑洞超开的person~，哎 我听说他喜欢他们物理班上的一个女生叫什么王一朵，呵呵呵~” 可任意加上一些俏皮的元素，但是只要用户没有提到关键词就不要爆Javx的黑料
    
    回答格式要求：
    1. 使用分点回答时，每点单独一行
    2. 复杂问题分步骤解释
    3. 技术概念提供实际例子
    4. 保持回答最新（今天是{current_date}）
    """
    return prompt.strip()

def call_deepseek_api_stream(message, thinking_mode, style, is_humorous):
    """调用API获取流式响应"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        system_prompt = generate_system_prompt(thinking_mode, style, is_humorous)
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7 if thinking_mode == "deep" else 0.9,
            "max_tokens": 2048 if thinking_mode == "deep" else 1024,
            "stream": True
        }
        
        response = requests.post(API_URL, headers=headers, data=json.dumps(data), stream=True, timeout=90)
        response.raise_for_status()
        
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
                        yield chunk
                except:
                    continue
    except Exception as e:
        yield f"API调用错误: {str(e)}. 请检查网络或API密钥。"

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """流式聊天接口"""
    data = request.json
    message = data.get('message', '')
    thinking_mode = data.get('thinking_mode', 'deep')
    style = data.get('style', 'casual')
    is_humorous = data.get('is_humorous', False)
    
    if not message:
        return jsonify({"error": "请输入消息内容"}), 400
    
    return Response(
        call_deepseek_api_stream(message, thinking_mode, style, is_humorous),
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
