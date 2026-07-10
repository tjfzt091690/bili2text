<p align="center">
  <img src="light_logo2.png" alt="bili2text logo" width="400"/>
</p>


<p align="center">
    <img src="https://img.shields.io/github/stars/lanbinshijie/bili2text" alt="GitHub stars"/>
    <img src="https://img.shields.io/github/license/lanbinshijie/bili2text" alt="GitHub"/>
    <img src="https://img.shields.io/github/last-commit/lanbinshijie/bili2text" alt="GitHub last commit"/>
    <img src="https://img.shields.io/github/v/release/lanbinshijie/bili2text" alt="GitHub release (latest by date)"/>
</p>

# Bili2text 📺

## 转移说明
因为作者的旧账号（lanbinshijie）已经停用，仓库已经转移到新账号（lanbinleo）

感谢各位的支持，如果有任何想法欢迎在issue中提出，或者提交pr~

v2版本开发进度，请查看dev分支；v3版本更名为v2版本

![alt text](./assets/new_v_sc.png)

## 简介 🌟
bili2text 是一个用于将 Bilibili 视频转换为文本的工具🛠️。这个项目通过一个简单的流程实现：下载视频、提取音频、分割音频，并使用语音识别模型将语音转换为文本。项目提供 Web 界面，支持多种语音识别引擎和 LLM 后处理功能，整个过程行云流水，一步到胃😂

## 功能 🚀
- 🎥**下载视频**：从 Bilibili 下载指定的视频，支持多P视频的下载，自动解析视频链接中的 BV 号。
- 🎵**提取音频**：从下载的视频中提取音频并分割成小段，以便于进行高效的语音转文字处理。
- 🤖**语音转文字**：支持多种语音识别引擎：
  - [Whisper](https://github.com/openai/whisper)（OpenAI 开源模型）
  - [Paraformer](https://modelscope.cn/models/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch)（阿里达摩院 ModelScope 模型）
  - [讯飞语音转写](https://www.xfyun.cn/services/ifasr)（讯飞开放平台 API）
- 🧠**LLM 后处理**：基于 OpenAI 兼容 API 的 LLM 服务，支持对转写文本进行摘要、纠错、翻译和自定义处理。
- 🌐**Web 界面**：基于 Flask 的 Web UI，支持异步任务处理，操作更便捷。

## 使用方法 📘

### 前置要求
- Python 3.10+
- PostgreSQL 数据库
- FFmpeg（音频处理依赖）

### 安装步骤

1. **克隆仓库**：
   ```bash
   git clone https://github.com/lanbinleo/bili2text.git
   cd bili2text
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**：
   复制 `.env.example` 为 `.env`，并根据实际情况修改配置：
   ```bash
   cp .env.example .env
   ```

   主要配置项说明：
   | 配置项 | 说明 |
   |--------|------|
   | `DATABASE_URL` | PostgreSQL 数据库连接地址 |
   | `WHISPER_MODEL` | Whisper 模型名称（如 `tiny`、`base`、`small`、`medium`、`large`） |
   | `LLM_PROVIDER` | LLM 服务提供商 |
   | `LLM_API_KEY` | LLM API 密钥 |
   | `LLM_API_BASE` | LLM API 地址（兼容 OpenAI 格式即可） |
   | `LLM_MODEL` | LLM 模型名称 |
   | `XUNFEI_APPID` / `XUNFEI_SECRET_KEY` | 讯飞开放平台凭证（使用讯飞转写时需要） |

4. **启动 Web 服务**：
   ```bash
   python run.py
   ```

   启动后访问 `http://localhost:5000` 即可使用 Web 界面。默认端口为 5000，可在 `.env` 中通过 `FLASK_PORT` 修改。

## 技术栈 🧰
- [Python](https://www.python.org/) 主要编程语言，负责实现程序逻辑功能
- [Flask](https://flask.palletsprojects.com/) Web 框架，提供 Web 界面和 API
- [Whisper](https://github.com/openai/whisper) OpenAI 语音转文字模型
- [ModelScope](https://modelscope.cn/) 阿里达摩院模型库（Paraformer 语音识别）
- [OpenAI API](https://platform.openai.com/docs/api-reference) LLM 后处理服务（兼容 OpenAI 格式的 API 均可使用）
- [PostgreSQL](https://www.postgresql.org/) 数据库
- [SQLAlchemy](https://www.sqlalchemy.org/) ORM 框架


## 运行截图 📷
<!-- assets/screenshot1.png -->
<img src="assets/screenshot3.png" alt="screenshot3" width="600"/>
<img src="assets/screenshot2.png" alt="screenshot2" width="600"/>
<img src="assets/screenshot1.png" alt="screenshot1" width="600"/>

## Star History ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=lanbinshijie/bili2text&type=Date)](https://star-history.com/#lanbinshijie/bili2text&Date)



## 许可证 📄
本项目根据 MIT 许可证发布。

## 贡献 💡
如果你想为这个项目做出贡献，欢迎提交 Pull Request 或创建 Issue。

## 投喂一下！

> TKTg2T7u7xdV4xDAzbzird2qmWoqLanbin

![image](https://github.com/user-attachments/assets/412470b8-7fd5-4632-a085-9c48a9d5e18b)

TRC20链！谢谢大家！

## 致谢 🙏
再此感谢Open Teens对青少年开源社区做出的贡献！[@OpenTeens](https://openteens.org)

## 使用须知 🖥️

**用户在使用 bili2text 工具时，必须遵守用户所在地区的相关版权法律和规定。请确保您有权利下载和转换的视频内容，尊重创作者的劳动成果。**