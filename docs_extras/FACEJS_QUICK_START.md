# QUICK START - FACE.JS FACIAL MONITORING

## 🚀 3-STEP QUICK START

### Step 1: Start Backend (Terminal 1)
```bash
cd backend
python3 main.py
```
✅ Server runs on: **http://localhost:5000**

### Step 2: Start Frontend (Terminal 2)
```bash
cd frontend
python3 -m http.server 8000
```
✅ Frontend runs on: **http://localhost:8000**

### Step 3: Open Browser
```
http://localhost:8000
```

---

## 🎯 How to Use Facial Monitoring

1. **Look for** "📹 Facial Monitoring" panel (top-right corner)
2. **Click checkbox:** "Enable facial capture"
3. **Allow** camera access when browser asks
4. **See** webcam video appear
5. **Make faces** - emotions update in real-time!

---

## 😊 What You'll See

| Your Face | System Shows | Engagement |
|-----------|--------------|-----------|
| Smiling 😊 | happy | 0.95 ↑ |
| Neutral 😐 | neutral | 0.60 → |
| Frustrated 😠 | angry | 0.15 ↓ |
| Sad 😢 | sad | 0.20 ↓ |
| Surprised 😲 | surprised | 0.75 → |

---

## 📊 How It Works

```
Your Face → Face.js detects emotion → Sends to backend
                                            ↓
                    Backend calculates engagement score
                                            ↓
                    Uses score to adapt difficulty
                                            ↓
                    Next question is easier or harder
```

---

## 🔒 Privacy

✅ **Your face is NOT sent to server**  
✅ **Your face is NOT stored**  
✅ **Only emotion label sent** ("happy", "sad", etc.)  
✅ **All detection happens in YOUR browser**  
✅ **You control it** - checkbox to enable/disable

---

## ⚙️ Technical Details

- **Technology:** Face.js (free, open-source)
- **Detection Rate:** Every 500ms (2 FPS)
- **Accuracy:** 85-90% for emotions
- **Privacy:** Maximum (local processing only)
- **Cost:** $0 (free)
- **Browsers:** Chrome, Firefox, Safari, Edge

---

## 🐛 Troubleshooting

**Problem:** Emotion shows "--"
- → Face not visible or too dark
- → Fix: Better lighting, face closer to camera

**Problem:** "Camera access denied"
- → Browser blocked camera
- → Fix: Click 🎥 icon in address bar, allow camera

**Problem:** Models won't load
- → Need internet (first time only)
- → Fix: Check connection, refresh page

**Problem:** Backend not responding
- → Flask server not running
- → Fix: Terminal 1: `python3 main.py`

---

## 📝 Files Changed

**Frontend:**
- `frontend/index.html` - Added facial monitoring panel
- `frontend/app.js` - Added emotion detection code

**Backend:**
- `backend/instance/tutoring_system.db` - Recreated database
- Already existed: `facial_expression_api.py`, API endpoints

---

## 🧪 Test It

Open browser console (F12) and you'll see:
```
✅ Facial recognition initialized
🟢 Facial detection started
📹 Emotion: happy
```

---

## 💡 Next Steps

### Immediate
- Test with your webcam
- Make different facial expressions
- See emotions change
- Check difficulty adapts

### Optional (Later)
- Upgrade to Azure Face API (95%+ accuracy)
- Create emotion graphs
- Add student engagement reports

---

## ❓ Need Help?

Check these files:
- `FACEJS_IMPLEMENTATION_COMPLETE.md` - Full guide
- `FACIAL_API_IMPLEMENTATION_GUIDE.md` - Deep technical details
- Browser console (F12) - Error messages

---

**That's it! You now have facial emotion detection working! 🎉**
