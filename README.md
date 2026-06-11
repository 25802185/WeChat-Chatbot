# WeChat-Chatbot - 虚拟恋人

基于 DeepSeek LLM 的微信虚拟恋人聊天机器人，通过微信 iLink 协议实现自动回复，支持情绪感知、记忆系统和多种互动技能。

## 功能特性

- **智能对话** - 基于 DeepSeek 大模型，支持自然流畅的中文对话
- **情绪感知** - 自动识别用户情绪，调整回复语气和 emoji
- **记忆系统** - 自动提取和记忆用户的重要信息（喜好、习惯、事件等）
- **角色心情** - 角色有独立的心情状态，会根据对话内容变化
- **关系系统** - 模拟恋爱关系的不同阶段
- **技能系统** - 内置多种互动技能：
  - 早晚安问候
  - 讲笑话
  - 纪念日提醒
  - 表情包互动
  - 情话生成
- **配置热重载** - 运行时发送"刷新配置"即可更新角色设定

## 项目结构

```
├── main.py              # 程序入口
├── bot.py               # 核心机器人逻辑
├── character.py         # 角色设定和 prompt 构建
├── character_mood.py    # 角色心情系统
├── emotion.py           # 情绪检测
├── relationship.py      # 关系阶段系统
├── llm.py               # LLM 调用封装
├── memory.py            # 记忆系统（短期/长期）
├── weixin_api.py        # 微信 iLink API 封装
├── messenger.py         # 消息发送
├── config.py            # 配置加载
├── config.yaml.example  # 配置文件模板
├── skills/              # 技能模块
│   ├── base.py          # 技能基类
│   ├── greeting.py      # 问候技能
│   ├── jokes.py         # 笑话技能
│   ├── anniversary.py   # 纪念日技能
│   ├── stickers.py      # 表情包技能
│   └── love_message.py  # 情话技能
└── tests/               # 单元测试
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml`，填入你的 DeepSeek API Key：

```yaml
llm:
  api_key: "your-api-key-here"
  base_url: "https://api.deepseek.com/v1"
  model: "deepseek-v4-pro"
```

### 3. 运行

```bash
python main.py
```

启动后会显示二维码，用微信扫码登录即可。

### 4. 运行测试

```bash
pytest tests/
```

## 配置说明

| 配置项 | 说明 |
|--------|------|
| `character.name` | 角色名字 |
| `character.personality` | 角色性格设定 |
| `character.speaking_style` | 说话风格规则 |
| `character.background` | 角色背景故事 |
| `llm.api_key` | DeepSeek API Key |
| `llm.model` | 使用的模型 |
| `llm.temperature` | 回复随机性（0-1） |
| `skills.greeting.morning_hour` | 早安时间 |
| `skills.greeting.night_hour` | 晚安时间 |

## 注意事项

- 本项目使用微信 iLink 协议，请遵守微信使用规范
- `config.yaml` 包含 API Key，已在 `.gitignore` 中排除，不会被上传
- 登录凭证保存在 `data/login.json`，也在 `.gitignore` 中
- 首次运行需要扫码登录，后续会自动加载已保存的凭证

## 技术栈

- Python 3.10+
- DeepSeek API (OpenAI 兼容)
- 微信 iLink 协议
