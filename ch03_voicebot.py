# pip install audio_recorder_streamlit

##### 기본 정보 입력 #####
import streamlit as st
from audio_recorder_streamlit import audio_recorder as audiorecorder
import openai
import os
from datetime import datetime
import numpy as np
from gtts import gTTS
import base64

##### 기능 구현 함수 #####
def STT(audio):
    filename = 'input.mp3'
    with open(filename, "wb") as wav_file:
        wav_file.write(audio)
    # 사용할 Whisper 모델명을 넣어야합니다.
    # 예: transcript = openai.Audio.transcribe(model="whisper-1", audio=open(filename, "rb"))
    # 모델명은 OpenAI의 사용 가능한 모델 중에서 선택해야 합니다.
    transcript = openai.Audio.transcribe("whisper-1", open(filename, "rb"))
    os.remove(filename)
    return transcript["text"]

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model, messages=prompt)
    system_message = response["choices"][0]["message"]
    return system_message["content"]

def TTS(response):
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    os.remove(filename)

##### 메인 함수 #####
def main():
    st.set_page_config(page_title="최완석의 음성 비서 프로그램", layout="wide")
    flag_start = False

    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    st.header("음성 비서 프로그램")
    st.markdown("---")

    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write("""
        - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다.
        - 답변은 OpenAI의 GPT 모델을 활용했습니다.
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
        """)

    with st.sidebar:
        openai.api_key = st.text_input("OPENAI API 키", "", type="password")
        model = st.radio("GPT 모델", ["gpt-4", "gpt-3.5-turbo"])
        if st.button("초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")
        if audio is not None and st.session_state.get("check_audio") is not None:
            if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]):
                st.audio(audio)
                question = STT(audio)
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"].append(("user", now, question))
                st.session_state["messages"].append({"role": "user", "content": question})
                st.session_state["check_audio"] = audio
                flag_start = True

    with col2:
        st.subheader("질문/답변")
        if flag_start:
            response = ask_gpt(st.session_state["messages"], model)
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("bot", now, response))
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.markdown(
                        f'<div style="display:flex;align-items:center;">'
                        f'<div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div>'
                        f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;justify-content:flex-end;">'
                        f'<div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div>'
                        f'<div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True
                    )
            TTS(response)

if __name__ == "__main__":
    main()
