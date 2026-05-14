"""
LLM路由模块 - 多模型管理与自动降级
"""
import json
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

import httpx
from loguru import logger

from config import settings


class LLMProvider(str, Enum):
    """LLM提供商"""
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    KIMI = "kimi"
    CLAUDE = "claude"


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.3
    timeout: int = 60


class LLMRouter:
    """LLM路由管理器 - 支持多模型和自动降级"""
    
    # 模型配置映射
    MODEL_CONFIGS = {
        "deepseek-chat": (LLMProvider.DEEPSEEK, "deepseek-chat"),
        "deepseek-reasoner": (LLMProvider.DEEPSEEK, "deepseek-reasoner"),
        "qwen-max": (LLMProvider.QWEN, "qwen-max"),
        "qwen-plus": (LLMProvider.QWEN, "qwen-plus"),
        "kimi": (LLMProvider.KIMI, "moonshot-v1-128k"),
        "kimi-128k": (LLMProvider.KIMI, "moonshot-v1-128k"),
        "claude": (LLMProvider.CLAUDE, "claude-3-sonnet-20240229"),
        "claude-opus": (LLMProvider.CLAUDE, "claude-3-opus-20240229"),
    }
    
    def __init__(self):
        self.configs: Dict[LLMProvider, LLMConfig] = {}
        self._init_configs()
        self.fallback_chain = self._build_fallback_chain()
    
    def _init_configs(self):
        """初始化LLM配置"""
        # DeepSeek配置
        if settings.llm.deepseek_api_key:
            self.configs[LLMProvider.DEEPSEEK] = LLMConfig(
                provider=LLMProvider.DEEPSEEK,
                api_key=settings.llm.deepseek_api_key,
                base_url=settings.llm.deepseek_base_url,
                model="deepseek-chat"
            )
        
        # 通义千问配置
        if settings.llm.qwen_api_key:
            self.configs[LLMProvider.QWEN] = LLMConfig(
                provider=LLMProvider.QWEN,
                api_key=settings.llm.qwen_api_key,
                base_url=settings.llm.qwen_base_url,
                model="qwen-max"
            )
        
        # Kimi配置
        if settings.llm.kimi_api_key:
            self.configs[LLMProvider.KIMI] = LLMConfig(
                provider=LLMProvider.KIMI,
                api_key=settings.llm.kimi_api_key,
                base_url=settings.llm.kimi_base_url,
                model="moonshot-v1-128k"
            )
        
        # Claude配置
        if settings.llm.claude_api_key:
            self.configs[LLMProvider.CLAUDE] = LLMConfig(
                provider=LLMProvider.CLAUDE,
                api_key=settings.llm.claude_api_key,
                base_url=settings.llm.claude_base_url,
                model="claude-3-sonnet-20240229"
            )
        
        if not self.configs:
            logger.warning("未配置任何LLM API密钥，请检查.env文件")
    
    def _build_fallback_chain(self) -> List[LLMProvider]:
        """构建降级链"""
        chain = []
        
        # 优先使用默认模型
        default_model = settings.llm.default_model
        if default_model in self.MODEL_CONFIGS:
            provider, _ = self.MODEL_CONFIGS[default_model]
            if provider in self.configs:
                chain.append(provider)
        
        # 添加其他可用的模型
        for provider in [LLMProvider.DEEPSEEK, LLMProvider.QWEN, LLMProvider.KIMI, LLMProvider.CLAUDE]:
            if provider in self.configs and provider not in chain:
                chain.append(provider)
        
        return chain
    
    def _get_config(self, provider: LLMProvider) -> Optional[LLMConfig]:
        """获取指定提供商的配置"""
        return self.configs.get(provider)
    
    def _build_request(self, config: LLMConfig, messages: List[Dict[str, str]], 
                       temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Dict:
        """构建API请求体"""
        return {
            "model": config.model,
            "messages": messages,
            "temperature": temperature or config.temperature,
            "max_tokens": max_tokens or config.max_tokens,
            "stream": False
        }
    
    def _parse_response(self, provider: LLMProvider, response_data: Dict) -> str:
        """解析API响应"""
        try:
            if provider == LLMProvider.CLAUDE:
                # Claude响应格式
                return response_data.get("content", [{}])[0].get("text", "")
            else:
                # OpenAI兼容格式 (DeepSeek, Qwen, Kimi)
                choices = response_data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            return ""
    
    async def _call_api(self, config: LLMConfig, messages: List[Dict[str, str]],
                        temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Optional[str]:
        """调用LLM API"""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Claude使用不同的header格式
        if config.provider == LLMProvider.CLAUDE:
            headers = {
                "x-api-key": config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        
        payload = self._build_request(config, messages, temperature, max_tokens)
        
        # Claude使用不同的API路径和payload格式
        if config.provider == LLMProvider.CLAUDE:
            system_messages = [m["content"] for m in messages if m.get("role") == "system"]
            claude_messages = [m for m in messages if m.get("role") != "system"]
            payload = {
                "model": config.model,
                "messages": claude_messages,
                "max_tokens": max_tokens or config.max_tokens,
                "temperature": temperature or config.temperature
            }
            if system_messages:
                payload["system"] = "\n\n".join(system_messages)
            url = f"{config.base_url}/messages"
        else:
            url = f"{config.base_url}/chat/completions"
        
        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return self._parse_response(config.provider, data)
        except Exception as e:
            logger.error(f"调用 {config.provider.value} API失败: {e}")
            return None
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        preferred_provider: Optional[LLMProvider] = None
    ) -> str:
        """
        发起对话，自动处理降级
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            preferred_provider: 优先使用的提供商
        
        Returns:
            LLM响应内容
        """
        # 构建降级链
        chain = []
        if preferred_provider and preferred_provider in self.configs:
            chain.append(preferred_provider)
        
        for provider in self.fallback_chain:
            if provider not in chain:
                chain.append(provider)
        
        if not chain:
            raise ValueError("没有可用的LLM提供商，请检查配置")
        
        # 依次尝试
        last_error = None
        for provider in chain:
            config = self._get_config(provider)
            if not config:
                continue
            
            logger.debug(f"尝试使用 {provider.value} 模型: {config.model}")
            
            result = await self._call_api(config, messages, temperature, max_tokens)
            
            if result:
                logger.info(f"成功使用 {provider.value} 获取响应")
                return result
            
            last_error = f"{provider.value} 调用失败"
            logger.warning(f"{provider.value} 调用失败，尝试下一个模型...")
            time.sleep(0.5)  # 短暂延迟避免过快切换
        
        raise RuntimeError(f"所有LLM模型均调用失败。最后错误: {last_error}")
    
    async def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        preferred_provider: Optional[LLMProvider] = None
    ) -> str:
        """
        分析任务专用方法
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            preferred_provider: 优先使用的提供商
        
        Returns:
            分析结果
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.chat(messages, temperature=temperature, preferred_provider=preferred_provider)
    
    async def analyze_with_long_context(
        self,
        system_prompt: str,
        user_prompt: str,
        context: str,
        temperature: float = 0.3
    ) -> str:
        """
        长文本分析，优先使用支持长上下文的模型
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            context: 长文本上下文
            temperature: 温度参数
        
        Returns:
            分析结果
        """
        # 优先使用Kimi (128K上下文)
        preferred = LLMProvider.KIMI if LLMProvider.KIMI in self.configs else None
        
        full_prompt = f"{user_prompt}\n\n【背景资料】\n{context}"
        
        return await self.analyze(system_prompt, full_prompt, temperature, preferred_provider=preferred)
    
    def is_available(self) -> bool:
        """检查是否有可用的LLM配置"""
        return len(self.configs) > 0
    
    def get_available_providers(self) -> List[str]:
        """获取所有可用的提供商列表"""
        return [p.value for p in self.configs.keys()]


# 全局LLM路由实例
llm_router = LLMRouter()
