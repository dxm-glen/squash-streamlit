### 공식 토너먼트 대회 템플릿

import streamlit as st
import sqlite3
import os
from datetime import datetime
import pytz
import yaml


# 설정 파일 로드
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()

# 데이터베이스 설정
DB_FOLDER = "db"
DB_FILE = "db.sqlite"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE)

# 서울 시간대 설정
seoul_tz = pytz.timezone("Asia/Seoul")


# 데이터베이스 연결 및 테이블 생성 함수
def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS matches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tournament_title TEXT,
                  place TEXT,
                  court TEXT,
                  round_type TEXT,
                  gender TEXT,
                  match_type TEXT,
                  player1 TEXT,
                  player2 TEXT,
                  score1 INTEGER,
                  score2 INTEGER,
                  date TEXT,
                  status TEXT)"""
    )
    conn.commit()
    conn.close()


def register_match(
    tournament_title, place, court, round_type, gender, match_type, player1, player2
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO matches (tournament_title, place, court, round_type, gender, match_type, player1, player2, date, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            tournament_title,
            place,
            court,
            round_type,
            gender,
            match_type,
            player1,
            player2,
            datetime.now(seoul_tz).strftime("%Y-%m-%d %H:%M:%S"),
            "pending",
        ),
    )
    conn.commit()
    conn.close()


def get_pending_matches(tournament_title, place, court):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT id, round_type, gender, match_type, player1, player2 
                 FROM matches 
                 WHERE tournament_title = ? AND place = ? AND court = ? AND status = 'pending'
                 ORDER BY date""",
        (tournament_title, place, court),
    )
    matches = c.fetchall()
    conn.close()
    return matches


def input_result(match_id, score1, score2):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """UPDATE matches 
                 SET score1 = ?, score2 = ?, status = 'finished' 
                 WHERE id = ?""",
        (score1, score2, match_id),
    )
    conn.commit()
    conn.close()


def delete_match(match_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()


def update_match(match_id, round_type, gender, match_type, player1, player2):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """UPDATE matches 
                 SET round_type = ?, gender = ?, match_type = ?, player1 = ?, player2 = ? 
                 WHERE id = ?""",
        (round_type, gender, match_type, player1, player2, match_id),
    )
    conn.commit()
    conn.close()


def get_match_info(match_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT round_type, gender, match_type, player1, player2 
                 FROM matches 
                 WHERE id = ?""",
        (match_id,),
    )
    match = c.fetchone()
    conn.close()
    return {
        "round_type": match[0],
        "gender": match[1],
        "match_type": match[2],
        "player1": match[3],
        "player2": match[4],
    }


def create_court_page(tournament_title, place, court):
    # 페이지 설정
    st.set_page_config(
        page_title=f"{tournament_title} - {place} {court} 코트",
        page_icon="👋",
    )

    # 데이터베이스 초기화
    init_db()

    st.header(f"_{tournament_title}_", divider="rainbow")
    st.subheader(f"{place}스쿼시 :blue[{court} 코트] :sunglasses:", divider="rainbow")

    # 관리자 모드 확인
    is_admin = st.session_state.get("admin_mode", False)

    if is_admin:
        # 정보 수정 다이얼로그
        @st.dialog("매치 정보 수정")
        def edit_match_info(match_id):
            match_info = get_match_info(match_id)

            edited_round_type = st.selectbox(
                "라운드",
                config["round_types"],
                index=config["round_types"].index(match_info["round_type"]),
                key=f"edit_round_type_{match_id}",
            )
            edited_gender = st.selectbox(
                "성별",
                config["genders"],
                index=config["genders"].index(match_info["gender"]),
                key=f"edit_gender_{match_id}",
            )
            edited_match_type = st.selectbox(
                "타입 선택",
                config["match_types"],
                index=config["match_types"].index(match_info["match_type"]),
                key=f"edit_match_type_{match_id}",
            )
            edited_player1 = st.text_input(
                "선수1 이름",
                value=match_info["player1"],
                key=f"edit_player1_{match_id}",
            )
            edited_player2 = st.text_input(
                "선수2 이름",
                value=match_info["player2"],
                key=f"edit_player2_{match_id}",
            )

            _, col1, col2 = st.columns([4, 1, 1])
            with col1:
                if st.button("취소", type="secondary", key=f"edit_cancel_{match_id}"):
                    st.rerun()
            with col2:
                if st.button("수정", type="primary", key=f"edit_confirm_{match_id}"):
                    update_match(
                        match_id,
                        edited_round_type,
                        edited_gender,
                        edited_match_type,
                        edited_player1,
                        edited_player2,
                    )
                    st.toast("매치 정보가 수정되었습니다.")
                    st.rerun()

        # 결과 입력 다이얼로그
        @st.dialog("결과 입력")
        def input_result_dialog(match_id):
            match_info = get_match_info(match_id)
            st.subheader(f"{match_info['player1']} VS {match_info['player2']}")

            col1, col2 = st.columns(2)
            with col1:
                score1 = st.number_input(
                    f"{match_info['player1']} 점수",
                    min_value=0,
                    max_value=21,
                    step=1,
                    key=f"score1_{match_id}",
                )
            with col2:
                score2 = st.number_input(
                    f"{match_info['player2']} 점수",
                    min_value=0,
                    max_value=21,
                    step=1,
                    key=f"score2_{match_id}",
                )

            if st.button("결과 저장", type="primary", key=f"save_result_{match_id}"):
                input_result(match_id, score1, score2)
                st.toast("결과가 저장되었습니다.")
                st.rerun()

        # 입력 섹션
        st.subheader("매치 정보 입력")

        col1, col2, col3 = st.columns(3)

        with col1:
            round_type = st.selectbox(
                "매치", config["round_types"], key="input_round_type"
            )
        with col2:
            gender = st.selectbox("성별", config["genders"], key="input_gender")
        with col3:
            match_type = st.selectbox(
                "타입 선택", config["match_types"], key="input_match_type"
            )

        col1, col2 = st.columns(2)
        with col1:
            player1 = st.text_input("선수1 이름", key="input_player1")
        with col2:
            player2 = st.text_input("선수2 이름", key="input_player2")

        _, _, col3 = st.columns([5, 1, 1])
        with col3:
            if st.button("매치 등록", type="primary", key="register_match"):
                if player1 and player2:
                    register_match(
                        tournament_title,
                        place,
                        court,
                        round_type,
                        gender,
                        match_type,
                        player1,
                        player2,
                    )
                    st.toast("매치 추가 완료.")
                    st.rerun()
                else:
                    st.toast("플레이어 이름을 모두 입력해주세요.")

    # 대기열 표시
    pending_matches = get_pending_matches(tournament_title, place, court)
    if pending_matches:
        st.markdown("---")
        for idx, match in enumerate(pending_matches):
            match_id, round_type, gender, match_type, player1, player2 = match
            coll, _, colr = st.columns([2, 3, 5])
            with coll:
                st.markdown(f"### 매치 {idx+1}")
            with colr:
                st.markdown(f"### **{round_type}** | **{gender}** | **{match_type}**")

            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(f"### {player1}")
            with col2:
                st.markdown("## VS")
            with col3:
                st.markdown(f"### {player2}")

            if is_admin:
                col1, col2, col3, col4 = st.columns([2, 2, 5, 2])
                with col1:
                    if st.button(
                        "정보 수정", key=f"update_input_{match_id}", type="secondary"
                    ):
                        edit_match_info(match_id)
                with col2:
                    if st.button(
                        "삭제", key=f"delete_match_{match_id}", type="secondary"
                    ):
                        delete_match(match_id)
                        st.rerun()
                with col4:
                    if st.button(
                        "결과 입력", key=f"result_input_{match_id}", type="primary"
                    ):
                        input_result_dialog(match_id)

            st.markdown("---")
    else:
        st.info("현재 등록된 매치가 없습니다.")

    if not is_admin:
        st.warning("매치 정보 입력 및 관리는 관리자 모드에서만 가능합니다.")
