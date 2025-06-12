from django.core.management.base import BaseCommand
from diagnosis.models import FaultKnowledge
from diagnosis.services import VectorDBService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '将知识库数据同步到向量数据库'

    def handle(self, *args, **options):
        vector_db = VectorDBService()
        
        # 获取所有知识库条目
        knowledge_entries = FaultKnowledge.objects.all()
        self.stdout.write(f'找到 {knowledge_entries.count()} 条知识库条目')
        
        # 同步到向量数据库
        for knowledge in knowledge_entries:
            try:
                # 准备数据
                knowledge_data = {
                    'id': knowledge.id,
                    'category': knowledge.category.name,
                    'title': knowledge.title,
                    'symptoms': knowledge.symptoms,
                    'solution': knowledge.solution
                }
                
                # 添加到向量数据库
                if vector_db.add_knowledge(knowledge_data):
                    self.stdout.write(self.style.SUCCESS(f'成功同步知识条目: {knowledge.title}'))
                else:
                    self.stdout.write(self.style.ERROR(f'同步知识条目失败: {knowledge.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理知识条目时出错: {knowledge.title}, 错误: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('同步完成')) 