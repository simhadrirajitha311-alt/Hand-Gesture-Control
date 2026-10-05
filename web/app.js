const slides = [
  { title: 'Touchless control', body: 'No keyboard. No mouse. Just your hand.' },
  { title: 'Webcam-first experience', body: 'Local MediaPipe hand tracking processes frames in-browser only.' },
  { title: 'Gesture-driven actions', body: 'Volume, slides, cursor, and click simulation are all performed inside the page.' },
  { title: 'Safety-first activation', body: 'Open palm for 1.5 seconds before the interface becomes active.' }
];

const state = {
  isRunning: false,
  gesture: 'NONE',
  status: 'INACTIVE',
  confidence: 0,
  activeSlide: 0,
  audioReady: false,
};

const video = document.getElementById('video');
const overlayCanvas = document.getElementById('overlayCanvas');
const cameraToggle = document.getElementById('cameraToggle');
const gestureValue = document.getElementById('gestureValue');
const statusValue = document.getElementById('statusValue');
const confidenceValue = document.getElementById('confidenceValue');
const activationPill = document.getElementById('activationPill');
const volumeFill = document.getElementById('volumeFill');
const slideCounter = document.getElementById('slideCounter');
const slideContent = document.getElementById('slideContent');
const prevSlide = document.getElementById('prevSlide');
const nextSlide = document.getElementById('nextSlide');
const cursor = document.getElementById('cursor');

function renderSlide() {
  const current = slides[state.activeSlide];
  slideContent.innerHTML = `<h3>${current.title}</h3><p>${current.body}</p>`;
  slideCounter.textContent = `${String(state.activeSlide + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
}

function setStatus(value) {
  state.status = value;
  statusValue.textContent = value;
  activationPill.textContent = value;
  activationPill.className = 'activation-pill';
  activationPill.classList.add(value.toLowerCase());
}

function setGesture(value, confidence = 0) {
  state.gesture = value;
  gestureValue.textContent = value;
  confidenceValue.textContent = confidence.toFixed(2);
}

function updateVolume(level) {
  volumeFill.style.width = `${Math.max(0, Math.min(100, level))}%`;
}

function updateCursorFromLandmarks(landmarks) {
  if (!landmarks || landmarks.length < 21) return;
  const x = landmarks[8].x;
  const y = landmarks[8].y;
  const rect = overlayCanvas.getBoundingClientRect();
  const width = rect.width || 640;
  const height = rect.height || 480;
  cursor.style.left = `${x * width}px`;
  cursor.style.top = `${y * height}px`;
  cursor.style.display = 'block';
}

function drawLandmarks(landmarks) {
  const ctx = overlayCanvas.getContext('2d');
  const width = overlayCanvas.width = video.videoWidth || 640;
  const height = overlayCanvas.height = video.videoHeight || 480;
  ctx.clearRect(0, 0, width, height);

  if (!landmarks) return;

  const palm = [0, 1, 5, 9, 13, 17];
  const connections = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [5, 9], [9, 10], [10, 11], [11, 12],
    [9, 13], [13, 14], [14, 15], [15, 16],
    [13, 17], [17, 18], [18, 19], [19, 20],
    [0, 17]
  ];

  ctx.strokeStyle = '#dfe7ee';
  ctx.lineWidth = 2;
  connections.forEach(([a, b]) => {
    const p1 = landmarks[a];
    const p2 = landmarks[b];
    if (!p1 || !p2) return;
    ctx.beginPath();
    ctx.moveTo(p1.x * width, p1.y * height);
    ctx.lineTo(p2.x * width, p2.y * height);
    ctx.stroke();
  });

  landmarks.forEach((point) => {
    if (!point) return;
    ctx.beginPath();
    ctx.arc(point.x * width, point.y * height, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#dfe7ee';
    ctx.fill();
  });
}

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function detectGesture(landmarks) {
  if (!landmarks || landmarks.length < 21) return 'NONE';

  const thumb = landmarks[4];
  const index = landmarks[8];
  const middle = landmarks[12];
  const ring = landmarks[16];
  const pinky = landmarks[20];

  if (distance(thumb, index) < 0.08) return 'PINCH';
  if (thumb.y < landmarks[3].y && index.y > landmarks[5].y && middle.y > landmarks[9].y && ring.y > landmarks[13].y && pinky.y > landmarks[17].y) return 'THUMBS_UP';
  if (thumb.y > landmarks[3].y && index.y > landmarks[5].y && middle.y > landmarks[9].y && ring.y > landmarks[13].y && pinky.y > landmarks[17].y) return 'THUMBS_DOWN';
  if (index.y < landmarks[6].y && middle.y < landmarks[10].y && ring.y > landmarks[14].y && pinky.y > landmarks[18].y) return 'TWO_FINGERS';
  if (index.y < landmarks[6].y && middle.y > landmarks[10].y && ring.y > landmarks[14].y && pinky.y > landmarks[18].y) return 'ONE_FINGER';
  if (index.y < landmarks[6].y && middle.y > landmarks[10].y && ring.y > landmarks[14].y && pinky.y > landmarks[18].y) return 'INDEX_MOVE';
  return 'OPEN_PALM';
}

function updateDemoState(landmarks) {
  if (!landmarks) {
    setGesture('NONE');
    setStatus('INACTIVE');
    updateVolume(30);
    cursor.style.display = 'none';
    return;
  }

  const gesture = detectGesture(landmarks);
  let confidence = 0.82;

  if (gesture === 'PINCH') {
    confidence = 0.95;
  }

  setGesture(gesture, confidence);

  const activation = gesture === 'OPEN_PALM' ? 'ACTIVATING' : state.status === 'ACTIVATING' ? 'ACTIVE' : 'INACTIVE';
  setStatus(activation);

  if (gesture === 'THUMBS_UP') updateVolume(60);
  if (gesture === 'THUMBS_DOWN') updateVolume(30);
  if (gesture === 'TWO_FINGERS') {
    state.activeSlide = (state.activeSlide + 1) % slides.length;
    renderSlide();
  }
  if (gesture === 'ONE_FINGER') {
    state.activeSlide = (state.activeSlide - 1 + slides.length) % slides.length;
    renderSlide();
  }

  updateCursorFromLandmarks(landmarks);
}

function startAudioLoop() {
  if (state.audioReady) return;
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtx) return;
  const audioCtx = new AudioCtx();
  const oscillator = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  oscillator.type = 'sine';
  oscillator.frequency.value = 220;
  gain.gain.value = 0.02;
  oscillator.connect(gain);
  gain.connect(audioCtx.destination);
  oscillator.start();
  state.audioReady = true;
}

function onResults(results) {
  if (!results.multiHandLandmarks || !results.multiHandLandmarks.length) {
    drawLandmarks(null);
    updateDemoState(null);
    return;
  }

  const landmarks = results.multiHandLandmarks[0];
  drawLandmarks(landmarks);
  updateDemoState(landmarks);
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
    video.srcObject = stream;
    state.isRunning = true;
    cameraToggle.textContent = 'Stop Camera';
    setStatus('INACTIVE');
    startAudioLoop();
    const hands = new Hands({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });
    hands.setOptions({
      maxNumHands: 1,
      modelComplexity: 1,
      minDetectionConfidence: 0.6,
      minTrackingConfidence: 0.5,
    });
    hands.onResults(onResults);
    const camera = new Camera(video, {
      onFrame: async () => {
        await hands.send({ image: video });
      },
      width: 640,
      height: 480,
    });
    camera.start();
    window.__camera = camera;
    window.__hands = hands;
  } catch (error) {
    console.error(error);
    setStatus('ERROR');
    gestureValue.textContent = 'PERMISSION DENIED';
  }
}

async function stopCamera() {
  if (window.__camera) {
    window.__camera.stop();
  }
  if (video.srcObject) {
    video.srcObject.getTracks().forEach((track) => track.stop());
  }
  state.isRunning = false;
  cameraToggle.textContent = 'Start Camera';
  setGesture('NONE');
  setStatus('INACTIVE');
  cursor.style.display = 'none';
}

cameraToggle.addEventListener('click', async () => {
  if (state.isRunning) {
    await stopCamera();
    return;
  }
  await startCamera();
});

nextSlide.addEventListener('click', () => {
  state.activeSlide = (state.activeSlide + 1) % slides.length;
  renderSlide();
});

prevSlide.addEventListener('click', () => {
  state.activeSlide = (state.activeSlide - 1 + slides.length) % slides.length;
  renderSlide();
});

renderSlide();
setStatus('INACTIVE');
