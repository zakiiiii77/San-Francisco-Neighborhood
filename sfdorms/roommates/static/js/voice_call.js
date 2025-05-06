let localConnection;
let remoteAudio = document.getElementById('remoteAudio');
let webSocket;
let localStream;
let isMuted = false;
let callStarted = false;

const callStatus = document.getElementById('callStatus');
const remoteUser = document.getElementById('remoteUser');

document.getElementById('startCall').onclick = async function () {

    if (callStarted) {
        alert("Call already in progress");
        return;
    }

    const localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

    localConnection = new RTCPeerConnection();

    localStream.getTracks().forEach(track => {
        localConnection.addTrack(track, localStream);
    });

    localConnection.ontrack = event => {
        remoteAudio.srcObject = event.streams[0];
        callStatus.textContent = "Status: Connected";
    };

    const room = window.roomName;
    webSocket = new webSocket(`ws://${window.location.host}/ws/call/${room}/`);

    webSocket.onmessage = async function (e) {
        const data = JSON.parse(e.data);

        if (data.username) {
            remoteUser.textContent = `Remote user: ${data.username}`;
        }

        if (data.type === 'offer') {
            await localConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
            const answer = await localConnection.createAnswer();
            await localConnection.setLocalDescription(answer);
            webSocket.send(JSON.stringify({ type:'answer', answer }));
        } else if (data.type === 'answer') {
            await localConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
        } else if (data.type === 'ice-candidate') {
            try {
                await localConnection.addIceCandidate(data.candidate);
            } catch (e) {
                console.error('Error adding ICE candidate', e);
            }
        }
    };

    localConnection.onicecandidate = event => {
        if (event.candidate) {
            webSocket.send(JSON.stringify({
                type: 'ice-candidate',
                candidate: event.candidate
            }));
        }
    };

    const offer = await localConnection.createOffer();
    await localConnection.setLocalDescription(offer);
    webSocket.onopen = () => {
        webSocket.send(JSON.stringify({ type: 'offer', offer, username: window.currentUsername }));
    };

    callStatus.textContent = "Status: Calling...";
    callStarted = true;
    document.getElementById('muteBtn').disapled = false;
    document.getElementById('hangupBtn').disapled = false;
};

document.getElementById('muteBtn').onclick = function () {
    if (!localStream) return;

    localStream.getAudioTracks().forEach(track => {
        track.enabled = isMuted;
    });

    isMuted = !isMuted;
    this.textContent = isMuted? 'Unmute' : 'Mute';
    callStatus.textContent = isMuted? "Status: Muted" : "Status: Connected";
};

document.getElementById('hangupBtn').onclick = function () {
    if (localConnection) {
        localConnection.close();
        localConnection = null;
    }

    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }

    if (webSocket) {
        webSocket.close();
        webSocket = null;
    }

    callStatus.textContent = "Status: Disconnected";
    remoteUser.textContent = "Remote user: N/A";
    isMuted = false;
    callStarted = false;
    document.getElementById('muteBtn').disapled = true;
    document.getElementById('hangupBtn').disapled = true;
    document.getElementById('muteBtn').textContent = 'Mute';
};

