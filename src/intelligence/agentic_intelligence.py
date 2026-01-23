"""
Agentic Intelligence - Main decision-making engine.
Layer 3: Decides how to handle tasks based on complexity and risk.
"""

import asyncio
from typing import Dict, Optional

from src.models.enhancements.task_analysis import (
    AgenticDecision,
    ApproachDecision,
    ComplexityScore,
    RiskScore,
    TaskAnalysisResult
)
from src.intelligence.task_analyzer import TaskAnalyzer
from src.intelligence.complexity_scorer import ComplexityScorer


class AgenticIntelligence:
    """
    Main intelligence layer - decides task approach.

    This is the core that makes the agent "agentic".
    Combines all 3 layers: Analysis → Scoring → Decision
    """

    # Decision thresholds (tunable)
    THRESHOLDS = {
        'complexity_spec_required': 0.7,   # >= 0.7 → need spec
        'risk_spec_required': 0.6,         # >= 0.6 → need spec
        'min_confidence': 0.6,             # < 0.6 → ask for clarification
        'proactive_threshold': 0.8,        # >= 0.8 → suggest proactively
        'min_steps_for_spec': 5,           # >= 5 steps → need spec
    }

    def __init__(
        self,
        ai_client=None,
        history_db=None,
        handbook_rules: Dict = None
    ):
        """
        Initialize agentic intelligence.

        Args:
            ai_client: AI client for complex analysis
            history_db: Database for finding similar past tasks
            handbook_rules: Company handbook rules
        """
        self.analyzer = TaskAnalyzer(ai_client, history_db)
        self.scorer = ComplexityScorer(handbook_rules)
        self.handbook_rules = handbook_rules or {}

    async def decide(self, user_request: str) -> AgenticDecision:
        """
        Analyze request and decide approach.

        This is the main entry point for agentic intelligence.

        Examples:
            1. Simple: "Send email to John" → EXECUTE_DIRECTLY
            2. Complex: "Build Odoo sales pipeline" → SPEC_DRIVEN
            3. Ambiguous: "Handle that thing" → CLARIFICATION_NEEDED
            4. Proactive: User just got urgent email → PROACTIVE_SUGGEST

        Args:
            user_request: Raw user request

        Returns:
            AgenticDecision with approach and reasoning
        """
        # Layer 1: Analyze task
        analysis = await self.analyzer.analyze(user_request)

        # Layer 2: Score complexity and risk
        complexity = self.scorer.score_complexity(analysis)
        risk = self.scorer.score_risk(analysis, self.handbook_rules)

        # Layer 3: Make decision
        approach = self._decide_approach(analysis, complexity, risk)
        confidence = self._calculate_confidence(analysis, complexity, risk)
        reasoning = self._build_reasoning(analysis, complexity, risk, approach)
        next_steps = self._recommend_next_steps(approach, analysis, complexity, risk)

        return AgenticDecision(
            approach=approach,
            confidence=confidence,
            reasoning=reasoning,
            complexity=complexity,
            risk=risk,
            recommended_next_steps=next_steps,
            approval_required=risk.requires_approval,
            estimated_duration=complexity.estimated_time
        )

    def _decide_approach(
        self,
        analysis: TaskAnalysisResult,
        complexity: ComplexityScore,
        risk: RiskScore
    ) -> ApproachDecision:
        """
        Core decision logic - determines the approach.

        Decision tree:
        1. Too ambiguous? → CLARIFICATION_NEEDED
        2. High complexity? → SPEC_DRIVEN
        3. High risk? → SPEC_DRIVEN
        4. Many steps? → SPEC_DRIVEN
        5. External + complex? → SPEC_DRIVEN
        6. Financial? → SPEC_DRIVEN
        7. Otherwise → EXECUTE_DIRECTLY

        Args:
            analysis: Task analysis
            complexity: Complexity score
            risk: Risk score

        Returns:
            Recommended approach
        """
        # Check for ambiguities first
        if len(analysis.ambiguities) > 2:
            return ApproachDecision.CLARIFICATION_NEEDED

        # Check confidence
        if analysis.confidence < self.THRESHOLDS['min_confidence']:
            return ApproachDecision.CLARIFICATION_NEEDED

        # High complexity → need spec
        if complexity.overall_score >= self.THRESHOLDS['complexity_spec_required']:
            return ApproachDecision.SPEC_DRIVEN

        # High risk → need spec
        if risk.overall_score >= self.THRESHOLDS['risk_spec_required']:
            return ApproachDecision.SPEC_DRIVEN

        # Many steps → need spec
        if complexity.estimated_steps >= self.THRESHOLDS['min_steps_for_spec']:
            return ApproachDecision.SPEC_DRIVEN

        # External communications + moderate complexity → need spec
        if risk.factors.get('external_comms', 0) >= 0.7 and complexity.overall_score >= 0.4:
            return ApproachDecision.SPEC_DRIVEN

        # Financial transactions → always spec (safety first)
        if risk.factors.get('financial_impact', 0) > 0:
            return ApproachDecision.SPEC_DRIVEN

        # Requires approval → spec-driven for traceability
        if risk.requires_approval:
            return ApproachDecision.SPEC_DRIVEN

        # Otherwise, execute directly
        return ApproachDecision.EXECUTE_DIRECTLY

    def _calculate_confidence(
        self,
        analysis: TaskAnalysisResult,
        complexity: ComplexityScore,
        risk: RiskScore
    ) -> float:
        """
        Calculate confidence in the decision.

        Args:
            analysis: Task analysis
            complexity: Complexity score
            risk: Risk score

        Returns:
            Confidence score 0-1
        """
        confidence = 1.0

        # Start with analysis confidence
        confidence = analysis.confidence

        # Reduce confidence for ambiguities
        confidence -= len(analysis.ambiguities) * 0.1

        # Reduce confidence for complexity/risk mismatch
        # (High complexity but low risk is unusual)
        if complexity.overall_score > 0.8 and risk.overall_score < 0.3:
            confidence -= 0.15

        # Reduce confidence if no similar past tasks
        if not analysis.similar_past_tasks:
            confidence -= 0.05

        # Reduce confidence for very high complexity
        if complexity.overall_score >= 0.9:
            confidence -= 0.1

        return max(confidence, 0.1)

    def _build_reasoning(
        self,
        analysis: TaskAnalysisResult,
        complexity: ComplexityScore,
        risk: RiskScore,
        approach: ApproachDecision
    ) -> list[str]:
        """
        Build human-readable reasoning for the decision.

        Args:
            analysis: Task analysis
            complexity: Complexity score
            risk: Risk score
            approach: Decided approach

        Returns:
            List of reasoning statements
        """
        reasons = []

        # Approach-specific reasoning
        if approach == ApproachDecision.EXECUTE_DIRECTLY:
            reasons.append(f"[OK] Simple task (complexity: {complexity.overall_score:.2f})")
            reasons.append(f"[OK] Low risk (risk score: {risk.overall_score:.2f})")
            reasons.append(f"[OK] Estimated {complexity.estimated_steps} step(s)")
            reasons.append(f"[OK] Can execute immediately in {complexity.estimated_time}")

        elif approach == ApproachDecision.SPEC_DRIVEN:
            # Explain why spec is needed
            if complexity.overall_score >= self.THRESHOLDS['complexity_spec_required']:
                reasons.append(f"[WARN] High complexity ({complexity.overall_score:.2f}) - needs planning")

            if risk.overall_score >= self.THRESHOLDS['risk_spec_required']:
                reasons.append(f"[WARN] Significant risk ({risk.overall_score:.2f}) - needs careful approach")

            if complexity.estimated_steps >= self.THRESHOLDS['min_steps_for_spec']:
                reasons.append(f"[WARN] Multi-step task ({complexity.estimated_steps} steps) - needs breakdown")

            if risk.factors.get('financial_impact', 0) > 0:
                amount = analysis.entities.get('amount', 'unknown')
                reasons.append(f"[MONEY] Financial transaction (${amount}) - requires spec for safety")

            if risk.requires_approval:
                reasons.append("[POLICY] Requires approval per company policy")

            reasons.append(f"[SPEC] Creating detailed spec first (est. {complexity.estimated_time})")

        elif approach == ApproachDecision.CLARIFICATION_NEEDED:
            reasons.append(f"[QUESTION] Found {len(analysis.ambiguities)} ambiguities:")
            for amb in analysis.ambiguities[:3]:  # Show top 3
                reasons.append(f"  - {amb}")
            if len(analysis.ambiguities) > 3:
                reasons.append(f"  - ... and {len(analysis.ambiguities) - 3} more")

        # Add complexity reasoning
        if complexity.reasoning:
            reasons.extend([f"  {r}" for r in complexity.reasoning[:2]])

        # Add risk reasoning
        if risk.reasoning:
            reasons.extend([f"  {r}" for r in risk.reasoning[:2]])

        return reasons

    def _recommend_next_steps(
        self,
        approach: ApproachDecision,
        analysis: TaskAnalysisResult,
        complexity: ComplexityScore,
        risk: RiskScore
    ) -> list[str]:
        """
        Recommend next steps based on approach.

        Args:
            approach: Decided approach
            analysis: Task analysis
            complexity: Complexity score
            risk: Risk score

        Returns:
            List of recommended next steps
        """
        steps = []

        if approach == ApproachDecision.EXECUTE_DIRECTLY:
            steps.append("1. Verify all required resources are available")
            steps.append(f"2. Execute task (estimated: {complexity.estimated_time})")
            steps.append("3. Log result and notify user")

        elif approach == ApproachDecision.SPEC_DRIVEN:
            steps.append("1. Generate detailed specification document")
            steps.append("2. Review spec for completeness and safety")
            if risk.requires_approval:
                steps.append("3. Submit spec for user approval")
                steps.append("4. Execute after approval")
            else:
                steps.append("3. Execute according to spec")
            steps.append("5. Validate results against spec")

        elif approach == ApproachDecision.CLARIFICATION_NEEDED:
            steps.append("1. Present ambiguities to user")
            steps.append("2. Collect clarifications")
            steps.append("3. Re-analyze with additional context")
            steps.append("4. Proceed with execution or spec generation")

        elif approach == ApproachDecision.PROACTIVE_SUGGEST:
            steps.append("1. Present suggestion to user with context")
            steps.append("2. If accepted, analyze and execute")
            steps.append("3. If rejected, learn preference")

        return steps

    async def explain_decision(self, decision: AgenticDecision) -> str:
        """
        Generate detailed explanation of decision.

        Args:
            decision: Agentic decision

        Returns:
            Human-readable explanation
        """
        explanation = []

        # Header
        explanation.append(f"Agentic Intelligence Decision")
        explanation.append(f"{'='*50}")

        # Approach
        explanation.append(f"\nRecommended Approach: {decision.approach.value.upper()}")
        explanation.append(f"Confidence: {decision.confidence:.1%}")

        # Scores
        explanation.append(f"\nAnalysis:")
        explanation.append(f"  - Complexity: {decision.complexity.overall_score:.2f} ({decision.complexity.estimated_steps} steps)")
        explanation.append(f"  - Risk: {decision.risk.overall_score:.2f}")
        explanation.append(f"  - Estimated Duration: {decision.estimated_duration}")
        explanation.append(f"  - Approval Required: {'Yes' if decision.approval_required else 'No'}")

        # Reasoning
        explanation.append(f"\nReasoning:")
        for reason in decision.reasoning:
            explanation.append(f"  {reason}")

        # Next Steps
        explanation.append(f"\nNext Steps:")
        for step in decision.recommended_next_steps:
            explanation.append(f"  {step}")

        return "\n".join(explanation)
