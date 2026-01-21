"""
Optional Facial Emotion Recognition Integration Module

This module provides safe, optional integration of facial emotion data 
into the adaptive tutoring engine. Facial emotion signals are used as
COMPLEMENTARY SIGNALS to enhance affective inference, never as primary drivers.

Design Principles:
1. OPTIONAL: System works perfectly if facial data unavailable or detection fails
2. GRACEFUL FALLBACK: Missing facial data → behavioral inference only (transparent to user)
3. HYBRID INFERENCE: When available, facial emotion + behavioral patterns = richer affective model
4. CONFIGURABLE: Can be enabled/disabled at any time without system changes
5. TRANSPARENT: All decisions logged with source clarity (facial vs behavioral)
6. PRIVACY-FIRST: Emotion labels not persisted; only engagement signals stored

Architecture:
- FacialSignalProcessor: Extracts engagement signals from facial emotion data
- FacialDataValidator: Ensures data quality and handles missing/invalid data
- AdaptationModifier: Applies facial signals as adjustments (never overrides)
- Configuration: Enable/disable at system level with fallback mode

Integration Points:
1. Engagement Tracker: Accepts optional facial_data parameter in track_affective_indicators()
2. Affective Analyzer: Blends facial emotion with behavioral inference
3. Adaptation Engine: Uses facial signals to refine difficulty adjustments
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from app.models.engagement import EngagementMetric
from app.models.session import Session, StudentResponse
from app import db
import logging

logger = logging.getLogger(__name__)


class FacialSignalConfig:
    """Configuration for facial emotion recognition integration"""
    
    # Master enable/disable
    ENABLED = False  # Set to True to activate facial emotion recognition
    
    # Fallback mode: if True, system logs failures but continues with behavioral inference
    FALLBACK_MODE = True  # Graceful degradation when facial data unavailable
    
    # Confidence levels for using facial signals
    MIN_EMOTION_CONFIDENCE = 0.60  # Only use if model is 60%+ confident
    MIN_VALID_FRAMES = 1  # Minimum frames needed for valid signal
    
    # Signal weights (how much facial data affects decisions)
    # Values between 0.0 (no effect) and 1.0 (full effect)
    EMOTION_TO_AFFECTIVE_WEIGHT = 0.50  # Facial emotion: 50% influence on affective inference
    ENGAGEMENT_SIGNAL_WEIGHT = 0.15  # 15% adjustment max from engagement signal
    DIFFICULTY_ADJUSTMENT_WEIGHT = 0.10  # Max 10% adjustment to difficulty delta
    HINT_SUGGESTION_WEIGHT = 0.20  # Max 20% adjustment to hint frequency
    
    # Emotion to engagement signal mapping
    # Values 0.0-1.0 representing engagement level inferred from emotion
    EMOTION_ENGAGEMENT_MAP = {
        'happy': 0.95,          # Very high engagement
        'excited': 1.0,         # Highest engagement
        'confident': 0.85,      # High engagement
        'neutral': 0.60,        # Medium engagement
        'confused': 0.40,       # Low engagement (needs help)
        'frustrated': 0.20,     # Very low engagement (struggling)
        'bored': 0.15,          # Minimal engagement (disinterested)
        'anxious': 0.30,        # Low engagement (worried)
        'sad': 0.25,            # Very low engagement (withdrawn)
        'angry': 0.10           # Minimal engagement (disengaged)
    }
    
    # Emotion to affective state mapping
    # Maps detected emotions to confidence/frustration/interest inferences
    EMOTION_AFFECTIVE_MAP = {
        'happy': {'confidence': 0.9, 'frustration': 0.05, 'interest': 0.95},
        'excited': {'confidence': 0.95, 'frustration': 0.0, 'interest': 1.0},
        'confident': {'confidence': 0.85, 'frustration': 0.1, 'interest': 0.8},
        'neutral': {'confidence': 0.5, 'frustration': 0.3, 'interest': 0.5},
        'confused': {'confidence': 0.3, 'frustration': 0.6, 'interest': 0.6},
        'frustrated': {'confidence': 0.2, 'frustration': 0.9, 'interest': 0.3},
        'bored': {'confidence': 0.4, 'frustration': 0.2, 'interest': 0.1},
        'anxious': {'confidence': 0.2, 'frustration': 0.7, 'interest': 0.5},
        'sad': {'confidence': 0.1, 'frustration': 0.8, 'interest': 0.2},
        'angry': {'confidence': 0.1, 'frustration': 1.0, 'interest': 0.1}
    }


class FacialDataValidator:
    """Validates and sanitizes facial data, providing graceful fallback"""
    
    @staticmethod
    def validate(facial_data: Optional[Dict]) -> Tuple[bool, Optional[Dict], str]:
        """
        Validate facial data quality and availability
        
        Returns:
            (is_valid: bool, cleaned_data: dict or None, reason: str)
        """
        if not facial_data:
            return False, None, "No facial data provided"
        
        if not isinstance(facial_data, dict):
            return False, None, "Facial data must be a dictionary"
        
        emotion = facial_data.get('emotion_detected', '').lower()
        confidence = facial_data.get('emotion_confidence', 0.0)
        
        # Must have emotion label
        if not emotion or emotion not in FacialSignalConfig.EMOTION_ENGAGEMENT_MAP:
            return False, None, f"Invalid or missing emotion label: {emotion}"
        
        # Must meet confidence threshold
        if not isinstance(confidence, (int, float)) or confidence < FacialSignalConfig.MIN_EMOTION_CONFIDENCE:
            return False, None, f"Confidence {confidence:.0%} below minimum {FacialSignalConfig.MIN_EMOTION_CONFIDENCE:.0%}"
        
        # Validate optional fields
        cleaned_data = {
            'emotion_detected': emotion,
            'emotion_confidence': float(confidence),
            'gaze_pattern': facial_data.get('gaze_pattern', '').lower() or None,
            'posture_type': facial_data.get('posture_type', '').lower() or None,
            'timestamp': facial_data.get('timestamp')
        }
        
        return True, cleaned_data, f"Valid facial data: {emotion} ({confidence:.0%})"
    
    @staticmethod
    def get_affective_values_from_emotion(emotion: str) -> Dict[str, float]:
        """
        Get affective state values (confidence, frustration, interest) from detected emotion
        
        Args:
            emotion: Detected emotion label
        
        Returns:
            Dict with confidence_level, frustration_level, interest_level (or None if invalid)
        """
        emotion = emotion.lower()
        affective_map = FacialSignalConfig.EMOTION_AFFECTIVE_MAP.get(emotion)
        
        if affective_map:
            return {
                'confidence_level': affective_map.get('confidence'),
                'frustration_level': affective_map.get('frustration'),
                'interest_level': affective_map.get('interest'),
                'source': 'facial_emotion_recognition'
            }
        
        return None


class FacialSignalProcessor:
    """
    Extracts engagement signals from facial emotion data with graceful fallback
    
    Input: Facial emotion detection data (emotion, confidence, optional gaze/posture)
    Output: Normalized engagement signal (0.0 - 1.0) for use in adaptation
    
    Key feature: Returns (signal, reason) tuple allowing callers to determine
    whether to use facial data or fall back to behavioral inference
    """
    
    def __init__(self, config: FacialSignalConfig = None):
        self.config = config or FacialSignalConfig()
        self.validator = FacialDataValidator()
        self.logger = logger
    
    def extract_engagement_signal(self, facial_data: Dict) -> Tuple[Optional[float], str]:
        """
        Extract a single engagement signal from facial emotion data
        
        Args:
            facial_data: Dictionary with keys:
                - emotion_detected: str (emotion label)
                - emotion_confidence: float (0.0-1.0)
                - gaze_pattern: str (optional: focused, scattered, away, etc.)
                - posture_type: str (optional: upright, slumped, etc.)
        
        Returns:
            (engagement_signal: 0.0-1.0 or None, reason: str)
            - Signal: None if data invalid (caller should use behavioral inference)
            - Reason: Always explains why signal was accepted or rejected
        """
        
        # Validate facial data
        is_valid, cleaned_data, validation_reason = self.validator.validate(facial_data)
        
        if not is_valid:
            self.logger.debug(f"[FACIAL] Signal extraction failed: {validation_reason}")
            return None, validation_reason
        
        facial_data = cleaned_data
        signal = 0.5  # Default neutral
        reasons = []
        
        # 1. Extract emotion signal (primary)
        emotion = facial_data['emotion_detected']
        emotion_confidence = facial_data['emotion_confidence']
        
        emotion_signal = self.config.EMOTION_ENGAGEMENT_MAP.get(emotion, 0.5)
        signal = emotion_signal
        reasons.append(
            f"Emotion: {emotion} (confidence: {emotion_confidence:.0%})"
        )
        
        # 2. Gaze pattern adjustment (secondary - slight modifier)
        gaze_pattern = facial_data.get('gaze_pattern')
        if gaze_pattern:
            gaze_adjustment = self._gaze_pattern_adjustment(gaze_pattern)
            if gaze_adjustment != 0:
                signal = max(0.0, min(1.0, signal + gaze_adjustment * 0.1))
                reasons.append(
                    f"Gaze: {gaze_pattern} ({gaze_adjustment:+.1f})"
                )
        
        # 3. Posture adjustment (tertiary - slight modifier)
        posture_type = facial_data.get('posture_type')
        if posture_type:
            posture_adjustment = self._posture_adjustment(posture_type)
            if posture_adjustment != 0:
                signal = max(0.0, min(1.0, signal + posture_adjustment * 0.1))
                reasons.append(
                    f"Posture: {posture_type} ({posture_adjustment:+.1f})"
                )
        
        reason = " | ".join(reasons) if reasons else "Emotion signal only"
        
        # Clamp to valid range
        signal = max(0.0, min(1.0, signal))
        
        self.logger.debug(f"[FACIAL] Signal extracted: {reason}")
        
        return signal, reason
    
    def _gaze_pattern_adjustment(self, gaze_pattern: str) -> float:
        """Adjustment to engagement signal based on gaze pattern"""
        adjustments = {
            'focused': 0.2,      # Increase signal (very focused)
            'reading': 0.1,      # Slight increase (reading content)
            'scattered': -0.3,   # Decrease signal (distracted)
            'downward': -0.5,    # Significant decrease (looking away/down)
            'away': -0.7,        # Strong decrease (completely away)
        }
        return adjustments.get(gaze_pattern, 0.0)
    
    def _posture_adjustment(self, posture_type: str) -> float:
        """Adjustment to engagement signal based on posture"""
        adjustments = {
            'upright_engaged': 0.15,    # Increase signal
            'leaning_forward': 0.25,    # Strong increase (very engaged)
            'relaxed': 0.0,             # No change
            'slumped': -0.25,           # Decrease signal (disengaged)
            'tense': -0.2,              # Decrease signal (stressed)
        }
        return adjustments.get(posture_type, 0.0)


class AdaptationModifier:
    """
    Applies facial emotion signals as optional modifiers to adaptation decisions
    
    Key behavior:
    - If facial data available and valid: Uses it to refine decisions
    - If facial data missing/invalid: Falls back to behavioral metrics only
    - Never overrides primary metrics (accuracy, performance)
    - All decisions logged with source clarity
    """
    
    def __init__(self, config: FacialSignalConfig = None):
        self.config = config or FacialSignalConfig()
        self.processor = FacialSignalProcessor(config)
        self.validator = FacialDataValidator()
        self.logger = logger
    
    def is_enabled(self) -> bool:
        """Check if facial signal integration is enabled"""
        return self.config.ENABLED
    
    def supports_fallback(self) -> bool:
        """Check if system should gracefully fall back when facial data unavailable"""
        return self.config.FALLBACK_MODE
    
    def modify_difficulty_adjustment(
        self,
        base_difficulty_delta: float,
        facial_engagement_signal: Optional[float],
        behavioral_engagement_score: float
    ) -> Tuple[float, str]:
        """
        Apply facial signal as optional modifier to difficulty adjustment
        
        Behavior:
        - If facial_enabled: Uses facial signal to refine adjustment (never overrides)
        - If facial_disabled or fallback_mode: Returns base_delta unchanged
        - If facial_enabled but signal None: Falls back to base_delta
        
        Args:
            base_difficulty_delta: Primary adjustment from accuracy/performance (-0.10 to +0.10)
            facial_engagement_signal: Engagement from facial data (0.0-1.0 or None)
            behavioral_engagement_score: Primary engagement score (0.0-1.0)
        
        Returns:
            (modified_delta, explanation string)
        """
        
        if not self.is_enabled():
            return base_difficulty_delta, "Facial integration disabled"
        
        if facial_engagement_signal is None:
            reason = "No facial signal available"
            if self.supports_fallback():
                self.logger.debug(f"[FACIAL] {reason}, using behavioral metrics only")
                return base_difficulty_delta, f"{reason} → using behavioral inference"
            else:
                self.logger.warning(f"[FACIAL] {reason} and fallback disabled")
                return base_difficulty_delta, f"{reason} (fallback required)"
        
        # Facial signal modifies difficulty by up to 10%
        # High engagement (facial) suggests slightly increased difficulty increase
        # Low engagement (facial) suggests slightly decreased difficulty increase
        
        # Calculate facial modifier as percentage of base delta
        facial_modifier = (facial_engagement_signal - 0.5) * 2  # Convert 0-1 to -1 to +1
        facial_adjustment = base_difficulty_delta * facial_modifier * self.config.DIFFICULTY_ADJUSTMENT_WEIGHT
        
        modified_delta = base_difficulty_delta + facial_adjustment
        
        # Clamp to reasonable bounds
        modified_delta = max(-0.15, min(0.15, modified_delta))
        
        explanation = (
            f"Facial signal: {facial_engagement_signal:.2f} "
            f"(base: {base_difficulty_delta:+.4f} → modified: {modified_delta:+.4f})"
        )
        
        self.logger.info(f"[FACIAL] Difficulty adjustment: {explanation}")
        
        return modified_delta, explanation
        return modified_delta, explanation
    
    def modify_engagement_score(
        self,
        base_engagement_score: float,
        facial_data: Optional[Dict]
    ) -> Tuple[float, str]:
        """
        Optionally enhance engagement score with facial emotion signals
        
        Behavior:
        - If facial_enabled and valid data: Blends facial signal with behavioral score
        - If facial_disabled or invalid data: Returns base_score unchanged
        - Falls back to behavioral inference when facial data unavailable
        
        Args:
            base_engagement_score: Engagement from behavioral metrics (0.0-1.0)
            facial_data: Facial expression data dictionary (or None)
        
        Returns:
            (modified_score: 0.0-1.0, explanation: str)
        """
        
        if not self.is_enabled():
            return base_engagement_score, "Facial integration disabled"
        
        # Validate facial data first
        is_valid, cleaned_data, validation_reason = self.validator.validate(facial_data)
        
        if not is_valid:
            if self.supports_fallback():
                self.logger.debug(f"[FACIAL] {validation_reason}, using behavioral score only")
                return base_engagement_score, f"{validation_reason} → using behavioral inference"
            else:
                self.logger.warning(f"[FACIAL] {validation_reason} and fallback disabled")
                return base_engagement_score, f"{validation_reason} (fallback required)"
        
        # Extract facial engagement signal from validated data
        facial_signal, signal_reason = self.processor.extract_engagement_signal(cleaned_data)
        
        if facial_signal is None:
            if self.supports_fallback():
                self.logger.debug(f"[FACIAL] Failed to extract signal, using behavioral score only")
                return base_engagement_score, f"Facial signal extraction failed → using behavioral inference"
            else:
                return base_engagement_score, "Facial signal extraction failed (fallback required)"
        
        # Blend facial signal with behavioral score
        # Facial signal has limited weight to avoid overriding behavioral metrics
        weight = self.config.ENGAGEMENT_SIGNAL_WEIGHT
        modified_score = (base_engagement_score * (1 - weight)) + (facial_signal * weight)
        
        explanation = (
            f"Engagement fusion: behavior={base_engagement_score:.2f} × {1-weight:.0%} + "
            f"facial={facial_signal:.2f} × {weight:.0%} = {modified_score:.2f} "
            f"({signal_reason})"
        )
        
        self.logger.info(f"[FACIAL] Engagement enhanced: {explanation}")
        
        return modified_score, explanation
    
    def suggest_hint_adjustment(
        self,
        base_hint_frequency: str,
        facial_engagement_signal: Optional[float]
    ) -> Tuple[str, str]:
        """
        Suggest hint frequency adjustment based on facial emotion signals
        
        Behavior:
        - If facial_enabled and signal available: Uses facial emotion to refine hint strategy
        - If facial_disabled or signal missing: Returns base_frequency unchanged
        - Falls back gracefully when facial data unavailable
        
        Args:
            base_hint_frequency: Primary suggestion ('minimal', 'normal', 'generous')
            facial_engagement_signal: Engagement from facial data (0.0-1.0 or None)
        
        Returns:
            (adjusted_frequency: str, explanation: str)
        """
        
        if not self.is_enabled():
            return base_hint_frequency, "Facial integration disabled"
        
        if facial_engagement_signal is None:
            if self.supports_fallback():
                self.logger.debug("[FACIAL] No signal available, using behavioral hint strategy")
                return base_hint_frequency, "No facial signal available → using behavioral strategy"
            else:
                return base_hint_frequency, "No facial signal available (fallback required)"
        
        # If facial signal shows high frustration (low engagement), suggest more hints
        if facial_engagement_signal < 0.35:
            if base_hint_frequency != 'generous':
                explanation = (
                    f"Facial emotion suggests frustration ({facial_engagement_signal:.0%}), "
                    f"increasing hint frequency from {base_hint_frequency} to generous"
                )
                self.logger.info(f"[FACIAL] Hint adjustment: {explanation}")
                return 'generous', explanation
        
        # If facial signal shows very high engagement, can reduce hints
        elif facial_engagement_signal > 0.85:
            if base_hint_frequency != 'minimal':
                explanation = (
                    f"Facial emotion suggests high engagement ({facial_engagement_signal:.0%}), "
                    f"reducing hint frequency from {base_hint_frequency} to minimal"
                )
                self.logger.info(f"[FACIAL] Hint adjustment: {explanation}")
                return 'minimal', explanation
        
        return base_hint_frequency, "No hint adjustment needed from facial emotion signal"
    
    def get_integration_metadata(self, facial_data: Optional[Dict]) -> Dict:
        """
        Generate metadata about how facial emotion data was used in this decision
        
        Returns:
            Dictionary with:
            - facial_integration_enabled: bool
            - facial_signal_used: bool (True if facial data influenced decision)
            - facial_engagement_signal: float or None
            - facial_signal_reason: str
            - fallback_mode_active: bool
            - facial_data_available: dict with actual data fields
        """
        
        if not self.is_enabled():
            return {
                'facial_integration_enabled': False,
                'facial_signal_used': False,
                'fallback_mode_active': self.supports_fallback(),
                'reason': 'Facial integration not enabled'
            }
        
        # Validate facial data
        is_valid, cleaned_data, validation_reason = self.validator.validate(facial_data)
        
        if not is_valid:
            return {
                'facial_integration_enabled': True,
                'facial_signal_used': False,
                'fallback_mode_active': self.supports_fallback(),
                'validation_error': validation_reason,
                'reason': f'Invalid facial data: {validation_reason}'
            }
        
        # Extract signal from validated data
        signal, reason = self.processor.extract_engagement_signal(cleaned_data)
        
        return {
            'facial_integration_enabled': True,
            'facial_signal_used': signal is not None,
            'fallback_mode_active': self.supports_fallback(),
            'facial_engagement_signal': round(signal, 4) if signal is not None else None,
            'facial_signal_reason': reason,
            'facial_data_available': {
                'emotion_detected': cleaned_data.get('emotion_detected'),
                'emotion_confidence': cleaned_data.get('emotion_confidence'),
                'gaze_pattern': cleaned_data.get('gaze_pattern'),
                'posture_type': cleaned_data.get('posture_type')
            }
        }


# Convenience function for use in adaptation engine
def get_facial_modifier() -> AdaptationModifier:
    """Factory function to get configured facial modifier instance"""
    return AdaptationModifier()
