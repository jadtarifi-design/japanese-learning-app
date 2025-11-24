import streamlit as st
import json
import os
import pykakasi

# --- Helper Functions ---

def levenshtein_distance(s1, s2):
    """
    Calculates the Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def generate_mock_data():
    """
    Generates a dummy database of Japanese words.
    """
    data = [
        {"id": 1, "word": "機会", "kana": "きかい", "meaning": "opportunity", "level": "N3", "rank": 500},
        {"id": 2, "word": "機械", "kana": "きかい", "meaning": "machine", "level": "N4", "rank": 600},
        {"id": 3, "word": "議会", "kana": "ぎかい", "meaning": "diet/congress", "level": "N3", "rank": 700},
        {"id": 4, "word": "理解", "kana": "りかい", "meaning": "understanding", "level": "N3", "rank": 200},
        {"id": 5, "word": "世界", "kana": "せかい", "meaning": "world", "level": "N5", "rank": 100},
        {"id": 6, "word": "正解", "kana": "せいかい", "meaning": "correct answer", "level": "N3", "rank": 800},
        {"id": 7, "word": "会社", "kana": "かいしゃ", "meaning": "company", "level": "N5", "rank": 150},
        {"id": 8, "word": "社会", "kana": "しゃかい", "meaning": "society", "level": "N4", "rank": 160},
        {"id": 9, "word": "社員", "kana": "しゃいん", "meaning": "company employee", "level": "N4", "rank": 300},
        {"id": 10, "word": "全員", "kana": "ぜんいん", "meaning": "all members", "level": "N4", "rank": 400},
        {"id": 11, "word": "安全", "kana": "あんぜん", "meaning": "safety", "level": "N4", "rank": 450},
        {"id": 12, "word": "完全", "kana": "かんぜん", "meaning": "perfect/complete", "level": "N3", "rank": 550},
        {"id": 13, "word": "学校", "kana": "がっこう", "meaning": "school", "level": "N5", "rank": 50},
        {"id": 14, "word": "格好", "kana": "かっこう", "meaning": "appearance/shape", "level": "N3", "rank": 900},
        {"id": 15, "word": "銀行", "kana": "ぎんこう", "meaning": "bank", "level": "N5", "rank": 250},
        {"id": 16, "word": "健康", "kana": "けんこう", "meaning": "health", "level": "N4", "rank": 350},
        {"id": 17, "word": "空港", "kana": "くうこう", "meaning": "airport", "level": "N4", "rank": 650},
        {"id": 18, "word": "高校", "kana": "こうこう", "meaning": "high school", "level": "N4", "rank": 220},
        {"id": 19, "word": "成功", "kana": "せいこう", "meaning": "success", "level": "N3", "rank": 750},
        {"id": 20, "word": "性格", "kana": "せいかく", "meaning": "personality", "level": "N3", "rank": 850},
        {"id": 21, "word": "生活", "kana": "せいかつ", "meaning": "daily life", "level": "N4", "rank": 180},
        {"id": 22, "word": "活動", "kana": "かつどう", "meaning": "activity", "level": "N3", "rank": 420},
        {"id": 23, "word": "動物", "kana": "どうぶつ", "meaning": "animal", "level": "N5", "rank": 320},
        {"id": 24, "word": "植物", "kana": "しょくぶつ", "meaning": "plant", "level": "N4", "rank": 950},
        {"id": 25, "word": "食事", "kana": "しょくじ", "meaning": "meal", "level": "N4", "rank": 280},
        {"id": 26, "word": "仕事", "kana": "しごと", "meaning": "work", "level": "N5", "rank": 120},
        {"id": 27, "word": "仕方", "kana": "しかた", "meaning": "method/way", "level": "N4", "rank": 520},
        {"id": 28, "word": "味方", "kana": "みかた", "meaning": "ally/supporter", "level": "N3", "rank": 920},
        {"id": 29, "word": "見方", "kana": "みかた", "meaning": "viewpoint", "level": "N3", "rank": 930},
        {"id": 30, "word": "先生", "kana": "せんせい", "meaning": "teacher", "level": "N5", "rank": 60},
    ]
    return data

def get_mock_sentences(word):
    """
    Mock function to fetch example sentences.
    """
    return [
        f"これは「{word}」を使った例文です。",
        f"「{word}」はとても重要です。",
        f"私は「{word}」が好きです。"
    ]

# --- Main Engine Class ---

class JapaneseLearningEngine:
    def __init__(self, master_list_path="master_vocab.json", user_state_path="user_state.json"):
        self.master_list_path = master_list_path
        self.user_state_path = user_state_path
        self.vocab_db = {} 
        self.user_state = {
            "studied_ids": [],
            "queue_ids": []
        }
        
        # Initialize pykakasi (New API)
        self.kks = pykakasi.kakasi()
        
        self.load_data()

    def load_data(self):
        # Load Master List
        if os.path.exists(self.master_list_path):
            with open(self.master_list_path, 'r', encoding='utf-8') as f:
                raw_list = json.load(f)
                self.vocab_db = {item['id']: item for item in raw_list}
        else:
            raw_list = generate_mock_data()
            self.vocab_db = {item['id']: item for item in raw_list}
            with open(self.master_list_path, 'w', encoding='utf-8') as f:
                json.dump(raw_list, f, ensure_ascii=False, indent=2)

        # Load User State
        if os.path.exists(self.user_state_path):
            with open(self.user_state_path, 'r', encoding='utf-8') as f:
                self.user_state = json.load(f)
        else:
            all_items = list(self.vocab_db.values())
            all_items.sort(key=lambda x: x['rank'])
            self.user_state["queue_ids"] = [item['id'] for item in all_items]
            self.user_state["studied_ids"] = []
            self.save_state()

    def save_state(self):
        with open(self.user_state_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_state, f, ensure_ascii=False, indent=2)

    def start_session(self, num_new_words=5):
        session_data = {
            "new_words": [],
            "contrastive_pairs": {}, 
            "root_suggestions": {}   
        }

        new_ids = self.user_state["queue_ids"][:num_new_words]
        
        if not new_ids:
            return session_data

        for nid in new_ids:
            new_word = self.vocab_db[nid]
            session_data["new_words"].append(new_word)

            # Contrastive
            contrasts = []
            for sid in self.user_state["studied_ids"]:
                studied_word = self.vocab_db[sid]
                dist = levenshtein_distance(new_word['kana'], studied_word['kana'])
                if dist <= 1:
                    contrasts.append(studied_word)
            
            if contrasts:
                session_data["contrastive_pairs"][nid] = contrasts

            # Roots
            roots = []
            chars = set(new_word['word'])
            for other_id, other_word in self.vocab_db.items():
                if other_id == nid: continue
                other_chars = set(other_word['word'])
                common = chars.intersection(other_chars)
                if common:
                    roots.append(other_word)
            
            if roots:
                session_data["root_suggestions"][nid] = roots[:3] 

        return session_data

    def commit_session(self, new_word_ids):
        self.user_state["queue_ids"] = [qid for qid in self.user_state["queue_ids"] if qid not in new_word_ids]
        current_studied = set(self.user_state["studied_ids"])
        for nid in new_word_ids:
            if nid not in current_studied:
                self.user_state["studied_ids"].append(nid)
        self.save_state()

    def transliterate(self, text):
        result = self.kks.convert(text)
        # Join with space for better readability
        return " ".join([item['hepburn'] for item in result])

# --- Streamlit App ---

def main():
    st.set_page_config(page_title="Japanese Vocab Engine", page_icon="🇯🇵")

    # Initialize Engine in Session State
    if 'engine' not in st.session_state:
        st.session_state['engine'] = JapaneseLearningEngine()
    
    engine = st.session_state['engine']

    # Title & Stats
    st.title("🇯🇵 Vocab Expansion")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queue", len(engine.user_state['queue_ids']))
    with col2:
        st.metric("Studied", len(engine.user_state['studied_ids']))

    st.divider()

    # Session State Management
    if 'current_session' not in st.session_state:
        st.session_state['current_session'] = None

    # Start Button
    if st.session_state['current_session'] is None:
        if st.button("Start Daily Session", type="primary", use_container_width=True):
            session = engine.start_session(num_new_words=5)
            if not session["new_words"]:
                st.info("No more words to learn!")
            else:
                st.session_state['current_session'] = session
                st.rerun()

    # Active Session Display
    else:
        session = st.session_state['current_session']
        
        st.subheader("Today's Words")
        
        for word in session["new_words"]:
            with st.container(border=True):
                # Header: Word + Kana
                st.markdown(f"## {word['word']} <span style='font-size:0.6em; color:gray'>({word['kana']})</span>", unsafe_allow_html=True)
                
                # Meaning & Meta
                st.markdown(f"**Meaning:** {word['meaning']}")
                st.caption(f"Level: {word['level']} | Rank: {word['rank']}")
                
                # Sentences
                st.markdown("---")
                st.markdown("**Example Sentences:**")
                sentences = get_mock_sentences(word['word'])
                for s in sentences:
                    romaji = engine.transliterate(s)
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <div style="font-size: 1.1em; font-weight: 500; color: #1f1f1f;">{s}</div>
                        <div style="color: #666; font-size: 0.9em; margin-top: 4px;">{romaji}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Contrastive Warning
                if word['id'] in session["contrastive_pairs"]:
                    st.warning("⚠️ **Phonetic Contrast Warning**")
                    st.markdown("Distinguish from these known words:")
                    for c_word in session["contrastive_pairs"][word['id']]:
                        st.markdown(f"- **{c_word['word']}** ({c_word['kana']}): {c_word['meaning']}")

                # Roots Expander
                if word['id'] in session["root_suggestions"]:
                    with st.expander("🌱 Morphological Roots (Shared Kanji)"):
                        for r_word in session["root_suggestions"][word['id']]:
                            st.markdown(f"- **{r_word['word']}** ({r_word['kana']}): {r_word['meaning']}")

        st.divider()
        
        # Finish Button
        if st.button("Finish Day & Commit", type="primary", use_container_width=True):
            ids_to_commit = [w['id'] for w in session["new_words"]]
            engine.commit_session(ids_to_commit)
            st.session_state['current_session'] = None
            st.success(f"Great job! {len(ids_to_commit)} words added to studied list.")
            st.rerun()

    # Sidebar for Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        st.write("Manage your learning progress.")
        
        if st.button("Reset All Progress", type="secondary", help="This will delete your history and start over."):
            if os.path.exists(engine.user_state_path):
                os.remove(engine.user_state_path)
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()
