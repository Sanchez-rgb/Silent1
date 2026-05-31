
# 情感分析模块 - 使用Transformers
import sys
import os
from typing import Tuple, List, Dict
import json
from tqdm.auto import tqdm

# 尝试导入transformers，第一次运行会下载模型
try:
    from transformers import BertForSequenceClassification, BertTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("警告: transformers未安装，将使用随机分类")


class SentimentAnalyzer:
    """情感分析器 - 使用uer/roberta-base-finetuned-dianping-chinese"""
    
    MODEL_NAME = "uer/roberta-base-finetuned-dianping-chinese"
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._loaded = False
    
    def _load_model(self):
        """加载模型（带下载进度提示）"""
        if self._loaded:
            return
        
        print(f"正在加载模型: {self.MODEL_NAME}")
        print("首次运行会下载约1.5GB的模型文件，请耐心等待...")
        
        try:
            # 使用tqdm显示下载进度
            if not os.path.exists(os.path.expanduser("~/.cache/huggingface/hub")):
                print("正在下载模型文件...")
            
            self.tokenizer = BertTokenizer.from_pretrained(
                self.MODEL_NAME,
                cache_dir="./model_cache"
            )
            
            self.model = BertForSequenceClassification.from_pretrained(
                self.MODEL_NAME,
                cache_dir="./model_cache"
            )
            
            self.model.to(self.device)
            self.model.eval()
            self._loaded = True
            print("模型加载完成！")
            
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("将使用简单的随机分类作为备选方案")
            self._loaded = False
    
    def analyze(self, text: str) -&gt; Tuple[str, float]:
        """
        分析单条文本的情感
        返回: (sentiment, confidence)
        sentiment: 'positive' | 'neutral' | 'negative'
        """
        if not TRANSFORMERS_AVAILABLE:
            return self._simple_analyze(text)
        
        if not self._loaded:
            self._load_model()
        
        if not self._loaded:
            return self._simple_analyze(text)
        
        try:
            # 分词和推理
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # 模型输出是二分类：0=负面，1=正面
            neg_prob = probabilities[0][0].item()
            pos_prob = probabilities[0][1].item()
            
            if pos_prob &gt; 0.6:
                sentiment = "positive"
                confidence = pos_prob
            elif neg_prob &gt; 0.6:
                sentiment = "negative"
                confidence = neg_prob
            else:
                sentiment = "neutral"
                confidence = max(pos_prob, neg_prob)
            
            return sentiment, confidence
            
        except Exception as e:
            print(f"情感分析出错: {e}")
            return self._simple_analyze(text)
    
    def _simple_analyze(self, text: str) -&gt; Tuple[str, float]:
        """简单的备选情感分析（当模型不可用时）"""
        import random
        
        positive_words = ['赞', '好', '棒', '优秀', '喜欢', '完美', '爱', '推荐', '厉害']
        negative_words = ['差', '烂', '糟', '垃圾', '不好', '差', '失望', '没用', '踩雷']
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count &gt; neg_count:
            return "positive", random.uniform(0.6, 0.95)
        elif neg_count &gt; pos_count:
            return "negative", random.uniform(0.6, 0.95)
        else:
            return "neutral", random.uniform(0.5, 0.7)
    
    def analyze_batch(self, texts: List[str]) -&gt; List[Tuple[str, float]]:
        """批量分析"""
        results = []
        for text in tqdm(texts, desc="正在分析情感"):
            results.append(self.analyze(text))
        return results


# 全局分析器实例
_sentiment_analyzer = None

def get_sentiment_analyzer() -&gt; SentimentAnalyzer:
    """获取全局分析器实例"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
