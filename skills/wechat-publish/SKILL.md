---
name: wechat-hotspot-publisher
description: 智能采集热点话题，10分制筛选优质选题，AI生成爆款内容（标题/封面/标签/图片/HTML排版），支持本地保存和微信公众号发布
---

# 微信公众号热点发布助手

## 任务目标
- 本Skill用于：自动从热点话题生成内容并发布到微信公众号
- 能力包含：
  - 智能体根据关键词生成热点列表
  - AI创作符合公众号调性的内容
  - 生成符合秀米模板的HTML排版
  - 智能选题筛选系统（10分制打分）
  - 支持本地保存和发布到微信公众号草稿箱

## 前置准备
- 依赖说明：
  ```bash
  # scripts脚本所需的依赖
  requests==2.31.0
  ```

## 发布方式

### 方式一：官方API发布（推荐）
1. 使用微信公众号认证服务号
2. 配置 WECHAT_APPID 和 WECHAT_APPSECRET
3. 自动上传到草稿箱

### 方式二：本地保存 + 手动发布（备用）
1. 生成内容后保存到本地
2. 手动复制到微信公众号后台
3. 适合个人订阅号，零配置

## 操作步骤

### 标准流程

**重要说明**：本技能支持"先生成预览，满意再发布"的模式。热点采集和内容生成阶段完全不需要任何配置。

#### 阶段一：内容生成（无需配置）

**默认模式**：生成**图文并茂的微信公众号爆款文**。

1. **确定内容方向**（无需配置）
   - 智能体询问用户关注的关键词（如：AI、量化、新能源等）
   - 智能体根据关键词生成5-10个相关热点话题列表
   - 用户选择感兴趣的话题

   **增强功能**：智能选题筛选
   - 支持智能打分系统（10分制）：热度(4分) + 争议性(2分) + 价值(3分) + 相关性(1分)
   - 自动筛选≥7分的高质量选题
   - 智能体会调用 `scripts/filter_topics.py` 进行评分

2. **生成完整内容**（无需配置）
   - 智能体根据选择的热点，生成包含以下元素的完整内容：
   
   **2.1 标题生成**：
   - 根据爆款风格模板生成吸引人的标题
   - 标题模板见 [references/viral-content-templates.md](references/viral-content-templates.md)
   
   **2.2 封面图（2.35:1）**：
   - 调用 `scripts/search_images.py --query "关键词" --cover` 搜索配图
   - 封面图比例：2.35:1（公众号标准比例）
   - 图片尺寸建议：900x383像素（公众号封面标准）
   
   **2.3 内文配图（3-5张）**：
   - 调用 `scripts/search_images.py --query "关键词"` 搜索3-5张高质量图片
   - 根据内容逻辑，将图片插入到文章的合适位置
   - 每张图片包含简短描述（HTML格式）
   
   **2.4 热点标签**：
   - 根据文章内容自动提取3-5个热点标签
   - 格式：#标签1 #标签2 #标签3（HTML格式，放在文末）
   
   **2.5 HTML排版**：
   - 严格遵循 [references/html-layout-guide.md](references/html-layout-guide.md) 中的排版规范
   - **结构分层**：一级、二级、三级标题清晰
   - **局部划线**：仅对关键短语/核心信息划线，不整句/整段高亮
   - **颜色规范**：浅黄(#fff3cd)、浅绿(#d4edda)、浅红(#f8d7da)、浅蓝(#e8f4f8)、浅紫(#f3e5f5)、浅橙(#fff8e1)
   - **划线密度**：不超过全文20%
   
   **2.6 内容风格**（爆款文）：
   - 参考 [references/viral-content-templates.md](references/viral-content-templates.md) 中的爆款风格模板
   - **高价值干货类**：数字开头，清单结构，实用性强
   - **犀利观点类**：反常识，观点鲜明，引发讨论
   - **热点评论类**：快速反应，独特角度
   - **故事洞察类**：具体场景，情节转折，金句总结
   - **技术解析类**：原理拆解，深入浅出，类比解释
   
   **2.7 排版要求**：
   - **可预览可复制**：生成完整的HTML格式，可直接预览和复制
   - **不包含作者信息**：不要添加作者名称、作者介绍等
   - **不包含制作信息**：不要添加"AI助手"等字样
   - **纯净输出**：仅包含文章标题、封面、内文、标签

3. **预览与调整**（无需配置）
   - 将生成的完整文章（HTML格式）展示给用户
   - 包含：标题、封面图、内文配图（3-5张）、热点标签、正文内容
   - HTML格式可直接预览和复制
   - 用户可以要求调整标题、内容、图片或排版
   - 在这个阶段，用户可以选择：
     - 继续调整内容
     - 保存到本地并手动发布（推荐）

#### 阶段二：发布到微信公众号

**配置环境变量**

设置微信公众号凭证（只需配置一次）：
```bash
# Windows
set WECHAT_APPID=your-appid
set WECHAT_APPSECRET=your-appsecret

# Linux/Mac
export WECHAT_APPID="your-appid"
export WECHAT_APPSECRET="your-appsecret"
```

**执行发布**

完整工作流（上传封面 + 创建草稿）：
```bash
python scripts/publish_wechat.py --mode workflow \
  --title "文章标题" \
  --content "HTML内容" \
  --cover "封面图片URL或本地路径" \
  --author "作者名" \
  --digest "文章摘要"
```

分步执行：
```bash
# 步骤1：上传封面图片
python scripts/publish_wechat.py --mode upload_cover \
  --cover "封面图片路径"
# 返回：封面图的 media_id

# 步骤2：创建草稿（使用步骤1返回的 media_id）
python scripts/publish_wechat.py --mode create_draft \
  --title "文章标题" \
  --content "HTML内容" \
  --media-id "MEDIA_ID_FROM_STEP_1" \
  --author "作者名" \
  --digest "文章摘要"
```

**方式二：本地保存 + 手动发布（备用）**

```bash
# 保存文章到本地
python scripts/save_article.py \
  --title "文章标题" \
  --content "文章内容(HTML)" \
  --cover "封面图URL" \
  --tags "标签1,标签2"
```

输出文件：
- `output/YYYY-MM-DD/article.html` - 完整HTML文件
- `output/YYYY-MM-DD/article.md` - Markdown版本
- `output/YYYY-MM-DD/metadata.json` - 元数据

## 资源索引

### 必要脚本
- [scripts/publish_wechat.py](scripts/publish_wechat.py)
  - 用途：微信公众号草稿箱发布
  - 功能：素材上传、草稿创建、完整工作流
  - 模式：workflow（完整工作流）、upload_cover（上传封面）、create_draft（创建草稿）
  
- [scripts/filter_topics.py](scripts/filter_topics.py)
  - 用途：智能选题打分筛选
  - 功能：10分制评分，筛选高质量选题
  
- [scripts/search_images.py](scripts/search_images.py)
  - 用途：Unsplash图片搜索
  - 功能：搜索封面图和内文配图
  
- [scripts/save_article.py](scripts/save_article.py)
  - 用途：保存文章到本地
  - 功能：生成HTML、Markdown、元数据

### 领域参考
- [references/viral-content-templates.md](references/viral-content-templates.md)
  - 何时读取：生成爆款风格内容时
  - 内容：5种爆款内容风格模板（高价值干货、犀利观点、热点评论、故事洞察、技术解析）
  
- [references/html-layout-guide.md](references/html-layout-guide.md)
  - 何时读取：生成HTML排版时
  - 内容：完整的HTML排版规范，包括结构分层、局部划线、颜色规范、秀米模板适配

## 注意事项

### 默认模式（无特殊要求时）
当用户没有特殊要求时，智能体应按以下默认模式生成内容：

**1. 内容要素**：
- 标题：爆款风格，吸引眼球
- 封面图：2.35:1比例，高质量配图
- 内文配图：3-5张，插入到合适位置
- 热点标签：3-5个，放在文末
- HTML排版：可预览可复制，结构清晰

**2. 排版要求**：
- 结构分层：一、二、三级标题
- 局部划线：仅对关键短语划线，不超过全文20%
- 颜色规范：浅色调（浅黄、浅绿、浅红、浅蓝、浅紫、浅橙）
- 纯净输出：不包含作者信息、制作信息等

### 安全原则
- **草稿箱优先**：微信公众号发布默认保存到草稿箱，不会直接发布到线上
- **人工确认**：所有发布操作都需要用户确认
- **环境变量**：WECHAT_APPID 和 WECHAT_APPSECRET 通过环境变量配置，不硬编码

### 图片处理
- **封面比例**：必须使用2.35:1比例，900x383像素
- **图片质量**：使用高质量图片，避免模糊
- **版权注意**：使用Unsplash等免费图库

## 使用示例

### 示例1：本地保存
```bash
python scripts/save_article.py \
  --title "AI时代的内容创作指南" \
  --content "<html>...</html>" \
  --cover "https://images.unsplash.com/..." \
  --tags "AI,工具,效率"
```

### 示例2：官方API发布
```bash
# 配置凭证
export WECHAT_APPID="wx..."
export WECHAT_APPSECRET="..."

# 执行发布
python scripts/publish_wechat.py --mode workflow \
  --title "AI时代的内容创作指南" \
  --content "<html>...</html>" \
  --cover "./cover.jpg"
```

### 示例3：选题筛选
```bash
python scripts/filter_topics.py \
  --input topics.json \
  --keywords "AI" \
  --min-score 7
```

### 示例4：图片搜索
```bash
# 搜索封面
python scripts/search_images.py --query "AI technology" --cover

# 搜索内文配图
python scripts/search_images.py --query "writing efficiency"
```

## 常见问题

### Q1: 如何使用微信公众号官方API？
- 需要认证服务号
- 在公众号后台获取 AppID 和 AppSecret
- 设置环境变量后使用 `publish_wechat.py`

### Q2: 没有认证服务号怎么办？
- 使用本地保存模式
- 手动复制内容到公众号后台
- 适合个人订阅号

### Q3: Unsplash API Key 在哪里获取？
- 访问 https://unsplash.com/developers
- 注册应用获取 Access Key
- 设置环境变量 `UNSPLASH_ACCESS_KEY`

### Q4: 如何确保排版规范？
- 严格遵循 html-layout-guide.md
- 智能体自动生成符合规范的HTML
- 支持预览和调整
