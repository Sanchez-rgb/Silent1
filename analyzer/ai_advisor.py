# AI 指导 - 规则引擎版
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class RuleBasedAdvisor:
    """基于规则的AI建议生成器"""
    
    # 关键词映射
    KEYWORDS = {
        "price": ["贵", "太贵", "价格", "不便宜", "性价比低", "买不起"],
        "speed": ["慢", "太慢", "物流", "发货", "等待", "很久"],
        "quality": ["差", "太差", "劣质", "质量不好", "做工"],
        "service": ["态度", "服务", "客服", "不理", "售后"],
        "fake": ["假货", "假的", "高仿", "不是正品", "仿冒"]
    }
    
    # 建议模板
    SUGGESTIONS = {
        "price": [
            "建议增加平价替代品推荐",
            "可以推出限时折扣或满减活动",
            "在标题中标注「性价比之选」",
            "分享同款产品的价格对比"
        ],
        "speed": [
            "下次大促提前预告，管理粉丝预期",
            "优化发货流程，提升物流效率",
            "说明发货时效，避免用户等待焦虑",
            "提供加急发货选项（可选付费）"
        ],
        "quality": [
            "加强品控检查，从源头把控质量",
            "录制开箱视频，展示产品细节",
            "提供更详细的产品说明和材质介绍",
            "考虑推出质保或退换保障"
        ],
        "service": [
            "提升客服响应速度，及时解答问题",
            "整理常见问题 FAQ，减少咨询压力",
            "增加人工客服时间，覆盖主要时段",
            "对服务不满意的用户主动沟通解决"
        ],
        "fake": [
            "展示授权证书和正品验证方式",
            "录制专柜/官方渠道采购视频",
            "分享品牌故事和官方合作背景",
            "提供正品保障承诺，假一赔三等"
        ],
        "general": [
            "感谢粉丝的反馈，持续优化中！",
            "关注评论区高频问题，积极改进",
            "保持与粉丝的良好互动",
            "定期分享产品动态和优化进度"
        ]
    }
    
    def __init__(self):
        pass
    
    def analyze_comments(self, comments):
        """分析评论，提取关键词"""
        keyword_counts = Counter()
        
        for comment in comments:
            text = comment.get("comment_text", "") or ""
            if not text:
                continue
            
            for category, keywords in self.KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text:
                        keyword_counts[category] += 1
        
        return keyword_counts
    
    def generate_advice(self, data):
        """生成建议"""
        comments = data.get("negative_comments", [])
        
        if not comments:
            return self._get_general_advice()
        
        keyword_counts = self.analyze_comments(comments)
        
        if not keyword_counts:
            return self._get_general_advice()
        
        top_category = max(keyword_counts.items(), key=lambda x: x[1])[0]
        
        suggestions = self.SUGGESTIONS.get(top_category, self.SUGGESTIONS["general"])
        
        advice_parts = []
        advice_parts.append("📊 根据评论分析，以下建议供您参考：\n")
        
        for i, suggestion in enumerate(suggestions[:3], 1):
            advice_parts.append(f"{i}. {suggestion}")
        
        return "\n".join(advice_parts)
    
    def _get_general_advice(self):
        """获取通用建议"""
        suggestions = self.SUGGESTIONS["general"]
        advice_parts = ["📊 以下通用建议供您参考：\n"]
        for i, suggestion in enumerate(suggestions[:3], 1):
            advice_parts.append(f"{i}. {suggestion}")
        return "\n".join(advice_parts)


# 全局实例
_advisor = RuleBasedAdvisor()

def get_ai_advisor():
    """获取 AI 建议生成器"""
    return _advisor
