// From: https://github.com/mdn/web-dictaphone

// set up basic variables for app

const record = document.querySelector('.microphone');
const audio = document.querySelector('.audio');

const recordText = "🎙";
const stopText = "🛑";

if (navigator.mediaDevices.getUserMedia) {
    const constraints = { audio: true };
    let chunks = [];
    
    let onSuccess = function(stream) {
        const mediaRecorder = new MediaRecorder(stream);
        let isRecording = false;
    
        record.onclick = function() {
            isRecording = !isRecording;
            if (!isRecording) {
                mediaRecorder.stop();
                console.log(mediaRecorder.state);
                record.innerText = recordText;
                audio.disabled = false;
                return;
            }

            mediaRecorder.start();
            console.log(mediaRecorder.state);
            record.innerText = stopText;
            audio.disabled = true;
        }
    
        mediaRecorder.onstop = function(e) {
          const blob = new Blob(chunks, {'type' : 'audio/ogg; codecs=opus'});
          chunks = [];
          const audioURL = window.URL.createObjectURL(blob);
          audio.src = audioURL;
        }
    
        mediaRecorder.ondataavailable = function(e) {
          chunks.push(e.data);
        }

        isRecording = true;
        mediaRecorder.start();
        record.innerText = stopText;
    }
    
    let onError = function(err) {
        console.log('Error : ' + err);
    }
    
    record.disabled = false;
    record.onclick = function() {
        navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);
    }
} else {
    console.log('getUserMedia not supported on your browser!');
}
