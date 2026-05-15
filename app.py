import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import streamlit.components.v1 as components
import mysql.connector

def save_to_database(original, corrected, error_type):
    db_pass = os.getenv("DB_PASSWORD")
    try:
        # 1. Nawiązanie połączenia
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=db_pass,
            database="language_assistant_db"
        )
        
        cursor = connection.cursor()
        
        # 2. Przygotowanie polecenia (używamy Twojego ID = 1)
        sql = """INSERT INTO conversation_logs (user_id, original_text, corrected_text, error_type) 
                 VALUES (%s, %s, %s, %s)"""
        values = (1, original, corrected, error_type)
        
        # 3. Wykonanie i zapisanie
        cursor.execute(sql, values)
        connection.commit()
        
        print("Successfully saved to database!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


MAX_CHARS = 300

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def copy_to_clipboard_button(text_to_copy):
    components.html(
        f"""
        <textarea id="text_to_copy" style="position:absolute; left:-9999px;">{text_to_copy}</textarea>
        <button onclick="
            const text = document.getElementById('text_to_copy');
            text.select();
            text.setSelectionRange(0, 99999);
            document.execCommand('copy');
            this.innerText='✅ Skopiowano!';
        " style="
            background-color:#262730;
            color:white;
            border:1px solid #4a4a4a;
            padding:10px 16px;
            border-radius:8px;
            cursor:pointer;
            font-size:16px;
        ">
            📋 Kopiuj wynik
        </button>
        """,
        height=60,
    )





st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 2.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 16px;
        padding: 14px;
        font-size: 1.05rem;
    }

    div[data-testid="stSelectbox"] > div {
        border-radius: 14px;
    }

    div[data-testid="stButton"] button {
        border-radius: 12px;
        padding: 0.55rem 1.1rem;
        font-weight: 600;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    .app-card {
        padding: 18px 20px;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        background: rgba(255,255,255,0.03);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.7rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        letter-spacing: -0.02em;
    }

    .muted-text {
        color: rgba(255,255,255,0.72);
        font-size: 0.98rem;
        line-height: 1.6;
    }

    div[data-testid="stExpander"] {
        border-radius: 16px !important;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
    }
</style>
""", unsafe_allow_html=True)


st.title("Language Assistant")

st.caption("AI assistant for translation and text improvement")

st.markdown(
    """
    <div class="app-card">
        <div class="muted-text">
            Translate text into different languages or improve its grammar and style using AI.
            Choose a mode, select a language, and enter your text.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if "history" not in st.session_state:
    st.session_state.history = []

mode = st.selectbox(
    "Select mode",
    ["Translation", "Text Improvement"]
)

explain = False

if mode == "Text Improvement":
    explain = st.checkbox("Explain corrections")

language = st.selectbox(
    "Select language",
    ["English", "Polish", "Spanish", "German", "Italian", "French", "Portuguese"]

)

st.divider()

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Input text</div>', unsafe_allow_html=True)
    text = st.text_area("Enter a sentence", label_visibility="visible")
    char_count = len(text)
    st.caption(f"{char_count} / {MAX_CHARS} characters")


def detect_language_with_ai(text):
    response = client.chat.completions.create(
        model = "gpt-4.1-mini",
        messages = [
            {
                "role": "system",
                "content": "Identify the language of the text. Return only one word (e.g., English, Polish, Spanish)."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content.strip()

st.markdown("")

col_btn1, col_btn2 = st.columns([1,4])

with col_btn1:
    submit = st.button("🚀 Submit")

if submit:
    if not text:
        st.warning("Enter a sentence first")
    elif len(text) > MAX_CHARS:
        st.error(f"Text is too long. Please enter up to {MAX_CHARS} characters.") 
    else:
        if mode == "Translation":
            prompt = f"""
            Translate the following text into {language}.
            Return only the translated text, without any additional comments.

            {text}
            """

        elif mode == "Text Improvement":
            detected_language = detect_language_with_ai(text)

            if detected_language.lower() != language.lower():
                st.error(
                    f"Detected language of the text is {detected_language}, but {language} was selected. "
                        "Please choose the correct language."
                )
                st.stop()

            if explain:
                prompt = f"""
                Correct the following text in {language}.
                Keep the same language.
                Do not translate it.
                Make it grammatically correct and natural.

                Then explain:
                - grammar corrections
                - vocabulary changes
                - tone improvements

                Keep the explanation simple and clear.

                Return in this format:

                Corrected text:
                ...

                Explanation:
                ...

                Text:
                {text}
                """
            else:
                prompt = f"""
                Correct the following text in {language}.
                Keep the same language.
                Do not translate it.
                Make it grammatically correct and natural.
                Return only the corrected text.

                Text:
                {text}
                """

        messages = [
            {"role": "system", "content": "You are a professional language assistant."},
            {"role": "user", "content": prompt}
        ]

        try:
            with st.spinner("Processing text..."):
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages
                )

                result = response.choices[0].message.content

                st.session_state.history.insert(0, {
                    "mode": mode,
                    "language": language,
                    "input": text,
                    "result": result,
                })

                #limit history to 5 items 
                st.session_state.history = st.session_state.history[:5]
        

        except Exception as e:
            st.error("An error occurred while processing the text.")
    
            st.exception(e)



with col2:
    if mode == "Translation":
        st.markdown('<div class="section-title">Translation</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-title">Corrected text</div>', unsafe_allow_html=True)

    if 'result' in locals():
        if mode == "Text correction" and explain:
            st.info(result)
        else:
            st.success(result)

        copy_to_clipboard_button(result)
            


st.markdown("---")

st.divider()

col_h1, col_h2 = st.columns([3,1])

with col_h1:
    st.subheader("History")
    st.caption("Your 5 most recent actions")

with col_h2:
    if st.button("🗑️ Clear History"):
        st.session_state.history = []


if not st.session_state.history:
    st.info("No history available. Enter text and click 'Submit' to see history here.")

else:
    for item in st.session_state.history:
        with st.expander(f"🌍{item['mode']} -> {item['language']}"):
            st.markdown(f"**Input Text:** {item['input']}")
            st.markdown(f"**Result:** {item['result']}")

        
# To jest testowe wywołanie - po uruchomieniu app.py dane powinny wpaść do bazy
save_to_database("I has a cat", "I have a cat", "Grammar")