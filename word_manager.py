import json
import os
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Optional
import uuid
from datetime import datetime, date
from logger import logger
from utils import resource_path

class WordType(Enum):
    N = "n"  # 名词
    VT = "vt"  # 他动词
    VI = "vi"  # 自动词
    VT_VI = "vt/vi"  # 他自动词
    ADJ1 = "adj1"  # い形容词
    ADJ2 = "adj2"  # な形容词
    FOREIGN = "外来词"
    MIMETIC = "拟声词"  # 拟声词
    ELSE = "else"

@dataclass
class Word:
    id: str
    japanese: str
    word_type: str
    explanation: str
    remembered: bool = False
    created_time: str = ""
    last_review_time: str = ""
    
    def __post_init__(self):
        if not self.created_time:
            self.created_time = datetime.now().date().isoformat()

class WordManager:
    def __init__(self, data_file="words_data.json"):
        self.data_file = resource_path(data_file)
        self.words = []
        self.load_data()
    
    def load_data(self):
        """从JSON文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.words = [Word(**word_data) for word_data in data]
            except Exception as e:
                logger.error(f"加载数据失败: {e}")
                self.words = []
        else:
            self.words = []
    
    def save_data(self):
        """保存数据到JSON文件"""
        try:
            data = [asdict(word) for word in self.words]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def add_word(self, japanese: str, word_type: str, explanation: str) -> Word:
        """添加新单词"""
        word = Word(
            id=str(uuid.uuid4()),
            japanese=japanese,
            word_type=word_type,
            explanation=explanation
        )
        self.words.append(word)
        self.save_data()
        return word
    
    def delete_words(self, word_ids: List[str]):
        """删除指定ID的单词"""
        self.words = [word for word in self.words if word.id not in word_ids]
        self.save_data()
    
    def update_word(self, word_id: str, **kwargs):
        """更新单词信息"""
        for word in self.words:
            if word.id == word_id:
                for key, value in kwargs.items():
                    if hasattr(word, key):
                        setattr(word, key, value)
                break
        self.save_data()
    
    def get_review_words(self, count: int = 10, word_type: Optional[str] = None) -> List[Word]:
        """根据复习算法获取单词列表"""
        today = date.today()
        word_scores = []

        source_words = self.words
        if word_type:
            source_words = [word for word in self.words if word.word_type == word_type]

        for word in source_words:
            try:
                review_date_str = word.last_review_time or word.created_time
                review_date = date.fromisoformat(review_date_str)
                days_diff = (today - review_date).days
            except (ValueError, TypeError):
                # 如果日期格式无效或不存在，则给予一个较高的分数
                days_diff = 365  

            x = 7 if not word.remembered else 0
            score = days_diff + x
            word_scores.append((score, word))
        
        # 按分数降序排序
        word_scores.sort(key=lambda x: x[0], reverse=True)
        
        # 返回得分最高的N个单词
        return [word for score, word in word_scores[:count]]

    def get_words_by_type(self, word_type: str) -> List[Word]:
        """获取指定类型的单词"""
        return [word for word in self.words if word.word_type == word_type]
    
    def search_words(self, keyword: str) -> List[Word]:
        """搜索包含关键词的单词"""
        if not keyword:
            return []
        keyword = keyword.lower()
        return [word for word in self.words if keyword in word.japanese.lower() or keyword in word.explanation.lower()]
        
    def get_word_by_id(self, word_id: str) -> Optional[Word]:
        """根据ID获取单词"""
        for word in self.words:
            if word.id == word_id:
                return word
        return None 