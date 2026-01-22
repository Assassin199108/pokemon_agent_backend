"""
Pokemon Agent FastAPI 应用
实时网络检索与对战型宝可梦Multi-Agent系统API
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
import os
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from ..core.tools import PokemonInfoTool, PokemonReactTool


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic 模型
class PokemonRequest(BaseModel):
    """宝可梦查询请求"""
    pokemon_name: str = Field(
        description="宝可梦名称（支持中文或英文）",
        example="Pikachu",
        min_length=2,
        max_length=50
    )


class PokemonInfoResponse(BaseModel):
    """PokemonInfoTool响应"""
    pokemon_name: str
    source_url: str
    extraction_timestamp: str
    data: Dict[str, Any]
    error: str | None = None


class PokemonReactResponse(BaseModel):
    """PokemonReactTool响应"""
    success: bool
    pokemon_name: str
    final_answer: Dict[str, Any] | None = None
    agent_output: str | None = None
    mode: str
    error: str | None = None


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    details: str | None = None
    timestamp: str


# 全局工具实例
pokemon_info_tool: PokemonInfoTool | None = None
pokemon_react_tool: PokemonReactTool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global pokemon_info_tool, pokemon_react_tool

    # 启动时初始化工具
    logger.info("正在初始化 PokemonInfoTool...")
    pokemon_info_tool = PokemonInfoTool()
    logger.info("PokemonInfoTool 初始化完成")

    logger.info("正在初始化 PokemonReactTool...")
    pokemon_react_tool = PokemonReactTool()
    logger.info("PokemonReactTool 初始化完成")

    yield

    # 关闭时清理资源
    logger.info("正在关闭应用...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Pokemon Agent API",
    description="""
    实时网络检索与对战型宝可梦Multi-Agent系统API

    ## 功能特性

    - **直接检索模式**：快速获取宝可梦基础信息
    - **智能Agent模式**：使用ReAct模式收集详细数据
    - **双语支持**：所有信息均提供中英文对照
    - **权威来源**：优先从wiki.52poke.com等权威站点获取数据

    ## API 端点

    - `POST /api/v1/pokemon/info` - 直接检索模式
    - `POST /api/v1/pokemon/react-info` - 智能Agent模式
    - `GET /health` - 健康检查
    """,
    version="0.1.0",
    lifespan=lifespan
)


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API 端点
@app.get(
    "/health",
    tags=["health"],
    summary="健康检查",
    description="检查API服务状态"
)
async def health_check() -> Dict[str, str]:
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "0.1.0"
    }


@app.post(
    "/api/v1/pokemon/info",
    tags=["pokemon"],
    summary="获取宝可梦信息（直接模式）",
    description="""
    使用 PokemonInfoTool 直接检索宝可梦信息

    工作流程：
    1. 通过Tavily API搜索宝可梦信息
    2. 智能选择权威来源（优先wiki.52poke.com）
    3. 抓取并解析网页内容
    4. 使用LLM提取结构化数据

    特点：快速、直接，适合获取基础信息
    """,
    response_model=PokemonInfoResponse,
    responses={
        400: {"model": ErrorResponse},
        408: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_pokemon_info(request: PokemonRequest) -> PokemonInfoResponse:
    """直接检索宝可梦信息"""
    try:
        if not pokemon_info_tool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PokemonInfoTool 未初始化"
            )

        logger.info(f"开始获取宝可梦信息: {request.pokemon_name}")

        # 调用工具
        result = pokemon_info_tool.run(request.pokemon_name)

        # 检查是否有错误
        if "error" in result and result["error"]:
            error_msg = result["error"]
            if "timed out" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail=error_msg
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )

        return PokemonInfoResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取宝可梦信息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post(
    "/api/v1/pokemon/react-info",
    tags=["agent"],
    summary="智能获取宝可梦信息（ReAct模式）",
    description="""
    使用 PokemonReactTool 通过ReAct模式智能收集宝可梦信息

    工作流程：
    1. 思考分析当前信息缺口
    2. 选择合适的工具进行行动
    3. 观察工具返回结果
    4. 重复思考→行动→观察，直到信息充分

    特点：智能、全面，适合获取详细信息

    此模式会自动使用MCP工具（如果可用）以及网络搜索和内容提取工具
    """,
    response_model=PokemonReactResponse,
    responses={
        400: {"model": ErrorResponse},
        408: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_pokemon_info_react(request: PokemonRequest) -> PokemonReactResponse:
    """使用ReAct模式智能检索宝可梦信息"""
    try:
        if not pokemon_react_tool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PokemonReactTool 未初始化"
            )

        logger.info(f"开始ReAct模式获取宝可梦信息: {request.pokemon_name}")

        # 调用工具
        result = pokemon_react_tool.run(request.pokemon_name)

        # 检查是否有错误
        if not result.get("success", False):
            error_msg = result.get("error", "未知错误")
            if "timed out" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail=error_msg
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )

        return PokemonReactResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ReAct模式获取宝可梦信息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/")
async def root():
    """根路径重定向到文档"""
    return {
        "message": "Pokemon Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


# 启动函数
def main():
    """启动应用"""
    # 检查必需的环境变量
    required_vars = ["ROUTER_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"缺少必需的环境变量: {', '.join(missing_vars)}")
        logger.error("请设置以下环境变量：")
        for var in missing_vars:
            logger.error(f"  - {var}")
        return

    # 启动服务
    logger.info("启动 Pokemon Agent API 服务...")
    uvicorn.run(
        "src.pokemon_agent.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
