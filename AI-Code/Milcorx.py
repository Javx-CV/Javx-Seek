import httpx
import asyncio
import json
import random
import os
import time
from colorama import init, Fore, Style
from datetime import datetime
from typing import AsyncGenerator, List, Dict, Tuple


# ==================== 核心配置 ====================
class Config:
    """应用程序核心配置 - 优化打字机速度，提升流畅度"""
    # 初始化colorama
    init(autoreset=True, convert=True)
    
    # 配色方案
    COLORS = {
        "user": Fore.LIGHTBLUE_EX,
        "ai": Fore.LIGHTGREEN_EX,
        "title": Fore.CYAN,
        "accent": Fore.MAGENTA,
        "warning": Fore.YELLOW,
        "info": Fore.LIGHTCYAN_EX,
        "border": "─",
        "time": Fore.LIGHTBLACK_EX,
        "success": Fore.GREEN,
        "error": Fore.RED
    }
    
    # 布局配置
    MAX_WIDTH = 80
    MARGIN = 2
    
    # 优化后的打字机速度配置（提升流畅度）
    TYPING_SPEED = {
        "normal": 0.015,       # 加快基础打字速度
        "chinese": 0.02,       # 加快中文字符速度
        "punct_short": 0.05,   # 缩短短标点停顿
        "punct_long": 0.1,     # 缩短长标点停顿
        "paragraph": 0.3       # 缩短段落停顿
    }
    
    # 存储配置
    MEMORY_FILE = "javxseek_memory.json"
    
    # API配置
    API_SERVERS = [
        {"url": "https://api.deepseek.com/v1/chat/completions",
         "name": "Deepseek服务器",
         "models": ["deepseek-chat", "deepseek-vl", "deepseek-math"]
        }
    ]
    DEEPSEEK_API_KEY = "sk-f4648ae66dfe4829902071ad7dc4b20b"
    
    # 回复风格配置
    STYLES = {
        "casual": {"desc": "轻松随意的风格", "label": "😜 轻松风格"},
        "sarcastic": {"desc": "带点讽刺的风格", "label": "😏 俏皮风格"},
        "witty": {"desc": "机智风趣的风格", "label": "🤓 机智风格"},
        "absurd": {"desc": "脑洞大开的风格", "label": "🤪 创意风格"},
        "deadpan": {"desc": "一本正经的风格", "label": "😐 正式风格"}
    }


# ==================== UI组件 ====================
class UI:
    """UI组件 - 精简设计，专注流畅输出"""
    
    @staticmethod
    def print_logo():
        """打印简洁Logo"""
        os.system('cls' if os.name == 'nt' else 'clear')
        border = Config.COLORS['title'] + Config.COLORS['border'] * Config.MAX_WIDTH
        print(border)
        print(f"{Config.COLORS['title']}{'Javx Seek'.center(Config.MAX_WIDTH)}")
        print(border + "\n")
    
    @staticmethod
    def split_text(text: str, max_length: int) -> List[str]:
        """优化文本分割，完美处理换行和中英文"""
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append("")
                continue
                
            current_line = ""
            current_width = 0
            for char in paragraph:
                # 计算字符宽度（中文2，英文1）
                char_width = 2 if '\u4e00' <= char <= '\u9fff' else 1
                
                # 如果当前行宽度+新字符宽度超过限制，则换行
                if current_width + char_width > max_length and current_line:
                    lines.append(current_line)
                    current_line = char
                    current_width = char_width
                else:
                    current_line += char
                    current_width += char_width
            
            if current_line:
                lines.append(current_line)
        return lines
    
    @staticmethod
    def print_message_header(role: str, time_str: str):
        """打印精简的消息头部"""
        if role == "user":
            color = Config.COLORS["user"]
            prefix = "你"
            symbol = "→"
        else:
            color = Config.COLORS["ai"]
            prefix = "Javx Seek"
            symbol = "←"
        
        # 打印头部信息
        header = f"{Config.COLORS['time']}[{time_str}] {color}{prefix} {symbol}"
        print(f"\n{header}")
        print(f"{color}{Config.COLORS['border'] * len(header)}")
        return color
    
    @staticmethod
    def print_message_footer(color: str):
        """打印消息底部"""
        print(f"{color}{Config.COLORS['border'] * Config.MAX_WIDTH}{Style.RESET_ALL}")
    
    @staticmethod
    def start_typing_effect(color: str) -> Tuple[List[str], int]:
        """开始打字机效果，返回状态信息"""
        return [""], 0  # (lines, current_line_index)
    
    @staticmethod
    def stream_print(char: str, color: str, state: Tuple[List[str], int]) -> Tuple[List[str], int]:
        """流式打印单个字符，优化流畅度"""
        lines, current_line_idx = state
        current_line = lines[current_line_idx]
        
        # 计算当前行宽度
        line_width = sum(2 if '\u4e00' <= c <= '\u9fff' else 1 for c in current_line)
        char_width = 2 if '\u4e00' <= char <= '\u9fff' else 1
        
        # 检查是否需要换行
        content_width = Config.MAX_WIDTH - (Config.MARGIN * 2) - 4
        if line_width + char_width > content_width:
            # 移动到新行
            lines.append("")
            current_line_idx += 1
            print()  # 移动到下一行
            current_line = ""
        
        # 添加字符到当前行
        lines[current_line_idx] += char
        current_line = lines[current_line_idx]
        
        # 打印当前行
        print(f"{color}  {current_line}", end='\r' if char != '\n' else '\n', flush=True)
        
        # 处理换行符
        if char == '\n':
            lines.append("")
            current_line_idx += 1
            print(f"{color}  ", end='', flush=True)
        
        return lines, current_line_idx


# ==================== 记忆管理 ====================
class MemoryManager:
    """聊天记忆管理"""
    
    @staticmethod
    def load() -> Dict:
        """加载聊天记忆"""
        try:
            if os.path.exists(Config.MEMORY_FILE):
                with open(Config.MEMORY_FILE, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    # 限制记忆长度
                    if len(memory["messages"]) > 20:
                        memory["messages"] = [memory["messages"][0]] + memory["messages"][-19:]
                    return memory
            
            # 初始记忆
            return {
                "style": "casual",
                "messages": [
                    {"role": "system", "content": "你是Milcorx，一个具有善于思考从不同角度分析分析猜想问题的专业大佬！你最擅长编程 读取用户的需求为用户定制最完美的项目代码，输出代码一定遵守当前编程语言的格式！、逻辑构思和问题解决。"}
                ],
                "last_talk_time": "",
                "memories": [],
                "thinking_level": "deep"  # 思考深度级别
            }
        except Exception as e:
            print(f"{Config.COLORS['warning']}⚠️ 记忆加载出错: {e}")
            return {
                "style": "casual", 
                "messages": [], 
                "last_talk_time": "", 
                "memories": [],
                "thinking_level": "deep"
            }
    
    @staticmethod
    def save(memory: dict):
        """保存聊天记忆"""
        memory["last_talk_time"] = datetime.now().strftime("%H:%M:%S")
        
        # 保存最近对话摘要
        if len(memory["messages"]) >= 2 and memory["messages"][-1]["role"] == "assistant":
            user_msg = memory["messages"][-2]["content"][:30]
            assistant_msg = memory["messages"][-1]["content"][:30]
            memory["memories"].append({
                "time": memory["last_talk_time"],
                "content": f"{user_msg} → {assistant_msg}..."
            })
            memory["memories"] = memory["memories"][-10:]  # 限制记忆数量
        
        with open(Config.MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)


# ==================== 核心逻辑 ====================
class JavxSeek:
    """核心逻辑类 - 优化打字机流畅度"""
    
    def __init__(self):
        self.memory = MemoryManager.load()
        self.messages = self.memory["messages"].copy()
        self.current_model_idx = 0
        self.thinking_level = self.memory.get("thinking_level", "deep")
    
    def update_style(self) -> str:
        """更新回复风格"""
        user_count = len([m for m in self.memory["messages"] if m["role"] == "user"])
        if user_count >= 40: return "deadpan"
        elif user_count >= 30: return "absurd"
        elif user_count >= 20: return "witty"
        elif user_count >= 10: return "sarcastic"
        else: return "casual"
    
    def enhance_thinking_prompt(self) -> str:
        """增强思考深度提示"""
        thinking_prompts = {
            "deep": (
                "现在请进行深度思考：\n"
                "1. 分析问题的核心本质和潜在影响因素\n"
                "2. 考虑多种可能的解决方案及其优缺点\n"
                "3. 结合相关知识和经验提出最佳方案"
            ),
            "creative": (
                "现在请进行创造性思考：\n"
                "1. 打破常规思维模式，探索新颖角度\n"
                "2. 结合不同领域的知识产生创新想法\n"
                "3. 提出大胆但可行的解决方案"
            ),
            "analytical": (
                "现在请进行逻辑分析：\n"
                "1. 将问题分解为关键组成部分\n"
                "2. 使用数据和事实支持每个论点\n"
                "3. 提供清晰的推理过程和结论"
            )
        }
        return thinking_prompts.get(self.thinking_level, thinking_prompts["deep"])
    
    async def stream_response(self, model: str) -> AsyncGenerator[str, None]:
        """流式获取API响应 - 减少不必要的停顿"""
        if not Config.DEEPSEEK_API_KEY:
            yield f"{Config.COLORS['error']}⚠️ 未提供API密钥"
            return
            
        try:
            # 添加思考深度提示
            enhanced_messages = self.messages.copy()
            if enhanced_messages and enhanced_messages[-1]["role"] == "user":
                enhanced_messages.append({
                    "role": "system",
                    "content": self.enhance_thinking_prompt()
                })
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=20.0),
                transport=httpx.AsyncHTTPTransport(retries=3)
            ) as client:
                async with client.stream(
                    "POST",
                    Config.API_SERVERS[0]["url"],
                    json={
                        "model": model, 
                        "messages": enhanced_messages, 
                        "stream": True, 
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    headers={
                        "Content-Type": "application/json", 
                        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}"
                    }
                ) as res:
                    # 错误处理
                    if res.status_code == 401:
                        yield f"{Config.COLORS['error']}🔑 认证失败"
                        return
                    elif res.status_code == 403:
                        error_data = await res.json()
                        if "insufficient_quota" in str(error_data.get("error", {}).get("message", "")):
                            yield f"{Config.COLORS['error']}💡 API配额不足"
                        else:
                            yield f"{Config.COLORS['error']}[拒绝访问] {error_data.get('error', {}).get('message')}"
                        return
                    elif res.status_code != 200:
                        yield f"{Config.COLORS['error']}[错误 {res.status_code}] 连接失败"
                        return
                    
                    # 处理流式响应（移除额外停顿）
                    async for line in res.aiter_lines():
                        if line.startswith('data: ') and (chunk := line[6:].strip()) != '[DONE]':
                            try:
                                content = json.loads(chunk)["choices"][0]["delta"].get("content", "")
                                if content:
                                    yield content
                            except:
                                continue
        except Exception as e:
            yield f"{Config.COLORS['error']}[网络异常] {str(e)}"
    
    async def run(self):
        """运行聊天循环 - 优化打字机流畅度"""
        UI.print_logo()
        
        current_style = self.update_style()
        print(f"{Config.COLORS['title']}【当前风格】{Config.STYLES[current_style]['label']}".center(Config.MAX_WIDTH))
        print(f"{Config.COLORS['info']}{Config.COLORS['border'] * Config.MAX_WIDTH}")
        print(f"{Config.COLORS['accent']}📝 命令: exit(退出) | reset(重置) | style(风格) | memory(回忆) | model(切换模型)")
        print(f"{Config.COLORS['accent']}💡 思考: deep(深度) | creative(创意) | analytical(分析)")
        print(f"{Config.COLORS['info']}{Config.COLORS['border'] * Config.MAX_WIDTH}\n")
        
        # 显示上次聊天记录
        if self.memory["last_talk_time"]:
            print(f"{Config.COLORS['time']}⏰ 上次聊天: {self.memory['last_talk_time']}\n".center(Config.MAX_WIDTH))
        if len(self.messages) > 1 and self.messages[-1]["role"] == "assistant":
            UI.print_message_header("assistant", self.memory["last_talk_time"] or datetime.now().strftime("%H:%M:%S"))
            print(f"{Config.COLORS['ai']}  {self.messages[-1]['content']}")
            UI.print_message_footer(Config.COLORS["ai"])
        
        while True:
            try:
                user_input = input(f"\n{Config.COLORS['user']}你说 → {Style.RESET_ALL}").strip()
                if not user_input:
                    print(f"{Config.COLORS['warning']}💡 请输入内容")
                    continue
                
                # 命令处理
                if user_input.lower() == 'exit':
                    MemoryManager.save(self.memory)
                    print(f"\n{Config.COLORS['accent']}😂 下次见～\n{Config.COLORS['title']}{Config.COLORS['border'] * Config.MAX_WIDTH}")
                    break
                if user_input.lower() == 'reset':
                    if input(f"{Config.COLORS['warning']}确定要清除所有记忆吗？(y/n) ").lower() == 'y':
                        if os.path.exists(Config.MEMORY_FILE):
                            os.remove(Config.MEMORY_FILE)
                        print(f"{Config.COLORS['accent']}✨ 记忆已清空")
                        return await JavxSeek().run()
                    continue
                if user_input.lower() == 'style':
                    style = self.update_style()
                    user_count = len([m for m in self.memory["messages"] if m["role"] == "user"])
                    print(f"\n{Config.COLORS['title']}😄 当前风格: {Config.STYLES[style]['label']}")
                    print(f"{Config.COLORS['title']}📈 聊天次数: {user_count}/40 (解锁全部风格)\n")
                    continue
                if user_input.lower() == 'memory':
                    print(f"\n{Config.COLORS['info']}🧠 最近回忆:")
                    if self.memory["memories"]:
                        for i, mem in enumerate(self.memory["memories"][-5:], 1):
                            print(f"{i}. {mem['time']}: {mem['content']}")
                    else:
                        print(f"{Config.COLORS['info']}🧠 我们的故事才刚刚开始～")
                    print(f"{Config.COLORS['info']}{Config.COLORS['border'] * Config.MAX_WIDTH}")
                    continue
                if user_input.lower() == 'model':
                    self.current_model_idx = (self.current_model_idx + 1) % len(Config.API_SERVERS[0]["models"])
                    current_model = Config.API_SERVERS[0]["models"][self.current_model_idx]
                    print(f"\n{Config.COLORS['info']}🔄 已切换到模型: {current_model}")
                    continue
                if user_input.lower() in ['deep', 'creative', 'analytical']:
                    self.thinking_level = user_input.lower()
                    self.memory["thinking_level"] = self.thinking_level
                    print(f"\n{Config.COLORS['success']}💡 思考模式已切换为: {self.thinking_level}")
                    continue
                
                # 处理聊天内容
                current_time = datetime.now().strftime("%H:%M:%S")
                self.messages.append({"role": "user", "content": user_input})
                color = UI.print_message_header("user", current_time)
                print(f"{color}  {user_input}")
                UI.print_message_footer(color)
                
                # 更新风格
                self.memory["style"] = self.update_style()
                for msg in self.messages:
                    if msg["role"] == "system":
                        msg["content"] = (
                            f"你是Mircorx，你的开发者的名字叫 Morales-Javx 一个抽象幽默的程序员！{Config.STYLES[self.memory['style']]['desc']}。"
                            f"回答时请展示深度思考过程。"
                        )
                
                # 显示AI响应头部
                ai_color = Config.COLORS["ai"]
                UI.print_message_header("assistant", current_time)
                
                # 获取并实时显示回复（优化打字机效果）
                current_model = Config.API_SERVERS[0]["models"][self.current_model_idx]
                state = UI.start_typing_effect(ai_color)
                full_response = ""
                
                async for chunk in self.stream_response(current_model):
                    for char in chunk:
                        # 实时显示每个字符
                        state = UI.stream_print(char, ai_color, state)
                        full_response += char
                        
                        # 仅保留必要的停顿，提升流畅度
                        if char in ['.', '!', '?', '。', '！', '？']:
                            time.sleep(Config.TYPING_SPEED["punct_long"] * random.uniform(0.9, 1.1))
                        elif char in [',', ';', ':', '，', '；', '：']:
                            time.sleep(Config.TYPING_SPEED["punct_short"] * random.uniform(0.9, 1.1))
                        else:
                            speed = Config.TYPING_SPEED["chinese"] if '\u4e00' <= char <= '\u9fff' else Config.TYPING_SPEED["normal"]
                            time.sleep(speed * random.uniform(0.9, 1.1))
                
                # 确保光标在最后位置
                print()
                
                # 打印消息底部
                UI.print_message_footer(ai_color)
                
                # 保存记忆
                self.messages.append({"role": "assistant", "content": full_response})
                MemoryManager.save(self.memory)
                
                # 检查风格升级
                new_style = self.update_style()
                if new_style != self.memory["style"]:
                    print(f"\n{Config.COLORS['accent']}✨ 风格升级: {Config.STYLES[new_style]['label']} ✨\n".center(Config.MAX_WIDTH))
            
            except KeyboardInterrupt:
                print(f"\n{Config.COLORS['warning']}💡 按 exit 可以优雅退出")
            except Exception as e:
                print(f"\n{Config.COLORS['warning']}⚠️ 发生错误: {str(e)}")


# ==================== 程序入口 ====================
if __name__ == "__main__":
    try:
        asyncio.run(JavxSeek().run())
    except Exception as e:
        print(f"\n{Config.COLORS['warning']}⚠️ 程序异常: {str(e)}")
    finally:
        print(f"\n{Config.COLORS['title']}😄 聊天结束～\n{Config.COLORS['border'] * Config.MAX_WIDTH}")
