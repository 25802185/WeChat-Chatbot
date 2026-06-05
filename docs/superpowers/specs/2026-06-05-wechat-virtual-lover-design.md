# 微信虚拟恋人 — 设计文档

## 概述

将一个有恋人性格的 AI 虚拟形象接入个人微信，用户通过微信 PC 客户端与虚拟恋人对话。使用 WeChatFerry hook 微信客户端，DeepSeek V4 Pro 作为对话引擎，本地 Windows 运行，仅服务用户一人。

## 核心需求

- **形态**：视觉形象（已有 IP）+ 聊天
- **平台**：个人微信号
- **AI 引擎**：DeepSeek V4 Pro（国产大模型，中文角色扮演能力强）
- **人设**：恋人型 — 温柔体贴、会撒娇、偶尔吃醋、有小脾气但好哄
- **部署**：本地 Windows 电脑
- **用户范围**：仅用户本人

## 架构

```
微信客户端 (Windows PC)
    ↕ DLL Hook
WeChatFerry (WCF)
    ↕ Python SDK
Bot 服务 (Python)
    ↕ OpenAI 兼容 API
DeepSeek V4 Pro
    ↕
人设 System Prompt + 对话历史 + 长期记忆
```

## 消息处理流程

1. WCF 监听微信消息事件
2. 收到消息 → 检查发送者是否为用户本人（通过微信号判断）→ 不匹配则忽略
3. 提取消息内容：
   - 文字消息：直接使用
   - 图片/语音/其他：回复撒娇式提示（如"人家看不懂图片嘛~"）
4. 加载该对话的最近 50-100 轮历史（根据 token 限制动态调整）
5. 拼接上下文：System Prompt（人设）+ 长期记忆 + 对话历史 + 当前消息
6. 调用 DeepSeek V4 Pro API
7. 保存本轮对话到历史记录
8. 通过 WCF 发回微信

## 人设系统

通过 System Prompt 定义虚拟恋人角色，核心要素：

- **身份**：名字、年龄、背景故事（可配置）
- **性格**：温柔但有小脾气、会撒娇、偶尔吃醋、会说甜蜜的话
- **说话风格**：口语化、带语气词（嘛、呀、哼、啦）、适当使用 emoji
- **行为模式**：主动关心对方日常、记住对方提过的事情、会追问细节

人设通过 `config.yaml` 配置，支持用户自定义所有细节。

## 数据存储

全部本地存储，不依赖外部数据库。

### config.yaml

```yaml
character:
  name: "小柔"
  age: 22
  personality: "温柔体贴，偶尔撒娇吃醋..."
  speaking_style: "口语化，带语气词..."
  background: "你们是在一次聚会上认识的..."

llm:
  api_key: "sk-xxx"
  base_url: "https://api.deepseek.com"
  model: "deepseek-v4-pro"
  max_tokens: 1024
  temperature: 0.85

user:
  wechat_id: "your_wechat_id"

wcf:
  port: 10086
```

### data/memory.json — 对话历史

```json
{
  "conversations": {
    "<user_wxid>": [
      {"role": "user", "content": "今天好累啊", "timestamp": "2026-06-05T10:30:00"},
      {"role": "assistant", "content": "辛苦啦~要不要休息一下？", "timestamp": "2026-06-05T10:30:05"}
    ]
  }
}
```

保留最近 50-100 轮对话，超出时滑动窗口截断最旧的消息。

### data/long_term.json — 长期记忆

```json
{
  "memories": [
    {"content": "用户生日是8月15日", "added": "2026-06-05"},
    {"content": "用户喜欢吃辣", "added": "2026-06-05"}
  ]
}
```

从对话中提取重要信息存储，作为 System Prompt 的补充上下文注入。

## 项目结构

```
talking/
├── main.py              # 入口，启动 WCF 监听，注册消息回调
├── bot.py               # 消息处理核心：过滤、拼接、调用、回复
├── llm.py               # DeepSeek API 调用封装（OpenAI 兼容格式）
├── character.py         # 人设 prompt 构建，从 config 加载
├── memory.py            # 对话历史读写 + 长期记忆管理
├── config.yaml          # 配置文件（人设、API key、用户信息）
├── requirements.txt     # Python 依赖
├── data/
│   ├── memory.json      # 对话历史
│   └── long_term.json   # 长期记忆
└── assets/
    └── avatar.png       # 虚拟形象头像
```

## 依赖

```
wcferry
openai
pyyaml
```

- Python 3.9+
- Windows 系统
- 微信 PC 客户端（需与 WCF 版本匹配）

## 启动方式

1. 登录微信 PC 客户端
2. `pip install -r requirements.txt`
3. 编辑 `config.yaml` 填入 API key 和微信号
4. `python main.py`
5. 控制台显示"监听中..."，开始对话

## 注意事项

- 微信版本需与 WeChatFerry 兼容，WCF 文档中会标注支持的版本号
- 建议使用微信小号，降低主号封号风险
- 微信窗口部分 WCF 版本要求不最小化
- DeepSeek API 费用极低，日常对话几乎无成本
