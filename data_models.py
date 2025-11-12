"""Data models for the XN Mental Health Chatbot."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class SeverityLevel(Enum):
    """Severity levels for mental health concerns."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRISIS = "crisis"

class ResourceType(Enum):
    """Types of mental health resources."""
    COUNSELING = "counseling"
    CRISIS_SUPPORT = "crisis_support"
    ACADEMIC_SUPPORT = "academic_support"
    PEER_SUPPORT = "peer_support"
    WELLNESS = "wellness"
    MINDBRIDGE_BENEFIT = "mindbridge_benefit"

@dataclass
class MentalHealthScenario:
    """Represents a mental health scenario with associated metadata."""
    id: str
    title: str
    description: str
    keywords: List[str]
    severity: SeverityLevel
    category: str
    common_triggers: List[str] = field(default_factory=list)
    recommended_resources: List[str] = field(default_factory=list)
    response_templates: List[str] = field(default_factory=list)

@dataclass
class Resource:
    """Represents a mental health resource or service."""
    id: str
    name: str
    description: str
    resource_type: ResourceType
    contact_info: Dict[str, str] = field(default_factory=dict)
    availability: str = ""
    cost: str = "Free"
    eligibility: List[str] = field(default_factory=list)
    website: Optional[str] = None
    is_crisis_resource: bool = False

@dataclass
class UserMessage:
    """Represents a user message in the conversation."""
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    detected_keywords: List[str] = field(default_factory=list)
    severity_assessment: Optional[SeverityLevel] = None
    matched_scenarios: List[str] = field(default_factory=list)

@dataclass
class BotResponse:
    """Represents a bot response with associated metadata."""
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    response_type: str = "general"  # general, crisis, resource_recommendation, etc.
    recommended_resources: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    requires_human_intervention: bool = False

@dataclass
class ConversationSession:
    """Represents a complete conversation session."""
    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    messages: List[UserMessage] = field(default_factory=list)
    responses: List[BotResponse] = field(default_factory=list)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    identified_concerns: List[str] = field(default_factory=list)
    recommended_resources: List[str] = field(default_factory=list)
    crisis_flags: List[str] = field(default_factory=list)
    is_active: bool = True

@dataclass
class Recommendation:
    """Represents a personalized recommendation for a user."""
    resource_id: str
    resource_name: str
    relevance_score: float
    reasoning: str
    priority: int = 1  # 1 = highest priority
    is_immediate: bool = False
    follow_up_actions: List[str] = field(default_factory=list)

@dataclass
class CrisisAssessment:
    """Represents a crisis risk assessment."""
    risk_level: SeverityLevel
    detected_indicators: List[str]
    immediate_actions: List[str]
    recommended_contacts: List[str]
    requires_immediate_intervention: bool
    assessment_timestamp: datetime = field(default_factory=datetime.now)