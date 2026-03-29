# 固定图片资源目录

用于存放微信公众号文章的固定图片素材。

## 目录结构

```
assets/
├── covers/                    # 封面图（2.35:1 比例，900x383px）
│   ├── default.jpg            # 默认封面（通用）
│   ├── tech_1.jpg             # 科技类 1
│   ├── tech_2.jpg             # 科技类 2
│   ├── business_1.jpg         # 商业类 1
│   ├── business_2.jpg         # 商业类 2
│   ├── ai_1.jpg               # AI专题 1
│   ├── ai_2.jpg               # AI专题 2
│   └── ...                    # 添加更多
└── illustrations/             # 内文插图（宽度 800-900px）
    ├── intro_1.jpg            # 开篇图 1
    ├── intro_2.jpg            # 开篇图 2
    ├── data_1.jpg             # 数据展示图 1
    ├── case_1.jpg             # 案例图 1
    ├── trend_1.jpg            # 趋势图 1
    └── ...                    # 添加更多
```

## 图片规格

### 封面图
- **比例**：2.35:1
- **尺寸**：900 x 383 px（或 1080 x 459 px）
- **格式**：JPG 或 PNG
- **大小**：不超过 2MB
- **风格**：与账号调性一致

### 内文插图
- **宽度**：800-900 px
- **高度**：自适应（不超过 600px）
- **格式**：JPG 或 PNG
- **大小**：单张不超过 1MB
- **数量**：每篇文章 3-5 张

## 使用方法

在 Visual Designer 中，使用以下方式引用固定图片：

```python
# 封面图
cover_path = "agents/assets/covers/tech_1.jpg"

# 内文插图
illustration_path = "agents/assets/illustrations/intro_1.jpg"
```

或在 Publisher 中直接上传：

```bash
python agents/skills/wechat-publish/scripts/publish_wechat.py \
  --mode workflow \
  --title "文章标题" \
  --content "HTML内容" \
  --cover "agents/assets/covers/tech_1.jpg"
```

## 图片命名规范

- 使用小写字母、数字和下划线
- 格式：`类别_序号.jpg`
- 示例：`tech_1.jpg`, `ai_main.jpg`, `intro_default.jpg`

## 图片来源建议

1. **自己拍摄/设计**：最符合品牌调性
2. **Unsplash 下载**：免费商用，高质量
3. **AI 生成**：Midjourney/DALL-E 生成专属图片
4. **设计工具**：Canva、创客贴制作

## 注意事项

1. **版权**：确保图片有使用权
2. **风格统一**：所有图片风格保持一致
3. **定期更新**：定期添加新图片，避免读者审美疲劳
4. **备份**：定期备份图片文件
