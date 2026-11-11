const API = '/api';
let sessionId = null;
let currentQuiz = null;
let userAnswers = {};

function switchTab(name, event) {
    document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
    document.querySelectorAll('.panel').forEach(function(p) { p.classList.remove('active'); });
    document.getElementById('tab-' + name).classList.add('active');
    if (event && event.target) event.target.classList.add('active');
    if (name === 'upload') loadDocs();
}

async function sendChat() {
    var input = document.getElementById('chatInput');
    var msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    addMsg('user', msg);
    addMsg('bot', 'Soch raha hoon...', true);
    document.getElementById('chatBtn').disabled = true;

    try {
        var res = await fetch(API + '/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg, session_id: sessionId, user_id: 'default_user'})
        });
        var data = await res.json();
        sessionId = data.session_id;
        removeLoading();

        var extra = '';
        if (data.sources && data.sources.length > 0) {
            extra = '<div style="margin-top:8px;">' + data.sources.map(function(s) {
                var name = s.split('/').pop();
                return '<span class="source-tag">&#128206; ' + name + '</span>';
            }).join('') + '</div>';
        }
        addMsg('bot', data.response + (extra ? '\n' : '') + extra);
    } catch(e) {
        removeLoading();
        addMsg('bot', 'Error: ' + e.message);
    }
    document.getElementById('chatBtn').disabled = false;
}

function addMsg(role, text, isLoading) {
    var box = document.getElementById('chatBox');
    var div = document.createElement('div');
    div.className = 'msg ' + (role === 'user' ? 'user' : 'bot') + (isLoading ? ' loading-msg' : '');
    var label = role === 'user' ? 'You' : 'EduAgent';
    div.innerHTML = '<div class="msg-label">' + label + '</div><div class="bubble">' + text + '</div>';
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function removeLoading() {
    var l = document.querySelector('.loading-msg');
    if (l) l.remove();
}

async function generateQuiz() {
    var topic = document.getElementById('quizTopic').value.trim();
    var count = document.getElementById('quizCount').value;
    if (!topic) { alert('Topic dalo!'); return; }

    document.getElementById('quizBtn').disabled = true;
    document.getElementById('quizArea').innerHTML = '<p class="loading">Quiz generate ho raha hai...</p>';
    userAnswers = {};

    try {
        var res = await fetch(API + '/quiz/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: topic, num_questions: parseInt(count)})
        });
        var data = await res.json();
        currentQuiz = data.questions;
        renderQuiz(data.questions, topic);
    } catch(e) {
        document.getElementById('quizArea').innerHTML = '<p style="color:#ef4444">Error: ' + e.message + '</p>';
    }
    document.getElementById('quizBtn').disabled = false;
}

function renderQuiz(questions, topic) {
    var html = '<h4 style="color:#94a3b8; margin-bottom:12px;">Topic: ' + topic + ' - ' + questions.length + ' Questions</h4>';
    questions.forEach(function(q, qi) {
        html += '<div style="margin-bottom:20px;"><p style="font-weight:600; margin-bottom:8px;">' + (qi+1) + '. ' + q.question + '</p>';
        Object.entries(q.options).forEach(function(entry) {
            var k = entry[0], v = entry[1];
            html += '<div class="quiz-option" id="opt-' + q.id + '-' + k + '" onclick="selectOption(' + q.id + ', \'' + k + '\', this)">' + k + '. ' + v + '</div>';
        });
        html += '</div>';
    });
    html += '<button class="send" onclick="submitQuiz(\'' + topic + '\')" style="margin-top:8px;">Submit Quiz</button>';
    document.getElementById('quizArea').innerHTML = html;
}

function selectOption(qid, key, el) {
    var opts = document.querySelectorAll('[id^="opt-' + qid + '-"]');
    opts.forEach(function(e) { e.classList.remove('selected'); });
    el.classList.add('selected');
    userAnswers[qid] = key;
}

async function submitQuiz(topic) {
    if (!currentQuiz) return;
    try {
        var res = await fetch(API + '/quiz/submit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: topic, user_id: 'default_user', questions: currentQuiz, answers: userAnswers})
        });
        var data = await res.json();

        if (data.results) {
            data.results.forEach(function(r) {
                var q = currentQuiz.find(function(q) { return q.id == r.question_id; });
                if (q) {
                    var correctEl = document.getElementById('opt-' + q.id + '-' + q.correct_answer);
                    if (correctEl) correctEl.classList.add('correct');
                    var userAns = userAnswers[q.id];
                    if (userAns && userAns !== q.correct_answer) {
                        var wrongEl = document.getElementById('opt-' + q.id + '-' + userAns);
                        if (wrongEl) wrongEl.classList.add('wrong');
                    }
                }
            });
        }

        var scoreDiv = document.createElement('div');
        scoreDiv.style.cssText = 'background:#0f172a; border-radius:8px; padding:16px; margin-top:16px;';
        scoreDiv.innerHTML = '<h4 style="color:#38bdf8">Score: ' + data.score + '%</h4><p style="margin-top:8px; color:#94a3b8">' + (data.feedback || '') + '</p>';
        document.getElementById('quizArea').appendChild(scoreDiv);
    } catch(e) {
        alert('Submission error: ' + e.message);
    }
}

async function doResearch() {
    var topic = document.getElementById('researchTopic').value.trim();
    if (!topic) { alert('Topic dalo!'); return; }
    document.getElementById('researchBtn').disabled = true;
    document.getElementById('researchResult').innerHTML = '<p class="loading">Research ho raha hai...</p>';

    try {
        var res = await fetch(API + '/research', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: topic})
        });
        var d = await res.json();

        var html = '<div style="margin-bottom:16px;"><div style="display:flex; gap:8px; align-items:center; margin-bottom:8px;"><h4 style="color:#38bdf8">' + (d.topic || topic) + '</h4><span class="tag">' + (d.difficulty || '') + '</span><span class="tag">' + (d.estimated_time || '') + '</span></div><p style="color:#94a3b8; line-height:1.6">' + (d.summary || '') + '</p></div>';

        if (d.key_concepts && d.key_concepts.length) {
            html += '<div style="margin-bottom:16px;"><h5 style="color:#e2e8f0; margin-bottom:8px;">Key Concepts</h5>';
            d.key_concepts.forEach(function(c) { html += '<span class="tag">&#128204; ' + c + '</span>'; });
            html += '</div>';
        }

        if (d.learning_path && d.learning_path.length) {
            html += '<h5 style="color:#e2e8f0; margin-bottom:8px;">Learning Path</h5>';
            d.learning_path.forEach(function(s) {
                html += '<div style="display:flex; gap:12px; margin-bottom:10px; padding:10px; background:#0f172a; border-radius:8px;"><div style="width:28px; height:28px; background:#38bdf8; color:#0f172a; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0;">' + s.step + '</div><div><div style="font-weight:600">' + s.title + '</div><div style="color:#94a3b8; font-size:0.85rem; margin-top:2px">' + s.description + '</div></div></div>';
            });
        }

        document.getElementById('researchResult').innerHTML = html;
    } catch(e) {
        document.getElementById('researchResult').innerHTML = '<p style="color:#ef4444">Error: ' + e.message + '</p>';
    }
    document.getElementById('researchBtn').disabled = false;
}

async function uploadFile(input) {
    var file = input.files[0];
    if (!file) return;
    var topic = document.getElementById('docTopic').value || 'general';
    var formData = new FormData();
    formData.append('file', file);
    formData.append('topic', topic);

    document.getElementById('uploadStatus').innerHTML = '<p class="loading">Uploading and processing...</p>';

    try {
        var res = await fetch(API + '/upload', {method: 'POST', body: formData});
        var d = await res.json();
        document.getElementById('uploadStatus').innerHTML = '<p style="color:#22c55e">&#9989; ' + d.message + '</p>';
        loadDocs();
    } catch(e) {
        document.getElementById('uploadStatus').innerHTML = '<p style="color:#ef4444">&#10060; Error: ' + e.message + '</p>';
    }
}

async function loadDocs() {
    try {
        var res = await fetch(API + '/documents');
        var docs = await res.json();
        var div = document.getElementById('docList');
        if (!docs.length) {
            div.innerHTML = '<h3>&#128218; Knowledge Base</h3><p style="color:#64748b; margin-top:8px;">No documents yet. Upload karo!</p>';
            return;
        }
        div.innerHTML = '<h3>&#128218; Knowledge Base</h3>' + docs.map(function(d) {
return '<div style="display:flex; justify-content:space-between; padding:10px; background:#0f172a; border-radius:8px; margin-top:8px;"><div><span style="color:#e2e8f0">&#128196; ' + d.filename + '</span><span class="tag" style="margin-left:8px">' + d.topic + '</span></div><div style="display:flex; align-items:center; gap:8px;"><span style="color:#64748b; font-size:0.8rem">' + d.chunks + ' chunks</span><button onclick="deleteDoc(' + d.id + ')" style="background:#ef444422; border:1px solid #ef4444; color:#ef4444; border-radius:6px; padding:2px 8px; cursor:pointer; font-size:0.75rem;">Delete</button></div></div>';        }).join('');
    } catch(e) {}
}

async function loadProgress() {
    var user = document.getElementById('progressUser').value.trim() || 'default_user';
    try {
        var res = await fetch(API + '/progress/' + user);
        var d = await res.json();

        if (!d.topics.length) {
            document.getElementById('progressArea').innerHTML = '<p style="color:#64748b">Koi quiz nahi diya abhi tak. Quiz tab mein jaao!</p>';
            return;
        }

        var html = '<div style="display:flex; gap:16px; margin-bottom:16px;"><div style="flex:1; background:#0f172a; border-radius:8px; padding:12px; text-align:center;"><div style="font-size:1.5rem; color:#38bdf8; font-weight:700">' + d.total_questions + '</div><div style="color:#94a3b8; font-size:0.8rem">Total Questions</div></div><div style="flex:1; background:#0f172a; border-radius:8px; padding:12px; text-align:center;"><div style="font-size:1.5rem; color:#38bdf8; font-weight:700">' + d.average_score + '%</div><div style="color:#94a3b8; font-size:0.8rem">Avg Score</div></div></div>';

        d.topics.forEach(function(t) {
            html += '<div style="background:#0f172a; border-radius:8px; padding:12px; margin-bottom:8px;"><div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span style="font-weight:600">' + t.topic + '</span><span style="color:#38bdf8">' + t.quiz_score + '%</span></div><div class="progress-bar"><div class="progress-fill" style="width:' + t.quiz_score + '%"></div></div><div style="color:#64748b; font-size:0.75rem; margin-top:4px">' + t.questions_correct + '/' + t.questions_attempted + ' correct</div></div>';
        });

        document.getElementById('progressArea').innerHTML = html;
    } catch(e) {
        document.getElementById('progressArea').innerHTML = '<p style="color:#ef4444">Error: ' + e.message + '</p>';
    }
}
async function deleteDoc(id) {
    if (!confirm('Delete this document?')) return;
    try {
        await fetch(`${API}/documents/${id}`, { method: 'DELETE' });
        loadDocs();
    } catch(e) {
        alert('Error: ' + e.message);
    }
}