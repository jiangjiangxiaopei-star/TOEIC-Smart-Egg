import streamlit as st
import json
import random
import time
import re

# 页面基本设置
st.set_page_config(page_title="蒋蒋的聪明蛋 Web", page_icon="🥚")

# 强制加载数据的函数
def load_data():
    try:
        with open('toeic_words.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"找不到数据文件: {e}")
        return {"阅读笔记": {}, "听力笔记": {}}

# 初始化网页的“记忆能力”
if 'stage' not in st.session_state:
    st.session_state.stage = "menu"
if 'words' not in st.session_state:
    st.session_state.words = []
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'wrongs' not in st.session_state:
    st.session_state.wrongs = []

data = load_data()

# --- 界面逻辑 ---
if st.session_state.stage == "menu":
    st.title("🥚 聪明蛋大挑战 Web")
    cat = st.selectbox("选择类别", list(data.keys()))
    test = st.selectbox("选择关卡", list(data[cat].keys()))
    
    if st.button("开始挑战！", use_container_width=True):
        st.session_state.words = data[cat][test].copy()
        random.shuffle(st.session_state.words)
        st.session_state.idx = 0
        st.session_state.wrongs = []
        st.session_state.stage = "quiz"
        st.rerun()

elif st.session_state.stage == "quiz":
    words = st.session_state.words
    i = st.session_state.idx
    
    if i < len(words):
        item = words[i]
        st.write(f"### 第 {i+1} / {len(words)} 个")
        
        # 网页发音脚本
        st.components.v1.html(f"""
            <script>
            var u = new SpeechSynthesisUtterance('{item['word']}');
            u.lang = 'en-US';
            window.speechSynthesis.speak(u);
            </script>
        """, height=0)
        
        user_ans = st.text_input("中文意思是什么？", key=f"q_{i}")
        
        if st.button("提交", use_container_width=True):
            clean = re.sub(r'\(.*?\)', '', item['translation']).strip()
            parts = re.split(r'[，,；;/、 ]', clean)
            if user_ans and any(user_ans in p or p in user_ans for p in parts if p.strip()):
                st.success(f"✨ 对啦！ {item['translation']}")
                time.sleep(1)
            else:
                st.error(f"⛽️ 加油！ 答案是：{item['translation']}")
                st.session_state.wrongs.append(item)
                time.sleep(2)
            
            st.session_state.idx += 1
            st.rerun()
    else:
        if not st.session_state.wrongs:
            st.balloons()
            st.success("🎉 太棒了蒋蒋！全部通关！")
            if st.button("回目录"):
                st.session_state.stage = "menu"
                st.rerun()
        else:
            st.session_state.stage = "retry"
            st.rerun()

elif st.session_state.stage == "retry":
    count = len(st.session_state.wrongs)
    st.markdown(f"## 💪 我们还有 <span style='color:red'>{count}</span> 个没记牢", unsafe_allow_html=True)
    st.header("再来一次！")
    time.sleep(2.5)
    st.session_state.words = st.session_state.wrongs.copy()
    random.shuffle(st.session_state.words)
    st.session_state.wrongs = []
    st.session_state.idx = 0
    st.session_state.stage = "quiz"
    st.rerun()