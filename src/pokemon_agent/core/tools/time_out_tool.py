# -*- coding: utf-8 -*-
import signal
import threading
import logging
from typing import Any, Callable, Optional, Dict
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# 超时异常类
class TimeoutError(Exception):
    """自定义超时异常"""
    pass


# 超时处理器
class TimeoutHandler:
    """基础超时处理器（上下文管理器）"""
    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, _type, _value, _traceback):
        signal.alarm(0)

    def raise_timeout(self, _signum, _frame):
        raise TimeoutError(f"Operation timed out after {self.seconds} seconds")


class TimeoutTool:
    """超时工具类，提供统一的超时处理机制"""

    def __init__(self, default_timeout: int = 30):
        """
        初始化超时工具

        Args:
            default_timeout: 默认超时时间（秒）
        """
        self.default_timeout = default_timeout
        logger.info(f"TimeoutTool初始化完成，默认超时时间: {default_timeout}秒")

    def timeout_handler(self, signum, frame):
        """信号处理器，用于超时中断"""
        raise TimeoutError(f"操作超时，超过 {self.default_timeout} 秒限制")

    @contextmanager
    def timeout_context(self, timeout: Optional[int] = None):
        """
        超时上下文管理器

        Args:
            timeout: 超时时间（秒），如果为None则使用默认值

        Yields:
            None

        Raises:
            TimeoutError: 当操作超时时
        """
        timeout_seconds = timeout or self.default_timeout

        # 设置信号处理器
        old_handler = signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            yield
        finally:
            # 恢复原来的信号处理器
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def run_with_timeout(self, func: Callable, *args, timeout: Optional[int] = None, **kwargs) -> Any:
        """
        在指定时间内运行函数，如果超时则抛出异常

        Args:
            func: 要执行的函数
            *args: 函数参数
            timeout: 超时时间（秒），如果为None则使用默认值
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果

        Raises:
            TimeoutError: 当操作超时时
            Exception: 当函数执行过程中出现其他异常时
        """
        timeout_seconds = timeout or self.default_timeout
        logger.info(f"开始执行函数 {func.__name__}，超时限制: {timeout_seconds}秒")

        result = None
        exception = None

        def worker():
            nonlocal result, exception
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                exception = e

        # 创建工作线程
        work_thread = threading.Thread(target=worker)
        work_thread.daemon = True
        work_thread.start()

        # 等待线程完成或超时
        work_thread.join(timeout_seconds)

        if work_thread.is_alive():
            # 线程仍在运行，说明超时了
            logger.warning(f"函数 {func.__name__} 执行超时 ({timeout_seconds}秒)")
            raise TimeoutError(f"函数 {func.__name__} 执行超时，超过 {timeout_seconds} 秒限制")

        if exception is not None:
            logger.error(f"函数 {func.__name__} 执行异常: {str(exception)}")
            raise exception

        logger.info(f"函数 {func.__name__} 执行成功")
        return result

    def timeout_decorator(self, timeout: Optional[int] = None):
        """
        超时装饰器

        Args:
            timeout: 超时时间（秒），如果为None则使用默认值

        Returns:
            装饰器函数
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.run_with_timeout(func, *args, timeout=timeout, **kwargs)
            return wrapper
        return decorator

    def create_timeout_error_response(self, operation: str, timeout: int, suggestion: str = "") -> Dict[str, Any]:
        """
        创建统一的超时错误响应格式

        Args:
            operation: 操作名称
            timeout: 超时时间
            suggestion: 建议信息

        Returns:
            错误响应字典
        """
        return {
            "success": False,
            "error": f"{operation}超时",
            "timeout": timeout,
            "suggestion": suggestion or f"操作超过{timeout}秒限制，请检查网络连接或稍后重试",
            "error_type": "timeout"
        }


# 全局实例
timeout_tool = TimeoutTool(default_timeout=30)


# 便捷函数
def run_with_timeout(func: Callable, *args, timeout: Optional[int] = None, **kwargs) -> Any:
    """便捷函数：在指定时间内运行函数"""
    return timeout_tool.run_with_timeout(func, *args, timeout=timeout, **kwargs)


def timeout_decorator(timeout: Optional[int] = None):
    """便捷函数：超时装饰器"""
    return timeout_tool.timeout_decorator(timeout)


def create_timeout_error_response(operation: str, timeout: int, suggestion: str = "") -> Dict[str, Any]:
    """便捷函数：创建超时错误响应"""
    return timeout_tool.create_timeout_error_response(operation, timeout, suggestion)