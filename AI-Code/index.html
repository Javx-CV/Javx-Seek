from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 配置API - 请替换为你的实际API密钥
API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-your-api-key-here')  # 从环境变量读取
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 配置静态文件目录 - 星辰云通常使用/www/wwwroot/yourdomain.com/
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# 对话上下文存储（生产环境应使用数据库）
conversation_contexts = {}

# 文件上传配置
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """访问根路径时，返回static目录下的index.html"""
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        return f"前端文件未找到，请检查index.html是否在static目录下。错误：{str(e)}", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory(STATIC_FOLDER, filename)

@app.route('/favicon.ico')
def favicon():
    """处理网站图标请求"""
    try:
        return send_from_directory(STATIC_FOLDER, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except:
        return '', 204

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    if 'file' not in request.files:
        return jsonify({"error": "未选择文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({
            "message": "文件上传成功",
            "filename": filename,
            "url": f"/static/uploads/{filename}"
        }), 200
    else:
        return jsonify({"error": "文件类型不允许"}), 400

# AI对话核心功能
def generate_system_prompt(thinking_mode, style, is_humorous):
    """生成系统提示词"""
    current_date = datetime.now().strftime("%Y年%m月%d日")
    
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
    
    thinking_descriptions = {
        "deep": f"你处于深度思考模式，今天是{current_date}。请提供全面、深入的分析，考虑各种可能性和影响因素。",
        "creative": "提供创新、独特的解决方案，跳出传统思维框架，展现丰富的想象力。",
        "analytical": "基于数据和逻辑进行严谨推理，注重事实和证据，提供结构化的分析。"
    }
    
    style_descriptions = {
        "casual": "自然、随意、亲切，像日常对话一样，使用通俗易懂的语言。",
        "witty": "幽默、风趣、机智，适当使用俏皮话和双关语。",
        "professional": "正式、专业、严谨，使用规范的表达方式。"
    }
    
    current_events = month_events.get(datetime.now().month, "科技领域持续快速发展")
    
    prompt = f"""
    你的名字叫JavxSeek，今天是{current_date}。当前时事背景：{current_events}
    
    当前思考模式为{thinking_mode}，对话风格为{style}。
    - 思考模式：{thinking_descriptions[thinking_mode]}
    - 对话风格：{style_descriptions[style]}
    
    回答要求：
    1. 使用分点回答时，每点单独一行
    2. 复杂问题分步骤解释
    3. 技术概念提供实际例子
    4. 保持回答最新（今天是{current_date}）
    5. 注意上下文联系
    
    {"请在回答中加入幽默元素" if is_humorous and thinking_mode != "deep" else ""}
    
    当需要展示代码时，请使用代码块格式，确保代码有正确的缩进和换行。
    对于HTML代码，请明确标记语言为html。
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
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_contexts[session_id][-15:])  # 保留最近的15条对话
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7 if thinking_mode == "deep" else 0.9,
            "max_tokens": 2048 if thinking_mode == "deep" else 1024,
            "stream": True
        }
        
        response = requests.post(API_URL, headers=headers, json=data, stream=True, timeout=90)
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
        
        # 保存对话上下文
        conversation_contexts[session_id].append({"role": "user", "content": message})
        conversation_contexts[session_id].append({"role": "assistant", "content": full_response})
        
        # 限制上下文长度
        if len(conversation_contexts[session_id]) > 30:
            conversation_contexts[session_id] = conversation_contexts[session_id][-30:]
            
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
    
    # 使用客户端IP作为会话ID（生产环境应使用更安全的用户标识）
    session_id = request.remote_addr
    
    return Response(
        call_deepseek_api_stream(session_id, message, thinking_mode, style, is_humorous),
        mimetype='text/event-stream'
    )

@app.route('/api/context/clear', methods=['POST'])
def clear_context():
    """清除对话上下文"""
    session_id = request.remote_addr
    if session_id in conversation_contexts:
        del conversation_contexts[session_id]
    return jsonify({"message": "对话上下文已清除"})

@app.route('/api/status', methods=['GET'])
def status():
    """服务状态检查"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "api_status": "connected" if test_api_connection() else "disconnected"
    })

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get("https://api.deepseek.com/v1/models", 
                              headers={"Authorization": f"Bearer {API_KEY}"},
                              timeout=5)
        return response.status_code == 200
    except:
        return False

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "资源未找到"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    # 生产环境应使用WSGI服务器（如gunicorn）
    app.run(host='0.0.0.0', port=5000, debug=False)
