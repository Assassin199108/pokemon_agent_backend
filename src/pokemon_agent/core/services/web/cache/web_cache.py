# -*- coding: utf-8 -*-
"""
Web缓存管理类
提供LRU缓存、统计管理和缓存操作功能
"""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class WebCache:
    """
    Web内容缓存管理类

    功能：
    - LRU缓存机制
    - 缓存统计管理
    - 缓存键生成和验证
    - 缓存存取操作
    """

    def __init__(self, max_size: int = 100, expire_days: int = 1):
        """
        初始化缓存

        Args:
            max_size: 最大缓存数量
            expire_days: 缓存过期天数
        """
        self.max_size = max_size
        self.expire_days = expire_days

        # 缓存统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }

        # 缓存数据存储
        self.cache_data: Dict[str, str] = {}

        logger.info(f"WebCache初始化完成，最大缓存: {max_size}, 过期时间: {expire_days}天")

    def _generate_cache_key(self, url: str) -> str:
        """
        生成缓存键

        Args:
            url: 目标URL

        Returns:
            缓存键字符串
        """
        # 基于URL和日期生成缓存键
        expire_date = time.strftime("%Y-%m-%d", time.time() - (self.expire_days * 86400))
        combined = f"{url}_{expire_date}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        检查缓存是否有效

        Args:
            cache_key: 缓存键

        Returns:
            是否有效
        """
        # 检查缓存是否存在
        if cache_key not in self.cache_data:
            return False

        # 基于日期检查缓存是否过期
        current_date = time.strftime("%Y-%m-%d")
        cache_date = time.strftime("%Y-%m-%d", time.time() - (self.expire_days * 86400))

        # 如果缓存键中的日期早于过期日期，则缓存无效
        return cache_date >= current_date

    def _cleanup_cache(self):
        """
        清理过期缓存和超出大小的缓存
        """
        # 清理过期缓存
        expired_keys = []
        for key in self.cache_data.keys():
            if not self._is_cache_valid(key):
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache_data[key]

        # 如果仍然超过大小限制，删除最旧的条目
        if len(self.cache_data) > self.max_size:
            # 简单的LRU：删除字典的前20%个条目
            keys_to_remove = list(self.cache_data.keys())[:int(self.max_size * 0.2)]
            for key in keys_to_remove:
                del self.cache_data[key]

        if expired_keys or len(self.cache_data) > self.max_size:
            logger.info(f"缓存清理完成，删除了 {len(expired_keys)} 个过期条目")

    def get(self, url: str) -> Optional[str]:
        """
        从缓存获取数据

        Args:
            url: 目标URL

        Returns:
            缓存的数据或None
        """
        self.stats["total_requests"] += 1

        cache_key = self._generate_cache_key(url)

        # 检查缓存是否存在且有效
        if cache_key in self.cache_data and self._is_cache_valid(cache_key):
            self.stats["hits"] += 1
            logger.info(f"缓存命中！URL: {url}")

            # 每10次命中记录一次统计
            if self.stats["hits"] % 10 == 0:
                self.log_stats()

            return self.cache_data[cache_key]

        # 缓存未命中
        self.stats["misses"] += 1
        logger.info(f"缓存未命中，URL: {url}")

        # 每10次未命中记录一次统计
        if self.stats["misses"] % 10 == 0:
            self.log_stats()

        return None

    def set(self, url: str, data: str):
        """
        将数据存入缓存

        Args:
            url: 目标URL
            data: 要缓存的数据
        """
        cache_key = self._generate_cache_key(url)

        # 清理缓存
        self._cleanup_cache()

        # 存入缓存
        self.cache_data[cache_key] = data
        logger.info(f"数据已缓存，URL: {url}")

    def is_cached(self, url: str) -> bool:
        """
        检查URL是否已缓存

        Args:
            url: 目标URL

        Returns:
            是否已缓存
        """
        cache_key = self._generate_cache_key(url)
        return cache_key in self.cache_data and self._is_cache_valid(cache_key)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        total = self.stats["total_requests"]
        if total == 0:
            return {
                "hits": 0,
                "misses": 0,
                "total_requests": 0,
                "hit_rate": 0.0,
                "cache_size": len(self.cache_data)
            }

        hit_rate = self.stats["hits"] / total
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "total_requests": total,
            "hit_rate": round(hit_rate * 100, 2),
            "cache_size": len(self.cache_data)
        }

    def clear(self):
        """
        清空所有缓存
        """
        self.cache_data.clear()
        logger.info("所有缓存数据已清空")

    def reset_stats(self):
        """
        重置缓存统计
        """
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }
        logger.info("缓存统计已重置")

    def print_info(self):
        """
        打印缓存详细信息
        """
        stats = self.get_stats()
        print("=== 缓存统计信息 ===")
        print(f"总请求数: {stats['total_requests']}")
        print(f"缓存命中: {stats['hits']}")
        print(f"缓存未命中: {stats['misses']}")
        print(f"命中率: {stats['hit_rate']}%")
        print(f"当前缓存大小: {stats['cache_size']}")
        print(f"最大缓存大小: {self.max_size}")
        print(f"缓存过期天数: {self.expire_days}")
        print("=================")

    def log_stats(self):
        """
        记录缓存统计到日志
        """
        stats = self.get_stats()
        logger.info(f"缓存统计 - 总请求: {stats['total_requests']}, 命中: {stats['hits']}, "
                   f"未命中: {stats['misses']}, 命中率: {stats['hit_rate']}%, "
                   f"缓存大小: {stats['cache_size']}/{self.max_size}")

    def get_cached_urls(self) -> List[str]:
        """
        获取所有缓存的键（调试用）

        Returns:
            缓存键列表
        """
        return list(self.cache_data.keys())

    def get_size_info(self) -> Dict[str, int]:
        """
        获取缓存大小信息

        Returns:
            大小信息字典
        """
        return {
            "current_size": len(self.cache_data),
            "max_size": self.max_size,
            "available_space": max(0, self.max_size - len(self.cache_data))
        }