## Why

传统赛艇教练预约流程缺乏灵活性，会员与教练之间的互动割裂，练后反馈闭环缺失。我们需要一个智能化的微信小程序，将预约、教练匹配、练后管理等功能整合为流畅的AI驱动体验，提升会员满意度与场馆运营效率。

## What Changes

- **AI智能教练推荐系统**：基于会员技术水平、偏好、历史训练数据，自动匹配最合适的教练
- **自然语言交互界面**：支持文字/语音输入，AI Agent理解会员意图，提供个性化服务
- **智能化预约流程**：动态日程管理，微信通知教练，确认流程自动化
- **练后闭环管理**：教练点评、AI改善建议、基于历史训练的智能再推荐
- **人性化关怀系统**：生日祝福、会籍续期提醒、活动推送等
- **会员画像引擎**：持续学习会员偏好，提供越来越精准的个性化服务

## Capabilities

### New Capabilities

- `ai-conversational-interface`: 文字/语音交互的AI对话界面，支持自然语言理解和上下文记忆
- `coach-intelligent-matching`: 基于会员画像（技术水平、性格偏好、训练历史）智能推荐教练
- `smart-scheduling`: 动态日程管理，教练日程自动协调，微信通知确认流程
- `training-feedback-loop`: 练后点评收集、AI建议生成、反馈闭环、针对性再推荐
- `member-engagement`: 生日祝福、会籍续期提醒、活动推送等个性化关怀
- `member-portrait`: 持续更新的会员画像，支撑所有个性化功能

### Modified Capabilities

- （无现有能力需要修改）

## Impact

- **新增前端**：微信小程序（WeChat Mini Program）+ AI对话组件
- **新增后端**：AI Agent服务、智能推荐引擎、日程管理服务
- **本地推理**：Apple Silicon M5 Max (ASR + Embedding + LLM)
- **外部集成**：微信通知API
- **数据存储**：SQLite（Directus）+ FastAPI
