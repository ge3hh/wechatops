# 微信公众号内容创作 Agent

基于多 Agent 架构的微信公众号自动化内容创作系统，集成了热点筛选、爆款写作、HTML排版、配图搜索等能力。

## 架构

```
ContentDirector（导演）
    ├── HotCollector（热点搜集员）
    │   └── 使用 10分制评分筛选优质选题
    ├── Writer（撰稿人）
    │   └── 参考爆款模板，生成HTML排版内容
    ├── Reviewer（审核员）←→ 迭代3轮+
    ├── VisualDesigner（视觉设计师）
    │   └── 使用 Unsplash 搜索配图
    └── Publisher（发布员）
        └── 使用 publish_wechat.py 官方API发布到草稿箱

Skills:
    └── wechat-publish（微信公众号发布工具）
        ├── filter_topics.py（10分制选题筛选）
        ├── search_images.py（Unsplash配图搜索）
        ├── save_article.py（本地保存）
        ├── publish_wechat.py（官方API发布）
        ├── viral-content-templates.md（爆款模板）
        └── html-layout-guide.md（HTML排版规范）
```

## 核心能力

### 1. 智能选题筛选（10分制）
- 热度/趋势（4分）
- 争议性（2分）
- 价值（3分）
- 相关性（1分）
- 自动筛选≥7分的高质量选题

### 2. 爆款内容生成
- 5种爆款风格模板
- HTML 规范排版（秀米风格）
- 局部划线（≤20%）
- 6种浅色调配色

### 3. 智能配图
- **固定图片库**：预置封面图和插图
- 封面图：2.35:1 比例（900×383px）
- 内文配图：3-5张
- 可选：Unsplash 图片搜索（需配置 API Key）
- 可选：AI 绘画 Prompts

### 4. 微信公众号发布
- 官方 API 发布到草稿箱
- 自动上传封面图
- 创建图文草稿
- 登录后台预览后发布

## 记忆系统

```
memory/
├── self/
│   ├── identity.md          # 基本信息
│   └── personality.md       # 性格设定
├── knowledge_base/          # 知识库（空框架，待填充）
│   ├── domain_data/         # 领域资料
│   ├── case_studies/        # 案例库
│   └── assets/              # 素材库
├── history/
│   └── articles.json        # 发布历史
├── mistakes_to_avoid.md     # 错误清单
└── style_guide.md           # 风格指南
```

## 前置准备

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置固定图片（推荐）

将准备好的图片放入对应目录：

```
agents/assets/
├── covers/                    # 封面图（900x383px，2.35:1）
│   ├── default.jpg
│   ├── tech.jpg
│   ├── business.jpg
│   └── ...
└── illustrations/             # 内文插图（800-900px宽）
    ├── intro.jpg
    ├── data.jpg
    └── ...
```

编辑 `agents/assets/image_map.json` 配置图片映射规则。

**可选：配置 Unsplash API Key**

如果需要使用 Unsplash 搜索图片：
1. 访问 https://unsplash.com/developers
2. 注册应用获取 Access Key
3. 设置环境变量：
   ```bash
   export UNSPLASH_ACCESS_KEY="your-access-key"
   ```

### 3. 配置微信公众号 API（必需）

配置微信公众号凭证，用于自动发布到草稿箱：

**方式一：使用配置脚本（推荐）**

Windows:
```bash
setup.bat
```

Linux/Mac:
```bash
source setup.sh
```

**方式二：手动配置**

Windows:
```bash
set WECHAT_APPID=your-appid
set WECHAT_APPSECRET=your-appsecret
```

Linux/Mac:
```bash
export WECHAT_APPID="your-appid"
export WECHAT_APPSECRET="your-appsecret"
```

**验证配置**：
```bash
python skills/wechat-publish/scripts/check_config.py
```

**凭证获取**：
1. 登录微信公众号后台（mp.weixin.qq.com）
2. 设置与开发 → 基本配置
3. 获取 AppID 和 AppSecret
4. 注意：需要认证服务号

### 4. 填写基础信息

编辑以下文件：

**`memory/self/identity.md`**
- 公众号名称
- 账号定位

**`memory/style_guide.md`**
- 账号领域
- 三个关键词
- 读者画像
- 内容标准

## 使用方式

### 启动

```bash
# Windows
start.bat

# 或直接
kimi --agent-file agent.yaml
```

### 使用指令

```markdown
"开始今日创作"           → 启动完整工作流
"搜集热点"               → 只执行热点搜集和筛选
"写关于XXX的文章"        → 指定话题创作
"审核这篇文章"           → 执行质量审核
"搜索配图"               → 使用 Unsplash 搜索图片
"保存并发布"             → 本地保存 + 发布指引
```

## 工作流程

1. **读取记忆** → 加载身份、性格、风格
2. **搜集热点** → 多平台获取热门话题，10分制评分
3. **用户确认** → 选择要写的 topic（≥7分推荐）
4. **撰写初稿** → Writer 完成第1版（含HTML排版、配图建议）
5. **审核迭代** → Reviewer 评分，≥8.5分通过，至少3轮
6. **搜索配图** → VisualDesigner 使用 Unsplash 搜索图片
7. **用户审核** → 确认文章和配图
8. **发布到公众号** → Publisher 使用官方 API 发布到草稿箱
9. **验证结果** → 确认草稿创建成功，提供查看指引

## 审核标准

| 维度 | 权重 | 通过标准 |
|-----|-----|---------|
| 观点鲜明度 | 20% | 有清晰立场，不骑墙 |
| 论据充实度 | 20% | 数据、案例充分 |
| 逻辑严密性 | 15% | 论证环环相扣 |
| 标题吸引力 | 15% | 有点击欲 |
| 开篇抓人度 | 10% | 前100字抓住读者 |
| 语言生动性 | 10% | 生动不生硬 |
| 结构清晰度 | 10% | 层次分明 |

**总分 ≥ 8.5 分才能发布**

## 输出文件

创作完成后，文件保存在 `output/YYYY-MM-DD/`：

- `文章标题.html` - 完整HTML（带样式，可浏览器预览）
- `文章标题_pure.html` - 纯HTML（适合复制到公众号）
- `文章标题.md` - Markdown版本
- `文章标题_metadata.json` - 元数据（标题、标签、评分等）

## 发布方式

### 方式一：官方API发布（推荐）

自动发布到微信公众号草稿箱：

```bash
python skills/wechat-publish/scripts/publish_wechat.py \
  --mode workflow \
  --title "文章标题" \
  --content "HTML内容" \
  --cover "封面图片URL或本地路径" \
  --author "作者名" \
  --digest "文章摘要"
```

发布后登录公众号后台查看草稿箱：
1. 访问 https://mp.weixin.qq.com
2. 内容与互动 → 草稿箱
3. 预览、编辑或直接发布

### 方式二：本地保存 + 手动发布（备用）

如果 API 发布失败：

1. 打开 `output/YYYY-MM-DD/文章标题_pure.html`
2. 全选复制内容
3. 登录 mp.weixin.qq.com
4. 新建图文消息，粘贴内容
5. 按配图方案制作封面图（900×383px）
6. 预览确认后发布

## 参考资料

### 爆款模板
`skills/wechat-publish/references/viral-content-templates.md`
- 高价值干货类
- 犀利观点类
- 热点评论类
- 故事洞察类
- 技术解析类

### HTML排版规范
`skills/wechat-publish/references/html-layout-guide.md`
- 结构分层
- 局部划线（≤20%）
- 6种浅色调配色
- 秀米模板适配

## 更新记录

每次创作后，系统会自动更新：
- `memory/history/articles.json` - 文章历史
- `memory/mistakes_to_avoid.md` - 错误记录（手动）

---

**开始使用**：编辑记忆文件后，运行 `start.bat` 或 `kimi --agent-file agent.yaml`
