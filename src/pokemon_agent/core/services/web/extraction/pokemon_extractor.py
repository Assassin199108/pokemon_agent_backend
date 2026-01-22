# -*- coding: utf-8 -*-
"""
宝可梦信息提取器类
提供信息提取逻辑、结果验证和格式化输出功能
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class PokemonExtractor:
    """
    宝可梦信息提取器

    功能：
    - 信息提取逻辑
    - 结果验证
    - 格式化输出
    - 数据质量评估
    """

    def __init__(self):
        """
        初始化宝可梦信息提取器
        """
        # 定义预期的宝可梦数据结构
        self.expected_structure = {
            "types": list,
            "abilities": list,
            "base_stats": dict,
            "evolution_chain": str,
            "basic_info": dict,
            "game_info": dict
        }

        # 定义基础统计期望
        self.expected_base_stats = [
            "hp", "attack", "defense", "special_attack", "special_defense", "speed"
        ]

        logger.info("PokemonExtractor初始化完成")

    def extract_and_validate(self, llm_result: str, url: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        提取并验证宝可梦信息

        Args:
            llm_result: LLM处理结果
            url: 来源URL

        Returns:
            tuple: (success, result, error_message)
        """
        try:
            # 解析JSON
            extracted_data = json.loads(llm_result)

            # 验证数据结构
            is_valid, validation_msg = self._validate_structure(extracted_data)
            if not is_valid:
                return False, self._create_error_response("数据结构验证失败", validation_msg, url), validation_msg

            # 验证数据质量
            quality_score, quality_issues = self._assess_data_quality(extracted_data)
            if quality_score < 0.3:  # 质量分数太低
                return False, self._create_error_response("数据质量过低", f"质量评分: {quality_score:.2f}，问题: {', '.join(quality_issues)}", url), f"数据质量评分过低: {quality_score:.2f}"

            # 标准化数据格式
            standardized_data = self._standardize_data(extracted_data)

            # 创建成功响应
            success_response = {
                "success": True,
                "url": url,
                "data": standardized_data,
                "quality_score": quality_score,
                "quality_issues": quality_issues,
                "message": "宝可梦信息提取成功"
            }

            logger.info(f"宝可梦信息提取成功，质量评分: {quality_score:.2f}")
            return True, success_response, ""

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {str(e)}"
            logger.error(error_msg)
            error_response = {
                "success": False,
                "error": "LLM返回的JSON格式无效",
                "raw_output": llm_result,
                "url": url,
                "suggestion": "大模型返回了非标准格式，请尝试其他网站或重新查询",
                "error_type": "json_parsing"
            }
            return False, error_response, error_msg

        except Exception as e:
            error_msg = f"信息提取异常: {str(e)}"
            logger.error(error_msg)
            error_response = {
                "success": False,
                "error": error_msg,
                "url": url,
                "suggestion": "信息提取过程中发生异常，请尝试其他网站",
                "error_type": "extraction_error"
            }
            return False, error_response, error_msg

    def _validate_structure(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证数据结构

        Args:
            data: 要验证的数据

        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "数据必须是字典类型"

        # 检查是否包含宝可梦相关信息
        pokemon_keys = ["types", "abilities", "base_stats", "evolution_chain", "basic_info", "game_info"]
        found_keys = [key for key in pokemon_keys if key in data]

        if not found_keys:
            return False, "未检测到宝可梦相关信息"

        # 验证数据类型
        type_errors = []
        for key in found_keys:
            if key in self.expected_structure:
                expected_type = self.expected_structure[key]
                if key in data and not isinstance(data[key], expected_type):
                    type_errors.append(f"{key} 应该是 {expected_type.__name__} 类型")

        if type_errors:
            return False, f"数据类型错误: {', '.join(type_errors)}"

        # 特别验证base_stats结构
        if "base_stats" in data:
            stats = data["base_stats"]
            if not isinstance(stats, dict):
                return False, "base_stats 必须是字典类型"

            missing_stats = [stat for stat in self.expected_base_stats if stat not in stats]
            if missing_stats:
                return False, f"base_stats 缺少必要字段: {', '.join(missing_stats)}"

        return True, ""

    def _assess_data_quality(self, data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        评估数据质量

        Args:
            data: 要评估的数据

        Returns:
            tuple: (quality_score, issues)
        """
        score = 0.0
        issues = []
        max_score = 0.0

        # 评估基础信息 (最大20分)
        max_score += 20
        if "basic_info" in data and data["basic_info"]:
            basic_info = data["basic_info"]
            if isinstance(basic_info, dict):
                if basic_info.get("name"):
                    score += 5
                else:
                    issues.append("缺少名称信息")

                if basic_info.get("national_dex_number"):
                    score += 5
                else:
                    issues.append("缺少全国图鉴编号")

                if basic_info.get("types") or ("types" in data and data["types"]):
                    score += 5
                else:
                    issues.append("缺少属性信息")

                if basic_info.get("height") or basic_info.get("weight"):
                    score += 5
                else:
                    issues.append("缺少身高体重信息")
        else:
            issues.append("缺少基本信息")

        # 评估战斗数据 (最大30分)
        max_score += 30
        if "base_stats" in data and data["base_stats"]:
            stats = data["base_stats"]
            valid_stats = 0
            for stat in self.expected_base_stats:
                if stat in stats and stats[stat]:
                    valid_stats += 1

            score += (valid_stats / len(self.expected_base_stats)) * 30
            if valid_stats < len(self.expected_base_stats):
                issues.append(f"基础数据不完整 ({valid_stats}/{len(self.expected_base_stats)})")
        else:
            issues.append("缺少基础战斗数据")

        # 评估特性信息 (最大15分)
        max_score += 15
        if "abilities" in data and data["abilities"]:
            abilities = data["abilities"]
            if isinstance(abilities, list) and len(abilities) > 0:
                score += min(len(abilities) * 5, 15)
            else:
                issues.append("特性信息格式不正确")
        else:
            issues.append("缺少特性信息")

        # 评估进化链信息 (最大15分)
        max_score += 15
        if "evolution_chain" in data and data["evolution_chain"]:
            evolution_text = data["evolution_chain"]
            if isinstance(evolution_text, str) and len(evolution_text.strip()) > 10:
                score += 15
            else:
                issues.append("进化链信息不完整")
        else:
            issues.append("缺少进化链信息")

        # 评估游戏信息 (最大20分)
        max_score += 20
        if "game_info" in data and data["game_info"]:
            game_info = data["game_info"]
            if isinstance(game_info, dict):
                if game_info.get("generation_introduced"):
                    score += 10
                else:
                    issues.append("缺少首次出现世代")

                if game_info.get("version_debut"):
                    score += 10
                else:
                    issues.append("缺少初次登场版本")
        else:
            issues.append("缺少游戏信息")

        # 计算最终分数
        final_score = score / max_score if max_score > 0 else 0

        logger.info(f"数据质量评估完成: {final_score:.2f}/{max_score}, 问题: {len(issues)}")
        return final_score, issues

    def _standardize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化数据格式

        Args:
            data: 原始数据

        Returns:
            标准化后的数据
        """
        standardized = {}

        # 标准化基本信息
        if "basic_info" in data:
            standardized["basic_info"] = self._standardize_basic_info(data["basic_info"])
        else:
            standardized["basic_info"] = {"name": "N/A", "national_dex_number": "N/A"}

        # 标准化属性信息
        if "types" in data:
            standardized["types"] = self._standardize_types(data["types"])
        else:
            standardized["types"] = ["N/A"]

        # 标准化特性信息
        if "abilities" in data:
            standardized["abilities"] = self._standardize_abilities(data["abilities"])
        else:
            standardized["abilities"] = ["N/A"]

        # 标准化基础数据
        if "base_stats" in data:
            standardized["base_stats"] = self._standardize_base_stats(data["base_stats"])
        else:
            standardized["base_stats"] = {stat: "N/A" for stat in self.expected_base_stats}

        # 标准化进化链
        if "evolution_chain" in data:
            standardized["evolution_chain"] = str(data["evolution_chain"]) if data["evolution_chain"] else "N/A"
        else:
            standardized["evolution_chain"] = "N/A"

        # 标准化游戏信息
        if "game_info" in data:
            standardized["game_info"] = self._standardize_game_info(data["game_info"])
        else:
            standardized["game_info"] = {"generation_introduced": "N/A", "version_debut": "N/A"}

        return standardized

    def _standardize_basic_info(self, basic_info: Dict[str, Any]) -> Dict[str, str]:
        """
        标准化基本信息

        Args:
            basic_info: 基本信息

        Returns:
            标准化后的基本信息
        """
        standardized = {
            "name": str(basic_info.get("name", "N/A")),
            "national_dex_number": str(basic_info.get("national_dex_number", "N/A")),
            "species": str(basic_info.get("species", "N/A")),
            "height": str(basic_info.get("height", "N/A")),
            "weight": str(basic_info.get("weight", "N/A")),
            "color": str(basic_info.get("color", "N/A"))
        }
        return standardized

    def _standardize_types(self, types: Any) -> List[str]:
        """
        标准化属性信息

        Args:
            types: 属性信息

        Returns:
            标准化后的属性列表
        """
        if isinstance(types, list):
            return [str(t) for t in types if t]
        elif isinstance(types, str):
            return [types] if types else ["N/A"]
        else:
            return ["N/A"]

    def _standardize_abilities(self, abilities: Any) -> List[str]:
        """
        标准化特性信息

        Args:
            abilities: 特性信息

        Returns:
            标准化后的特性列表
        """
        if isinstance(abilities, list):
            return [str(a) for a in abilities if a]
        elif isinstance(abilities, str):
            return [abilities] if abilities else ["N/A"]
        else:
            return ["N/A"]

    def _standardize_base_stats(self, base_stats: Dict[str, Any]) -> Dict[str, str]:
        """
        标准化基础数据

        Args:
            base_stats: 基础数据

        Returns:
            标准化后的基础数据
        """
        standardized = {}
        for stat in self.expected_base_stats:
            if stat in base_stats:
                standardized[stat] = str(base_stats[stat])
            else:
                standardized[stat] = "N/A"
        return standardized

    def _standardize_game_info(self, game_info: Dict[str, Any]) -> Dict[str, str]:
        """
        标准化游戏信息

        Args:
            game_info: 游戏信息

        Returns:
            标准化后的游戏信息
        """
        standardized = {
            "generation_introduced": str(game_info.get("generation_introduced", "N/A")),
            "version_debut": str(game_info.get("version_debut", "N/A")),
            "location_methods": str(game_info.get("location_methods", "N/A"))
        }
        return standardized

    def _create_error_response(self, error: str, suggestion: str, url: str) -> Dict[str, Any]:
        """
        创建错误响应

        Args:
            error: 错误信息
            suggestion: 建议信息
            url: 来源URL

        Returns:
            错误响应字典
        """
        return {
            "success": False,
            "error": error,
            "url": url,
            "suggestion": suggestion,
            "error_type": "validation_error"
        }

    def extract_key_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取关键信息摘要

        Args:
            data: 完整的宝可梦数据

        Returns:
            关键信息摘要
        """
        summary = {}

        # 基本信息
        if "basic_info" in data:
            basic_info = data["basic_info"]
            summary["name"] = basic_info.get("name", "N/A")
            summary["number"] = basic_info.get("national_dex_number", "N/A")

        # 属性
        if "types" in data and data["types"]:
            summary["types"] = data["types"]

        # 总种族值
        if "base_stats" in data:
            stats = data["base_stats"]
            total = 0
            valid_stats = 0
            for stat, value in stats.items():
                try:
                    if isinstance(value, str) and value.isdigit():
                        total += int(value)
                        valid_stats += 1
                    elif isinstance(value, (int, float)):
                        total += int(value)
                        valid_stats += 1
                except (ValueError, TypeError):
                    pass

            summary["base_stat_total"] = str(total) if valid_stats > 0 else "N/A"

        # 特性数量
        if "abilities" in data and data["abilities"]:
            summary["ability_count"] = len([a for a in data["abilities"] if a != "N/A"])

        return summary

    def get_extraction_statistics(self, extraction_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取提取统计信息

        Args:
            extraction_results: 提取结果列表

        Returns:
            统计信息
        """
        if not extraction_results:
            return {}

        total_extractions = len(extraction_results)
        successful_extractions = len([r for r in extraction_results if r.get("success", False)])

        quality_scores = []
        for result in extraction_results:
            if result.get("success", False) and "quality_score" in result:
                quality_scores.append(result["quality_score"])

        stats = {
            "total_extractions": total_extractions,
            "successful_extractions": successful_extractions,
            "success_rate": (successful_extractions / total_extractions * 100) if total_extractions > 0 else 0,
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "min_quality_score": min(quality_scores) if quality_scores else 0,
            "max_quality_score": max(quality_scores) if quality_scores else 0
        }

        return stats