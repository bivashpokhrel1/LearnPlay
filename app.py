"""
LearnPlay — Korean & Python Learning Hub
==========================================
4 games in one app:
- DumbQuiz: Korean language quiz
- PyQuiz: Python programming quiz
- Flashko: Korean flashcards
- ScramKo: Korean word scramble
"""

import streamlit as st
import random
import json
import os
from datetime import datetime
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LearnPlay",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Outfit:wght@400;500;600;700;800;900&family=Fira+Code:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    background: #0c0c14;
    color: #f0f0ff;
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0px transparent; }
    50%       { box-shadow: 0 0 18px var(--glow); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-6px); }
}
@keyframes spin-slow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

/* Home screen cards */
.game-card {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 20px;
    padding: 28px 20px 20px;
    text-align: center;
    cursor: pointer;
    transition: transform 0.25s cubic-bezier(.34,1.56,.64,1), border-color 0.25s, box-shadow 0.25s;
    margin-bottom: 16px;
    animation: fadeInUp 0.5s ease both;
    position: relative;
    overflow: hidden;
}
.game-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, transparent 40%, rgba(255,255,255,0.03) 100%);
    pointer-events: none;
}
.game-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6);
}
.game-icon {
    font-size: 2.8rem; margin-bottom: 12px; display: block;
    animation: float 3s ease-in-out infinite;
}
.game-title { font-size: 1.25rem; font-weight: 900; margin-bottom: 4px; }
.game-desc { font-size: 0.78rem; color: #555; }
.game-stats {
    font-size: 0.78rem; margin-top: 10px; font-weight: 700;
    display: inline-block;
    background: linear-gradient(90deg, currentColor, #fff, currentColor);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
}

/* Top scorer pill on card */
.top-scorer-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0d0d18; border: 1px solid #2a2a4a;
    border-radius: 99px; padding: 4px 12px;
    font-size: 0.72rem; font-weight: 700;
    margin-top: 10px;
    animation: fadeInUp 0.6s ease both;
}
.top-scorer-name { color: #f0f0ff; }
.top-scorer-score { color: inherit; }

/* Hero */
.hero { text-align: center; padding: 20px 0 12px 0; animation: fadeInUp 0.4s ease both; }
.hero-title {
    font-size: 3.2rem; font-weight: 900;
    background: linear-gradient(135deg, #6366f1 0%, #ec4899 50%, #f59e0b 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -2px;
    animation: shimmer 4s linear infinite;
}
.hero-sub { font-size: 0.88rem; color: #444; margin-top: 4px; }

/* Home leaderboard */
.home-lb {
    background: #13131f; border: 1px solid #1e1e30;
    border-radius: 14px; padding: 16px 20px; margin-top: 24px;
    animation: fadeInUp 0.7s ease both;
}
.home-lb-title {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #444; margin-bottom: 12px;
}
.home-lb-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #0f0f1a;
    font-size: 0.85rem;
}
.home-lb-row:last-child { border-bottom: none; }
.home-lb-rank { min-width: 24px; font-weight: 800; }
.home-lb-game { font-size: 0.7rem; color: #444; min-width: 70px; }
.home-lb-name { flex: 1; color: #f0f0ff; font-weight: 600; }
.home-lb-score { font-weight: 800; }

/* Question card */
.q-card {
    background: #13131f; border: 1px solid #1e1e30;
    border-radius: 14px; padding: 24px; margin: 12px 0;
}
.q-cat { font-size: 0.65rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #444; margin-bottom: 8px; }
.q-text { font-size: 1.05rem; font-weight: 600; color: #f0f0ff; margin-bottom: 8px; line-height: 1.5; }
.q-korean { font-size: 1.8rem; color: #6366f1; margin: 6px 0; }
.code-block {
    background: #0c0c14; border: 1px solid #1e1e30; border-radius: 8px;
    padding: 10px 14px; font-family: 'Fira Code', monospace; font-size: 0.82rem;
    color: #f0f0ff; margin: 8px 0; white-space: pre; overflow-x: auto;
}
.diff-easy { background:#0d2e1a; color:#4ade80; border:1px solid #4ade8033; border-radius:99px; padding:2px 8px; font-size:0.65rem; font-weight:700; }
.diff-medium { background:#2e2a0d; color:#f59e0b; border:1px solid #f59e0b33; border-radius:99px; padding:2px 8px; font-size:0.65rem; font-weight:700; }
.diff-hard { background:#2e0d0d; color:#f87171; border:1px solid #f8717133; border-radius:99px; padding:2px 8px; font-size:0.65rem; font-weight:700; }

.correct-box { background:#0d2e1a; border-left:3px solid #4ade80; border-radius:0 8px 8px 0; padding:10px 14px; color:#4ade80; font-weight:700; margin:6px 0; }
.wrong-box { background:#2e0d0d; border-left:3px solid #f87171; border-radius:0 8px 8px 0; padding:10px 14px; color:#f87171; font-weight:700; margin:6px 0; }
.explanation { background:#13131f; border:1px solid #1e1e30; border-radius:8px; padding:10px 14px; color:#888; font-size:0.82rem; margin:6px 0; }

/* Flashcard */
.flash-front { background:linear-gradient(135deg,#1a1a2e,#16213e); border:1px solid #2a2a4a; border-radius:18px; padding:40px 28px; text-align:center; min-height:200px; display:flex; flex-direction:column; align-items:center; justify-content:center; margin:12px 0; }
.flash-back { background:linear-gradient(135deg,#1a2e1a,#162116); border:1px solid #2a4a2a; border-radius:18px; padding:40px 28px; text-align:center; min-height:200px; display:flex; flex-direction:column; align-items:center; justify-content:center; margin:12px 0; }
.card-korean { font-size:3rem; font-weight:700; color:#8b5cf6; margin-bottom:6px; }
.card-romanized { font-size:0.95rem; color:#555; }
.card-english { font-size:1.6rem; font-weight:700; color:#4ade80; margin-bottom:6px; }
.card-example { font-size:0.82rem; color:#777; font-style:italic; margin-top:6px; }

/* ScramKo */
.scramble-card { background:#13131f; border:1px solid #1e1e30; border-radius:14px; padding:28px; text-align:center; margin:12px 0; }
.scrambled-word { font-size:2.2rem; font-weight:900; letter-spacing:6px; color:#f59e0b; margin:14px 0; }
.meaning-text { font-size:0.95rem; color:#888; }
.answer-reveal { background:#0c0c14; border:1px solid #1e1e30; border-radius:8px; padding:12px; text-align:center; margin:6px 0; }
.korean-big { font-size:1.8rem; color:#8b5cf6; font-weight:700; }

/* Score card */
.score-card { background:#13131f; border:1px solid #1e1e30; border-radius:14px; padding:24px; text-align:center; margin:12px 0; }
.big-score { font-size:3.5rem; font-weight:900; background:linear-gradient(135deg,#6366f1,#ec4899); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }

/* Leaderboard */
.lb-row { display:flex; align-items:center; padding:8px 0; border-bottom:1px solid #1a1a2a; font-size:0.88rem; }
.lb-row:last-child { border-bottom:none; }
.lb-rank { color:#444; min-width:28px; font-weight:700; }
.lb-name { flex:1; color:#f0f0ff; }
.lb-score { color:#6366f1; font-weight:700; }

.progress-text { color:#444; font-size:0.82rem; text-align:center; }

/* Buttons */
.stButton > button {
    background:#13131f !important; border:1px solid #1e1e30 !important;
    color:#f0f0ff !important; border-radius:8px !important;
    font-family:'Outfit',sans-serif !important; font-weight:700 !important;
}
.stButton > button:hover { border-color:#6366f1 !important; color:#6366f1 !important; }

.stTextInput > div > div > input {
    background:#13131f !important; border:1px solid #1e1e30 !important;
    border-radius:8px !important; color:#f0f0ff !important;
    font-family:'Outfit','Noto Sans KR',sans-serif !important;
    font-size:1rem !important; text-align:center !important;
}
.stSelectbox > div > div { background:#13131f !important; border-color:#1e1e30 !important; color:#f0f0ff !important; }
section[data-testid="stSidebar"] { background:#080810 !important; border-right:1px solid #1e1e30 !important; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Data Banks
# ─────────────────────────────────────────────
DUMBQUIZ_QUESTIONS = [
    # ── VOCABULARY ──────────────────────────────────────────────────────────
    {"category":"Vocabulary","difficulty":"easy","question":"What does '안녕하세요' mean?","korean":"안녕하세요","options":["Hello","Goodbye","Thank you","Sorry"],"answer":0,"explanation":"'안녕하세요' (annyeonghaseyo) is the formal way to say hello in Korean."},
    {"category":"Vocabulary","difficulty":"easy","question":"How do you say 'thank you' formally?","korean":"","options":["괜찮아요","감사합니다","미안해요","좋아요"],"answer":1,"explanation":"'감사합니다' (gamsahamnida) means thank you formally."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '물' mean?","korean":"물","options":["Fire","Water","Food","Rice"],"answer":1,"explanation":"'물' (mul) means water."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '밥' mean?","korean":"밥","options":["Soup","Noodles","Rice/Meal","Bread"],"answer":2,"explanation":"'밥' (bap) means cooked rice or a meal."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '사람' mean?","korean":"사람","options":["Animal","Person","Place","Thing"],"answer":1,"explanation":"'사람' (saram) means person or people."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '집' mean?","korean":"집","options":["School","Hospital","House/Home","Office"],"answer":2,"explanation":"'집' (jip) means house or home."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '책' mean?","korean":"책","options":["Pen","Book","Desk","Chair"],"answer":1,"explanation":"'책' (chaek) means book."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '차' mean?","korean":"차","options":["Bus","Bicycle","Car/Tea","Train"],"answer":2,"explanation":"'차' (cha) means car or tea depending on context."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '고양이' mean?","korean":"고양이","options":["Dog","Cat","Bird","Fish"],"answer":1,"explanation":"'고양이' (goyangi) means cat."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '개' mean?","korean":"개","options":["Cat","Rabbit","Dog","Horse"],"answer":2,"explanation":"'개' (gae) means dog."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '오늘' mean?","korean":"오늘","options":["Yesterday","Tomorrow","Today","Now"],"answer":2,"explanation":"'오늘' (oneul) means today."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '내일' mean?","korean":"내일","options":["Yesterday","Today","Tomorrow","Later"],"answer":2,"explanation":"'내일' (naeil) means tomorrow."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '어제' mean?","korean":"어제","options":["Today","Yesterday","Tomorrow","Before"],"answer":1,"explanation":"'어제' (eoje) means yesterday."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '친구' mean?","korean":"친구","options":["Enemy","Stranger","Friend","Teacher"],"answer":2,"explanation":"'친구' (chingu) means friend."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '학교' mean?","korean":"학교","options":["Hospital","Market","School","Library"],"answer":2,"explanation":"'학교' (hakgyo) means school."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '어디예요?' mean?","korean":"어디예요?","options":["What is it?","Where is it?","How much?","When is it?"],"answer":1,"explanation":"'어디예요?' means 'Where is it?'"},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '얼마예요?' mean?","korean":"얼마예요?","options":["How many?","What time?","How much?","How far?"],"answer":2,"explanation":"'얼마예요?' means 'How much is it?'"},
    {"category":"Vocabulary","difficulty":"medium","question":"Which word means 'delicious'?","korean":"","options":["맛있어요","맛없어요","배고파요","배불러요"],"answer":0,"explanation":"'맛있어요' (masisseoyo) means delicious."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '바쁘다' mean?","korean":"바쁘다","options":["Lazy","Happy","Busy","Bored"],"answer":2,"explanation":"'바쁘다' (bappeuda) means to be busy."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '시간' mean?","korean":"시간","options":["Money","Space","Time","Speed"],"answer":2,"explanation":"'시간' (sigan) means time or hour."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '날씨' mean?","korean":"날씨","options":["Season","Weather","Temperature","Wind"],"answer":1,"explanation":"'날씨' (nalssi) means weather."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '음식' mean?","korean":"음식","options":["Drink","Food","Restaurant","Kitchen"],"answer":1,"explanation":"'음식' (eumsik) means food."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '주말' mean?","korean":"주말","options":["Weekday","Holiday","Weekend","Morning"],"answer":2,"explanation":"'주말' (jumal) means weekend."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '여행' mean?","korean":"여행","options":["Work","Study","Travel","Rest"],"answer":2,"explanation":"'여행' (yeohaeng) means travel or trip."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '병원' mean?","korean":"병원","options":["School","Hospital","Pharmacy","Clinic"],"answer":1,"explanation":"'병원' (byeongwon) means hospital."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '시장' mean?","korean":"시장","options":["Restaurant","Market","Mall","Store"],"answer":1,"explanation":"'시장' (sijang) means market or mayor."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '전화' mean?","korean":"전화","options":["Email","Letter","Telephone/Call","Message"],"answer":2,"explanation":"'전화' (jeonhwa) means telephone or phone call."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '괜찮아요' mean?","korean":"괜찮아요","options":["I'm hungry","I'm tired","It's okay","I'm busy"],"answer":2,"explanation":"'괜찮아요' means 'it's okay' or 'I'm fine'."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '피곤해요' mean?","korean":"피곤해요","options":["I'm hungry","I'm happy","I'm tired","I'm cold"],"answer":2,"explanation":"'피곤해요' means 'I'm tired'."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '그리워요' mean?","korean":"그리워요","options":["I'm angry","I miss (someone)","I'm jealous","I'm scared"],"answer":1,"explanation":"'그리워요' (geuriwoyo) means 'I miss (someone)'."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '부럽다' mean?","korean":"부럽다","options":["Angry","Jealous/Envious","Sad","Disappointed"],"answer":1,"explanation":"'부럽다' (bureoptda) means to be jealous or envious."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '복잡하다' mean?","korean":"복잡하다","options":["Simple","Empty","Complicated/Crowded","Quiet"],"answer":2,"explanation":"'복잡하다' (bokjaphada) means complicated or crowded."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '약속' mean?","korean":"약속","options":["Secret","Promise/Appointment","Contract","Dream"],"answer":1,"explanation":"'약속' (yaksok) means promise or appointment."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '추억' mean?","korean":"추억","options":["Future","Dream","Memory/Nostalgia","Regret"],"answer":2,"explanation":"'추억' (chueok) means memory or nostalgic recollection."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '설레다' mean?","korean":"설레다","options":["To be bored","To feel excited/flutter","To be nervous","To be calm"],"answer":1,"explanation":"'설레다' means to feel excited or have butterflies — often used for romantic anticipation."},
    {"category":"Vocabulary","difficulty":"hard","question":"What does '눈치' mean?","korean":"눈치","options":["Eyesight","Social awareness/reading the room","Intuition","Gossip"],"answer":1,"explanation":"'눈치' is the Korean concept of reading social situations and others' feelings."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '회사' mean?","korean":"회사","options":["School","Hospital","Company/Office","Government"],"answer":2,"explanation":"'회사' (hoesa) means company or office."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '지하철' mean?","korean":"지하철","options":["Bus","Taxi","Subway/Metro","Train"],"answer":2,"explanation":"'지하철' (jihacheol) means subway or metro."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '감사' mean?","korean":"감사","options":["Sorry","Gratitude/Thanks","Hello","Goodbye"],"answer":1,"explanation":"'감사' (gamsa) means gratitude or thanks."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '사랑' mean?","korean":"사랑","options":["Hate","Fear","Love","Happiness"],"answer":2,"explanation":"'사랑' (sarang) means love."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '행복' mean?","korean":"행복","options":["Sadness","Anger","Happiness","Loneliness"],"answer":2,"explanation":"'행복' (haengbok) means happiness."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '꿈' mean?","korean":"꿈","options":["Reality","Dream/Goal","Memory","Wish"],"answer":1,"explanation":"'꿈' (kkum) means dream or goal."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '하나' mean?","korean":"하나","options":["Two","Three","One","Four"],"answer":2,"explanation":"'하나' (hana) is the native Korean word for one."},
    {"category":"Vocabulary","difficulty":"easy","question":"What does '둘' mean?","korean":"둘","options":["One","Two","Three","Four"],"answer":1,"explanation":"'둘' (dul) is the native Korean word for two."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '맵다' mean?","korean":"맵다","options":["Sweet","Sour","Salty","Spicy"],"answer":3,"explanation":"'맵다' (maepda) means spicy or hot (taste)."},
    {"category":"Vocabulary","difficulty":"medium","question":"What does '달다' mean?","korean":"달다","options":["Sour","Bitter","Sweet","Salty"],"answer":2,"explanation":"'달다' (dalda) means sweet."},

    # ── GRAMMAR ──────────────────────────────────────────────────────────────
    {"category":"Grammar","difficulty":"easy","question":"In Korean, where does the verb go in a sentence?","korean":"","options":["Beginning","Middle","End","Anywhere"],"answer":2,"explanation":"Korean is Subject-Object-Verb (SOV). The verb always comes at the end."},
    {"category":"Grammar","difficulty":"medium","question":"Which ending makes a verb polite?","korean":"","options":["-다","-아/어요","-고싶다","-지마"],"answer":1,"explanation":"The '-아/어요' ending makes verbs polite."},
    {"category":"Grammar","difficulty":"medium","question":"What does '이다' mean?","korean":"이다","options":["To do","To be","To go","To eat"],"answer":1,"explanation":"'이다' is the Korean 'to be'."},
    {"category":"Grammar","difficulty":"hard","question":"What particle marks the subject?","korean":"","options":["을/를","에서","이/가","의"],"answer":2,"explanation":"'이/가' marks the subject. '을/를' marks the object."},
    {"category":"Grammar","difficulty":"hard","question":"How do you make a verb negative?","korean":"","options":["Add 안 before","Add 못 after","Change to -없다","Add 아니 at end"],"answer":0,"explanation":"Add '안' before the verb: 가요 → 안 가요."},
    {"category":"Grammar","difficulty":"easy","question":"What is the Korean sentence order?","korean":"","options":["SVO like English","SOV — verb at end","VSO","OVS"],"answer":1,"explanation":"Korean uses Subject-Object-Verb order."},
    {"category":"Grammar","difficulty":"medium","question":"What does '을/를' mark in a sentence?","korean":"을/를","options":["Subject","Object","Location","Time"],"answer":1,"explanation":"'을/를' are object markers in Korean."},
    {"category":"Grammar","difficulty":"medium","question":"What does '에서' indicate?","korean":"에서","options":["Possession","Direction","Location of action","Time"],"answer":2,"explanation":"'에서' marks the location where an action takes place."},
    {"category":"Grammar","difficulty":"medium","question":"What does '의' indicate?","korean":"의","options":["Subject","Object","Possession","Direction"],"answer":2,"explanation":"'의' is the possessive particle, similar to 's in English."},
    {"category":"Grammar","difficulty":"hard","question":"What does '-고 싶다' express?","korean":"-고 싶다","options":["Ability","Want to do something","Have to do","Did in the past"],"answer":1,"explanation":"'-고 싶다' expresses desire or 'want to'. 먹고 싶다 = want to eat."},
    {"category":"Grammar","difficulty":"hard","question":"What does '-았/었어요' indicate?","korean":"","options":["Future tense","Present tense","Past tense","Conditional"],"answer":2,"explanation":"'-았/었어요' is the past tense ending in polite Korean."},
    {"category":"Grammar","difficulty":"hard","question":"What does '-ㄹ/을 거예요' indicate?","korean":"","options":["Past tense","Future intention","Present state","Command"],"answer":1,"explanation":"'-ㄹ/을 거예요' expresses future intention or plan."},
    {"category":"Grammar","difficulty":"medium","question":"What does '-지 마세요' mean?","korean":"-지 마세요","options":["Please do","Please don't","You must","You can"],"answer":1,"explanation":"'-지 마세요' is a polite negative command — 'please don't'."},
    {"category":"Grammar","difficulty":"hard","question":"What does '-아/어서' connect?","korean":"","options":["Contrast","Reason/cause","Sequence only","Condition"],"answer":1,"explanation":"'-아/어서' connects clauses showing reason or cause: 'because'."},
    {"category":"Grammar","difficulty":"hard","question":"What does '-면' express?","korean":"-면","options":["Although","Because","If/When (condition)","After"],"answer":2,"explanation":"'-면' expresses a conditional: 'if' or 'when'."},
    {"category":"Grammar","difficulty":"medium","question":"What does '못' before a verb mean?","korean":"못","options":["Don't (won't)","Can't (inability)","Shouldn't","Didn't"],"answer":1,"explanation":"'못' expresses inability — can't do something. '안' expresses choice not to."},
    {"category":"Grammar","difficulty":"easy","question":"How do you say 'I' formally in Korean?","korean":"","options":["나","저","우리","그"],"answer":1,"explanation":"'저' (jeo) is the formal/humble way to say 'I'. '나' is informal."},
    {"category":"Grammar","difficulty":"medium","question":"What is the topic marker in Korean?","korean":"","options":["이/가","을/를","은/는","에서"],"answer":2,"explanation":"'은/는' is the topic marker, used to introduce or contrast topics."},
    {"category":"Grammar","difficulty":"hard","question":"What does '-ㄴ/은 것 같다' express?","korean":"","options":["Certainty","Seems like / I think","Command","Desire"],"answer":1,"explanation":"'-ㄴ/은 것 같다' expresses conjecture: 'it seems like' or 'I think'."},
    {"category":"Grammar","difficulty":"hard","question":"What does '한테' indicate?","korean":"한테","options":["Location","To (a person) / from (a person)","Possession","Time"],"answer":1,"explanation":"'한테' marks the recipient or source of an action with people."},

    # ── CULTURE ───────────────────────────────────────────────────────────────
    {"category":"Culture","difficulty":"easy","question":"What is 'Hangul'?","korean":"한글","options":["Korean food","Korean alphabet","Korean money","Korean flag"],"answer":1,"explanation":"Hangul (한글) is the Korean writing system, created in 1443 by King Sejong."},
    {"category":"Culture","difficulty":"easy","question":"What is 'Kimchi'?","korean":"김치","options":["A Korean dance","A fermented vegetable dish","A type of noodle","A Korean drama"],"answer":1,"explanation":"Kimchi is a traditional Korean fermented dish, usually made with cabbage."},
    {"category":"Culture","difficulty":"medium","question":"What is '추석'?","korean":"추석","options":["New Year","Harvest festival","Buddha's birthday","Independence Day"],"answer":1,"explanation":"Chuseok (추석) is a major Korean harvest festival, similar to Thanksgiving."},
    {"category":"Culture","difficulty":"easy","question":"What is 'Taekwondo'?","korean":"태권도","options":["Korean food","Korean martial art","Korean dance","Korean music"],"answer":1,"explanation":"Taekwondo (태권도) is Korea's national martial art and Olympic sport."},
    {"category":"Culture","difficulty":"medium","question":"What is '설날'?","korean":"설날","options":["Harvest festival","Korean New Year","Children's Day","Independence Day"],"answer":1,"explanation":"Seollal (설날) is the Korean Lunar New Year — one of the biggest holidays."},
    {"category":"Culture","difficulty":"medium","question":"What is 'Bibimbap'?","korean":"비빔밥","options":["A Korean soup","Mixed rice dish","Grilled meat","Spicy noodles"],"answer":1,"explanation":"Bibimbap (비빔밥) is a popular Korean dish of rice mixed with vegetables, meat, and gochujang."},
    {"category":"Culture","difficulty":"easy","question":"What is 'Hanbok'?","korean":"한복","options":["Korean house","Traditional Korean clothing","Korean ceremony","Korean instrument"],"answer":1,"explanation":"Hanbok (한복) is the traditional Korean clothing worn on special occasions."},
    {"category":"Culture","difficulty":"medium","question":"Who created Hangul?","korean":"","options":["King Taejo","King Sejong","King Gojong","King Seonjo"],"answer":1,"explanation":"King Sejong the Great created Hangul in 1443 during the Joseon Dynasty."},
    {"category":"Culture","difficulty":"medium","question":"What does '빨리빨리' culture refer to?","korean":"빨리빨리","options":["Slowness and patience","Fast-paced, hurry-up culture","Respect for elders","Hard work ethic"],"answer":1,"explanation":"'빨리빨리' (ppalli ppalli) means 'hurry hurry' — it reflects Korea's fast-paced culture."},
    {"category":"Culture","difficulty":"hard","question":"What is 'Nunchi'?","korean":"눈치","options":["A Korean game","Reading social cues and situations","A type of food","A traditional dance"],"answer":1,"explanation":"Nunchi (눈치) is the Korean concept of reading the room and understanding others' feelings."},
    {"category":"Culture","difficulty":"medium","question":"What is 'Ramyeon'?","korean":"라면","options":["Korean BBQ","Korean instant noodles","Rice cake","Dumplings"],"answer":1,"explanation":"Ramyeon (라면) is Korean instant noodles — a beloved comfort food."},
    {"category":"Culture","difficulty":"easy","question":"What is 'Samgyeopsal'?","korean":"삼겹살","options":["Grilled pork belly","Grilled beef","Grilled chicken","Grilled fish"],"answer":0,"explanation":"Samgyeopsal (삼겹살) is grilled pork belly — a very popular Korean BBQ dish."},
    {"category":"Culture","difficulty":"medium","question":"What is the Korean age system?","korean":"","options":["Same as international age","Everyone starts at age 1 and ages on New Year","Ages counted from birth month","Ages counted in lunar calendar only"],"answer":1,"explanation":"In the traditional Korean age system, everyone is 1 year old at birth and gains a year on New Year's Day."},
    {"category":"Culture","difficulty":"hard","question":"What is 'Jeong' in Korean culture?","korean":"정","options":["Respect for teachers","Deep emotional bond/attachment","Competitive spirit","Work ethic"],"answer":1,"explanation":"'Jeong' (정) is a deep emotional bond or attachment between people — a uniquely Korean concept."},
    {"category":"Culture","difficulty":"medium","question":"What is 'Norebang'?","korean":"노래방","options":["A Korean restaurant","Private karaoke room","Street food market","Dance studio"],"answer":1,"explanation":"Norebang (노래방) means 'song room' — private karaoke booths where groups sing together."},
    {"category":"Culture","difficulty":"easy","question":"What is 'Tteok'?","korean":"떡","options":["Korean candy","Korean rice cake","Korean fried rice","Korean soup"],"answer":1,"explanation":"Tteok (떡) is Korean rice cake, used in many traditional dishes and celebrations."},
    {"category":"Culture","difficulty":"medium","question":"What is '한옥'?","korean":"한옥","options":["Modern apartment","Traditional Korean house","Government building","Temple"],"answer":1,"explanation":"Hanok (한옥) is a traditional Korean house, known for its elegant curved roofs."},
    {"category":"Culture","difficulty":"hard","question":"What does '눈치가 빠르다' mean?","korean":"눈치가 빠르다","options":["Quick feet","Good at reading situations","Fast reader","Sharp eyes"],"answer":1,"explanation":"'눈치가 빠르다' means to be quick at reading social situations and others' feelings."},
    {"category":"Culture","difficulty":"medium","question":"What is 'Soju'?","korean":"소주","options":["Korean beer","Korean traditional liquor","Korean tea","Korean soft drink"],"answer":1,"explanation":"Soju (소주) is a clear Korean distilled liquor — the world's best-selling spirit."},
    {"category":"Culture","difficulty":"easy","question":"What is '태극기'?","korean":"태극기","options":["Korean anthem","Korean flag","Korean seal","Korean currency"],"answer":1,"explanation":"Taegukgi (태극기) is the national flag of South Korea."},
    {"category":"Culture","difficulty":"medium","question":"What is 'Hallyu'?","korean":"한류","options":["Korean food wave","Korean Wave — spread of Korean pop culture","Korean language","Korean history"],"answer":1,"explanation":"Hallyu (한류) means the Korean Wave — the global spread of Korean pop culture including K-pop, K-drama, and food."},

    # ── K-POP ────────────────────────────────────────────────────────────────
    {"category":"K-Pop","difficulty":"easy","question":"Which group sings 'Dynamite'?","korean":"","options":["BLACKPINK","EXO","BTS","TWICE"],"answer":2,"explanation":"BTS released 'Dynamite' in 2020 — their first all-English song."},
    {"category":"K-Pop","difficulty":"medium","question":"What does '사랑해' mean?","korean":"사랑해","options":["I miss you","I love you","I hate you","I'm happy"],"answer":1,"explanation":"'사랑해' (saranghae) means 'I love you' in informal Korean."},
    {"category":"K-Pop","difficulty":"medium","question":"Which girl group is known for 'How You Like That'?","korean":"","options":["TWICE","aespa","BLACKPINK","Red Velvet"],"answer":2,"explanation":"'How You Like That' is by BLACKPINK, released in 2020."},
    {"category":"K-Pop","difficulty":"hard","question":"What does 'daebak' mean?","korean":"대박","options":["Boring","Awesome/jackpot","Goodbye","Let's eat"],"answer":1,"explanation":"'대박' (daebak) means 'awesome' or 'jackpot' — used widely in K-pop fandoms."},
    {"category":"K-Pop","difficulty":"easy","question":"What does 'oppa' mean?","korean":"오빠","options":["Younger brother","Older brother (said by females)","Friend","Teacher"],"answer":1,"explanation":"'오빠' (oppa) is used by females to address older males — popular in K-pop fan culture."},
    {"category":"K-Pop","difficulty":"medium","question":"What does 'maknae' mean?","korean":"막내","options":["Oldest member","Middle member","Youngest member","Leader"],"answer":2,"explanation":"'막내' (maknae) means the youngest member of a group."},
    {"category":"K-Pop","difficulty":"medium","question":"What is a 'comeback' in K-pop?","korean":"","options":["Returning from hiatus","Releasing new music/album","Winning an award","Going on tour"],"answer":1,"explanation":"In K-pop, a 'comeback' refers to a group releasing new music, even if they never went away."},
    {"category":"K-Pop","difficulty":"easy","question":"What does 'fighting' (파이팅) mean in Korean?","korean":"파이팅","options":["Let's fight","Good luck / You can do it","I'm angry","Goodbye"],"answer":1,"explanation":"'파이팅' (paiting) is a cheer meaning 'good luck' or 'you can do it'."},
    {"category":"K-Pop","difficulty":"medium","question":"What is an 'idol' in K-pop?","korean":"","options":["A god","A K-pop singer/performer","A fan","A songwriter"],"answer":1,"explanation":"An 'idol' in K-pop refers to a trained singer/performer who debuts under an entertainment company."},
    {"category":"K-Pop","difficulty":"hard","question":"What does 'sasaeng' mean?","korean":"사생팬","options":["Loyal fan","Obsessive/stalker fan","New fan","Casual fan"],"answer":1,"explanation":"'사생팬' (sasaengpaen) refers to obsessive fans who invade idols' privacy."},
    {"category":"K-Pop","difficulty":"medium","question":"Which group has members RM, Jin, Suga, J-Hope, Jimin, V, and Jungkook?","korean":"","options":["EXO","GOT7","BTS","MONSTA X"],"answer":2,"explanation":"BTS (방탄소년단) has these seven members and is one of the biggest K-pop groups globally."},
    {"category":"K-Pop","difficulty":"easy","question":"What does 'unnie' mean?","korean":"언니","options":["Older sister (said by females)","Younger sister","Mother","Friend"],"answer":0,"explanation":"'언니' (unnie) is used by females to address older females."},
    {"category":"K-Pop","difficulty":"medium","question":"What is a 'fansite master'?","korean":"","options":["Official fan club manager","Fan who takes professional photos of idols","Fan who runs the official website","Fan who organizes concerts"],"answer":1,"explanation":"A fansite master is a fan who professionally photographs idols at events and shares photos."},
    {"category":"K-Pop","difficulty":"hard","question":"What does 'bias' mean in K-pop fan culture?","korean":"","options":["Least favorite member","Favorite member","Random member","Group leader"],"answer":1,"explanation":"Your 'bias' is your favorite member of a K-pop group."},
    {"category":"K-Pop","difficulty":"medium","question":"What is 'aegyo'?","korean":"애교","options":["Angry behavior","Cute/baby-like behavior to charm others","Formal speech","Dance moves"],"answer":1,"explanation":"'애교' (aegyo) means acting cute or baby-like to charm others — very common in K-pop."},
    {"category":"K-Pop","difficulty":"easy","question":"Which company is BTS under?","korean":"","options":["SM Entertainment","JYP Entertainment","YG Entertainment","HYBE (Big Hit)"],"answer":3,"explanation":"BTS is under HYBE (formerly Big Hit Entertainment)."},
    {"category":"K-Pop","difficulty":"medium","question":"What does 'fanchant' mean?","korean":"","options":["A fan's favorite song","Choreographed chants fans do during performances","Fan club name","Fan letter"],"answer":1,"explanation":"A fanchant is a specific chant or call-and-response that fans do during live performances."},
    {"category":"K-Pop","difficulty":"hard","question":"What is a 'light stick'?","korean":"","options":["A concert ticket","Official fan merchandise glowing stick used at concerts","A phone app","A fan badge"],"answer":1,"explanation":"A light stick is official fan merchandise — a glowing wand fans wave at concerts, unique to each group."},
    {"category":"K-Pop","difficulty":"medium","question":"What does 'visual' mean in K-pop?","korean":"","options":["The main dancer","The member considered the most attractive","The main vocalist","The rapper"],"answer":1,"explanation":"The 'visual' is the member considered the most attractive or the face of the group."},
    {"category":"K-Pop","difficulty":"easy","question":"What does 'noona' mean?","korean":"누나","options":["Younger sister","Older sister (said by males)","Female friend","Mother"],"answer":1,"explanation":"'누나' (noona) is used by males to address older females."},
    {"category":"K-Pop","difficulty":"hard","question":"What is a 'disbandment' in K-pop?","korean":"","options":["Going on vacation","A group officially ending their activities together","Taking a break","Changing agency"],"answer":1,"explanation":"Disbandment means a K-pop group officially ends their activities as a group."},
]

PYQUIZ_QUESTIONS = [
    # ── BASICS ──────────────────────────────────────────────────────────────
    {"category":"Basics","difficulty":"easy","question":"What is the output of print(type(42))?","code":"print(type(42))","options":["<class 'float'>","<class 'int'>","<class 'str'>","<class 'num'>"],"answer":1,"explanation":"42 is an integer literal. type() returns the class of the object."},
    {"category":"Basics","difficulty":"easy","question":"Which keyword is used to define a function in Python?","code":"","options":["function","define","def","func"],"answer":2,"explanation":"'def' is used to define a function in Python. Example: def my_func():"},
    {"category":"Basics","difficulty":"easy","question":"What does len('hello') return?","code":"len('hello')","options":["4","5","6","Error"],"answer":1,"explanation":"'hello' has 5 characters, so len() returns 5."},
    {"category":"Basics","difficulty":"easy","question":"What is the correct way to create a comment in Python?","code":"","options":["// This is a comment","/* comment */","# This is a comment","-- comment"],"answer":2,"explanation":"Python uses # for single-line comments. No /* */ or // like other languages."},
    {"category":"Basics","difficulty":"easy","question":"What does this print?\nx = 5\ny = 2\nprint(x // y)","code":"x = 5\ny = 2\nprint(x // y)","options":["2.5","2","3","1"],"answer":1,"explanation":"// is floor division — it divides and rounds down. 5 // 2 = 2."},
    {"category":"Basics","difficulty":"easy","question":"What is the output of print(10 % 3)?","code":"print(10 % 3)","options":["3","1","0","3.33"],"answer":1,"explanation":"% is the modulo operator — returns the remainder. 10 % 3 = 1."},
    {"category":"Basics","difficulty":"easy","question":"Which of these is a valid variable name in Python?","code":"","options":["2variable","my-var","_myvar","my var"],"answer":2,"explanation":"Variable names can start with a letter or underscore. No spaces or hyphens."},
    {"category":"Basics","difficulty":"easy","question":"What does print(2 ** 3) output?","code":"print(2 ** 3)","options":["6","8","9","Error"],"answer":1,"explanation":"** is the exponentiation operator. 2 ** 3 = 2³ = 8."},
    {"category":"Basics","difficulty":"medium","question":"What is the output?\nx = [1, 2, 3]\nprint(x[-1])","code":"x = [1, 2, 3]\nprint(x[-1])","options":["1","2","3","Error"],"answer":2,"explanation":"Negative indexing in Python starts from the end. x[-1] returns the last element, which is 3."},
    {"category":"Basics","difficulty":"medium","question":"What does this return?\nprint(bool(0))","code":"print(bool(0))","options":["True","False","0","Error"],"answer":1,"explanation":"0, empty strings, empty lists, and None are all falsy in Python. bool(0) = False."},
    {"category":"Basics","difficulty":"medium","question":"What is the output?\nprint('Python' * 2)","code":"print('Python' * 2)","options":["PythonPython","Python2","Python Python","Error"],"answer":0,"explanation":"String multiplication repeats the string. 'Python' * 2 = 'PythonPython'."},
    {"category":"Basics","difficulty":"medium","question":"What keyword is used to exit a loop early?","code":"","options":["exit","stop","break","end"],"answer":2,"explanation":"'break' exits a loop immediately. 'continue' skips to the next iteration."},
    {"category":"Basics","difficulty":"medium","question":"What is the output?\nfor i in range(3):\n    print(i)","code":"for i in range(3):\n    print(i)","options":["1 2 3","0 1 2 3","0 1 2","1 2"],"answer":2,"explanation":"range(3) generates 0, 1, 2. It starts at 0 and excludes the end value."},
    {"category":"Basics","difficulty":"hard","question":"What is the output?\nx = 'hello'\nprint(x[1:3])","code":"x = 'hello'\nprint(x[1:3])","options":["hel","el","ell","he"],"answer":1,"explanation":"Slicing [1:3] returns characters from index 1 up to (not including) index 3: 'el'."},
    {"category":"Basics","difficulty":"hard","question":"What is the output?\nprint(list(range(2, 10, 3)))","code":"print(list(range(2, 10, 3)))","options":["[2, 5, 8]","[2, 4, 6, 8]","[2, 5, 8, 11]","[3, 6, 9]"],"answer":0,"explanation":"range(start, stop, step): starts at 2, steps by 3: 2, 5, 8. Stops before 10."},
    {"category":"Basics","difficulty":"hard","question":"What does this print?\nx = 5\nprint(f'Value is {x * 2}')","code":"x = 5\nprint(f'Value is {x * 2}')","options":["Value is x * 2","Value is {x * 2}","Value is 10","Error"],"answer":2,"explanation":"f-strings evaluate expressions inside {}. x * 2 = 10, so output is 'Value is 10'."},

    # ── DATA TYPES ──────────────────────────────────────────────────────────
    {"category":"Data Types","difficulty":"easy","question":"Which data type is immutable in Python?","code":"","options":["List","Dictionary","Tuple","Set"],"answer":2,"explanation":"Tuples are immutable — you cannot change their elements after creation. Lists, dicts, and sets are mutable."},
    {"category":"Data Types","difficulty":"easy","question":"What is the output?\nprint(type([1, 2, 3]))","code":"print(type([1, 2, 3]))","options":["<class 'tuple'>","<class 'array'>","<class 'list'>","<class 'set'>"],"answer":2,"explanation":"[1, 2, 3] uses square brackets, which creates a list in Python."},
    {"category":"Data Types","difficulty":"easy","question":"How do you create an empty dictionary?","code":"","options":["dict = []","dict = ()","dict = {}","dict = set()"],"answer":2,"explanation":"{} creates an empty dictionary. set() creates an empty set (not {}, which is a dict)."},
    {"category":"Data Types","difficulty":"medium","question":"What is the output?\nx = {1, 2, 2, 3}\nprint(len(x))","code":"x = {1, 2, 2, 3}\nprint(len(x))","options":["4","3","2","Error"],"answer":1,"explanation":"Sets don't allow duplicates. {1, 2, 2, 3} becomes {1, 2, 3}, so len = 3."},
    {"category":"Data Types","difficulty":"medium","question":"What does this return?\nx = (1, 2, 3)\nprint(x[1])","code":"x = (1, 2, 3)\nprint(x[1])","options":["1","2","3","Error"],"answer":1,"explanation":"Tuples support indexing. x[1] returns the element at index 1, which is 2."},
    {"category":"Data Types","difficulty":"medium","question":"What is the output?\nd = {'a': 1, 'b': 2}\nprint(d.get('c', 0))","code":"d = {'a': 1, 'b': 2}\nprint(d.get('c', 0))","options":["None","Error","KeyError","0"],"answer":3,"explanation":"dict.get(key, default) returns the default value if key doesn't exist. 'c' not in d, so returns 0."},
    {"category":"Data Types","difficulty":"medium","question":"What does list.append() do?","code":"","options":["Adds item at beginning","Removes last item","Adds item at end","Sorts the list"],"answer":2,"explanation":"append() adds an element to the END of a list. Use insert(0, item) to add at the beginning."},
    {"category":"Data Types","difficulty":"hard","question":"What is the output?\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)","code":"x = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)","options":["[1, 2, 3]","[1, 2, 3, 4]","Error","[4, 1, 2, 3]"],"answer":1,"explanation":"y = x doesn't copy the list — both variables point to the same object. Modifying y also modifies x."},
    {"category":"Data Types","difficulty":"hard","question":"What is the output?\nprint('a' in {'a': 1, 'b': 2})","code":"print('a' in {'a': 1, 'b': 2})","options":["True","False","1","Error"],"answer":0,"explanation":"'in' checks for keys in a dictionary. 'a' is a key, so it returns True."},
    {"category":"Data Types","difficulty":"hard","question":"What does this output?\nx = [1, 2, 3, 4, 5]\nprint(x[::2])","code":"x = [1, 2, 3, 4, 5]\nprint(x[::2])","options":["[1, 3, 5]","[2, 4]","[1, 2, 3]","[5, 3, 1]"],"answer":0,"explanation":"[::2] slices with step 2, starting from the beginning: indices 0, 2, 4 → [1, 3, 5]."},

    # ── FUNCTIONS ───────────────────────────────────────────────────────────
    {"category":"Functions","difficulty":"easy","question":"What does a function return if no return statement?","code":"","options":["0","Empty string","None","Error"],"answer":2,"explanation":"Python functions return None implicitly if there's no return statement."},
    {"category":"Functions","difficulty":"easy","question":"What is a lambda function?","code":"","options":["A function in a class","A recursive function","An anonymous one-line function","A built-in function"],"answer":2,"explanation":"Lambda creates small anonymous functions: lambda x: x * 2 is equivalent to def f(x): return x * 2."},
    {"category":"Functions","difficulty":"medium","question":"What is the output?\ndef add(a, b=5):\n    return a + b\nprint(add(3))","code":"def add(a, b=5):\n    return a + b\nprint(add(3))","options":["3","5","8","Error"],"answer":2,"explanation":"b has a default value of 5. add(3) uses a=3 and default b=5. 3 + 5 = 8."},
    {"category":"Functions","difficulty":"medium","question":"What does *args allow in a function?","code":"","options":["Only keyword arguments","Variable number of positional arguments","Only one argument","Named arguments"],"answer":1,"explanation":"*args allows a function to accept any number of positional arguments as a tuple."},
    {"category":"Functions","difficulty":"medium","question":"What is the output?\nresult = list(map(lambda x: x**2, [1, 2, 3]))\nprint(result)","code":"result = list(map(lambda x: x**2, [1, 2, 3]))\nprint(result)","options":["[1, 4, 9]","[1, 2, 3]","[2, 4, 6]","Error"],"answer":0,"explanation":"map() applies the lambda to each element. x**2 squares each: 1→1, 2→4, 3→9."},
    {"category":"Functions","difficulty":"hard","question":"What is the output?\ndef counter():\n    count = 0\n    def inc():\n        nonlocal count\n        count += 1\n        return count\n    return inc\nc = counter()\nprint(c(), c())","code":"def counter():\n    count = 0\n    def inc():\n        nonlocal count\n        count += 1\n        return count\n    return inc\nc = counter()\nprint(c(), c())","options":["0 1","1 1","1 2","Error"],"answer":2,"explanation":"nonlocal allows inner function to modify outer variable. c() increments count each call: 1, then 2."},
    {"category":"Functions","difficulty":"hard","question":"What does a list comprehension do?","code":"[x*2 for x in range(5)]","options":["Creates a generator","Creates a new list using a loop expression","Filters a list","Sorts a list"],"answer":1,"explanation":"List comprehension creates a new list by applying an expression to each item. [x*2 for x in range(5)] = [0, 2, 4, 6, 8]."},
    {"category":"Functions","difficulty":"hard","question":"What is the output?\nprint(list(filter(lambda x: x > 2, [1, 2, 3, 4])))","code":"print(list(filter(lambda x: x > 2, [1, 2, 3, 4])))","options":["[1, 2]","[3, 4]","[2, 3, 4]","[1, 2, 3, 4]"],"answer":1,"explanation":"filter() keeps only elements where the lambda returns True. x > 2 is True for 3 and 4."},

    # ── OOP ─────────────────────────────────────────────────────────────────
    {"category":"OOP","difficulty":"easy","question":"What keyword is used to define a class in Python?","code":"","options":["object","struct","class","type"],"answer":2,"explanation":"'class' keyword defines a class in Python. Example: class MyClass:"},
    {"category":"OOP","difficulty":"easy","question":"What is __init__ in Python?","code":"","options":["A destructor","A constructor method","A static method","A class variable"],"answer":1,"explanation":"__init__ is the constructor method — called automatically when a new object is created."},
    {"category":"OOP","difficulty":"medium","question":"What does 'self' refer to in a class method?","code":"","options":["The class itself","The parent class","The current instance","A global variable"],"answer":2,"explanation":"'self' refers to the current instance of the class. It's passed automatically as the first argument."},
    {"category":"OOP","difficulty":"medium","question":"What is inheritance in Python?","code":"","options":["Copying a class","A class acquiring properties of another class","Creating multiple objects","Hiding class data"],"answer":1,"explanation":"Inheritance allows a class to acquire attributes and methods from a parent class using class Child(Parent)."},
    {"category":"OOP","difficulty":"medium","question":"What does this output?\nclass Dog:\n    def speak(self):\n        return 'Woof'\nd = Dog()\nprint(d.speak())","code":"class Dog:\n    def speak(self):\n        return 'Woof'\nd = Dog()\nprint(d.speak())","options":["speak","Woof","Dog","Error"],"answer":1,"explanation":"d.speak() calls the speak method on the Dog instance, which returns 'Woof'."},
    {"category":"OOP","difficulty":"hard","question":"What is encapsulation?","code":"","options":["Inheriting from parent","Hiding internal data using private attributes","Using multiple classes","Overriding methods"],"answer":1,"explanation":"Encapsulation hides internal implementation details. In Python, use _ (protected) or __ (private) prefix."},
    {"category":"OOP","difficulty":"hard","question":"What is a @staticmethod?","code":"","options":["A method that modifies class state","A method that doesn't need self or cls","A method only for subclasses","A method that runs at startup"],"answer":1,"explanation":"@staticmethod defines a method that doesn't receive self or cls — it belongs to the class but doesn't access instance/class data."},

    # ── LIBRARIES ───────────────────────────────────────────────────────────
    {"category":"Libraries","difficulty":"easy","question":"Which library is used for data manipulation in Python?","code":"","options":["NumPy","Matplotlib","Pandas","Scikit-learn"],"answer":2,"explanation":"Pandas is the go-to library for data manipulation with DataFrames and Series."},
    {"category":"Libraries","difficulty":"easy","question":"What does import numpy as np do?","code":"import numpy as np","options":["Installs numpy","Imports numpy with alias 'np'","Creates a numpy file","Removes numpy"],"answer":1,"explanation":"'import ... as' imports a library with a shorter alias. np is the conventional alias for numpy."},
    {"category":"Libraries","difficulty":"medium","question":"What does np.array([1,2,3]).shape return?","code":"np.array([1,2,3]).shape","options":["3","(3,)","[3]","(1,3)"],"answer":1,"explanation":"shape returns a tuple of dimensions. A 1D array of 3 elements has shape (3,)."},
    {"category":"Libraries","difficulty":"medium","question":"What library is used for machine learning in Python?","code":"","options":["Pandas","Flask","Scikit-learn","Requests"],"answer":2,"explanation":"Scikit-learn (sklearn) is the most popular ML library for classical machine learning algorithms."},
    {"category":"Libraries","difficulty":"medium","question":"What does requests.get(url) do?","code":"","options":["Downloads a file","Sends a GET HTTP request","Opens a browser","Creates a server"],"answer":1,"explanation":"requests.get() sends an HTTP GET request to a URL and returns a Response object."},
    {"category":"Libraries","difficulty":"hard","question":"What does pd.DataFrame.groupby() do?","code":"","options":["Sorts the DataFrame","Groups rows by a column for aggregation","Filters rows","Merges two DataFrames"],"answer":1,"explanation":"groupby() groups rows by column values, then you can apply aggregation functions like sum(), mean()."},
    {"category":"Libraries","difficulty":"hard","question":"What is the purpose of Matplotlib?","code":"","options":["Web scraping","Data visualization and plotting","Database management","API requests"],"answer":1,"explanation":"Matplotlib is Python's primary plotting library for creating charts, graphs, and visualizations."},
    {"category":"Libraries","difficulty":"easy","question":"What does os.path.join() do?","code":"","options":["Downloads a file","Joins path components correctly for the OS","Opens a file","Checks if path exists"],"answer":1,"explanation":"os.path.join() joins path components using the correct separator for the operating system."},
    {"category":"Libraries","difficulty":"medium","question":"What does json.dumps() do?","code":"","options":["Reads a JSON file","Converts Python object to JSON string","Parses JSON string","Deletes JSON data"],"answer":1,"explanation":"json.dumps() serializes a Python object (dict, list) into a JSON-formatted string."},
    {"category":"Libraries","difficulty":"hard","question":"What is a virtual environment in Python?","code":"","options":["A cloud server","An isolated Python environment with its own packages","A virtual machine","A testing framework"],"answer":1,"explanation":"A virtual environment (venv) creates an isolated space with its own Python packages, preventing conflicts between projects."},
]

FLASHKO_CARDS = [
    # ── VOCABULARY ──────────────────────────────
    {"category": "Vocabulary", "korean": "안녕하세요", "romanized": "Annyeonghaseyo", "english": "Hello (formal)", "example": "안녕하세요! 저는 비바쉬예요."},
    {"category": "Vocabulary", "korean": "감사합니다", "romanized": "Gamsahamnida", "english": "Thank you (formal)", "example": "도와주셔서 감사합니다."},
    {"category": "Vocabulary", "korean": "미안해요", "romanized": "Mianhaeyo", "english": "I'm sorry", "example": "늦어서 미안해요."},
    {"category": "Vocabulary", "korean": "괜찮아요", "romanized": "Gwaenchanayo", "english": "It's okay / I'm fine", "example": "걱정하지 마세요, 괜찮아요."},
    {"category": "Vocabulary", "korean": "사랑해요", "romanized": "Saranghaeyo", "english": "I love you", "example": "나는 너를 사랑해요."},
    {"category": "Vocabulary", "korean": "친구", "romanized": "Chingu", "english": "Friend", "example": "그는 내 친구예요."},
    {"category": "Vocabulary", "korean": "가족", "romanized": "Gajok", "english": "Family", "example": "가족이 소중해요."},
    {"category": "Vocabulary", "korean": "학교", "romanized": "Hakgyo", "english": "School", "example": "나는 학교에 가요."},
    {"category": "Vocabulary", "korean": "집", "romanized": "Jip", "english": "House / Home", "example": "집에 가고 싶어요."},
    {"category": "Vocabulary", "korean": "물", "romanized": "Mul", "english": "Water", "example": "물 한 잔 주세요."},
    {"category": "Vocabulary", "korean": "책", "romanized": "Chaek", "english": "Book", "example": "저는 책을 읽어요."},
    {"category": "Vocabulary", "korean": "사람", "romanized": "Saram", "english": "Person / People", "example": "좋은 사람이에요."},
    {"category": "Vocabulary", "korean": "시간", "romanized": "Sigan", "english": "Time / Hour", "example": "시간이 없어요."},
    {"category": "Vocabulary", "korean": "날씨", "romanized": "Nalssi", "english": "Weather", "example": "오늘 날씨가 좋아요."},
    {"category": "Vocabulary", "korean": "여행", "romanized": "Yeohaeng", "english": "Travel / Trip", "example": "여행을 좋아해요."},
    {"category": "Vocabulary", "korean": "음악", "romanized": "Eumak", "english": "Music", "example": "음악을 들어요."},
    {"category": "Vocabulary", "korean": "영화", "romanized": "Yeonghwa", "english": "Movie / Film", "example": "영화 보러 가요."},
    {"category": "Vocabulary", "korean": "꿈", "romanized": "Kkum", "english": "Dream / Goal", "example": "꿈을 포기하지 마세요."},
    {"category": "Vocabulary", "korean": "행복", "romanized": "Haengbok", "english": "Happiness", "example": "행복한 하루 보내세요."},
    {"category": "Vocabulary", "korean": "사랑", "romanized": "Sarang", "english": "Love", "example": "사랑은 아름다워요."},
    {"category": "Vocabulary", "korean": "눈", "romanized": "Nun", "english": "Eye / Snow", "example": "눈이 와요. (Snow is falling.)"},
    {"category": "Vocabulary", "korean": "마음", "romanized": "Maeum", "english": "Heart / Mind", "example": "마음이 따뜻해요."},
    {"category": "Vocabulary", "korean": "길", "romanized": "Gil", "english": "Road / Way", "example": "이 길이 맞아요?"},
    {"category": "Vocabulary", "korean": "하늘", "romanized": "Haneul", "english": "Sky", "example": "하늘이 파래요."},
    {"category": "Vocabulary", "korean": "바다", "romanized": "Bada", "english": "Sea / Ocean", "example": "바다에 가고 싶어요."},
    {"category": "Vocabulary", "korean": "산", "romanized": "San", "english": "Mountain", "example": "산이 높아요."},
    {"category": "Vocabulary", "korean": "꽃", "romanized": "Kkot", "english": "Flower", "example": "꽃이 예뻐요."},
    {"category": "Vocabulary", "korean": "나무", "romanized": "Namu", "english": "Tree", "example": "나무가 커요."},
    {"category": "Vocabulary", "korean": "강아지", "romanized": "Gangaji", "english": "Puppy / Dog", "example": "강아지가 귀여워요."},
    {"category": "Vocabulary", "korean": "고양이", "romanized": "Goyangi", "english": "Cat", "example": "고양이가 자고 있어요."},
    {"category": "Vocabulary", "korean": "학생", "romanized": "Haksaeng", "english": "Student", "example": "저는 학생이에요."},
    {"category": "Vocabulary", "korean": "선생님", "romanized": "Seonsaengnim", "english": "Teacher", "example": "선생님이 친절해요."},
    {"category": "Vocabulary", "korean": "병원", "romanized": "Byeongwon", "english": "Hospital", "example": "병원에 가야 해요."},
    {"category": "Vocabulary", "korean": "지하철", "romanized": "Jihacheol", "english": "Subway / Metro", "example": "지하철을 타요."},
    {"category": "Vocabulary", "korean": "약속", "romanized": "Yaksok", "english": "Promise / Appointment", "example": "약속을 지켜요."},
    {"category": "Vocabulary", "korean": "추억", "romanized": "Chueok", "english": "Memory / Nostalgia", "example": "좋은 추억이에요."},
    {"category": "Vocabulary", "korean": "설레다", "romanized": "Seolleda", "english": "To feel excited / flutter", "example": "내일 여행이라 설레요."},
    {"category": "Vocabulary", "korean": "그리워요", "romanized": "Geuriwoyo", "english": "I miss (someone/something)", "example": "고향이 그리워요."},
    {"category": "Vocabulary", "korean": "피곤해요", "romanized": "Pigonhaeyo", "english": "I'm tired", "example": "오늘 너무 피곤해요."},
    {"category": "Vocabulary", "korean": "배고파요", "romanized": "Baegopayo", "english": "I'm hungry", "example": "배고파요, 뭐 먹을까요?"},

    # ── PHRASES ──────────────────────────────────
    {"category": "Phrases", "korean": "잘 지내요?", "romanized": "Jal jinaeyo?", "english": "How are you?", "example": "오랜만이에요! 잘 지내요?"},
    {"category": "Phrases", "korean": "잘 지내요", "romanized": "Jal jinaeyo", "english": "I'm doing well", "example": "네, 잘 지내요. 고마워요."},
    {"category": "Phrases", "korean": "만나서 반가워요", "romanized": "Mannaseo bangawoyo", "english": "Nice to meet you", "example": "처음 뵙겠습니다. 만나서 반가워요."},
    {"category": "Phrases", "korean": "잠깐만요", "romanized": "Jamkkanmanyo", "english": "Just a moment / Wait a moment", "example": "잠깐만요, 곧 올게요."},
    {"category": "Phrases", "korean": "모르겠어요", "romanized": "Moreugesseoyo", "english": "I don't know", "example": "그 답을 모르겠어요."},
    {"category": "Phrases", "korean": "이해해요", "romanized": "Ihaehaeyo", "english": "I understand", "example": "네, 이해해요. 감사해요."},
    {"category": "Phrases", "korean": "도와주세요", "romanized": "Dowajuseyo", "english": "Please help me", "example": "길을 잃었어요. 도와주세요!"},
    {"category": "Phrases", "korean": "천천히 말해주세요", "romanized": "Cheoncheonhi malhaejuseyo", "english": "Please speak slowly", "example": "한국어를 배워요. 천천히 말해주세요."},
    {"category": "Phrases", "korean": "다시 말해주세요", "romanized": "Dasi malhaejuseyo", "english": "Please say that again", "example": "못 들었어요. 다시 말해주세요."},
    {"category": "Phrases", "korean": "얼마예요?", "romanized": "Eolmayeyo?", "english": "How much is it?", "example": "이 옷 얼마예요?"},
    {"category": "Phrases", "korean": "어디예요?", "romanized": "Eodiyeyo?", "english": "Where is it?", "example": "화장실이 어디예요?"},
    {"category": "Phrases", "korean": "맛있어요!", "romanized": "Masisseoyo!", "english": "It's delicious!", "example": "이 김치찌개 정말 맛있어요!"},
    {"category": "Phrases", "korean": "안 돼요", "romanized": "An dwaeyo", "english": "It's not okay / No way", "example": "그렇게 하면 안 돼요."},
    {"category": "Phrases", "korean": "파이팅!", "romanized": "Paiting!", "english": "You can do it! / Fighting!", "example": "시험 잘 봐요! 파이팅!"},
    {"category": "Phrases", "korean": "수고했어요", "romanized": "Sugohasseoyo", "english": "Good work / You worked hard", "example": "오늘도 수고했어요!"},
    {"category": "Phrases", "korean": "배불러요", "romanized": "Baebulleoyo", "english": "I'm full", "example": "많이 먹었어요. 배불러요."},
    {"category": "Phrases", "korean": "잘 먹겠습니다", "romanized": "Jal meokgessseumnida", "english": "I will eat well (said before eating)", "example": "잘 먹겠습니다! 감사해요."},
    {"category": "Phrases", "korean": "잘 먹었습니다", "romanized": "Jal meogeossseumnida", "english": "I ate well (said after eating)", "example": "정말 맛있었어요. 잘 먹었습니다."},
    {"category": "Phrases", "korean": "어서 오세요", "romanized": "Eoseo oseyo", "english": "Welcome (to a shop)", "example": "어서 오세요! 무엇을 도와드릴까요?"},
    {"category": "Phrases", "korean": "조심하세요", "romanized": "Josimhaseyo", "english": "Be careful / Take care", "example": "길이 미끄러워요. 조심하세요."},

    # ── NUMBERS ──────────────────────────────────
    {"category": "Numbers", "korean": "하나", "romanized": "Hana", "english": "One (native Korean)", "example": "사과 하나 주세요."},
    {"category": "Numbers", "korean": "둘", "romanized": "Dul", "english": "Two (native Korean)", "example": "커피 둘 주세요."},
    {"category": "Numbers", "korean": "셋", "romanized": "Set", "english": "Three (native Korean)", "example": "셋까지 세어요."},
    {"category": "Numbers", "korean": "넷", "romanized": "Net", "english": "Four (native Korean)", "example": "넷이서 밥 먹어요."},
    {"category": "Numbers", "korean": "다섯", "romanized": "Daseot", "english": "Five (native Korean)", "example": "다섯 살이에요."},
    {"category": "Numbers", "korean": "여섯", "romanized": "Yeoseot", "english": "Six (native Korean)", "example": "여섯 시에 만나요."},
    {"category": "Numbers", "korean": "일곱", "romanized": "Ilgop", "english": "Seven (native Korean)", "example": "일곱 개 있어요."},
    {"category": "Numbers", "korean": "여덟", "romanized": "Yeodeol", "english": "Eight (native Korean)", "example": "여덟 명이에요."},
    {"category": "Numbers", "korean": "아홉", "romanized": "Ahop", "english": "Nine (native Korean)", "example": "아홉 시예요."},
    {"category": "Numbers", "korean": "열", "romanized": "Yeol", "english": "Ten (native Korean)", "example": "열 개 주세요."},
    {"category": "Numbers", "korean": "일", "romanized": "Il", "english": "One (Sino-Korean)", "example": "일 층에 있어요."},
    {"category": "Numbers", "korean": "이", "romanized": "I", "english": "Two (Sino-Korean)", "example": "이 번 출구예요."},
    {"category": "Numbers", "korean": "삼", "romanized": "Sam", "english": "Three (Sino-Korean)", "example": "삼 월이에요. (It's March)"},
    {"category": "Numbers", "korean": "사", "romanized": "Sa", "english": "Four (Sino-Korean)", "example": "사 층에 살아요."},
    {"category": "Numbers", "korean": "오", "romanized": "O", "english": "Five (Sino-Korean)", "example": "오 분 후에 와요."},
    {"category": "Numbers", "korean": "백", "romanized": "Baek", "english": "One hundred", "example": "백 원짜리 동전이에요."},
    {"category": "Numbers", "korean": "천", "romanized": "Cheon", "english": "One thousand", "example": "천 원이에요."},
    {"category": "Numbers", "korean": "만", "romanized": "Man", "english": "Ten thousand", "example": "만 원 주세요."},
    {"category": "Numbers", "korean": "첫째", "romanized": "Cheotjjae", "english": "First", "example": "첫째 아들이에요."},
    {"category": "Numbers", "korean": "둘째", "romanized": "Duljjae", "english": "Second", "example": "둘째 딸이에요."},

    # ── COLORS ───────────────────────────────────
    {"category": "Colors", "korean": "빨간색", "romanized": "Ppalgan saek", "english": "Red", "example": "빨간색 장미예요."},
    {"category": "Colors", "korean": "파란색", "romanized": "Paran saek", "english": "Blue", "example": "하늘은 파란색이에요."},
    {"category": "Colors", "korean": "노란색", "romanized": "Noran saek", "english": "Yellow", "example": "해바라기는 노란색이에요."},
    {"category": "Colors", "korean": "초록색", "romanized": "Chorok saek", "english": "Green", "example": "풀은 초록색이에요."},
    {"category": "Colors", "korean": "흰색", "romanized": "Huin saek", "english": "White", "example": "눈은 흰색이에요."},
    {"category": "Colors", "korean": "검은색", "romanized": "Geomeun saek", "english": "Black", "example": "밤하늘은 검은색이에요."},
    {"category": "Colors", "korean": "분홍색", "romanized": "Bunhong saek", "english": "Pink", "example": "벚꽃은 분홍색이에요."},
    {"category": "Colors", "korean": "보라색", "romanized": "Bora saek", "english": "Purple", "example": "라벤더는 보라색이에요."},
    {"category": "Colors", "korean": "주황색", "romanized": "Juhwang saek", "english": "Orange", "example": "당근은 주황색이에요."},
    {"category": "Colors", "korean": "갈색", "romanized": "Gal saek", "english": "Brown", "example": "초콜릿은 갈색이에요."},
    {"category": "Colors", "korean": "회색", "romanized": "Hoe saek", "english": "Gray", "example": "하늘이 회색이에요."},
    {"category": "Colors", "korean": "금색", "romanized": "Geum saek", "english": "Gold", "example": "왕관은 금색이에요."},
    {"category": "Colors", "korean": "은색", "romanized": "Eun saek", "english": "Silver", "example": "반지가 은색이에요."},
    {"category": "Colors", "korean": "하늘색", "romanized": "Haneul saek", "english": "Sky blue", "example": "하늘색 티셔츠예요."},
    {"category": "Colors", "korean": "연두색", "romanized": "Yeondu saek", "english": "Light green / Yellow-green", "example": "새싹은 연두색이에요."},

    # ── FOOD ─────────────────────────────────────
    {"category": "Food", "korean": "김치", "romanized": "Gimchi", "english": "Kimchi", "example": "김치찌개 좋아해요."},
    {"category": "Food", "korean": "비빔밥", "romanized": "Bibimbap", "english": "Mixed rice bowl", "example": "비빔밥 하나 주세요."},
    {"category": "Food", "korean": "삼겹살", "romanized": "Samgyeopsal", "english": "Grilled pork belly", "example": "삼겹살 먹으러 가요."},
    {"category": "Food", "korean": "떡볶이", "romanized": "Tteokbokki", "english": "Spicy rice cakes", "example": "떡볶이 정말 맵지만 맛있어요."},
    {"category": "Food", "korean": "불고기", "romanized": "Bulgogi", "english": "Marinated grilled beef", "example": "불고기 냄새가 좋아요."},
    {"category": "Food", "korean": "순두부찌개", "romanized": "Sundubu jjigae", "english": "Soft tofu stew", "example": "순두부찌개가 따뜻해요."},
    {"category": "Food", "korean": "냉면", "romanized": "Naengmyeon", "english": "Cold noodles", "example": "여름에 냉면이 좋아요."},
    {"category": "Food", "korean": "치킨", "romanized": "Chikin", "english": "Korean fried chicken", "example": "치킨이랑 맥주 시켜요."},
    {"category": "Food", "korean": "라면", "romanized": "Ramyeon", "english": "Korean instant noodles", "example": "라면 끓여 줄게요."},
    {"category": "Food", "korean": "김밥", "romanized": "Gimbap", "english": "Korean rice rolls", "example": "소풍에 김밥 싸요."},
    {"category": "Food", "korean": "된장찌개", "romanized": "Doenjang jjigae", "english": "Soybean paste stew", "example": "된장찌개가 구수해요."},
    {"category": "Food", "korean": "잡채", "romanized": "Japchae", "english": "Glass noodle stir-fry", "example": "명절에 잡채를 먹어요."},
    {"category": "Food", "korean": "팥빙수", "romanized": "Patbingsu", "english": "Shaved ice with red beans", "example": "여름에 팥빙수가 최고예요."},
    {"category": "Food", "korean": "호떡", "romanized": "Hotteok", "english": "Sweet filled pancake", "example": "겨울에 호떡을 먹어요."},
    {"category": "Food", "korean": "소주", "romanized": "Soju", "english": "Korean distilled liquor", "example": "삼겹살이랑 소주를 마셔요."},
    {"category": "Food", "korean": "막걸리", "romanized": "Makgeolli", "english": "Korean rice wine", "example": "비 오는 날엔 막걸리예요."},
    {"category": "Food", "korean": "어묵", "romanized": "Eomuk", "english": "Fish cake", "example": "길거리에서 어묵을 먹어요."},
    {"category": "Food", "korean": "순대", "romanized": "Sundae", "english": "Korean blood sausage", "example": "순대 국밥 먹어요."},
    {"category": "Food", "korean": "갈비", "romanized": "Galbi", "english": "Grilled ribs", "example": "갈비가 부드러워요."},
    {"category": "Food", "korean": "전", "romanized": "Jeon", "english": "Korean savory pancake", "example": "비 오는 날엔 전이 생각나요."},
]

SCRAMKO_WORDS = [
    # Vocabulary
    {"category": "Vocabulary", "korean": "안녕", "romanized": "ANNYEONG", "meaning": "Hello / Bye (informal)"},
    {"category": "Vocabulary", "korean": "사랑", "romanized": "SARANG", "meaning": "Love"},
    {"category": "Vocabulary", "korean": "친구", "romanized": "CHINGU", "meaning": "Friend"},
    {"category": "Vocabulary", "korean": "가족", "romanized": "GAJOK", "meaning": "Family"},
    {"category": "Vocabulary", "korean": "학교", "romanized": "HAKGYO", "meaning": "School"},
    {"category": "Vocabulary", "korean": "선생", "romanized": "SEONSAENG", "meaning": "Teacher"},
    {"category": "Vocabulary", "korean": "학생", "romanized": "HAKSAENG", "meaning": "Student"},
    {"category": "Vocabulary", "korean": "시간", "romanized": "SIGAN", "meaning": "Time"},
    {"category": "Vocabulary", "korean": "날씨", "romanized": "NALSSI", "meaning": "Weather"},
    {"category": "Vocabulary", "korean": "여행", "romanized": "YEOHAENG", "meaning": "Travel"},
    {"category": "Vocabulary", "korean": "음악", "romanized": "EUMAK", "meaning": "Music"},
    {"category": "Vocabulary", "korean": "영화", "romanized": "YEONGHWA", "meaning": "Movie"},
    {"category": "Vocabulary", "korean": "꿈", "romanized": "KKUM", "meaning": "Dream"},
    {"category": "Vocabulary", "korean": "행복", "romanized": "HAENGBOK", "meaning": "Happiness"},
    {"category": "Vocabulary", "korean": "하늘", "romanized": "HANEUL", "meaning": "Sky"},
    {"category": "Vocabulary", "korean": "바다", "romanized": "BADA", "meaning": "Sea / Ocean"},
    {"category": "Vocabulary", "korean": "나무", "romanized": "NAMU", "meaning": "Tree"},
    {"category": "Vocabulary", "korean": "꽃", "romanized": "KKOT", "meaning": "Flower"},
    {"category": "Vocabulary", "korean": "마음", "romanized": "MAEUM", "meaning": "Heart / Mind"},
    {"category": "Vocabulary", "korean": "길", "romanized": "GIL", "meaning": "Road / Way"},
    {"category": "Vocabulary", "korean": "눈", "romanized": "NUN", "meaning": "Eye / Snow"},
    {"category": "Vocabulary", "korean": "입", "romanized": "IP", "meaning": "Mouth"},
    {"category": "Vocabulary", "korean": "손", "romanized": "SON", "meaning": "Hand"},
    {"category": "Vocabulary", "korean": "발", "romanized": "BAL", "meaning": "Foot"},
    {"category": "Vocabulary", "korean": "머리", "romanized": "MEORI", "meaning": "Head / Hair"},
    {"category": "Vocabulary", "korean": "집", "romanized": "JIP", "meaning": "House / Home"},
    {"category": "Vocabulary", "korean": "책", "romanized": "CHAEK", "meaning": "Book"},
    {"category": "Vocabulary", "korean": "물", "romanized": "MUL", "meaning": "Water"},
    {"category": "Vocabulary", "korean": "불", "romanized": "BUL", "meaning": "Fire"},
    {"category": "Vocabulary", "korean": "밥", "romanized": "BAP", "meaning": "Rice / Meal"},
    {"category": "Vocabulary", "korean": "옷", "romanized": "OT", "meaning": "Clothes"},
    {"category": "Vocabulary", "korean": "차", "romanized": "CHA", "meaning": "Car / Tea"},
    {"category": "Vocabulary", "korean": "문", "romanized": "MUN", "meaning": "Door"},
    {"category": "Vocabulary", "korean": "창문", "romanized": "CHANGMUN", "meaning": "Window"},
    {"category": "Vocabulary", "korean": "의자", "romanized": "UIJA", "meaning": "Chair"},
    {"category": "Vocabulary", "korean": "책상", "romanized": "CHAEKSANG", "meaning": "Desk"},
    {"category": "Vocabulary", "korean": "전화", "romanized": "JEONHWA", "meaning": "Phone / Call"},
    {"category": "Vocabulary", "korean": "컴퓨터", "romanized": "KEOMPYUTEO", "meaning": "Computer"},
    {"category": "Vocabulary", "korean": "병원", "romanized": "BYEONGWON", "meaning": "Hospital"},
    {"category": "Vocabulary", "korean": "지하철", "romanized": "JIHACHEOL", "meaning": "Subway"},
    {"category": "Vocabulary", "korean": "버스", "romanized": "BEOSEU", "meaning": "Bus"},
    {"category": "Vocabulary", "korean": "비행기", "romanized": "BIHAENGGI", "meaning": "Airplane"},
    {"category": "Vocabulary", "korean": "회사", "romanized": "HOESA", "meaning": "Company"},
    {"category": "Vocabulary", "korean": "약속", "romanized": "YAKSOK", "meaning": "Promise"},
    {"category": "Vocabulary", "korean": "추억", "romanized": "CHUEOK", "meaning": "Memory"},
    {"category": "Vocabulary", "korean": "봄", "romanized": "BOM", "meaning": "Spring"},
    {"category": "Vocabulary", "korean": "여름", "romanized": "YEOREUM", "meaning": "Summer"},
    {"category": "Vocabulary", "korean": "가을", "romanized": "GAEUL", "meaning": "Autumn"},
    {"category": "Vocabulary", "korean": "겨울", "romanized": "GYEOUL", "meaning": "Winter"},
    {"category": "Vocabulary", "korean": "오늘", "romanized": "ONEUL", "meaning": "Today"},
    {"category": "Vocabulary", "korean": "내일", "romanized": "NAEIL", "meaning": "Tomorrow"},
    {"category": "Vocabulary", "korean": "어제", "romanized": "EOJE", "meaning": "Yesterday"},
    {"category": "Vocabulary", "korean": "아침", "romanized": "ACHIM", "meaning": "Morning"},
    {"category": "Vocabulary", "korean": "점심", "romanized": "JEOMSIM", "meaning": "Lunch / Noon"},
    {"category": "Vocabulary", "korean": "저녁", "romanized": "JEONYEOK", "meaning": "Evening"},
    {"category": "Vocabulary", "korean": "밤", "romanized": "BAM", "meaning": "Night"},
    {"category": "Vocabulary", "korean": "주말", "romanized": "JUMAL", "meaning": "Weekend"},

    # Food
    {"category": "Food", "korean": "김치", "romanized": "GIMCHI", "meaning": "Kimchi"},
    {"category": "Food", "korean": "비빔밥", "romanized": "BIBIMBAP", "meaning": "Mixed rice bowl"},
    {"category": "Food", "korean": "떡볶이", "romanized": "TTEOKBOKKI", "meaning": "Spicy rice cakes"},
    {"category": "Food", "korean": "불고기", "romanized": "BULGOGI", "meaning": "Marinated beef"},
    {"category": "Food", "korean": "삼겹살", "romanized": "SAMGYEOPSAL", "meaning": "Grilled pork belly"},
    {"category": "Food", "korean": "냉면", "romanized": "NAENGMYEON", "meaning": "Cold noodles"},
    {"category": "Food", "korean": "치킨", "romanized": "CHIKIN", "meaning": "Fried chicken"},
    {"category": "Food", "korean": "라면", "romanized": "RAMYEON", "meaning": "Instant noodles"},
    {"category": "Food", "korean": "김밥", "romanized": "GIMBAP", "meaning": "Rice rolls"},
    {"category": "Food", "korean": "된장", "romanized": "DOENJANG", "meaning": "Soybean paste"},
    {"category": "Food", "korean": "소주", "romanized": "SOJU", "meaning": "Korean liquor"},
    {"category": "Food", "korean": "막걸리", "romanized": "MAKGEOLLI", "meaning": "Rice wine"},
    {"category": "Food", "korean": "호떡", "romanized": "HOTTEOK", "meaning": "Sweet pancake"},
    {"category": "Food", "korean": "순대", "romanized": "SUNDAE", "meaning": "Blood sausage"},
    {"category": "Food", "korean": "잡채", "romanized": "JAPCHAE", "meaning": "Glass noodles"},
    {"category": "Food", "korean": "갈비", "romanized": "GALBI", "meaning": "Grilled ribs"},
    {"category": "Food", "korean": "어묵", "romanized": "EOMUK", "meaning": "Fish cake"},
    {"category": "Food", "korean": "파전", "romanized": "PAJEON", "meaning": "Green onion pancake"},
    {"category": "Food", "korean": "미역국", "romanized": "MIYEOKGUK", "meaning": "Seaweed soup"},
    {"category": "Food", "korean": "삼계탕", "romanized": "SAMGYETANG", "meaning": "Ginseng chicken soup"},

    # Phrases
    {"category": "Phrases", "korean": "감사", "romanized": "GAMSA", "meaning": "Thanks / Gratitude"},
    {"category": "Phrases", "korean": "미안", "romanized": "MIAN", "meaning": "Sorry"},
    {"category": "Phrases", "korean": "괜찮", "romanized": "GWAENCHANA", "meaning": "It's okay"},
    {"category": "Phrases", "korean": "파이팅", "romanized": "PAITING", "meaning": "Fighting! / You can do it!"},
    {"category": "Phrases", "korean": "대박", "romanized": "DAEBAK", "meaning": "Awesome / Jackpot"},
    {"category": "Phrases", "korean": "화이팅", "romanized": "HWAITING", "meaning": "Fighting! (alternate)"},
    {"category": "Phrases", "korean": "어서", "romanized": "EOSEO", "meaning": "Welcome / Hurry"},
    {"category": "Phrases", "korean": "잠깐", "romanized": "JAMKKAN", "meaning": "Just a moment"},
    {"category": "Phrases", "korean": "수고", "romanized": "SUGO", "meaning": "Good work"},
    {"category": "Phrases", "korean": "맞아", "romanized": "MAJA", "meaning": "That's right"},
    {"category": "Phrases", "korean": "진짜", "romanized": "JINJJA", "meaning": "Really / Seriously"},
    {"category": "Phrases", "korean": "왜요", "romanized": "WAEYO", "meaning": "Why?"},
    {"category": "Phrases", "korean": "어디", "romanized": "EODI", "meaning": "Where?"},
    {"category": "Phrases", "korean": "언제", "romanized": "EONJE", "meaning": "When?"},
    {"category": "Phrases", "korean": "얼마", "romanized": "EOLMA", "meaning": "How much?"},

    # Numbers
    {"category": "Numbers", "korean": "하나", "romanized": "HANA", "meaning": "One (native)"},
    {"category": "Numbers", "korean": "둘", "romanized": "DUL", "meaning": "Two (native)"},
    {"category": "Numbers", "korean": "셋", "romanized": "SET", "meaning": "Three (native)"},
    {"category": "Numbers", "korean": "넷", "romanized": "NET", "meaning": "Four (native)"},
    {"category": "Numbers", "korean": "다섯", "romanized": "DASEOT", "meaning": "Five (native)"},
    {"category": "Numbers", "korean": "여섯", "romanized": "YEOSEOT", "meaning": "Six (native)"},
    {"category": "Numbers", "korean": "일곱", "romanized": "ILGOP", "meaning": "Seven (native)"},
    {"category": "Numbers", "korean": "여덟", "romanized": "YEODEOL", "meaning": "Eight (native)"},
    {"category": "Numbers", "korean": "아홉", "romanized": "AHOP", "meaning": "Nine (native)"},
    {"category": "Numbers", "korean": "열", "romanized": "YEOL", "meaning": "Ten (native)"},
    {"category": "Numbers", "korean": "백", "romanized": "BAEK", "meaning": "One hundred"},
    {"category": "Numbers", "korean": "천", "romanized": "CHEON", "meaning": "One thousand"},
    {"category": "Numbers", "korean": "만", "romanized": "MAN", "meaning": "Ten thousand"},

    # Colors
    {"category": "Colors", "korean": "빨강", "romanized": "PPALGANG", "meaning": "Red"},
    {"category": "Colors", "korean": "파랑", "romanized": "PARANG", "meaning": "Blue"},
    {"category": "Colors", "korean": "노랑", "romanized": "NORANG", "meaning": "Yellow"},
    {"category": "Colors", "korean": "초록", "romanized": "CHOROK", "meaning": "Green"},
    {"category": "Colors", "korean": "흰색", "romanized": "HUINSAEK", "meaning": "White"},
    {"category": "Colors", "korean": "검정", "romanized": "GEOMJEONG", "meaning": "Black"},
    {"category": "Colors", "korean": "분홍", "romanized": "BUNHONG", "meaning": "Pink"},
    {"category": "Colors", "korean": "보라", "romanized": "BORA", "meaning": "Purple"},
    {"category": "Colors", "korean": "주황", "romanized": "JUHWANG", "meaning": "Orange"},
    {"category": "Colors", "korean": "갈색", "romanized": "GALSAEK", "meaning": "Brown"},
    {"category": "Colors", "korean": "회색", "romanized": "HOESAEK", "meaning": "Gray"},
    {"category": "Colors", "korean": "금색", "romanized": "GEUMSAEK", "meaning": "Gold"},
]


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def load_scores(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return []

def save_score(filename, name, score, total):
    scores = load_scores(filename)
    scores.append({"name": name, "score": score, "date": datetime.now().strftime("%Y-%m-%d")})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(filename, "w") as f:
        json.dump(scores, f)

def scramble_word(word):
    letters = list(word)
    for _ in range(20):
        random.shuffle(letters)
        if "".join(letters) != word and len(word) > 1:
            return "".join(letters)
    return word[::-1] if len(word) > 1 else word + "?"

def render_leaderboard(filename, total):
    scores = load_scores(filename)
    if scores:
        for i, s in enumerate(scores):
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."
            st.markdown(f'''<div class="lb-row"><span class="lb-rank">{medal}</span><span class="lb-name">{s['name']}</span><span class="lb-score">{s['score']}/{total}</span><span style="color:#333;font-size:0.75rem;margin-left:8px;">{s['date']}</span></div>''', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#444;font-size:0.85rem;padding:8px 0;">No scores yet — be the first!</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home",
        "game_state": "start",
        "questions": [], "current": 0, "score": 0,
        "answered": False, "selected": None, "score_saved": False,
        "cards": [], "flipped": False, "learned": set(),
        "words": [], "correct": False, "hint_used": False,
        "hint_count": 0, "scrambled": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# Sidebar — AI Settings
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 AI Hint Settings")
    # Auto-load from Streamlit secrets if available
    secret_key = ""
    try:
        secret_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    if secret_key:
        st.session_state.openai_key = secret_key
        st.success("✅ AI Hints enabled!")
    else:
        openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", help="Get from platform.openai.com/api-keys")
        if openai_key:
            st.session_state.openai_key = openai_key
            st.success("✅ AI Hints enabled!")
        else:
            st.info("💡 Add API key to enable AI Hints")
    st.markdown("---")
    st.markdown("**AI Chat** — ask follow-up questions about any wrong answer.")

# ─────────────────────────────────────────────
# AI Hint Function
# ─────────────────────────────────────────────
def get_ai_hint(question, correct_answer, explanation, category):
    key = st.session_state.get("openai_key", "")
    if not key or not OPENAI_AVAILABLE:
        return None
    try:
        client = OpenAI(api_key=key)
        prompt = f"You are a friendly tutor. A student got this wrong:\nQuestion: {question}\nCorrect Answer: {correct_answer}\nCategory: {category}\nExplanation: {explanation}\n\nGive a short friendly 2-sentence explanation. Keep it simple and encouraging."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception:
        return None

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
col_back, col_title = st.columns([1, 6])
with col_title:
    st.markdown('''<div class="hero"><div class="hero-title">🎮 LearnPlay</div><div class="hero-sub">Korean & Python Learning Hub</div></div>''', unsafe_allow_html=True)
with col_back:
    if st.session_state.page != "home":
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Home"):
            st.session_state.page = "home"
            st.session_state.game_state = "start"
            st.rerun()

# ─────────────────────────────────────────────
# HOME SCREEN
# ─────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Helper: get top scorer for a game ──
    def top_scorer(filename, total):
        scores = load_scores(filename)
        if scores:
            s = scores[0]
            return f'<span class="top-scorer-pill" style="color:#f59e0b;">🏆 <span class="top-scorer-name">{s["name"]}</span> <span class="top-scorer-score">{s["score"]}/{total}</span></span>'
        return '<span class="top-scorer-pill" style="color:#444;">🏆 No scores yet</span>'

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'''
        <div class="game-card" style="border-color:#6366f133;--glow:#6366f155;animation-delay:0s;">
            <span class="game-icon">🇰🇷</span>
            <div class="game-title" style="color:#818cf8;">DumbQuiz</div>
            <div class="game-desc">Korean language quiz</div>
            <div class="game-stats" style="color:#6366f1;">20 questions per game</div>
            {top_scorer("lp_dumbquiz.json", 20)}
        </div>''', unsafe_allow_html=True)
        if st.button("Play DumbQuiz", use_container_width=True, key="go_dq"):
            st.session_state.page = "dumbquiz"
            st.session_state.game_state = "start"
            st.rerun()

    with col2:
        st.markdown(f'''
        <div class="game-card" style="border-color:#4ade8033;--glow:#4ade8055;animation-delay:0.1s;">
            <span class="game-icon">🐍</span>
            <div class="game-title" style="color:#4ade80;">PyQuiz</div>
            <div class="game-desc">Python programming quiz</div>
            <div class="game-stats" style="color:#4ade80;">20 questions per game</div>
            {top_scorer("lp_pyquiz.json", 20)}
        </div>''', unsafe_allow_html=True)
        if st.button("Play PyQuiz", use_container_width=True, key="go_pq"):
            st.session_state.page = "pyquiz"
            st.session_state.game_state = "start"
            st.rerun()

    with col1:
        st.markdown(f'''
        <div class="game-card" style="border-color:#ec489933;--glow:#ec489955;animation-delay:0.2s;">
            <span class="game-icon">🃏</span>
            <div class="game-title" style="color:#ec4899;">Flashko</div>
            <div class="game-desc">Korean flashcards</div>
            <div class="game-stats" style="color:#ec4899;">20 cards per session</div>
            {top_scorer("lp_dumbquiz.json", 20)}
        </div>''', unsafe_allow_html=True)
        if st.button("Play Flashko", use_container_width=True, key="go_fk"):
            st.session_state.page = "flashko"
            st.session_state.game_state = "start"
            st.session_state.cards = random.sample(FLASHKO_CARDS, 20)
            st.session_state.current = 0
            st.session_state.flipped = False
            st.session_state.learned = set()
            st.rerun()

    with col2:
        st.markdown(f'''
        <div class="game-card" style="border-color:#f59e0b33;--glow:#f59e0b55;animation-delay:0.3s;">
            <span class="game-icon">🔤</span>
            <div class="game-title" style="color:#f59e0b;">ScramKo</div>
            <div class="game-desc">Korean word scramble</div>
            <div class="game-stats" style="color:#f59e0b;">10 words per game</div>
            {top_scorer("lp_scramko.json", 10)}
        </div>''', unsafe_allow_html=True)
        if st.button("Play ScramKo", use_container_width=True, key="go_sk"):
            st.session_state.page = "scramko"
            st.session_state.game_state = "start"
            st.rerun()

    # ── Combined Leaderboard ──
    all_scores = []
    for fname, gname, total in [
        ("lp_dumbquiz.json","🇰🇷 DumbQuiz",20),
        ("lp_pyquiz.json","🐍 PyQuiz",20),
        ("lp_scramko.json","🔤 ScramKo",10),
    ]:
        for s in load_scores(fname):
            all_scores.append({**s, "game": gname, "total": total, "pct": s["score"]/total})

    all_scores.sort(key=lambda x: x["pct"], reverse=True)

    if all_scores:
        st.markdown('''<div class="home-lb">
            <div class="home-lb-title">🏆 Hall of Fame — All Games</div>''', unsafe_allow_html=True)
        for i, s in enumerate(all_scores[:10]):
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."
            pct_color = "#4ade80" if s["pct"] >= 0.8 else "#f59e0b" if s["pct"] >= 0.5 else "#f87171"
            st.markdown(f'''<div class="home-lb-row">
                <span class="home-lb-rank">{medal}</span>
                <span class="home-lb-game">{s["game"]}</span>
                <span class="home-lb-name">{s["name"]}</span>
                <span class="home-lb-score" style="color:{pct_color};">{s["score"]}/{s["total"]}</span>
                <span style="color:#333;font-size:0.72rem;margin-left:6px;">{s["date"]}</span>
            </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# QUIZ ENGINE (shared by DumbQuiz + PyQuiz)
# ─────────────────────────────────────────────
def run_quiz(questions_bank, score_file, color, total=20):
    if st.session_state.game_state == "start":
        label = "Korean Language Quiz" if score_file == "lp_dumbquiz.json" else "Python Programming Quiz"
        emoji = "🇰🇷" if score_file == "lp_dumbquiz.json" else "🐍"
        qcount = len(questions_bank)
        st.markdown(f'''<div class="q-card" style="text-align:center;padding:32px;">
            <div style="font-size:2.5rem;margin-bottom:12px;">{emoji}</div>
            <div style="font-size:1.2rem;font-weight:800;margin-bottom:6px;">{label}</div>
            <div style="color:#444;margin-bottom:4px;">20 random questions from {qcount} question bank</div>
        </div>''', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            if st.button("🚀 Start", use_container_width=True):
                st.session_state.questions = random.sample(questions_bank, min(total, len(questions_bank)))
                st.session_state.current = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.selected = None
                st.session_state.score_saved = False
                st.session_state.game_state = "playing"
                st.rerun()
        st.markdown("### 🏆 High Scores")
        render_leaderboard(score_file, total)

    elif st.session_state.game_state == "playing":
        q = st.session_state.questions[st.session_state.current]
        qnum = st.session_state.current + 1
        st.progress(qnum / total)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="progress-text">Q {qnum}/{total}</div>', unsafe_allow_html=True)
        with c2: diff=q['difficulty']; st.markdown(f'<div style="text-align:center"><span class="diff-{diff}">{diff}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="progress-text" style="text-align:right;">Score: {st.session_state.score}</div>', unsafe_allow_html=True)

        code_html = f'<div class="code-block">{q["code"]}</div>' if q.get("code") else ""
        korean_html = f'<div class="q-korean">{q["korean"]}</div>' if q.get("korean") else ""
        st.markdown(f'''<div class="q-card"><div class="q-cat">{q['category']}</div><div class="q-text">{q['question']}</div>{korean_html}{code_html}</div>''', unsafe_allow_html=True)

        if not st.session_state.answered:
            cols = st.columns(2)
            for i, opt in enumerate(q["options"]):
                with cols[i % 2]:
                    if st.button(opt, key=f"opt_{i}", use_container_width=True):
                        st.session_state.answered = True
                        st.session_state.selected = i
                        if i == q["answer"]: st.session_state.score += 1
                        st.rerun()
        else:
            sel = st.session_state.selected
            correct = sel == q["answer"]
            cols = st.columns(2)
            for i, opt in enumerate(q["options"]):
                with cols[i % 2]:
                    if i == q["answer"]: st.success(f"✓ {opt}")
                    elif i == sel and not correct: st.error(f"✗ {opt}")
                    else: st.button(opt, key=f"os_{i}", disabled=True, use_container_width=True)
            if correct:
                st.markdown('<div class="correct-box">✓ Correct!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="wrong-box">✗ Wrong. Answer: <strong>{q["options"][q["answer"]]}</strong></div>', unsafe_allow_html=True)
                chat_key = f"ai_chat_{st.session_state.current}"
                if st.session_state.get("openai_key") and OPENAI_AVAILABLE:
                    # Init chat history for this question
                    if chat_key not in st.session_state:
                        # Auto-send first explanation
                        system = f"You are a friendly tutor helping a student learn. They got this question wrong: '{q['question']}'. The correct answer is: '{q['options'][q['answer']]}'. Category: {q['category']}. Base explanation: {q['explanation']}. Answer follow-up questions about this topic. Keep responses short (2-3 sentences), friendly, and encouraging."
                        with st.spinner("🤖 AI is explaining..."):
                            try:
                                client = OpenAI(api_key=st.session_state.openai_key)
                                resp = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[
                                        {"role": "system", "content": system},
                                        {"role": "user", "content": "Explain why this is the correct answer in a simple friendly way."}
                                    ],
                                    max_tokens=150, temperature=0.7,
                                )
                                ai_msg = resp.choices[0].message.content
                                st.session_state[chat_key] = {
                                    "system": system,
                                    "history": [
                                        {"role": "user", "content": "Explain why this is the correct answer in a simple friendly way."},
                                        {"role": "assistant", "content": ai_msg}
                                    ]
                                }
                            except Exception as e:
                                st.session_state[chat_key] = {"system": "", "history": [], "error": str(e)}
                        st.rerun()

                    # Render chat
                    if chat_key in st.session_state and "history" in st.session_state[chat_key]:
                        chat_data = st.session_state[chat_key]
                        st.markdown('<div style="background:#0f0f1a;border:1px solid #1e1e30;border-radius:10px;padding:14px;margin:8px 0;">', unsafe_allow_html=True)
                        for msg in chat_data["history"]:
                            if msg["role"] == "assistant":
                                st.markdown(f'<div style="background:#1a1a2e;border-left:3px solid #6366f1;border-radius:0 8px 8px 0;padding:10px 14px;color:#a5b4fc;font-size:0.85rem;margin:4px 0;"><b>🤖 AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div style="background:#1e1e2e;border-left:3px solid #ec4899;border-radius:0 8px 8px 0;padding:10px 14px;color:#f9a8d4;font-size:0.85rem;margin:4px 0;text-align:right;"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Follow-up input
                        follow_up = st.text_input("Ask a follow-up question...", key=f"followup_{st.session_state.current}_{len(chat_data['history'])}", placeholder="e.g. Can you give me an example?", label_visibility="collapsed")
                        c_send, c_clear = st.columns([3, 1])
                        with c_send:
                            if st.button("Send 💬", key=f"send_{st.session_state.current}_{len(chat_data['history'])}", use_container_width=True):
                                if follow_up.strip():
                                    chat_data["history"].append({"role": "user", "content": follow_up.strip()})
                                    with st.spinner("🤖 Thinking..."):
                                        try:
                                            client = OpenAI(api_key=st.session_state.openai_key)
                                            msgs = [{"role": "system", "content": chat_data["system"]}] + chat_data["history"]
                                            resp = client.chat.completions.create(
                                                model="gpt-4o-mini",
                                                messages=msgs,
                                                max_tokens=150, temperature=0.7,
                                            )
                                            ai_reply = resp.choices[0].message.content
                                            chat_data["history"].append({"role": "assistant", "content": ai_reply})
                                            st.session_state[chat_key] = chat_data
                                        except Exception as e:
                                            chat_data["history"].append({"role": "assistant", "content": f"Sorry, I couldn't respond. Error: {str(e)}"})
                                            st.session_state[chat_key] = chat_data
                                    st.rerun()
                        with c_clear:
                            if st.button("Clear 🗑", key=f"clear_{st.session_state.current}", use_container_width=True):
                                del st.session_state[chat_key]
                                st.rerun()
                else:
                    st.markdown('<div style="font-size:0.75rem;color:#333;margin:4px 0;">💡 Add OpenAI key in sidebar for AI chat</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="explanation">💡 {q["explanation"]}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lbl = "See Results 🎉" if qnum == total else "Next →"
            c1,c2,c3 = st.columns([1,2,1])
            with c2:
                if st.button(lbl, use_container_width=True):
                    st.session_state.current += 1
                    st.session_state.answered = False
                    st.session_state.selected = None
                    if st.session_state.current >= total: st.session_state.game_state = "result"
                    st.rerun()

    elif st.session_state.game_state == "result":
        score = st.session_state.score
        pct = score / total
        if pct >= 0.9: grade,gc = "🏆 Expert!","#4ade80"
        elif pct >= 0.7: grade,gc = "⭐ Advanced!","#6366f1"
        elif pct >= 0.5: grade,gc = "👍 Intermediate!",color
        else: grade,gc = "💪 Keep Practicing!","#f87171"
        st.markdown(f'''<div class="score-card"><div class="big-score">{score}/{total}</div>
        <div style="color:#444;margin:6px 0;">{score} out of {total} correct</div>
        <div style="color:{gc};font-weight:800;font-size:1.05rem;">{grade}</div></div>''', unsafe_allow_html=True)
        if not st.session_state.score_saved:
            name = st.text_input("Enter name for leaderboard", placeholder="Your name...", max_chars=20)
            c1,c2 = st.columns(2)
            with c1:
                if st.button("💾 Save", use_container_width=True):
                    if name.strip():
                        save_score(score_file, name.strip(), score, total)
                        st.session_state.score_saved = True
                        st.rerun()
                    else: st.warning("Enter a name")
            with c2:
                if st.button("Skip", use_container_width=True):
                    st.session_state.score_saved = True
                    st.rerun()
        st.markdown("### 🏆 High Scores")
        render_leaderboard(score_file, total)
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            if st.button("🔄 Play Again", use_container_width=True):
                st.session_state.game_state = "start"
                st.session_state.score_saved = False
                st.rerun()

# ─────────────────────────────────────────────
# DUMBQUIZ PAGE
# ─────────────────────────────────────────────
if st.session_state.page == "dumbquiz":
    run_quiz(DUMBQUIZ_QUESTIONS, "lp_dumbquiz.json", "#818cf8")

# ─────────────────────────────────────────────
# PYQUIZ PAGE
# ─────────────────────────────────────────────
elif st.session_state.page == "pyquiz":
    run_quiz(PYQUIZ_QUESTIONS, "lp_pyquiz.json", "#4ade80")

# ─────────────────────────────────────────────
# FLASHKO PAGE
# ─────────────────────────────────────────────
elif st.session_state.page == "flashko":
    cards = st.session_state.cards
    current = st.session_state.current

    if current >= len(cards):
        st.markdown(f'''<div class="score-card">
            <div style="font-size:2.5rem;">🎉</div>
            <div style="font-size:1.3rem;font-weight:800;margin:10px 0;">All done!</div>
            <div style="color:#444;">Completed {len(cards)} cards · {len(st.session_state.learned)} marked as learned</div>
        </div>''', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔀 New Shuffle", use_container_width=True):
                st.session_state.cards = random.sample(FLASHKO_CARDS, 20)
                st.session_state.current = 0
                st.session_state.flipped = False
                st.session_state.learned = set()
                st.rerun()
        with c2:
            if st.button("🔁 Restart", use_container_width=True):
                st.session_state.current = 0
                st.session_state.flipped = False
                st.rerun()
    else:
        card = cards[current]
        st.progress((current + 1) / len(cards))
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="progress-text">Card {current+1}/{len(cards)}</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="text-align:center;font-size:0.7rem;color:#555;">{card["category"]}</div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="progress-text" style="text-align:right;">{len(st.session_state.learned)} learned</div>', unsafe_allow_html=True)

        learned_html = '<div style="font-size:0.75rem;color:#4ade80;margin-top:10px;">✓ Marked as learned</div>' if current in st.session_state.learned else ""

        if not st.session_state.flipped:
            st.markdown(f'''<div class="flash-front">
                <div style="font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#333;margin-bottom:12px;">{card["category"]}</div>
                <div class="card-korean">{card["korean"]}</div>
                <div class="card-romanized">{card["romanized"]}</div>
                <div style="font-size:0.72rem;color:#2a2a4a;margin-top:12px;">Click Reveal to see answer</div>
                {learned_html}
            </div>''', unsafe_allow_html=True)
            c1,c2,c3 = st.columns([1,2,1])
            with c2:
                if st.button("👁️ Reveal", use_container_width=True):
                    st.session_state.flipped = True
                    st.rerun()
        else:
            st.markdown(f'''<div class="flash-back">
                <div style="font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#2a4a2a;margin-bottom:12px;">{card["category"]}</div>
                <div class="card-korean">{card["korean"]}</div>
                <div class="card-romanized">{card["romanized"]}</div>
                <div class="card-english">{card["english"]}</div>
                <div class="card-example">{card["example"]}</div>
                {learned_html}
            </div>''', unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1:
                if st.button("✓ Learned", use_container_width=True):
                    st.session_state.learned.add(current)
                    st.session_state.current += 1
                    st.session_state.flipped = False
                    st.rerun()
            with c2:
                if st.button("→ Next", use_container_width=True):
                    st.session_state.current += 1
                    st.session_state.flipped = False
                    st.rerun()
            with c3:
                if st.button("↺ Flip", use_container_width=True):
                    st.session_state.flipped = False
                    st.rerun()
        if current > 0:
            c1,c2,c3 = st.columns([1,2,1])
            with c2:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.current -= 1
                    st.session_state.flipped = False
                    st.rerun()

# ─────────────────────────────────────────────
# SCRAMKO PAGE
# ─────────────────────────────────────────────
elif st.session_state.page == "scramko":
    if st.session_state.game_state == "start":
        st.markdown('''<div class="scramble-card" style="padding:32px;">
            <div style="font-size:2.5rem;margin-bottom:12px;">🔤</div>
            <div style="font-size:1.2rem;font-weight:800;margin-bottom:6px;">Unscramble the Korean!</div>
            <div style="color:#555;margin-bottom:6px;">Romanized letters are scrambled — type the correct romanization</div>
            <div style="color:#f59e0b;font-size:0.82rem;">10 words · 117 word bank · Hint available</div>
        </div>''', unsafe_allow_html=True)
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            if st.button("🎮 Start", use_container_width=True):
                selected = random.sample(SCRAMKO_WORDS, 10)
                st.session_state.words = selected
                st.session_state.current = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.correct = False
                st.session_state.hint_used = False
                st.session_state.hint_count = 0
                st.session_state.score_saved = False
                st.session_state.scrambled = scramble_word(selected[0]["romanized"])
                st.session_state.game_state = "playing"
                st.rerun()
        st.markdown("### 🏆 High Scores")
        render_leaderboard("lp_scramko.json", 10)

    elif st.session_state.game_state == "playing":
        word = st.session_state.words[st.session_state.current]
        wnum = st.session_state.current + 1
        st.progress(wnum / 10)
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="progress-text">Word {wnum}/10</div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="text-align:center;font-size:0.65rem;color:#555;">{word["category"]}</div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="progress-text" style="text-align:right;">Score: {st.session_state.score}</div>', unsafe_allow_html=True)

        hint_html = f'<div style="font-size:0.82rem;color:#8b5cf6;margin-top:8px;">💡 Hint: {word["romanized"][0]}{"_ " * (len(word["romanized"])-1)} ({len(word["romanized"])} letters)</div>' if st.session_state.hint_used else ""
        st.markdown(f'''<div class="scramble-card">
            <div style="font-size:0.65rem;letter-spacing:3px;color:#333;text-transform:uppercase;margin-bottom:12px;">WORD {wnum} OF 10</div>
            <div class="meaning-text">"{word['meaning']}"</div>
            <div class="scrambled-word">{st.session_state.scrambled}</div>
            <div style="font-size:0.78rem;color:#333;">Unscramble the romanization above</div>
            {hint_html}
        </div>''', unsafe_allow_html=True)

        if not st.session_state.answered:
            user_input = st.text_input("Answer", placeholder="Type romanization...", label_visibility="collapsed", key=f"si_{wnum}").upper().strip()
            c1,c2,c3 = st.columns(3)
            with c1:
                if st.button("✓ Submit", use_container_width=True):
                    if user_input:
                        st.session_state.answered = True
                        st.session_state.correct = user_input == word["romanized"]
                        if st.session_state.correct: st.session_state.score += 1
                        st.rerun()
            with c2:
                if not st.session_state.hint_used:
                    if st.button("💡 Hint", use_container_width=True):
                        st.session_state.hint_used = True
                        st.session_state.hint_count += 1
                        st.rerun()
            with c3:
                if st.button("⏭ Skip", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.correct = False
                    st.rerun()
        else:
            if st.session_state.correct: st.markdown('<div class="correct-box">✓ Correct! 🎉</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="wrong-box">✗ Wrong!</div>', unsafe_allow_html=True)
            st.markdown(f'''<div class="answer-reveal">
                <div style="font-size:0.75rem;color:#333;margin-bottom:4px;">Correct answer:</div>
                <div class="korean-big">{word['korean']}</div>
                <div style="color:#888;font-size:0.95rem;font-weight:700;">{word['romanized']}</div>
                <div style="color:#444;font-size:0.82rem;margin-top:4px;">{word['meaning']}</div>
            </div>''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lbl = "See Results 🎉" if wnum == 10 else "Next Word →"
            c1,c2,c3 = st.columns([1,2,1])
            with c2:
                if st.button(lbl, use_container_width=True):
                    nxt = st.session_state.current + 1
                    st.session_state.current = nxt
                    st.session_state.answered = False
                    st.session_state.correct = False
                    st.session_state.hint_used = False
                    if nxt >= 10: st.session_state.game_state = "result"
                    else: st.session_state.scrambled = scramble_word(st.session_state.words[nxt]["romanized"])
                    st.rerun()

    elif st.session_state.game_state == "result":
        score = st.session_state.score
        pct = score / 10
        if pct >= 0.9: grade,gc = "🏆 Word Master!","#f59e0b"
        elif pct >= 0.7: grade,gc = "⭐ Great!","#8b5cf6"
        elif pct >= 0.5: grade,gc = "👍 Good!","#38bdf8"
        else: grade,gc = "💪 Keep Practicing!","#f87171"
        st.markdown(f'''<div class="score-card"><div class="big-score">{score}/10</div>
        <div style="color:#444;margin:6px 0;">{score} of 10 words unscrambled · {st.session_state.hint_count} hints used</div>
        <div style="color:{gc};font-weight:800;font-size:1.05rem;">{grade}</div></div>''', unsafe_allow_html=True)
        if not st.session_state.score_saved:
            name = st.text_input("Name for leaderboard", placeholder="Your name...", max_chars=20)
            c1,c2 = st.columns(2)
            with c1:
                if st.button("💾 Save", use_container_width=True):
                    if name.strip():
                        save_score("lp_scramko.json", name.strip(), score, 10)
                        st.session_state.score_saved = True
                        st.rerun()
                    else: st.warning("Enter a name")
            with c2:
                if st.button("Skip", use_container_width=True):
                    st.session_state.score_saved = True
                    st.rerun()
        st.markdown("### 🏆 High Scores")
        render_leaderboard("lp_scramko.json", 10)
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            if st.button("🔄 Play Again", use_container_width=True):
                st.session_state.game_state = "start"
                st.session_state.score_saved = False
                st.rerun()

# Footer
st.markdown('''<div style="text-align:center;color:#111;font-size:0.78rem;margin-top:48px;padding-top:14px;border-top:1px solid #111;">
LearnPlay · Korean & Python Learning Hub · Team Aatank Capstone Project
</div>''', unsafe_allow_html=True)
