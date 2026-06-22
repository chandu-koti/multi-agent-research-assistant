from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMClient(ABC):
    """
    Abstract interface for LLM client operations.
    Decouples LangGraph agent state transitions from the LLM invocation code.
    """
    @abstractmethod
    def generate_plan(self, topic: str) -> Dict[str, Any]:
        """
        Generate a structured research plan for the given topic.
        
        Returns:
            Dict[str, Any] containing 'topic', 'research_questions', and 'research_plan'.
        """
        pass

    @abstractmethod
    def generate_research_notes(self, topic: str, plan: Dict[str, Any]) -> List[str]:
        """
        Synthesize detailed research notes answering the plan's questions.
        
        Returns:
            List[str] representing research notes.
        """
        pass

    @abstractmethod
    def generate_analysis(self, topic: str, research_results: List[str]) -> str:
        """
        Extract findings, opportunities, risks, and trends from research.
        
        Returns:
            str representing structured analysis.
        """
        pass

    @abstractmethod
    def generate_report(
        self, topic: str, plan: Dict[str, Any], research_results: List[str], analysis: str, sources: List[Dict[str, str]]
    ) -> str:
        """
        Compile plan, notes, analysis, and sources into a markdown document.
        
        Returns:
            str representing complete markdown report.
        """
        pass


class MockLLMClient(BaseLLMClient):
    """
    Deterministic mock implementation of the BaseLLMClient.
    Provides realistic mock responses based on templates to simulate LLM logic.
    """
    def generate_plan(self, topic: str) -> Dict[str, Any]:
        return {
            "topic": topic,
            "research_questions": [
                f"How does {topic} affect contemporary industry standards?",
                f"What are the core technical constraints in implementing {topic}?",
                f"What recent breakthroughs have shifted the trajectory of {topic}?"
            ],
            "research_plan": [
                f"Analyze foundational papers and design patterns of {topic}.",
                f"Assess integration trade-offs, benchmarks, and architectural designs.",
                f"Investigate future growth vectors, industry constraints, and open issues."
            ]
        }

    def generate_research_notes(self, topic: str, plan: Dict[str, Any]) -> List[str]:
        # During Tavily integration, ResearchAgent reads the plan and fetches search findings directly.
        # This fallback note generator serves as a backup.
        questions = plan.get("research_questions", [])
        notes = []
        for i, q in enumerate(questions, start=1):
            notes.append(
                f"Research Note {i} on '{topic}' addressing query '{q}':\n"
                f"- Foundational architectures focus heavily on latency reduction, scalability, and modular APIs.\n"
                f"- Integration benchmarks show a 40% performance improvement compared to legacy architectures."
            )
        return notes

    def generate_analysis(self, topic: str, research_results: List[str]) -> str:
        # Check if we have real search findings returned from Tavily
        has_real_results = (
            len(research_results) > 0 
            and not any("Tavily search failed" in r for r in research_results)
            and not any("No content snippet available" in r for r in research_results)
        )
        
        if has_real_results:
            snippets = []
            # Extract snippets from real results (first 3 results max)
            for i, res in enumerate(research_results[:3]):
                clean_snippet = res[:150].replace("\n", " ").strip() + "..."
                snippets.append(f"- Derived Insight {i+1}: {clean_snippet}")
            insights_str = "\n".join(snippets)
        else:
            insights_str = f"- Default Analysis: Standard baseline assessment of {topic} (web search unavailable)."

        return (
            "### KEY FINDINGS\n"
            f"- Synthesized analysis for topic '{topic}'.\n"
            f"{insights_str}\n\n"
            "### OPPORTUNITIES\n"
            f"- Leveraging live content from {topic} optimizes runtime decision latency.\n"
            "- Integrating standard configurations permits rapid prototyping.\n\n"
            "### RISKS\n"
            "- Reliance on external search APIs introduces transient query errors.\n"
            "- Scraped documents may contain unvalidated or incomplete content.\n\n"
            "### FUTURE TRENDS\n"
            "- Emergence of highly optimized web parsing filters.\n"
            "- Contextual multi-query pipelines automating web knowledge aggregation."
        )

    def generate_report(
        self, topic: str, plan: Dict[str, Any], research_results: List[str], analysis: str, sources: List[Dict[str, str]]
    ) -> str:
        questions_str = "\n".join([f"- {q}" for q in plan.get("research_questions", [])])
        
        # Parse analysis sections to map them under correct headers
        sections = {"KEY FINDINGS": "", "OPPORTUNITIES": "", "RISKS": "", "FUTURE TRENDS": ""}
        current_section = None
        for line in analysis.split("\n"):
            if "KEY FINDINGS" in line:
                current_section = "KEY FINDINGS"
                continue
            elif "OPPORTUNITIES" in line:
                current_section = "OPPORTUNITIES"
                continue
            elif "RISKS" in line:
                current_section = "RISKS"
                continue
            elif "FUTURE TRENDS" in line:
                current_section = "FUTURE TRENDS"
                continue
            
            if current_section and line.strip():
                sections[current_section] += line + "\n"

        # Build Sources section listing title and URL
        if sources:
            sources_list = []
            for src in sources:
                title = src.get("title") or "Untitled Source"
                url = src.get("url") or "#"
                sources_list.append(f"- [{title}]({url})")
            sources_str = "\n".join(sources_list)
        else:
            sources_str = "*No external sources were referenced.*"

        report = (
            f"# Executive Summary\n"
            f"This comprehensive report details the strategic and technical assessment of **{topic}**.\n"
            f"Based on our initial search planning, we evaluated current challenges and future trends.\n\n"
            f"# Research Questions\n"
            f"{questions_str}\n\n"
            f"# Key Findings\n"
            f"{sections['KEY FINDINGS'].strip()}\n\n"
            f"# Opportunities\n"
            f"{sections['OPPORTUNITIES'].strip()}\n\n"
            f"# Risks\n"
            f"{sections['RISKS'].strip()}\n\n"
            f"# Future Trends\n"
            f"{sections['FUTURE TRENDS'].strip()}\n\n"
            f"# Sources\n"
            f"{sources_str}\n\n"
            f"# Conclusion\n"
            f"The research concludes that **{topic}** represents a highly promising domain. "
            f"Addressing complexity risks early optimizes integration outcomes."
        )
        return report
