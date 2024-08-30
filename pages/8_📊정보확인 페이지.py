import streamlit as st
import sqlite3
import pandas as pd
import os

# 데이터베이스 설정
DB_FOLDER = "db"
DB_FILE = "db.sqlite"
DB_PATH = os.path.join(DB_FOLDER, DB_FILE)

# 페이지 설정
st.set_page_config(page_title="스쿼시 토너먼트 - 통계", page_icon="📊", layout="wide")


# 데이터베이스에서 데이터 가져오기
@st.cache_data(ttl=60)  # 1분마다 자동으로 캐시 무효화
def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM matches WHERE status = 'finished'"  # 완료된 매치만 선택
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])

    # 컬럼 순서 변경
    columns_order = [
        "player1",
        "score1",
        "score2",
        "player2",
        "round_type",
        "gender",
        "match_type",
        "place",
        "court",
        "tournament_title",
        "date",
        "id",
        "status",
    ]
    df = df[columns_order]

    return df


# 데이터 로드
df = load_data()

st.title("데이터 확인 페이지")

# 새로고침 버튼
if st.button("데이터 새로고침", type="primary"):
    st.cache_data.clear()
    st.rerun()


# 필터 옵션
def filter_options():
    col1, col2, col3 = st.columns(3)

    with col1:
        player_name = st.text_input("선수 이름 검색")
        selected_gender = st.selectbox(
            "성별", ["전체"] + df["gender"].unique().tolist()
        )

    with col2:
        selected_place = st.selectbox("장소", ["전체"] + df["place"].unique().tolist())
        selected_court = st.selectbox("코트", ["전체"] + df["court"].unique().tolist())

    with col3:
        selected_match_type = st.selectbox(
            "매치 타입", ["전체"] + df["match_type"].unique().tolist()
        )
        selected_round = st.selectbox(
            "라운드", ["전체"] + df["round_type"].unique().tolist()
        )

    return (
        selected_place,
        selected_court,
        selected_round,
        selected_gender,
        selected_match_type,
        player_name,
    )


# 데이터 필터링 및 표시
def display_filtered_data(
    selected_place,
    selected_court,
    selected_round,
    selected_gender,
    selected_match_type,
    player_name,
):
    filtered_df = df.copy()
    if selected_place != "전체":
        filtered_df = filtered_df[filtered_df["place"] == selected_place]
    if selected_court != "전체":
        filtered_df = filtered_df[filtered_df["court"] == selected_court]
    if selected_round != "전체":
        filtered_df = filtered_df[filtered_df["round_type"] == selected_round]
    if selected_gender != "전체":
        filtered_df = filtered_df[filtered_df["gender"] == selected_gender]
    if selected_match_type != "전체":
        filtered_df = filtered_df[filtered_df["match_type"] == selected_match_type]
    if player_name:
        filtered_df = filtered_df[
            (filtered_df["player1"].str.contains(player_name, case=False))
            | (filtered_df["player2"].str.contains(player_name, case=False))
        ]

    st.header("데이터")
    st.dataframe(filtered_df)


# 탭 생성
tab1, tab2 = st.tabs(["검색 정보", "상세 데이터"])

with tab1:
    st.header("필터 옵션")
    filter_values = filter_options()

    # 검색 버튼
    if st.button("검색", type="primary"):
        display_filtered_data(*filter_values)

with tab2:
    st.header("전체 데이터")
    st.dataframe(df)
