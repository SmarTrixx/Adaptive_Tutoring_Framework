# Engagement Fusion Layer
# Combines behavioral, cognitive, and affective indicators into unified engagement state

from enum import Enum
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from app.engagement.indicators import EngagementIndicators


class EngagementState(Enum):
    """Categorical engagement state."""
    HIGHLY_ENGAGED = "highly_engaged"
    ENGAGED = "engaged"
    NEUTRAL = "neutral"
    STRUGGLING = "struggling"
    DISENGAGED = "disengaged"


@dataclass
class FusedEngagementState:
    """
    Unified engagement representation combining all modalities.
    """
    # Numeric score: 0.0 = completely disengaged, 1.0 = highly engaged
    engagement_score: float
    
    # Categorical state
    categorical_state: EngagementState
    
    # Component scores (normalized 0.0-1.0)
    behavioral_score: float
    cognitive_score: float
    affective_score: float
    
    # Confidence in this assessment (how much data backed this?)
    confidence: float
    
    # Key drivers (what's affecting engagement most?)
    primary_driver: str
    secondary_driver: Optional[str]
    
    # Timestamp
    timestamp: datetime
    
    def to_dict(self):
        """Convert to dictionary for logging/serialization."""
        return {
            'engagement_score': round(self.engagement_score, 4),
            'categorical_state': self.categorical_state.value,
            'component_scores': {
                'behavioral': round(self.behavioral_score, 4),
                'cognitive': round(self.cognitive_score, 4),
                'affective': round(self.affective_score, 4)
            },
            'confidence': round(self.confidence, 4),
            'drivers': {
                'primary': self.primary_driver,
                'secondary': self.secondary_driver
            },
            'timestamp': self.timestamp.isoformat()
        }


class EngagementFusionEngine:
    """
    Fuses behavioral, cognitive, and affective indicators into unified engagement state.
    Uses weighted averaging to ensure no single modality dominates.
    """
    
    # Weights: must sum to 1.0
    # Behavioral gets 40% (most observable/reliable)
    # Cognitive gets 40% (performance-based, reliable)
    # Affective gets 20% (simulated, less reliable)
    BEHAVIORAL_WEIGHT = 0.40
    COGNITIVE_WEIGHT = 0.40
    AFFECTIVE_WEIGHT = 0.20
    
    # Thresholds for categorical mapping
    HIGHLY_ENGAGED_THRESHOLD = 0.80
    ENGAGED_THRESHOLD = 0.60
    NEUTRAL_THRESHOLD = 0.40
    STRUGGLING_THRESHOLD = 0.20
    # Below 0.20 = disengaged
    
    def fuse(self, indicators: EngagementIndicators) -> FusedEngagementState:
        """
        Fuse engagement indicators into unified state.
        
        Args:
            indicators: EngagementIndicators containing all three modalities
            
        Returns:
            FusedEngagementState: Unified engagement representation
        """
        
        if not indicators.is_valid:
            # Return neutral state if indicators not valid
            return self._neutral_state()
        
        # Normalize and compute component scores
        behavioral_score = self._normalize_behavioral(indicators)
        cognitive_score = self._normalize_cognitive(indicators)
        affective_score = self._normalize_affective(indicators)
        
        # Weighted fusion (ensure all components respected)
        engagement_score = (
            behavioral_score * self.BEHAVIORAL_WEIGHT +
            cognitive_score * self.COGNITIVE_WEIGHT +
            affective_score * self.AFFECTIVE_WEIGHT
        )
        
        # Clamp to [0, 1]
        engagement_score = max(0.0, min(1.0, engagement_score))
        
        # Map to categorical state
        categorical_state = self._score_to_category(engagement_score)
        
        # Identify drivers
        primary_driver, secondary_driver = self._identify_drivers(
            behavioral_score, cognitive_score, affective_score,
            indicators
        )
        
        # Compute confidence
        confidence = self._compute_confidence(indicators)
        
        return FusedEngagementState(
            engagement_score=engagement_score,
            categorical_state=categorical_state,
            behavioral_score=behavioral_score,
            cognitive_score=cognitive_score,
            affective_score=affective_score,
            confidence=confidence,
            primary_driver=primary_driver,
            secondary_driver=secondary_driver,
            timestamp=datetime.utcnow()
        )
    
    
    def _normalize_behavioral(self, indicators: EngagementIndicators) -> float:
        """
        Normalize behavioral indicators to 0.0-1.0 engagement scale.
        High behavioral engagement:
        - Consistent response times (low deviation)
        - No long inactivity
        - Minimal hints (struggling = not engaged)
        - No rapid guessing
        """
        
        # Consistency: low deviation = engaged
        consistency_component = 1.0 - indicators.response_time_deviation
        
        # Inactivity: no long pauses = engaged
        # >30s inactivity = 0, 0s = 1.0
        inactivity_component = max(0.0, 1.0 - (indicators.inactivity_duration / 60.0))
        
        # Hints: some hints okay, but many = struggling
        # 0 hints = 1.0, 3+ hints = 0.3
        if indicators.hint_usage_count == 0:
            hints_component = 1.0
        elif indicators.hint_usage_count == 1:
            hints_component = 0.8
        elif indicators.hint_usage_count == 2:
            hints_component = 0.6
        else:
            hints_component = max(0.2, 1.0 - (indicators.hint_usage_count * 0.2))
        
        # Guessing: low guessing probability = engaged
        guessing_component = 1.0 - indicators.rapid_guessing_probability
        
        # Average (equal weights)
        behavioral_score = (consistency_component + inactivity_component + 
                           hints_component + guessing_component) / 4
        
        return max(0.0, min(1.0, behavioral_score))
    
    
    def _normalize_cognitive(self, indicators: EngagementIndicators) -> float:
        """
        Normalize cognitive indicators to 0.0-1.0 engagement scale.
        High cognitive engagement:
        - Improving accuracy trend
        - Consistent (not random) performance
        - Moderate cognitive load (not overwhelming)
        """
        
        # Accuracy trend: improving = engaged
        # -1 = declining, 0 = stable, 1 = improving
        # Map to engagement: -1 = 0.2, 0 = 0.5, 1 = 0.9
        trend_component = (indicators.accuracy_trend + 1.0) / 2.0 * 0.7 + 0.2
        
        # Consistency: high consistency = engaged
        consistency_component = indicators.consistency_score
        
        # Cognitive load: moderate is best (not too easy, not overwhelming)
        # 0 = boring (0.3), 0.5 = optimal (1.0), 1.0 = overwhelmed (0.2)
        if indicators.inferred_cognitive_load < 0.5:
            load_component = 0.3 + (indicators.inferred_cognitive_load * 1.4)
        else:
            load_component = 1.0 - ((indicators.inferred_cognitive_load - 0.5) * 1.6)
        load_component = max(0.2, min(1.0, load_component))
        
        # Average
        cognitive_score = (trend_component + consistency_component + load_component) / 3
        
        return max(0.0, min(1.0, cognitive_score))
    
    
    def _normalize_affective(self, indicators: EngagementIndicators) -> float:
        """
        Normalize affective indicators to 0.0-1.0 engagement scale.
        High affective engagement:
        - Low frustration probability
        - Low confusion probability
        - Low boredom probability
        """
        
        # Convert probabilities to engagement components
        # Low probability = high engagement
        frustration_component = 1.0 - indicators.frustration_probability
        confusion_component = 1.0 - indicators.confusion_probability
        boredom_component = 1.0 - indicators.boredom_probability
        
        # Average
        affective_score = (frustration_component + confusion_component + boredom_component) / 3
        
        return max(0.0, min(1.0, affective_score))
    
    
    def _score_to_category(self, score: float) -> EngagementState:
        """Map numeric engagement score to categorical state."""
        if score >= self.HIGHLY_ENGAGED_THRESHOLD:
            return EngagementState.HIGHLY_ENGAGED
        elif score >= self.ENGAGED_THRESHOLD:
            return EngagementState.ENGAGED
        elif score >= self.NEUTRAL_THRESHOLD:
            return EngagementState.NEUTRAL
        elif score >= self.STRUGGLING_THRESHOLD:
            return EngagementState.STRUGGLING
        else:
            return EngagementState.DISENGAGED
    
    
    def _identify_drivers(self, behavioral: float, cognitive: float, affective: float,
                         indicators: EngagementIndicators) -> Tuple[str, Optional[str]]:
        """
        Identify primary and secondary drivers of engagement state.
        """
        
        drivers = []
        
        # Behavioral drivers
        if indicators.hint_usage_count > 2:
            drivers.append(("Struggling (many hints)", "behavioral"))
        elif indicators.response_time_deviation > 0.8:
            drivers.append(("Variable response times", "behavioral"))
        elif indicators.rapid_guessing_probability > 0.5:
            drivers.append(("Rapid guessing detected", "behavioral"))
        elif indicators.inactivity_duration > 30:
            drivers.append(("Long inactivity periods", "behavioral"))
        
        # Cognitive drivers
        if indicators.accuracy_trend < -0.3:
            drivers.append(("Declining accuracy", "cognitive"))
        elif indicators.inferred_cognitive_load > 0.8:
            drivers.append(("High cognitive load", "cognitive"))
        elif indicators.consistency_score < 0.3:
            drivers.append(("Inconsistent performance", "cognitive"))
        
        # Affective drivers
        if indicators.frustration_probability > 0.7:
            drivers.append(("Frustration detected", "affective"))
        elif indicators.confusion_probability > 0.7:
            drivers.append(("Confusion detected", "affective"))
        elif indicators.boredom_probability > 0.7:
            drivers.append(("Boredom detected", "affective"))
        
        # If no negative drivers, mention positive ones
        if not drivers:
            if behavioral > 0.8:
                drivers.append(("Steady behavioral engagement", "behavioral"))
            if cognitive > 0.8:
                drivers.append(("Strong cognitive performance", "cognitive"))
            if affective > 0.8:
                drivers.append(("Positive affective state", "affective"))
        
        primary = drivers[0][0] if drivers else "No clear driver"
        secondary = drivers[1][0] if len(drivers) > 1 else None
        
        return primary, secondary
    
    
    def _compute_confidence(self, indicators: EngagementIndicators) -> float:
        """
        Compute confidence in fusion assessment.
        More data (larger window) = higher confidence.
        """
        
        # Window size confidence: 5+ responses = good confidence
        if indicators.window_size < 3:
            return 0.3
        elif indicators.window_size < 5:
            return 0.6
        elif indicators.window_size < 10:
            return 0.85
        else:
            return 1.0
    
    
    def _neutral_state(self) -> FusedEngagementState:
        """Return neutral engagement state when data is insufficient."""
        return FusedEngagementState(
            engagement_score=0.5,
            categorical_state=EngagementState.NEUTRAL,
            behavioral_score=0.5,
            cognitive_score=0.5,
            affective_score=0.5,
            confidence=0.0,
            primary_driver="Insufficient data",
            secondary_driver=None,
            timestamp=datetime.utcnow()
        )


class FusionLogger:
    """Logs fused engagement state for debugging/analysis."""
    
    @staticmethod
    def log_fusion(session_id: str, fused_state: FusedEngagementState):
        """Log fused engagement state."""
        print(f"\n🔗 FUSED ENGAGEMENT STATE - Session {session_id}")
        print("="*70)
        
        print(f"\n📊 UNIFIED SCORE: {fused_state.engagement_score:.4f}")
        print(f"   State: {fused_state.categorical_state.value.upper()}")
        print(f"   Confidence: {fused_state.confidence:.1%}")
        
        print("\n📈 COMPONENT SCORES:")
        print(f"   Behavioral:  {fused_state.behavioral_score:.4f}")
        print(f"   Cognitive:   {fused_state.cognitive_score:.4f}")
        print(f"   Affective:   {fused_state.affective_score:.4f}")
        
        print("\n🎯 DRIVERS:")
        print(f"   Primary:   {fused_state.primary_driver}")
        if fused_state.secondary_driver:
            print(f"   Secondary: {fused_state.secondary_driver}")
        
        print("="*70 + "\n")
