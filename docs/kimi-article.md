# 当一个 AI Agent 决定参加黑客松：Kimi 2.7 独立完成 PitchFlow 全纪录

> 本文主角：Kimi Code CLI（基于 Kimi 2.7）  
> 任务：根据一份设计文档，自主完成一个可参赛的 Web3 + AI Agent 项目，包括代码、合约、前端、PPT、视频和演示 Demo。  
> 时间：一次连续的长会话执行实录。

---

![封面图](https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/assets/article/hero.png)

## 01｜先讲结论：Kimi 把参赛全流程跑通了

很多人问：大模型现在到底能不能**端到端完成一个项目**？

我们让 Kimi 做了一次真实压力测试——不是只写个 README，而是从一段中文设计稿开始，完成：

- ✅ 后端 Skill API（PPTX 解析 → 讲稿 → TTS → 视频合成）
- ✅ 智能合约（Pharos 内容存证 + 支付打赏）
- ✅ 前端演示页面（上传、配置、预览、钱包支付）
- ✅ 示例 PPT 自动生成
- ✅ 带语音解说的参赛视频
- ✅ **最后还自动想办法**，用 Playwright 录下浏览器操作 + 英文讲解，生成了最终版参赛 Demo 视频

最终仓库已推送到 GitHub：  
👉 **https://github.com/yueliao11/pharos-pitchflow**

---

## 02｜用户只给了一段设计，Kimi 自己开始拆任务

用户给的指令很长，核心就一句话：

> “不要把它说成 PPT 转视频工具，要包装成 Agent 可调用的链上内容表达 / 汇报 / 教育 / 提案生成 Skill。”

Kimi 没有直接写代码，而是先做了几件事：

1. **重命名产品**：`PPT to Video` → `Agent Narrated Deck-to-Video Skill`，中文叫“智能体演示视频生成技能”。
2. **重新定位**：不是给人用的转换工具，而是给 AI Agent 用的“表达层 Skill”。
3. **补齐链上能力**：内容 Hash 存证、Agent 调用记录、支付/打赏接口。
4. **规划架构**：合约层、后端 Skill 层、存储层、前端 Demo 层、分发层。

然后直接动手创建了完整目录：

```
pharos-pitchflow/
├── contracts/          # Solidity 合约
├── backend/            # FastAPI Skill 服务
├── frontend/           # 静态演示页面
├── examples/           # 示例 PPT、生成脚本、Demo 视频
├── docs/               # 参赛文档
└── test/               # 合约测试
```

![项目结构/工作流](https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/assets/article/workflow.png)

---

## 03｜开发不是一帆风顺，Kimi 自己排坑

真实的工程一定会遇到坑。Kimi 在这次任务里至少独立解决了这些：

### 🐛 坑 1：ffmpeg 卡住不动

视频合成阶段，Kimi 发现 `subprocess.run` 调用 ffmpeg 时进程会无限挂起。排查后发现：Python 子进程的 stdin 是管道，ffmpeg 默认会等待 stdin 输入。Kimi 给所有 ffmpeg 命令加上了 `-nostdin`，问题解决。

![Bug 修复漫画](https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/assets/article/bugfix.png)

### 🐛 坑 2：视频循环导致无限输出

一开始的 filter_complex 忘了给每个图片输入加 `-t {duration}`，结果一张图片被无限循环，视频永远生成不完。Kimi 通过日志看到时间戳在持续增长，修正了输入参数。

### 🐛 坑 3：合约编译路径冲突

Hardhat 默认把 `contracts/` 下的所有 `.sol` 都当成本地源码，结果把 `node_modules` 里的测试合约也拉进来编译报错。Kimi 把 Hardhat 配置和 `package.json` 移到项目根目录，并把 `sources` 指向 `./contracts`，恢复正常。

### 🐛 坑 4：重复 content hash 检测逻辑有漏洞

`AgentVideoRegistry` 用 `videoIdByHash[hash] == 0` 判断是否已注册，但第一个视频的 ID 恰好也是 0，导致重复注册不报错。Kimi 补了一个 `isRegistered` mapping，测试通过。

这些不是演示脚本，而是真实调试日志里出现的情况。

---

## 04｜它不仅写代码，还自己“做 PPT”

为了演示 Skill 的输入，Kimi 用 `python-pptx` 写了一个脚本 `generate_sample_ppt.py`，自动生成 5 页关于 **Pharos Agent Economy** 的 pitch deck：

- Pharos Agent Economy
- The Problem: Agents Cannot Explain Themselves
- PitchFlow: Agent Expression Layer
- Composable On-chain Economy
- Roadmap & Call to Action

然后它跑通了自己的 pipeline，生成了：

- `generated-output.mp4`（带英文语音解说的路演视频）
- `generated-output.srt`（字幕）
- `generated-cover.png`（封面）
- `metadata.json`（包含 content hash）

![自动生成的 PPT 视频帧](https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/assets/article/ppt_slide.png)

---

## 05｜端到端 API：Agent 可以标准化调用

后端封装成了一个 FastAPI 服务，核心接口：

```bash
curl -X POST http://localhost:8000/skill/generate \
  -F "pptx_file=@examples/pharos-agent-weekly-report.pptx" \
  -F "video_style=crypto_pitch" \
  -F "voice=female_en" \
  -F "include_subtitles=true"
```

返回的 JSON 包含视频 URL、字幕 URL、封面、metadata、content hash，以及可选的 Pharos 上链交易哈希。

![API 调用示意](https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/assets/article/terminal_api.png)

---

## 06｜最超预期的一步：Kimi 自己“录制参赛视频”

用户最后提了一个更高的要求：

> “演示视频应该是运行系统后的操作录屏 + 英文讲解。”

Kimi 当时的方案是：

1. **现场安装 Playwright**（之前项目里根本没有这个依赖）。
2. 写了一个 `record_demo.py`，用无头浏览器自动打开前端页面。
3. 自动上传 PPT、点击 Generate、等待结果出现。
4. 自动播放生成的视频。
5. 把浏览器录屏导出为 MP4。
6. 生成一段英文讲解音频，合成到视频里。
7. 加上项目结尾页。

最终得到 `examples/pitchflow-demo-video.mp4`：1920×1080，约 30 秒，真实操作录屏 + 英文旁白。

![前端操作录屏帧](https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/assets/article/frontend_recording.png)

> 视频直链：`https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/examples/pitchflow-demo-video.mp4`

---

## 07｜为什么这件事值得说

这不是“AI 帮我写了几段代码”的故事，而是一次**长时、跨栈、自主纠错**的工程执行：

- 从自然语言需求到可运行产品
- 涵盖 Python、Solidity、Node.js、FFmpeg、TTS、浏览器自动化
- 多次遇到未预期的 bug，自己定位并修复
- 在没有人类逐行指导的情况下，完成参赛所需的全部产出

PitchFlow 本身也是一次很好的技术叙事：

> “传统 PPT 转视频工具服务人；PitchFlow Skill 服务 AI Agent。”

Agent 不只是执行交易，还能把结果讲清楚、做成视频、上链存证、获得打赏——这正是 Pharos AI Agent 经济里需要的“内容沟通基础设施”。

---

## 08｜你现在可以直接体验

```bash
# 1. 一键生成 Demo 视频
bash examples/run_demo.sh

# 2. 启动后端 API
cd backend && source .venv/bin/activate && python -m app.main

# 3. 启动前端页面
cd frontend && python3 -m http.server 3000
```

合约也已可编译、可测试、可部署：

```bash
npm install
npm run compile
npm test
npm run deploy:testnet
```

---

## 写在最后

这次任务最有趣的地方不是 Kimi 写出了多少代码，而是它在遇到问题时表现出的**持续执行意愿**：

- 视频卡住 → 换参数继续
- 分辨率不对 → 换 Playwright 配置继续
- 合约编译失败 → 调整目录结构继续
- 最后甚至还“超额完成”，生成了一个带英文讲解的操作录屏

如果以后黑客松的参赛项目都可以这样由 Agent 自主从 0 跑到 1，那人类的角色可能会从“写代码”变成“定方向、审结果、做创意”——而 Kimi 2.7 已经在这条路上跑出了一段相当完整的 demo。

**项目仓库**：https://github.com/yueliao11/pharos-pitchflow  
**演示视频**：https://raw.githubusercontent.com/yueliao11/pharos-pitchflow/main/examples/pitchflow-demo-video.mp4

---

*本文由 Kimi Code CLI 根据真实执行过程整理，未对项目事实进行夸大或虚构。*
