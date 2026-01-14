#!/usr/bin/env python3
"""
Educational Publishing Pipeline: Multi-Agent Orchestration

Models a real educational publishing organization with interacting agents:

┌─────────────────────────────────────────────────────────────────────────┐
│                         SENIOR EDITOR (Orchestrator)                     │
│         Manages workflow, resolves conflicts, makes final decisions      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│ SME (Writer) │◄─────────►│ Dev Editor   │◄─────────►│ Fact Checker │
│              │  feedback  │              │  feedback  │              │
│ Writes from  │           │ Shapes for   │           │ Verifies vs  │
│ evidence     │           │ learning     │           │ source docs  │
└──────────────┘           └──────────────┘           └──────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼                               ▼
           ┌──────────────┐                ┌──────────────┐
           │ Copy Editor  │                │ Assessment   │
           │              │                │ Designer     │
           │ Language &   │                │              │
           │ style polish │                │ Creates exam │
           └──────────────┘                │ questions    │
                                           └──────────────┘

Workflow:
1. SME writes initial draft from evidence
2. Dev Editor reviews for pedagogy, may request SME revision
3. Fact Checker verifies, may request SME correction
4. Copy Editor polishes language
5. Assessment Designer creates questions
6. Senior Editor integrates and resolves conflicts
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use env vars directly

# Configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-pro-preview"  # Gemini Pro 3 - highest quality
MAX_REVISION_ROUNDS = 2

# Paths
CLAIMS_FILE = Path("ops/artifacts/claims.jsonl")
CHAPTER_PLAN_FILE = Path("ops/artifacts/chapter_plan.json")
CHAPTERS_DIR = Path("book/chapters")
LOGS_DIR = Path("ops/logs/publishing_pipeline")


class ReviewDecision(Enum):
    """Possible decisions from a reviewing agent."""
    APPROVE = "approve"
    REQUEST_REVISION = "request_revision"
    REJECT = "reject"


@dataclass
class AgentFeedback:
    """Feedback from one agent to another."""
    from_agent: str
    to_agent: str
    decision: ReviewDecision
    comments: List[str]
    severity: str  # "minor", "moderate", "major"
    specific_fixes: List[Dict[str, str]]  # {"issue": ..., "suggestion": ...}


@dataclass
class AgentPass:
    """Result from a single agent pass."""
    agent_name: str
    role: str
    content: str
    score: float
    feedback_given: List[AgentFeedback]
    feedback_received: List[AgentFeedback]
    revision_round: int
    duration_seconds: float


@dataclass
class ChapterHistory:
    """Complete history of a chapter through the pipeline."""
    chapter_id: str
    title: str
    passes: List[AgentPass]
    final_content: str
    total_revisions: int
    final_scores: Dict[str, float]
    total_duration: float


# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

class BaseAgent:
    """Base class for all publishing agents."""
    
    def __init__(self, client, name: str, role: str, temperature: float = 0.3):
        self.client = client
        self.name = name
        self.role = role
        self.temperature = temperature
    
    def call_llm(self, prompt: str) -> str:
        """Make LLM API call."""
        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=self.temperature)
        )
        return response.text
    
    def parse_json_response(self, response: str, default: Dict) -> Dict:
        """Extract JSON from response."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except:
            pass
        return default


class SubjectMatterExpert(BaseAgent):
    """
    SME: Subject Matter Expert / Content Writer
    Role: Write accurate, comprehensive content from source evidence
    """
    
    SYSTEM_PROMPT = """אתה מומחה תוכן (Subject Matter Expert) בביולוגיה ווירולוגיה.
    
תפקידך: לכתוב תוכן מדויק ומקיף מבוסס אך ורק על הראיות שסופקו.

כללים:
1. השתמש רק בעובדות מהראיות. אין להמציא.
2. ציין מקורות: <!-- claim_XXXXX -->
3. הגדר כל מונח חדש: **מונח** (English)
4. כתוב בעברית אקדמית ברורה
5. מונחים מדעיים נשארים באנגלית: DNA, RNA, mRNA, MHC

אם קיבלת משוב לתיקון, התייחס באופן ספציפי לכל נקודה."""
    
    def write_draft(self, chapter_plan: Dict, evidence: str, 
                   feedback: List[AgentFeedback] = None) -> Tuple[str, float]:
        """Write or revise chapter draft."""
        
        feedback_section = ""
        if feedback:
            feedback_section = "\n\n📝 משוב לתיקון:\n"
            for fb in feedback:
                feedback_section += f"מ-{fb.from_agent}:\n"
                for comment in fb.comments:
                    feedback_section += f"  • {comment}\n"
                for fix in fb.specific_fixes:
                    feedback_section += f"  → תקן: {fix['issue']} ← {fix['suggestion']}\n"
        
        prompt = f"""
{self.SYSTEM_PROMPT}

---
פרק {chapter_plan['chapter_id']}: {chapter_plan['title']}
{feedback_section}

ראיות:
{evidence[:70000]}

---
מבנה חובה:
# פרק {chapter_plan['chapter_id']}: {chapter_plan['title']}
## מטרות למידה
## מפת דרכים  
## תוכן מרכזי (עם תתי-כותרות ###)
## תיבה: נקודת מבט של מומחה
## תיבה: מעבדה כהדגמה
## טעויות נפוצות ומלכודות
## סיכום מהיר
## מושגי מפתח

כתוב את הפרק (מינימום 1500 מילים):
"""
        
        content = self.call_llm(prompt)
        content = content.replace("```markdown", "").replace("```", "").strip()
        
        # Self-assess completeness
        score = 0.75 if feedback else 0.7
        if "## מטרות למידה" in content and "## סיכום מהיר" in content:
            score += 0.1
        if len(content.split()) > 1500:
            score += 0.1
            
        return content, min(score, 1.0)


class DevelopmentalEditor(BaseAgent):
    """
    Developmental Editor
    Role: Shape content for optimal learning and pedagogy
    """
    
    SYSTEM_PROMPT = """אתה עורך פיתוח (Developmental Editor) המתמחה בפדגוגיה.

תפקידך: לוודא שהתוכן מובנה ללמידה אפקטיבית.

בדוק:
1. האם מטרות הלמידה ברורות ומדידות?
2. האם יש התקדמות לוגית מפשוט למורכב?
3. האם יש מספיק דוגמאות והמחשות?
4. האם הסיכום תואם את המטרות?
5. האם יש סימני עדיפות למבחן (✅ חובה, ℹ️ רקע)?

אם נדרשים שינויים מבניים - בקש revision מה-SME.
אם השינויים קוסמטיים - תקן בעצמך."""
    
    def review(self, content: str, chapter_plan: Dict) -> Tuple[str, ReviewDecision, AgentFeedback, float]:
        """Review content for pedagogical quality."""
        
        prompt = f"""
{self.SYSTEM_PROMPT}

---
תוכן לבדיקה:
{content}

---
החזר JSON:
{{
    "decision": "approve" | "request_revision",
    "pedagogical_score": 0.0-1.0,
    "issues": [
        {{"type": "structure|clarity|examples|signals", "description": "...", "severity": "minor|moderate|major", "suggestion": "..."}}
    ],
    "improvements_made": ["שיפור 1", "שיפור 2"],
    "improved_content": "התוכן המשופר (אם תיקנת בעצמך)..."
}}
"""
        
        response = self.call_llm(prompt)
        data = self.parse_json_response(response, {
            "decision": "approve",
            "pedagogical_score": 0.75,
            "issues": [],
            "improvements_made": [],
            "improved_content": content
        })
        
        decision = ReviewDecision.REQUEST_REVISION if data["decision"] == "request_revision" else ReviewDecision.APPROVE
        
        # Build feedback for SME
        specific_fixes = [
            {"issue": i["description"], "suggestion": i.get("suggestion", "")}
            for i in data.get("issues", []) if i.get("severity") == "major"
        ]
        
        feedback = AgentFeedback(
            from_agent="DevelopmentalEditor",
            to_agent="SubjectMatterExpert",
            decision=decision,
            comments=[i["description"] for i in data.get("issues", [])],
            severity="major" if any(i.get("severity") == "major" for i in data.get("issues", [])) else "minor",
            specific_fixes=specific_fixes
        )
        
        improved_content = data.get("improved_content", content)
        if not improved_content or len(improved_content) < 500:
            improved_content = content
            
        return improved_content, decision, feedback, data.get("pedagogical_score", 0.75)


class FactChecker(BaseAgent):
    """
    Fact Checker
    Role: Verify all claims against source evidence
    """
    
    SYSTEM_PROMPT = """אתה בודק עובדות (Fact Checker) קפדן.

תפקידך: לוודא שכל טענה בטקסט נתמכת בראיות המקוריות.

בדוק:
1. האם כל עובדה מופיעה בראיות?
2. האם ציטוטי claim_id נכונים?
3. האם אין הגזמות או עיוותים?
4. האם מספרים ונתונים מדויקים?

סמן טענות לא נתמכות: ⚠️ [UNVERIFIED]
תקן אי-דיוקים קטנים ישירות.
בקש revision מה-SME לבעיות משמעותיות."""
    
    def verify(self, content: str, evidence: str) -> Tuple[str, ReviewDecision, AgentFeedback, float]:
        """Verify content accuracy against evidence."""
        
        prompt = f"""
{self.SYSTEM_PROMPT}

---
תוכן לאימות:
{content}

---
ראיות מקוריות:
{evidence[:50000]}

---
החזר JSON:
{{
    "decision": "approve" | "request_revision",
    "accuracy_score": 0.0-1.0,
    "verified_claims": 0,
    "unverified_claims": [
        {{"claim": "הטענה", "issue": "למה לא נתמכת", "severity": "minor|major"}}
    ],
    "corrections_made": ["תיקון 1", "תיקון 2"],
    "corrected_content": "התוכן המתוקן..."
}}
"""
        
        response = self.call_llm(prompt)
        data = self.parse_json_response(response, {
            "decision": "approve",
            "accuracy_score": 0.8,
            "unverified_claims": [],
            "corrections_made": [],
            "corrected_content": content
        })
        
        decision = ReviewDecision.REQUEST_REVISION if data["decision"] == "request_revision" else ReviewDecision.APPROVE
        
        # Build feedback
        major_issues = [c for c in data.get("unverified_claims", []) if c.get("severity") == "major"]
        
        feedback = AgentFeedback(
            from_agent="FactChecker",
            to_agent="SubjectMatterExpert",
            decision=decision,
            comments=[f"{c['claim']}: {c['issue']}" for c in data.get("unverified_claims", [])],
            severity="major" if major_issues else "minor",
            specific_fixes=[{"issue": c["claim"], "suggestion": "הסר או מצא ראיה"} for c in major_issues]
        )
        
        corrected = data.get("corrected_content", content)
        if not corrected or len(corrected) < 500:
            corrected = content
            
        return corrected, decision, feedback, data.get("accuracy_score", 0.8)


class CopyEditor(BaseAgent):
    """
    Copy Editor
    Role: Polish language, fix grammar, ensure consistency
    """
    
    SYSTEM_PROMPT = """אתה עורך לשון (Copy Editor) מקצועי.

תפקידך: לשפר את איכות השפה והעקביות.

תקן:
1. שגיאות כתיב ודקדוק
2. משפטים מסורבלים
3. חוסר עקביות במינוח
4. RTL formatting issues

שמור על:
- סגנון אקדמי אך נגיש
- מונחים באנגלית: DNA, RNA, mRNA
- הגדרות בפורמט: **מונח** (English)"""
    
    def polish(self, content: str) -> Tuple[str, float]:
        """Polish content for language quality."""
        
        prompt = f"""
{self.SYSTEM_PROMPT}

---
תוכן לעריכה:
{content}

---
החזר JSON:
{{
    "polished_content": "התוכן הערוך...",
    "edits_made": ["עריכה 1", "עריכה 2"],
    "language_score": 0.0-1.0
}}
"""
        
        response = self.call_llm(prompt)
        data = self.parse_json_response(response, {
            "polished_content": content,
            "edits_made": [],
            "language_score": 0.85
        })
        
        polished = data.get("polished_content", content)
        if not polished or len(polished) < 500:
            polished = content
            
        return polished, data.get("language_score", 0.85)


class AssessmentDesigner(BaseAgent):
    """
    Assessment Designer
    Role: Create high-quality exam questions
    """
    
    SYSTEM_PROMPT = """אתה מעצב הערכה (Assessment Designer) מומחה.

תפקידך: ליצור שאלות מבחן איכותיות.

צור:
1. 4-5 שאלות אמריקאיות (רמות שונות)
2. 2 שאלות קצרות
3. 1 שאלת חשיבה/יישום

פורמט לשאלות אמריקאיות:
1. שאלה?
   *   (א) אפשרות
   *   (ב) אפשרות
   *   (ג) אפשרות
   *   (ד) אפשרות
   **תשובה:** [אות]

הקפד:
- מסיחים סבירים (לא מגוחכים)
- רמות קושי מגוונות
- התמקדות בנקודות חובה למבחן"""
    
    def create_assessment(self, content: str, chapter_title: str) -> Tuple[str, float]:
        """Create assessment section."""
        
        prompt = f"""
{self.SYSTEM_PROMPT}

---
תוכן הפרק "{chapter_title}":
{content}

---
צור את מקטע השאלות (## שאלות לתרגול):
"""
        
        questions = self.call_llm(prompt)
        questions = questions.replace("```markdown", "").replace("```", "").strip()
        
        # Ensure proper header
        if not questions.startswith("## שאלות"):
            questions = "## שאלות לתרגול\n\n" + questions
        
        # Score based on content
        score = 0.7
        if questions.count("**תשובה:**") >= 4:
            score += 0.15
        if "שאלת חשיבה" in questions or "שאלות קצרות" in questions:
            score += 0.1
            
        return questions, min(score, 1.0)


class SeniorEditor:
    """
    Senior Editor / Orchestrator
    Role: Manage the entire publishing workflow, resolve conflicts
    """
    
    def __init__(self, client):
        self.client = client
        self.claims_map = {}
        
        # Initialize all agents
        self.sme = SubjectMatterExpert(client, "SME", "Subject Matter Expert", temperature=0.5)
        self.dev_editor = DevelopmentalEditor(client, "DevEditor", "Developmental Editor", temperature=0.3)
        self.fact_checker = FactChecker(client, "FactChecker", "Fact Checker", temperature=0.1)
        self.copy_editor = CopyEditor(client, "CopyEditor", "Copy Editor", temperature=0.2)
        self.assessment = AssessmentDesigner(client, "Assessment", "Assessment Designer", temperature=0.4)
    
    def load_claims(self) -> Dict[str, Dict]:
        """Load evidence claims."""
        if self.claims_map:
            return self.claims_map
            
        if CLAIMS_FILE.exists():
            with open(CLAIMS_FILE, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    try:
                        data = json.loads(line)
                        claim_id = f"claim_{i:05d}"
                        data["claim_id"] = claim_id
                        self.claims_map[claim_id] = data
                    except:
                        pass
        
        return self.claims_map
    
    def get_evidence(self, claim_ids: List[str]) -> str:
        """Format evidence for agents."""
        evidence = []
        for cid in claim_ids:
            if cid in self.claims_map:
                c = self.claims_map[cid]
                evidence.append(f"- [{cid}] {c['text']} ({c.get('type', 'fact')})")
        return "\n".join(evidence)
    
    def process_chapter(self, chapter_plan: Dict) -> ChapterHistory:
        """Run the complete publishing workflow for a chapter."""
        
        chapter_id = chapter_plan['chapter_id']
        title = chapter_plan['title']
        claim_ids = chapter_plan.get('claim_ids', [])
        evidence = self.get_evidence(claim_ids)
        
        print(f"\n{'='*70}")
        print(f"📚 SENIOR EDITOR: Processing Chapter {chapter_id}")
        print(f"   Title: {title}")
        print(f"{'='*70}")
        
        passes = []
        total_start = time.time()
        revision_round = 0
        content = ""
        
        # =========================================================
        # PHASE 1: Initial Draft from SME
        # =========================================================
        print("\n📝 PHASE 1: Initial Draft")
        print("   → Assigning to Subject Matter Expert...")
        
        start = time.time()
        content, sme_score = self.sme.write_draft(chapter_plan, evidence)
        
        passes.append(AgentPass(
            agent_name="SubjectMatterExpert",
            role="Initial Draft",
            content=content,
            score=sme_score,
            feedback_given=[],
            feedback_received=[],
            revision_round=0,
            duration_seconds=time.time() - start
        ))
        
        print(f"   ✓ Draft complete ({len(content.split())} words, score: {sme_score:.0%})")
        time.sleep(2)
        
        # =========================================================
        # PHASE 2: Developmental Review (with possible revision loop)
        # =========================================================
        print("\n🎓 PHASE 2: Developmental Review")
        
        for round_num in range(MAX_REVISION_ROUNDS + 1):
            print(f"   → Round {round_num + 1}: Developmental Editor reviewing...")
            
            start = time.time()
            content, decision, feedback, ped_score = self.dev_editor.review(content, chapter_plan)
            
            passes.append(AgentPass(
                agent_name="DevelopmentalEditor",
                role="Pedagogical Review",
                content=content,
                score=ped_score,
                feedback_given=[feedback] if decision == ReviewDecision.REQUEST_REVISION else [],
                feedback_received=[],
                revision_round=round_num,
                duration_seconds=time.time() - start
            ))
            
            if decision == ReviewDecision.APPROVE:
                print(f"   ✓ Approved (pedagogy: {ped_score:.0%})")
                break
            elif round_num < MAX_REVISION_ROUNDS:
                print(f"   ↺ Revision requested: {len(feedback.comments)} issues")
                print("   → Sending back to SME...")
                time.sleep(2)
                
                start = time.time()
                content, sme_score = self.sme.write_draft(chapter_plan, evidence, [feedback])
                
                passes.append(AgentPass(
                    agent_name="SubjectMatterExpert",
                    role="Revision",
                    content=content,
                    score=sme_score,
                    feedback_given=[],
                    feedback_received=[feedback],
                    revision_round=round_num + 1,
                    duration_seconds=time.time() - start
                ))
                
                print("   ✓ SME revised draft")
                revision_round = round_num + 1
            time.sleep(2)
        
        # =========================================================
        # PHASE 3: Fact Checking (with possible revision loop)
        # =========================================================
        print("\n🔍 PHASE 3: Fact Checking")
        
        for round_num in range(MAX_REVISION_ROUNDS + 1):
            print(f"   → Round {round_num + 1}: Fact Checker verifying...")
            
            start = time.time()
            content, decision, feedback, acc_score = self.fact_checker.verify(content, evidence)
            
            passes.append(AgentPass(
                agent_name="FactChecker",
                role="Accuracy Verification",
                content=content,
                score=acc_score,
                feedback_given=[feedback] if decision == ReviewDecision.REQUEST_REVISION else [],
                feedback_received=[],
                revision_round=round_num,
                duration_seconds=time.time() - start
            ))
            
            if decision == ReviewDecision.APPROVE:
                print(f"   ✓ Verified (accuracy: {acc_score:.0%})")
                break
            elif round_num < MAX_REVISION_ROUNDS:
                print(f"   ↺ Corrections needed: {len(feedback.specific_fixes)} major issues")
                print("   → Sending back to SME...")
                time.sleep(2)
                
                start = time.time()
                content, sme_score = self.sme.write_draft(chapter_plan, evidence, [feedback])
                
                passes.append(AgentPass(
                    agent_name="SubjectMatterExpert",
                    role="Accuracy Revision",
                    content=content,
                    score=sme_score,
                    feedback_given=[],
                    feedback_received=[feedback],
                    revision_round=revision_round + round_num + 1,
                    duration_seconds=time.time() - start
                ))
                
                print("   ✓ SME corrected content")
            time.sleep(2)
        
        # =========================================================
        # PHASE 4: Copy Editing (polish, no revision loop)
        # =========================================================
        print("\n✏️  PHASE 4: Copy Editing")
        print("   → Copy Editor polishing...")
        
        start = time.time()
        content, lang_score = self.copy_editor.polish(content)
        
        passes.append(AgentPass(
            agent_name="CopyEditor",
            role="Language Polish",
            content=content,
            score=lang_score,
            feedback_given=[],
            feedback_received=[],
            revision_round=0,
            duration_seconds=time.time() - start
        ))
        
        print(f"   ✓ Polished (language: {lang_score:.0%})")
        time.sleep(2)
        
        # =========================================================
        # PHASE 5: Assessment Creation
        # =========================================================
        print("\n📋 PHASE 5: Assessment Creation")
        print("   → Assessment Designer creating questions...")
        
        start = time.time()
        questions, assess_score = self.assessment.create_assessment(content, title)
        
        passes.append(AgentPass(
            agent_name="AssessmentDesigner",
            role="Question Creation",
            content=questions,
            score=assess_score,
            feedback_given=[],
            feedback_received=[],
            revision_round=0,
            duration_seconds=time.time() - start
        ))
        
        print(f"   ✓ Questions created (quality: {assess_score:.0%})")
        
        # =========================================================
        # PHASE 6: Senior Editor Final Integration
        # =========================================================
        print("\n👔 PHASE 6: Senior Editor Final Review")
        
        # Integrate questions into content
        if "## שאלות לתרגול" in content:
            # Replace existing questions section
            import re
            content = re.sub(r'## שאלות לתרגול.*', questions, content, flags=re.DOTALL)
        else:
            content += "\n\n" + questions
        
        # Calculate final scores
        final_scores = {
            "content": sme_score,
            "pedagogy": ped_score,
            "accuracy": acc_score,
            "language": lang_score,
            "assessment": assess_score,
            "overall": (sme_score + ped_score + acc_score + lang_score + assess_score) / 5
        }
        
        total_duration = time.time() - total_start
        
        print(f"\n{'─'*50}")
        print("   ✅ CHAPTER COMPLETE")
        print("   Final scores:")
        print(f"      Content:    {final_scores['content']:.0%}")
        print(f"      Pedagogy:   {final_scores['pedagogy']:.0%}")
        print(f"      Accuracy:   {final_scores['accuracy']:.0%}")
        print(f"      Language:   {final_scores['language']:.0%}")
        print(f"      Assessment: {final_scores['assessment']:.0%}")
        print("      ─────────────────")
        print(f"      OVERALL:    {final_scores['overall']:.0%}")
        print(f"   Total revisions: {revision_round}")
        print(f"   Total time: {total_duration:.1f}s")
        print(f"{'─'*50}")
        
        return ChapterHistory(
            chapter_id=chapter_id,
            title=title,
            passes=passes,
            final_content=content,
            total_revisions=revision_round,
            final_scores=final_scores,
            total_duration=total_duration
        )


class PublishingPipeline:
    """Main pipeline controller."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        self.client = None
        self.senior_editor = None
        
        if GENAI_AVAILABLE and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.senior_editor = SeniorEditor(self.client)
            print("✅ Publishing Pipeline initialized")
            print("   Agents: SME, DevEditor, FactChecker, CopyEditor, AssessmentDesigner")
            print("   Orchestrator: SeniorEditor")
        else:
            print("❌ Failed to initialize pipeline")
    
    def run(self, chapter_ids: List[str] = None) -> List[ChapterHistory]:
        """Run the full publishing pipeline."""
        
        # Load data
        self.senior_editor.load_claims()
        
        with open(CHAPTER_PLAN_FILE, 'r', encoding='utf-8') as f:
            plans = json.load(f)
        
        if chapter_ids:
            plans = [p for p in plans if p['chapter_id'] in chapter_ids]
        
        print(f"\n{'='*70}")
        print("📖 EDUCATIONAL PUBLISHING PIPELINE")
        print(f"   Chapters to process: {len(plans)}")
        print(f"   Max revision rounds: {MAX_REVISION_ROUNDS}")
        print(f"{'='*70}")
        
        results = []
        CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        for plan in plans:
            try:
                history = self.senior_editor.process_chapter(plan)
                results.append(history)
                
                # Save chapter
                filename = f"{plan['chapter_id']}_{plan['title'].replace(' ', '_').replace('/', '-')}.md"
                output_path = CHAPTERS_DIR / filename
                output_path.write_text(history.final_content, encoding='utf-8')
                print(f"\n💾 Saved: {output_path.name}")
                
                # Save history log
                log_path = LOGS_DIR / f"{plan['chapter_id']}_history.json"
                with open(log_path, 'w', encoding='utf-8') as f:
                    # Convert to serializable format
                    log_data = {
                        "chapter_id": history.chapter_id,
                        "title": history.title,
                        "total_revisions": history.total_revisions,
                        "final_scores": history.final_scores,
                        "total_duration": history.total_duration,
                        "passes": [
                            {
                                "agent": p.agent_name,
                                "role": p.role,
                                "score": p.score,
                                "revision_round": p.revision_round,
                                "duration": p.duration_seconds
                            }
                            for p in history.passes
                        ]
                    }
                    json.dump(log_data, f, ensure_ascii=False, indent=2)
                
                # Wait between chapters
                print("⏳ Waiting 10s before next chapter...")
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Failed to process chapter {plan['chapter_id']}: {e}")
                import traceback
                traceback.print_exc()
        
        # Final summary
        if results:
            avg_overall = sum(r.final_scores['overall'] for r in results) / len(results)
            total_revisions = sum(r.total_revisions for r in results)
            
            print(f"\n{'='*70}")
            print("📊 PIPELINE COMPLETE")
            print(f"   Chapters processed: {len(results)}/{len(plans)}")
            print(f"   Average quality: {avg_overall:.0%}")
            print(f"   Total revision rounds: {total_revisions}")
            print(f"{'='*70}")
        
        return results


def main():
    """Run the educational publishing pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Educational Publishing Pipeline")
    parser.add_argument("--chapters", nargs="*", help="Specific chapter IDs")
    parser.add_argument("--dry-run", action="store_true", help="Show plan only")
    args = parser.parse_args()
    
    if args.dry_run:
        with open(CHAPTER_PLAN_FILE, 'r') as f:
            plans = json.load(f)
        print("Would process:")
        for p in plans:
            print(f"  {p['chapter_id']}: {p['title']}")
        return
    
    pipeline = PublishingPipeline()
    pipeline.run(chapter_ids=args.chapters)


if __name__ == "__main__":
    main()
