# app.py → এটা এখন পুরো ক্রিকেট চ্যাটবটের মতো কাজ করবে
import streamlit as st
import httpx
import asyncio
from datetime import datetime

st.set_page_config(page_title="AI ক্রিকেট চ্যাটবট", page_icon="CRICKET", layout="centered")
st.title("AI ক্রিকেট চ্যাটবট")
st.caption("যেকোনো ক্রিকেট প্রশ্ন করুন — বাংলায় বা ইংরেজিতে!")

API_KEY = "5831a20f-600d-47e5-abbe-856c6ac34e1c"

# ক্যাশ
if "matches" not in st.session_state:
    st.session_state.matches = []
    st.session_state.last_update = ""

async def get_matches():
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url)
            if r.status_code == 200:
                return r.json().get("data", [])
    except:
        pass
    return st.session_state.matches

# চ্যাট হিস্ট্রি
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "আসসালামু আলাইকুম!\nক্রিকেট নিয়ে যা খুশি জিজ্ঞেস করতে পারেন!\n\nউদাহরণ:\n• আজকের ম্যাচ কী?\n• বাংলাদেশ কবে খেলবে?\n• ইন্ডিয়া vs অস্ট্রেলিয়া কে জিতেছে?\n• লাইভ স্কোর কী?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("আপনার প্রশ্ন লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("খুঁজে দিচ্ছি..."):
            matches = asyncio.run(get_matches())
            st.session_state.matches = matches
            now = datetime.now()
            reply = ""
            txt = prompt.lower().strip()

            # ১. আজকের ম্যাচ
            if any(w in txt for w in ["আজকে", "today", "আজকের", "today match", "আজ কী খেলা"]):
                today = now.strftime("%Y-%m-%d")
                today_matches = [m for m in matches if m.get("date", "").startswith(today)]
                reply += f"**আজকের ম্যাচ ({len(today_matches)}টি):**\n\n"
                for m in today_matches:
                    reply += f"**{m.get('name','')}**\n"
                    reply += f"{m.get('status','')}\n"
                    reply += f"ভেন্যু: {m.get('venue','')}\n\n"

            # ২. লাইভ ম্যাচ
            elif any(w in txt for w in ["লাইভ", "live", "চলছে", "running", "স্কোর কত"]):
                live = [m for m in matches if m.get("matchStarted") and not m.get("matchEnded")]
                if live:
                    reply += "**লাইভ ম্যাচ:**\n\n"
                    for m in live:
                        reply += f"**{m.get('name')}**\n"
                        if m.get("score"):
                            for s in m["score"]:
                                reply += f"→ {s['inning']}: {s['r']}/{s['w']} ({s['o']})\n"
                        reply += f"{m.get('status')}\n\n"
                else:
                    reply += "এই মুহূর্তে কোনো লাইভ ম্যাচ নেই\n"

            # ৩. কোন দেশ/টিমের ম্যাচ
            elif any(team in txt for team in ["india", "bangladesh", "pakistan", "australia", "england", "new zealand", "south africa", "sri lanka", "west indies", "afghanistan", "বাংলাদেশ", "ইন্ডিয়া", "পাকিস্তান"]):
                found = []
                for m in matches:
                    teams = " ".join(m.get("teams", [])).lower()
                    if any(word in teams for word in txt.split()):
                        found.append(m)
                if found:
                    reply += f"**{prompt} এর ম্যাচ:**\n\n"
                    for m in found:
                        reply += f"**{m.get('name')}**\n"
                        reply += f"{m.get('status')}\n"
                        reply += f"তারিখ: {m.get('date','')} | ভেন্যু: {m.get('venue','')}\n"
                        if m.get("score"):
                            for s in m["score"]:
                                reply += f"{s['inning']}: {s['r']}/{s['w']}\n"
                        reply += "\n"
                else:
                    reply += f"\"{prompt}\" এর কোনো ম্যাচ পাওয়া যায়নি\n"

            # ৪. কে জিতেছে?
            elif any(w in txt for w in ["কে জিতেছে", "who won", "winner", "জিতলো"]):
                completed = [m for m in matches if m.get("matchEnded") and "won" in m.get("status","").lower()]
                if completed:
                    reply += "**সাম্প্রতিক জয়ী দল:**\n\n"
                    for m in completed[-5:]:
                        reply += f"**{m.get('status')}** → {m.get('name')}\n"
                else:
                    reply += "সাম্প্রতিক কোনো ম্যাচ শেষ হয়নি\n"

            # ৫. ডিফল্ট – সব ম্যাচের লিস্ট
            else:
                reply += f"**সর্বশেষ ম্যাচ আপডেট:**\n\n"
                for m in matches[:7]:
                    reply += f"• {m.get('name')}\n   {m.get('status')}\n\n"

            reply += f"\n_আপডেট: {now.strftime('%I:%M %p')}_"
            st.markdown(reply, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})