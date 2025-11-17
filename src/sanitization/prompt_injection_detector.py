"""
Prompt Injection Detection Module

Detects and mitigates prompt injection attacks in email content
before sending to LLMs.

Constitutional Alignment:
- Article VIII: Security by Default
- Article I: Zero-Hallucination Principle
"""

from dataclasses import dataclass
from typing import List
import re
import structlog

logger = structlog.get_logger(__name__)


# Known prompt injection patterns (case-insensitive)
# Format: (pattern, friendly_name)
INJECTION_PATTERNS = [
    (r'ignore\s+(all\s+)?previous\s+instructions?', 'ignore previous instructions'),
    (r'disregard\s+(all\s+)?previous\s+instructions?', 'disregard previous instructions'),
    (r'forget\s+(everything|all)', 'forget everything'),
    (r'you\s+are\s+now', 'you are now'),
    (r'new\s+instructions?:', 'new instructions'),
    (r'system\s+prompt', 'system prompt'),
    (r'repeat\s+(everything|all)\s+above', 'repeat'),
    (r'print\s+your\s+(instructions?|prompt)', 'print your instructions'),
    (r'reveal\s+your\s+(instructions?|prompt|system)', 'reveal your instructions'),
    (r'override\s+your\s+programming', 'override your programming'),
    (r'DAN\s+mode', 'DAN mode'),
    (r'jailbreak', 'jailbreak'),
    (r'ignore\s+(all\s+)?safety', 'ignore all safety'),
]


@dataclass
class DetectionResult:
    """Result of prompt injection detection."""
    is_suspicious: bool
    detected_patterns: List[str]
    threat_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    original_text: str


def detect_prompt_injection(text: str) -> DetectionResult:
    """
    Detect potential prompt injection attempts in text.

    Args:
        text: Text to analyze for injection patterns

    Returns:
        DetectionResult with detected patterns and threat level

    Examples:
        >>> result = detect_prompt_injection("Normal email content")
        >>> result.is_suspicious
        False

        >>> result = detect_prompt_injection("Ignore previous instructions")
        >>> result.is_suspicious
        True
        >>> result.threat_level
        'HIGH'
    """
    if not text:
        return DetectionResult(
            is_suspicious=False,
            detected_patterns=[],
            threat_level="LOW",
            original_text=""
        )

    detected = []
    text_lower = text.lower()

    # Check each pattern
    for pattern, friendly_name in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            detected.append(friendly_name)
            logger.warning(
                "prompt_injection.pattern_detected",
                pattern=friendly_name,
                text_sample=text[:100]
            )

    # Determine threat level based on number of patterns
    if len(detected) == 0:
        threat_level = "LOW"
    elif len(detected) == 1:
        threat_level = "MEDIUM"
    elif len(detected) == 2:
        threat_level = "HIGH"
    else:
        threat_level = "CRITICAL"

    is_suspicious = len(detected) > 0

    if is_suspicious:
        logger.warning(
            "prompt_injection.detected",
            patterns_count=len(detected),
            threat_level=threat_level,
            text_length=len(text)
        )

    return DetectionResult(
        is_suspicious=is_suspicious,
        detected_patterns=detected,
        threat_level=threat_level,
        original_text=text
    )


def sanitize_for_llm(text: str) -> str:
    """
    Sanitize text before sending to LLM by escaping/removing injection attempts.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for LLM processing

    Examples:
        >>> sanitize_for_llm("Normal text")
        'Normal text'

        >>> sanitize_for_llm("Ignore previous instructions")
        '[SANITIZED] previous instructions'
    """
    if not text:
        return text

    # Detect injection attempts
    detection = detect_prompt_injection(text)

    if not detection.is_suspicious:
        return text

    # Sanitize by replacing detected patterns
    sanitized = text
    for pattern, friendly_name in INJECTION_PATTERNS:
        if friendly_name in detection.detected_patterns:
            # Replace pattern with sanitized version
            sanitized = re.sub(
                pattern,
                '[SANITIZED]',
                sanitized,
                flags=re.IGNORECASE
            )

    logger.info(
        "prompt_injection.sanitized",
        original_length=len(text),
        sanitized_length=len(sanitized),
        patterns_removed=len(detection.detected_patterns)
    )

    return sanitized


class PromptInjectionDetected(Exception):
    """Raised when prompt injection is detected and blocked."""
    pass
