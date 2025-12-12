"""
Facial Expression API Integration Module

Implements real-time facial expression recognition using:
1. Client-side: Face.js library (or Azure/AWS SDK)
2. Server-side: Backend processing and emotion mapping
3. WebSocket: Real-time streaming (optional)

This module handles:
- Webcam capture and face detection
- Emotion inference (6 main emotions)
- Expression to engagement mapping
- Multimodal fusion with other indicators
"""

from datetime import datetime
from app.models.engagement import EngagementMetric
from app.models.session import Session, StudentResponse
from app import db
import json


class FacialExpressionIntegrator:
    """
    Integrates facial expression recognition with tutoring system
    
    Can use multiple providers:
    1. Azure Face API (most accurate)
    2. AWS Rekognition (good accuracy)
    3. Face.js (local, privacy-first)
    4. MediaPipe (free, open-source)
    """
    
    def __init__(self, provider='face.js', api_key=None):
        """
        Initialize facial expression integrator
        
        Args:
            provider: 'face.js', 'azure', 'aws', or 'mediapipe'
            api_key: API key for cloud providers (if applicable)
        """
        self.provider = provider
        self.api_key = api_key
        
        # Emotion mappings to engagement values
        self.emotion_engagement_map = {
            'happy': {'engagement': 0.95, 'confidence': 0.9, 'frustration': 0.0},
            'excited': {'engagement': 0.95, 'confidence': 0.9, 'frustration': 0.0},
            'neutral': {'engagement': 0.6, 'confidence': 0.6, 'frustration': 0.2},
            'confused': {'engagement': 0.4, 'confidence': 0.2, 'frustration': 0.4},
            'frustrated': {'engagement': 0.2, 'confidence': 0.1, 'frustration': 0.9},
            'angry': {'engagement': 0.1, 'confidence': 0.05, 'frustration': 1.0},
            'sad': {'engagement': 0.3, 'confidence': 0.2, 'frustration': 0.6},
            'fearful': {'engagement': 0.2, 'confidence': 0.1, 'frustration': 0.7},
            'disgusted': {'engagement': 0.1, 'confidence': 0.1, 'frustration': 0.8},
        }
        
        self.recording_sessions = {}  # session_id -> recording data
    
    def process_facial_frame(self, session_id, frame_data):
        """
        Process a single frame of facial data
        
        Args:
            session_id: Current session ID
            frame_data: {
                'emotion': 'happy',
                'confidence': 0.95,
                'x': 100,  # face position
                'y': 200,
                'width': 150,
                'height': 150,
                'landmarks': {...}  # optional: facial landmarks
            }
        
        Returns:
            Processed engagement data
        """
        if not frame_data:
            return None
        
        emotion = frame_data.get('emotion', 'neutral').lower()
        confidence = frame_data.get('confidence', 0.5)
        
        # Validate emotion
        if emotion not in self.emotion_engagement_map:
            emotion = 'neutral'
        
        # Get engagement mapping
        engagement_data = self.emotion_engagement_map[emotion]
        
        # Apply confidence weighting
        weighted_engagement = engagement_data['engagement'] * confidence
        weighted_frustration = engagement_data['frustration'] * confidence
        weighted_confidence = engagement_data['confidence'] * confidence
        
        return {
            'emotion': emotion,
            'emotion_confidence': confidence,
            'engagement_score': weighted_engagement,
            'frustration_level': weighted_frustration,
            'confidence_level': weighted_confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def record_session_start(self, session_id, student_id):
        """Start recording facial expressions for a session"""
        self.recording_sessions[session_id] = {
            'student_id': student_id,
            'session_id': session_id,
            'frames': [],
            'start_time': datetime.utcnow(),
            'face_detected_count': 0,
            'face_not_detected_count': 0
        }
    
    def add_frame(self, session_id, frame_data):
        """Add a facial frame to session recording"""
        if session_id not in self.recording_sessions:
            return False
        
        if not frame_data:
            self.recording_sessions[session_id]['face_not_detected_count'] += 1
            return False
        
        processed = self.process_facial_frame(session_id, frame_data)
        self.recording_sessions[session_id]['frames'].append(processed)
        self.recording_sessions[session_id]['face_detected_count'] += 1
        
        return True
    
    def record_session_end(self, session_id):
        """End facial recording and get summary"""
        if session_id not in self.recording_sessions:
            return None
        
        recording = self.recording_sessions[session_id]
        frames = recording['frames']
        
        if not frames:
            del self.recording_sessions[session_id]
            return None
        
        # Calculate statistics
        emotions = [f['emotion'] for f in frames]
        engagement_scores = [f['engagement_score'] for f in frames]
        frustration_levels = [f['frustration_level'] for f in frames]
        
        from statistics import mean, stdev
        
        avg_engagement = mean(engagement_scores) if engagement_scores else 0.5
        avg_frustration = mean(frustration_levels) if frustration_levels else 0.0
        engagement_stability = stdev(engagement_scores) if len(engagement_scores) > 1 else 0.0
        
        # Most common emotion
        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        summary = {
            'session_id': session_id,
            'student_id': recording['student_id'],
            'duration_seconds': (datetime.utcnow() - recording['start_time']).total_seconds(),
            'frames_recorded': len(frames),
            'face_detection_rate': (recording['face_detected_count'] / 
                                   (recording['face_detected_count'] + recording['face_not_detected_count'])),
            'avg_engagement': avg_engagement,
            'avg_frustration': avg_frustration,
            'engagement_stability': engagement_stability,
            'dominant_emotion': dominant_emotion,
            'emotion_breakdown': self._emotion_breakdown(emotions),
            'recommendations': self._generate_recommendations(avg_engagement, avg_frustration)
        }
        
        del self.recording_sessions[session_id]
        return summary
    
    def _emotion_breakdown(self, emotions):
        """Get breakdown of emotions in session"""
        if not emotions:
            return {}
        
        breakdown = {}
        total = len(emotions)
        for emotion in set(emotions):
            count = emotions.count(emotion)
            breakdown[emotion] = round(count / total, 2)
        
        return breakdown
    
    def _generate_recommendations(self, avg_engagement, avg_frustration):
        """Generate pedagogical recommendations based on facial analysis"""
        recommendations = []
        
        if avg_engagement < 0.4:
            recommendations.append('Low engagement detected - consider simplifying content or taking a break')
        elif avg_engagement > 0.8:
            recommendations.append('High engagement maintained - student is focused')
        
        if avg_frustration > 0.6:
            recommendations.append('High frustration detected - reduce difficulty or provide hints')
        elif avg_frustration < 0.2:
            recommendations.append('Low frustration - content difficulty appropriate')
        
        if avg_engagement > 0.7 and avg_frustration < 0.3:
            recommendations.append('Optimal state - student is both engaged and confident')
        
        return recommendations
    
    def save_recording_to_db(self, session_id, summary):
        """Save facial recording summary to database"""
        session = Session.query.get(session_id)
        if not session:
            return False
        
        # Store in EngagementMetric
        metric = EngagementMetric(
            session_id=session_id,
            student_id=session.student_id,
            engagement_score=summary['avg_engagement'],
            engagement_level='high' if summary['avg_engagement'] > 0.7 else ('low' if summary['avg_engagement'] < 0.4 else 'medium'),
            facial_expression_data=json.dumps({
                'dominant_emotion': summary['dominant_emotion'],
                'emotion_breakdown': summary['emotion_breakdown'],
                'face_detection_rate': summary['face_detection_rate'],
                'frustration_level': summary['avg_frustration']
            })
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return True


class WebcamCapture:
    """
    Frontend utility for webcam capture and face detection
    This class provides JavaScript snippets for the frontend
    """
    
    @staticmethod
    def get_face_js_script():
        """Get Face.js library and webcam capture code"""
        return """
<!-- Face.js Library (Local face detection, privacy-first) -->
<script async src="https://cdn.jsdelivr.net/npm/@vladmandic/face-api/dist/face-api.js"></script>

<script>
class WebcamFacialCapture {
    constructor(videoElementId, canvasElementId) {
        this.video = document.getElementById(videoElementId);
        this.canvas = document.getElementById(canvasElementId);
        this.stream = null;
        this.isRunning = false;
        this.detectionInterval = null;
        this.sessionId = null;
    }
    
    async initialize() {
        try {
            // Request camera permission
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 },
                audio: false 
            });
            this.video.srcObject = this.stream;
            
            // Load face detection models
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
                faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
                faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
                faceapi.nets.faceExpressionNet.loadFromUri('/models')
            ]);
            
            console.log('✅ Facial recognition initialized');
            return true;
        } catch (error) {
            console.error('Error initializing webcam:', error);
            return false;
        }
    }
    
    async startDetection(sessionId, detectionCallback) {
        this.sessionId = sessionId;
        this.isRunning = true;
        
        // Detect faces every 500ms (2 FPS)
        this.detectionInterval = setInterval(async () => {
            if (!this.isRunning) return;
            
            const detections = await faceapi
                .detectAllFaces(this.video, new faceapi.TinyFaceDetector())
                .withFaceLandmarks()
                .withFaceExpressions();
            
            if (detections.length > 0) {
                const detection = detections[0];
                const expressions = detection.expressions;
                
                // Get dominant emotion
                const emotions = {
                    'neutral': expressions.neutral,
                    'happy': expressions.happy,
                    'sad': expressions.sad,
                    'angry': expressions.angry,
                    'fearful': expressions.fearful,
                    'disgusted': expressions.disgusted,
                    'surprised': expressions.surprised
                };
                
                const dominantEmotion = Object.keys(emotions).reduce((a, b) =>
                    emotions[a] > emotions[b] ? a : b
                );
                
                const frameData = {
                    emotion: dominantEmotion,
                    confidence: emotions[dominantEmotion],
                    x: detection.detection.box.x,
                    y: detection.detection.box.y,
                    width: detection.detection.box.width,
                    height: detection.detection.box.height,
                    timestamp: new Date().toISOString()
                };
                
                // Send to backend
                detectionCallback(frameData);
                
                // Draw detection box (optional)
                this.drawDetection(detection);
            }
        }, 500);
    }
    
    drawDetection(detection) {
        const ctx = this.canvas.getContext('2d');
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const box = detection.detection.box;
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 2;
        ctx.strokeRect(box.x, box.y, box.width, box.height);
    }
    
    stopDetection() {
        this.isRunning = false;
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
        }
    }
    
    async stop() {
        this.stopDetection();
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Initialize on page load
async function initializeFacialCapture() {
    const capture = new WebcamFacialCapture('webcam-video', 'webcam-canvas');
    const initialized = await capture.initialize();
    
    if (!initialized) {
        console.error('Failed to initialize facial capture');
        return;
    }
    
    // Start detection when question starts
    capture.startDetection(sessionId, async (frameData) => {
        // Send frame data to backend
        try {
            await fetch('/api/analytics/affective/record-facial', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    frame_data: frameData
                })
            });
        } catch (error) {
            console.error('Error sending facial data:', error);
        }
    });
    
    return capture;
}
</script>

<!-- HTML for webcam display -->
<div id="facial-capture" style="display: none; margin: 20px 0;">
    <h3>Facial Expression Monitoring</h3>
    <video id="webcam-video" autoplay playsinline 
           style="width: 320px; height: 240px; border: 2px solid #ddd; border-radius: 8px;"></video>
    <canvas id="webcam-canvas" 
            style="width: 320px; height: 240px; display: none;"></canvas>
</div>
"""
    
    @staticmethod
    def get_azure_face_api_script(api_key, endpoint):
        """Get Azure Face API integration code"""
        return f"""
<!-- Azure Face API Integration -->
<script src="https://cdn.jsdelivr.net/npm/@azure/cognitiveservices-face/"></script>

<script>
class AzureFacialCapture {{
    constructor(subscriptionKey, endpoint) {{
        this.subscriptionKey = '{api_key}';
        this.endpoint = '{endpoint}';
        this.client = new Face.FaceClient(
            {{ credentials: new Identity.ClientSecretCredential("tenant", "client", "secret") }},
            endpoint
        );
    }}
    
    async captureAndAnalyze(imageData) {{
        try {{
            const detectedFaces = await this.client.face.detectWithUrl(imageUrl, {{
                returnFaceAttributes: ['emotion', 'age', 'gender', 'headPose']
            }});
            
            if (detectedFaces.length === 0) {{
                return null;
            }}
            
            const face = detectedFaces[0];
            const emotions = face.faceAttributes.emotion;
            
            // Get dominant emotion
            const dominantEmotion = Object.keys(emotions).reduce((a, b) =>
                emotions[a] > emotions[b] ? a : b
            );
            
            return {{
                emotion: dominantEmotion,
                confidence: emotions[dominantEmotion],
                age: face.faceAttributes.age,
                gender: face.faceAttributes.gender,
                timestamp: new Date().toISOString()
            }};
        }} catch (error) {{
            console.error('Azure Face API error:', error);
            return null;
        }}
    }}
}}
</script>
"""


class PrivacyOptions:
    """
    Privacy-first options for facial expression capture
    """
    
    @staticmethod
    def get_privacy_guide():
        """Get guidance on privacy options"""
        return {
            'local_only': {
                'description': 'All processing happens in browser, no data sent to server',
                'libraries': ['Face.js', 'MediaPipe', 'TensorFlow.js'],
                'privacy': 'Maximum - no data leaves device',
                'accuracy': 'Good (85-90%)',
                'pros': ['Privacy', 'No API costs', 'Works offline'],
                'cons': ['Slightly lower accuracy', 'Requires device resources']
            },
            'on_demand': {
                'description': 'Optional facial capture during testing',
                'provider_options': ['Azure Face', 'AWS Rekognition', 'Google Cloud Vision'],
                'privacy': 'High - user can opt-in/out',
                'accuracy': 'Very high (95%+)',
                'pros': ['High accuracy', 'Works for complex expressions'],
                'cons': ['Requires API key', 'User consent needed', 'Latency']
            },
            'hybrid': {
                'description': 'Local detection for basic emotions, cloud for complex analysis',
                'how_it_works': 'Face.js for real-time, Azure API for periodic deep analysis',
                'privacy': 'High - only complex frames sent',
                'accuracy': 'Very high (95%+)',
                'pros': ['Best of both worlds', 'Low latency', 'Lower API costs'],
                'cons': ['Complexity', 'Dual maintenance']
            }
        }
