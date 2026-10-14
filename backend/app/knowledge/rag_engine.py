from typing import Any


class KnowledgeService:
    """
    RAG Knowledge Layer abstraction storing semantic embeddings of NEXORA sales playbooks,
    past successful outreach, project history, and RFP templates.
    """
    def __init__(self):
        # Pre-populated enterprise knowledge base snippets
        self._knowledge_base: list[dict[str, Any]] = [
            {
                "id": "kb_playbook_01",
                "title": "NEXORA Enterprise Expansion Playbook",
                "category": "sales_playbook",
                "content": "For target companies in expansion mode, highlight NEXORA's Rapid Scale-Up Services, Automated Pipeline Integration, and Executive Dashboard visibility. Focus on reducing time-to-market and operational friction.",
                "keywords": ["expansion", "growth", "scale", "infrastructure", "pipeline"]
            },
            {
                "id": "kb_playbook_02",
                "title": "NEXORA Tech Stack Modernization Guide",
                "category": "technical_offerings",
                "content": "When pursuing companies modernizing legacy systems, position NEXORA Agentic AI Architecture, Event-Driven Integrations, and PostgreSQL source-of-truth migration capabilities.",
                "keywords": ["tech", "legacy", "modernization", "architecture", "ai", "postgresql"]
            },
            {
                "id": "kb_outreach_01",
                "title": "High Converting C-Suite Cold Outreach Template",
                "category": "outreach_template",
                "content": "Subject: Alignment on {company_name}'s upcoming {project_name}\nBody: Hello {first_name}, noticed {company_name}'s expansion into {location}. At NEXORA, we've helped similar market leaders streamline operational pursuits with 40% higher conversion.",
                "keywords": ["outreach", "c-suite", "template", "conversion", "email"]
            }
        ]

    def search(self, query: str, top_k: int = 2) -> list[dict[str, Any]]:
        query_words = set(query.lower().split())
        scored = []
        for doc in self._knowledge_base:
            score = 0
            doc_text = (doc["title"] + " " + doc["content"]).lower()
            for word in query_words:
                if len(word) > 2 and word in doc_text:
                    score += 1.0
            for kw in doc.get("keywords", []):
                if kw in query_words:
                    score += 2.0
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]
        if not results:
            results = self._knowledge_base[:top_k]
        return results


knowledge_service = KnowledgeService()
