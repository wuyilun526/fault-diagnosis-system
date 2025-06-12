from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from dashscope import Generation
import logging
import json
import traceback
import re
from .models import FaultCase
from .serializers import FaultCaseSerializer
from knowledge_base.models import FaultCategory, FaultKnowledge
import os
import dashscope
from .services import VectorDBService

logger = logging.getLogger(__name__)

def clean_json_string(json_str):
    """清理 JSON 字符串，移除控制字符并处理换行符"""
    # 1. 移除所有控制字符
    json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str)
    # 2. 将换行符替换为空格
    json_str = re.sub(r'\n', ' ', json_str)
    # 3. 将多个空格替换为单个空格
    json_str = re.sub(r'\s+', ' ', json_str)
    return json_str

class FaultCaseViewSet(viewsets.ModelViewSet):
    queryset = FaultCase.objects.all()
    serializer_class = FaultCaseSerializer
    permission_classes = [AllowAny]
    vector_db = VectorDBService()

    def clean_json_string(self, json_str):
        """清理JSON字符串，移除控制字符和多余空白"""
        if not json_str:
            return None
            
        # 移除 Markdown 代码块标记
        json_str = json_str.replace('```json', '').replace('```', '')
        
        # 查找第一个 { 和最后一个 } 之间的内容
        start = json_str.find('{')
        end = json_str.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = json_str[start:end]
        else:
            logger.error(f"Could not find JSON in response: {json_str}")
            return None
        
        # 移除所有控制字符
        json_str = ''.join(char for char in json_str if ord(char) >= 32)
        
        # 替换换行符为空格
        json_str = json_str.replace('\n', ' ')
        
        # 替换多个空格为单个空格
        json_str = re.sub(r'\s+', ' ', json_str)
        
        # 移除开头和结尾的空白字符
        json_str = json_str.strip()
        
        return json_str

    def find_matching_knowledge(self, category_name, alert_info):
        """使用向量数据库查找匹配的知识条目"""
        try:
            # 使用向量数据库搜索相似的知识条目
            matched_knowledge_list = self.vector_db.search_knowledge(alert_info, top_k=1)
            
            if not matched_knowledge_list:
                logger.info("No matching knowledge found in vector database")
                return None

            # 获取最匹配的知识条目
            matched_knowledge = matched_knowledge_list[0]
            logger.info(f"Found matching knowledge: {matched_knowledge['title']} with score: {matched_knowledge['score']}")

            # 如果相似度分数太低，认为没有匹配的知识
            if matched_knowledge['score'] > 0.8:  # 可以根据实际情况调整阈值
                logger.info("Similarity score too low, no matching knowledge")
                return None

            # 返回匹配的知识条目
            return FaultKnowledge.objects.get(id=matched_knowledge['id'])
        except Exception as e:
            logger.error(f"Error finding matching knowledge: {str(e)}")
            return None

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        try:
            logger.info("Received request data: %s", request.data)
            
            # 获取请求数据
            alert_info = request.data.get('alert_info', '')
            metrics_info = request.data.get('metrics_info', '')
            log_info = request.data.get('log_info', '')

            # 验证必填字段
            if not alert_info:
                return Response(
                    {'error': '告警信息不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 先从知识库中检索相关的知识条目
            # 只使用告警信息进行检索，避免其他信息干扰
            alert_relate_info = alert_info
            matched_knowledge_list = self.vector_db.search_knowledge(alert_relate_info, top_k=3)
            logger.info("Found %d matching knowledge entries", len(matched_knowledge_list))

            # 构建提示词
            prompt = f"""作为一个故障诊断专家，请分析以下故障信息，并提供诊断结果。
请以JSON格式返回，包含以下字段：
- category: 故障分类（请根据故障特征给出最合适的分类）
- analysis: 分析结果
- solution: 解决方案

故障信息：
告警信息：{alert_info}
"""

            # 如果有指标信息，添加到提示词中
            if metrics_info:
                prompt += f"指标信息：{metrics_info}\n"

            # 如果有日志信息，添加到提示词中
            if log_info:
                prompt += f"日志信息：{log_info}\n"

            # 如果有匹配的知识条目，添加到提示词中作为参考
            if matched_knowledge_list:
                prompt += "\n参考知识库中的相关案例：\n"
                for knowledge in matched_knowledge_list:
                    prompt += f"""
案例标题：{knowledge['title']}
故障分类：{knowledge['category']}
症状描述：{knowledge['symptoms']}
解决方案：{knowledge['solution']}
相似度：{knowledge['score']:.2f}
---"""

            prompt += "\n请基于以上信息，特别是参考知识库中的相关案例，给出准确的诊断结果。请确保返回的是合法的JSON格式。"

            # 记录完整的 prompt
            logger.info("Final prompt for LLM:\n%s", prompt)

            # 检查API密钥
            api_key = os.getenv('DASHSCOPE_API_KEY')
            if not api_key:
                logger.error("DASHSCOPE_API_KEY not set")
                return Response(
                    {'error': 'API密钥未配置'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 设置API密钥
            dashscope.api_key = api_key

            # 调用API
            try:
                response = Generation.call(
                    model='qwen-max',
                    prompt=prompt,
                    result_format='message',
                    max_tokens=1500,
                    temperature=0.7,
                    top_p=0.8,
                )
                logger.info("API Response: %s", response)
            except Exception as e:
                logger.error("API call failed: %s", str(e))
                return Response(
                    {'error': f'API调用失败: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if response.status_code != 200:
                logger.error("API returned error: %s", response)
                return Response(
                    {'error': f'API返回错误: {response.message}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 获取API响应内容
            try:
                content = response.output.choices[0].message.content
                logger.info("API Response content: %s", content)
            except (AttributeError, IndexError) as e:
                logger.error("Failed to get API response content: %s", str(e))
                return Response(
                    {'error': '无法获取API响应内容'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 清理并解析JSON
            try:
                # 清理JSON字符串
                cleaned_content = self.clean_json_string(content)
                if not cleaned_content:
                    logger.error("Cleaned content is empty")
                    return Response(
                        {'error': 'API返回内容为空'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                # 尝试解析JSON
                result = json.loads(cleaned_content)
                logger.info("Parsed JSON result: %s", result)
            except json.JSONDecodeError as e:
                logger.error("JSON parsing error: %s", str(e))
                logger.error("Failed content: %s", cleaned_content)
                return Response(
                    {'error': f'JSON解析错误: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 验证返回的JSON格式
            required_fields = ['category', 'analysis', 'solution']
            if not all(field in result for field in required_fields):
                logger.error("Missing required fields in JSON response")
                return Response(
                    {'error': 'API返回的JSON格式不正确，缺少必要字段'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 保存诊断结果
            case = FaultCase.objects.create(
                alert_info=alert_info,
                metrics_info=metrics_info,
                log_info=log_info,
                analysis_result=json.dumps(result)
            )

            # 如果找到匹配的知识条目，记录最匹配的一条
            if matched_knowledge_list:
                best_match = matched_knowledge_list[0]
                # 降低相似度阈值到 5%，因为我们现在使用百分比
                if best_match['score'] > 5:  # 相似度阈值
                    case.matched_knowledge_id = best_match['id']
                    case.save()
                    logger.info(f"Matched knowledge with score: {best_match['score']:.2f}%")
                else:
                    logger.info(f"No knowledge matched, best score: {best_match['score']:.2f}%")

            # 添加参考的知识库案例到返回结果中
            reference_cases = []
            if matched_knowledge_list:
                for knowledge in matched_knowledge_list:
                    if knowledge['score'] > 5:  # 只返回相似度大于5%的案例
                        reference_cases.append({
                            'id': knowledge['id'],
                            'title': knowledge['title'],
                            'category': knowledge['category'],
                            'symptoms': knowledge['symptoms'],
                            'solution': knowledge['solution'],
                            'similarity': f"{knowledge['score']:.2f}%"
                        })

            return Response({
                'id': case.id,
                'category': result['category'],
                'analysis': result['analysis'],
                'solution': result['solution'],
                'matched_knowledge_id': case.matched_knowledge_id,
                'reference_cases': reference_cases  # 添加参考案例
            })

        except Exception as e:
            logger.error("Unexpected error in analyze endpoint: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            return Response(
                {'error': f'服务器内部错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
