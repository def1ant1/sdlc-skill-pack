from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class ConversationState(str, Enum):
    IDLE = "idle"
    EXPLORING = "exploring"
    DRAFTING_PLAN = "drafting_plan"
    REFINING_PLAN = "refining_plan"
    CREATING_WORKFLOW = "creating_workflow"
    EXECUTING_WORKFLOW = "executing_workflow"
    AWAITING_APPROVAL = "awaiting_approval"
    CURATING_KNOWLEDGE = "curating_knowledge"
    SCHEDULING_TASK = "scheduling_task"
    REVIEWING_RESULTS = "reviewing_results"


@dataclass
class ConversationContext:
    goal: str = ""
    active_artifacts: set[str] = field(default_factory=set)
    resolved_questions: set[str] = field(default_factory=set)
    paused_state: ConversationState | None = None


class ConversationStateMachine:
    """Intent-driven conversational state manager with interruption handling."""

    def __init__(self) -> None:
        self.state = ConversationState.IDLE
        self.context = ConversationContext()

    def transition(
        self,
        utterance: str,
        *,
        approved: bool | None = None,
        corrected: bool = False,
        interruption: str | None = None,
        artifacts: Iterable[str] | None = None,
        resolved_question: str | None = None,
        goal: str | None = None,
    ) -> ConversationState:
        text = utterance.lower().strip()

        if goal:
            self.context.goal = goal.strip()
        if artifacts:
            self.context.active_artifacts.update(artifacts)
        if resolved_question:
            self.context.resolved_questions.add(resolved_question.strip().lower())

        self._handle_interruption(interruption)

        if corrected:
            if self.state == ConversationState.CREATING_WORKFLOW:
                self.state = ConversationState.REFINING_PLAN
            elif self.state == ConversationState.EXECUTING_WORKFLOW:
                self.state = ConversationState.CREATING_WORKFLOW
            else:
                self.state = ConversationState.EXPLORING

        if self.state == ConversationState.AWAITING_APPROVAL and approved is not None:
            self.state = (
                ConversationState.EXECUTING_WORKFLOW if approved else ConversationState.REFINING_PLAN
            )
            return self.state

        if self._intake_needed(text):
            self.state = ConversationState.EXPLORING
        elif any(k in text for k in ["plan", "approach", "strategy"]):
            self.state = ConversationState.DRAFTING_PLAN
        elif any(k in text for k in ["refine", "change", "adjust", "update plan"]):
            self.state = ConversationState.REFINING_PLAN
        elif any(k in text for k in ["workflow", "pipeline", "automate"]):
            self.state = ConversationState.CREATING_WORKFLOW
        elif any(k in text for k in ["run", "execute", "start"]):
            self.state = ConversationState.EXECUTING_WORKFLOW
        elif any(k in text for k in ["approve", "approval", "confirm"]):
            self.state = ConversationState.AWAITING_APPROVAL
        elif any(k in text for k in ["document", "capture", "remember", "knowledge"]):
            self.state = ConversationState.CURATING_KNOWLEDGE
        elif any(k in text for k in ["schedule", "remind", "later", "tomorrow"]):
            self.state = ConversationState.SCHEDULING_TASK
        elif any(k in text for k in ["result", "review", "retrospective", "what happened"]):
            self.state = ConversationState.REVIEWING_RESULTS
        elif any(k in text for k in ["done", "thanks", "complete"]):
            self.state = ConversationState.IDLE

        return self.state

    def _intake_needed(self, utterance: str) -> bool:
        question = utterance.strip("? ")
        if not question:
            return False
        if question in self.context.resolved_questions:
            return False
        intake_terms = ["help", "need", "figure out", "not sure", "what should"]
        return any(term in utterance for term in intake_terms)

    def _handle_interruption(self, interruption: str | None) -> None:
        if not interruption:
            return

        action = interruption.lower().strip()
        if action == "pause":
            self.context.paused_state = self.state
            self.state = ConversationState.IDLE
        elif action == "switch":
            self.state = ConversationState.EXPLORING
        elif action == "forget":
            self.context.goal = ""
            self.context.active_artifacts.clear()
            self.context.resolved_questions.clear()
            self.context.paused_state = None
            self.state = ConversationState.IDLE
        elif action == "resume" and self.context.paused_state:
            self.state = self.context.paused_state
            self.context.paused_state = None
