import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from pydantic import BaseModel, Field
from crewai import Task, Crew, Process
from agents.sam import get_sam_agent


class NewsletterSummary(BaseModel):
    title: str = Field(description="文章或電子報標題")
    source: str = Field(description="電子報品牌或寄件者")
    date: str = Field(description="格式為 YYYY-MM-DD")
    topics: List[str] = Field(description="2-4 個主題標籤")
    summary: str = Field(description="3-5 句繁體中文重點摘要")
    url: str = Field(default="", description="原文連結，若無則為空字串")


def analyze_email_content(subject: str, sender: str, date: str, body: str) -> dict:
    """接收來自 API/n8n 的信件文字，交由 Sam 進行摘要提煉，回傳 dict"""
    sam = get_sam_agent()

    newsletter_task = Task(
        description=(
            f"請深度分析以下電子報內容，並精準提煉關鍵資訊：\n\n"
            f"【郵件主旨】: {subject}\n"
            f"【寄件者】: {sender}\n"
            f"【日期】: {date}\n"
            f"【郵件內文】:\n{body[:3500]}\n\n"
            f"請提煉出以下欄位（全部使用繁體中文撰寫，topics 可中英混用）：\n"
            f"- title: 精準的文章/電子報標題\n"
            f"- source: 電子報品牌或出版者名稱（可直接參考寄件者）\n"
            f"- date: 格式為 YYYY-MM-DD，若內文無明確日期則使用 {date}\n"
            f"- topics: 2-4 個關鍵主題標籤\n"
            f"- summary: 3-5 句精準摘要，提煉核心商業洞察與重要結論\n"
            f"- url: 若內文中有明確原文連結則填入，否則留空字串\n"
        ),
        expected_output="一個符合 NewsletterSummary 結構的物件，欄位需完整填寫。",
        agent=sam,
        output_pydantic=NewsletterSummary,
    )

    crew = Crew(
        agents=[sam],
        tasks=[newsletter_task],
        process=Process.sequential,
        verbose=True,
    )

    crew_output = crew.kickoff()
    parsed: NewsletterSummary = crew_output.pydantic
    return parsed.model_dump()
