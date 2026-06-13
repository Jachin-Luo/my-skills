---
name: my-skills
description: '展示我独立安装的 skill 及触发词。当用户问"我有哪些skill"、"skill列表"、"可用技能"、"触发词"时使用。'
---

# 我的 Skills

> 仅统计独立安装的 skill（不含内置）

---

| 分类 | 父Skill | 子Skill | 触发词 |
|------|---------|---------|--------|
| 💰 投资 | deep-analysis | investor-panel | 投资评审、大佬评审、多角度分析 |
| 💰 投资 | deep-analysis | lhb-analyzer | 龙虎榜、谁在买、游资、机构 |
| 💰 投资 | deep-analysis | trap-detector | 杀猪盘、朋友推荐、群里说 |
| 💰 投资 | deep-analysis | uzi-skill-pitfalls | UZI分析、股票陷阱 |
| 💰 投资 | deep-analysis | — | 深度分析、DCF、值不值得买 |
| 🎨 设计 | qiaomu-mondo-poster-design | — | Mondo风格、海报设计、书籍封面 |
| 🎨 设计 | kami | — | 简历、PPT、一页纸、落地页、排版 |
| 📱 社交 | wewrite | — | 公众号、微信文章 |
| 📱 社交 | xiaohongshu-mcp | — | 小红书、发布笔记、小红书搜索 |
| 📱 社交 | xhs-writer-skill | — | 写小红书、小红书笔记、小红书图文、小红书种草 |
| 📱 社交 | comic-creator | — | 做个漫画、帮我画个漫画发小红书、创作漫画、四格漫画 |
| 📱 社交 | follow-builders | — | AI日报、每日讯息 |
| 🔮 命理 | bazi | — | 八字、命理、四柱 |
| 🔧 运维 | docker-deployment | — | Docker部署、容器 |
| 🔧 运维 | reverse-proxy | — | Nginx反代、域名配置、SSL |
| 📰 资讯 | daily-ai-news | — | AI新闻、科技资讯 |
| 🔍 搜索 | smart-search-cli | — | 智能搜索 |
| 📊 收藏 | repo-collector | — | 收集仓库 |
| 📊 飞书 | feishu-doc-api | — | 飞书文档API、lark-cli陷阱、wiki管理 |

---

**统计：** 6个分类，20个skill（1个父skill + 4个子skill + 15个独立skill）

**使用方式：**
- 说"my skills"或"我有哪些skill"查看此列表
- 说具体的触发词即可使用对应 skill
- 例如："帮我做个漫画"、"深度分析茅台"、"写个小红书笔记"

**维护**：安装新 skill 后更新此表。更新后推送到 GitHub：
```bash
cd ~/.hermes/skills/my-skills && git add . && git commit -m "更新 skills 列表" && git push
```
仓库地址：`Jachin-Luo/my-skills`
