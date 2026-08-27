// VOX-AI Web Phone UI & Live Metrics JavaScript Controller

let socket = null;
let isCallActive = false;
let session_id = null;
let turnCount = 0;
let audioContext = null;

function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function startCall() {
    initAudioContext();
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/call`;

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        isCallActive = true;
        updateUIState(true);
        addTranscriptMessage("system", "Call connected to VOX-AI Voice Engine.");
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleServerEvent(data);
        } catch (e) {
            console.error("Error parsing WebSocket event:", e);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        addTranscriptMessage("system", "Connection error encountered.");
    };

    socket.onclose = () => {
        isCallActive = false;
        updateUIState(false);
        addTranscriptMessage("system", "Call ended.");
    };
}

function endCall() {
    if (socket) {
        socket.close();
        socket = null;
    }
    isCallActive = false;
    updateUIState(false);
}

function sendInterrupt() {
    if (socket && isCallActive) {
        socket.send(JSON.stringify({ action: "interrupt" }));
        addTranscriptMessage("system", "⚡ User interrupted AI mid-speech!");
        setAvatarState("interrupted");
    }
}

function sendSimulatedSpeech() {
    const inputEl = document.getElementById("sim-speech-input");
    const text = inputEl.value.trim();
    if (!text) return;

    if (!isCallActive) {
        startCall();
        setTimeout(() => {
            sendSpeechText(text);
        }, 500);
    } else {
        sendSpeechText(text);
    }
    inputEl.value = "";
}

function sendSpeechText(text) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        addTranscriptMessage("user", text);
        socket.send(JSON.stringify({ action: "speak_text", text: text }));
        setAvatarState("thinking");
    }
}

function presetScenario(text) {
    document.getElementById("sim-speech-input").value = text;
    sendSimulatedSpeech();
}

function handleServerEvent(data) {
    if (data.event === "connected") {
        session_id = data.session_id;
        document.getElementById("session-badge").innerText = `Session: ${session_id}`;
    }
    else if (data.event === "stt_complete") {
        if (data.stt_latency_ms) {
            document.getElementById("stt-latency-val").innerText = `${data.stt_latency_ms} ms`;
        }
    }
    else if (data.event === "sentiment_analysis") {
        updateSentimentUI(data.sentiment, data.is_escalated);
    }
    else if (data.event === "llm_complete") {
        if (data.response_text) {
            addTranscriptMessage("assistant", data.response_text);
        }
        if (data.llm_latency_ms) {
            document.getElementById("llm-latency-val").innerText = `${data.llm_latency_ms} ms`;
        }
        if (data.function_calls && data.function_calls.length > 0) {
            logFunctionCalls(data.function_calls);
        }
        setAvatarState("speaking");
    }
    else if (data.event === "audio_chunk") {
        if (data.tts_latency_ms) {
            document.getElementById("tts-latency-val").innerText = `${data.tts_latency_ms} ms`;
        }
        if (data.audio_base64) {
            playAudioBase64(data.audio_base64);
        }
    }
    else if (data.event === "turn_complete") {
        const breakdown = data.latency_breakdown;
        if (breakdown) {
            document.getElementById("total-latency-val").innerText = `${breakdown.total_end_to_end_ms} ms`;
            if (breakdown.within_target) {
                document.getElementById("total-latency-val").className = "text-xl font-bold text-emerald-400 my-1";
            } else {
                document.getElementById("total-latency-val").className = "text-xl font-bold text-amber-400 my-1";
            }
        }
        turnCount++;
        document.getElementById("turn-counter").innerText = `Turns: ${turnCount}`;
        setAvatarState("listening");
    }
    else if (data.event === "interrupted") {
        setAvatarState("interrupted");
    }
}

function updateSentimentUI(sentiment, isEscalated) {
    const score = sentiment.score;
    const label = sentiment.label;
    const textEl = document.getElementById("sentiment-text");
    const badgeEl = document.getElementById("escalation-badge");
    const iconContainer = document.getElementById("sentiment-icon-badge");

    textEl.innerText = `${label.toUpperCase()} (${score})`;

    if (sentiment.is_angry) {
        textEl.className = "text-sm font-bold text-rose-400";
        iconContainer.innerHTML = `<i class="fa-solid fa-face-angry text-rose-400"></i>`;
    } else if (score < 0) {
        textEl.className = "text-sm font-bold text-amber-400";
        iconContainer.innerHTML = `<i class="fa-solid fa-face-frown text-amber-400"></i>`;
    } else if (score > 0) {
        textEl.className = "text-sm font-bold text-emerald-400";
        iconContainer.innerHTML = `<i class="fa-solid fa-face-smile text-emerald-400"></i>`;
    } else {
        textEl.className = "text-sm font-bold text-slate-200";
        iconContainer.innerHTML = `<i class="fa-solid fa-face-meh text-slate-400"></i>`;
    }

    if (isEscalated) {
        badgeEl.className = "bg-rose-950/80 border border-rose-700/80 px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-300 flex items-center space-x-2 animate-pulse";
        badgeEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i><span>ESCALATED: Tier-2 Human Agent</span>`;
    } else {
        badgeEl.className = "bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 flex items-center space-x-2";
        badgeEl.innerHTML = `<i class="fa-solid fa-shield-halved"></i><span>Status: Normal AI Support</span>`;
    }
}

function updateUIState(active) {
    const btnStart = document.getElementById("btn-start-call");
    const btnEnd = document.getElementById("btn-end-call");
    const btnInterrupt = document.getElementById("btn-interrupt");
    const statusText = document.getElementById("call-status-text");

    if (active) {
        btnStart.disabled = true;
        btnStart.classList.add("opacity-50", "cursor-not-allowed");

        btnEnd.disabled = false;
        btnEnd.classList.remove("opacity-50", "cursor-not-allowed");
        btnEnd.classList.add("bg-rose-600", "hover:bg-rose-500");

        btnInterrupt.disabled = false;
        btnInterrupt.classList.remove("opacity-50", "cursor-not-allowed");
        btnInterrupt.classList.add("bg-amber-600", "hover:bg-amber-500");

        statusText.innerText = "Call Connected - Listening";
        setAvatarState("listening");
    } else {
        btnStart.disabled = false;
        btnStart.classList.remove("opacity-50", "cursor-not-allowed");

        btnEnd.disabled = true;
        btnEnd.classList.add("opacity-50", "cursor-not-allowed");

        btnInterrupt.disabled = true;
        btnInterrupt.classList.add("opacity-50", "cursor-not-allowed");

        statusText.innerText = "Call Ended";
        setAvatarState("idle");
    }
}

function setAvatarState(state) {
    const avatar = document.getElementById("avatar-container");
    const icon = document.getElementById("avatar-icon");
    const visualizer = document.getElementById("visualizer-box");

    if (state === "speaking") {
        avatar.className = "w-28 h-28 rounded-full bg-emerald-950/80 border-4 border-emerald-500 flex items-center justify-center transition-all duration-300 shadow-xl shadow-emerald-500/30 pulse-wave";
        icon.className = "fa-solid fa-volume-high text-4xl text-emerald-400";
        visualizer.classList.remove("opacity-30");
    } else if (state === "thinking") {
        avatar.className = "w-28 h-28 rounded-full bg-indigo-950/80 border-4 border-indigo-500 flex items-center justify-center transition-all duration-300 shadow-xl shadow-indigo-500/30";
        icon.className = "fa-solid fa-brain text-4xl text-indigo-400 animate-pulse";
        visualizer.classList.add("opacity-30");
    } else if (state === "interrupted") {
        avatar.className = "w-28 h-28 rounded-full bg-amber-950/80 border-4 border-amber-500 flex items-center justify-center transition-all duration-300 shadow-xl shadow-amber-500/30";
        icon.className = "fa-solid fa-hand text-4xl text-amber-400";
        visualizer.classList.add("opacity-30");
    } else if (state === "listening") {
        avatar.className = "w-28 h-28 rounded-full bg-cyan-950/80 border-4 border-cyan-500 flex items-center justify-center transition-all duration-300 shadow-xl shadow-cyan-500/30";
        icon.className = "fa-solid fa-microphone text-4xl text-cyan-400";
        visualizer.classList.add("opacity-30");
    } else {
        avatar.className = "w-28 h-28 rounded-full bg-slate-800 border-4 border-slate-700 flex items-center justify-center transition-all duration-300 shadow-xl";
        icon.className = "fa-solid fa-robot text-4xl text-slate-400";
        visualizer.classList.add("opacity-30");
    }
}

function addTranscriptMessage(role, text) {
    const container = document.getElementById("transcript-container");
    const emptyMsg = container.querySelector(".italic");
    if (emptyMsg) {
        container.innerHTML = "";
    }

    const msgDiv = document.createElement("div");
    if (role === "user") {
        msgDiv.className = "bg-slate-800 border border-slate-700/60 rounded-xl p-3 text-right ml-8";
        msgDiv.innerHTML = `<span class="text-[10px] text-cyan-400 font-semibold block mb-1">User</span><p class="text-slate-200">${escapeHtml(text)}</p>`;
    } else if (role === "assistant") {
        msgDiv.className = "bg-cyan-950/50 border border-cyan-800/60 rounded-xl p-3 text-left mr-8";
        msgDiv.innerHTML = `<span class="text-[10px] text-emerald-400 font-semibold block mb-1">VOX-AI Agent</span><p class="text-slate-200">${escapeHtml(text)}</p>`;
    } else {
        msgDiv.className = "bg-slate-900 border border-slate-800 text-slate-400 text-center text-[11px] py-1 rounded-lg";
        msgDiv.innerText = text;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function logFunctionCalls(calls) {
    const container = document.getElementById("function-log-container");
    const emptyMsg = container.querySelector(".italic");
    if (emptyMsg) {
        container.innerHTML = "";
    }

    calls.forEach(call => {
        const itemDiv = document.createElement("div");
        itemDiv.className = "bg-slate-950 border border-slate-800 rounded-lg p-2 text-[11px]";
        itemDiv.innerHTML = `
            <div class="text-indigo-400 font-bold">⚡ ${call.tool_name}(${JSON.stringify(call.arguments)})</div>
            <div class="text-slate-400 text-[10px] mt-1">Result: ${JSON.stringify(call.result)}</div>
        `;
        container.appendChild(itemDiv);
    });
    container.scrollTop = container.scrollHeight;
}

function playAudioBase64(base64Data) {
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes.buffer], { type: "audio/wav" });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play().catch(e => console.log("Audio autoplay prevented by browser:", e));
    } catch (e) {
        console.error("Error playing audio chunk:", e);
    }
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
