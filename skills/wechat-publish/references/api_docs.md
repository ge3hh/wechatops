# 微信公众号 API 文档

## 素材管理接口

### 上传图文消息内的图片获取URL
```
POST https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=ACCESS_TOKEN
```

### 新增永久素材
```
POST https://api.weixin.qq.com/cgi-bin/material/add_news?access_token=ACCESS_TOKEN
```

## 草稿箱接口

### 新建草稿
```
POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN
```

请求体：
```json
{
  "articles": [
    {
      "title": "TITLE",
      "author": "AUTHOR",
      "digest": "DIGEST",
      "content": "CONTENT",
      "content_source_url": "CONTENT_SOURCE_URL",
      "thumb_media_id": "THUMB_MEDIA_ID",
      "need_open_comment": 0,
      "only_fans_can_comment": 0
    }
  ]
}
```

## 发布接口

### 发布草稿
```
POST https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token=ACCESS_TOKEN
```

## 获取 Access Token

```
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
```

## 注意事项

1. 需要认证服务号才能使用这些接口
2. access_token 有效期 2 小时，需要缓存
3. 图文消息内容需要是微信支持的 HTML 标签
4. 图片需要先上传到微信服务器获取 media_id
