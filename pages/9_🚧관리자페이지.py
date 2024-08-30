import streamlit as st
import sqlite3
import pandas as pd
import os
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

# 페이지 설정
st.set_page_config(page_title="데이터베이스 관리", page_icon="🛠️", layout="wide")


# 비밀번호 확인 함수
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        password = st.text_input(
            "데이터베이스 관리자 비밀번호를 입력하세요", type="password"
        )
        if st.button("확인"):
            if password == config["db_admin_password"]:
                st.session_state.password_correct = True
                st.success(
                    "비밀번호가 확인되었습니다. 데이터베이스 관리 기능을 사용할 수 있습니다."
                )
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True


# 데이터베이스 연결 함수
def connect_db():
    return sqlite3.connect(DB_PATH)


# 테이블 목록 가져오기
def get_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]


# 테이블 데이터 가져오기
def get_table_data(table_name):
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


# 데이터 수정 함수
def update_data(table_name, updated_df):
    conn = connect_db()
    cursor = conn.cursor()

    # 기존 데이터 삭제
    cursor.execute(f"DELETE FROM {table_name}")

    # 새 데이터 삽입
    updated_df.to_sql(table_name, conn, if_exists="append", index=False)

    conn.commit()
    conn.close()


# ID로 데이터 삭제 함수
def delete_by_id(table_name, id_to_delete):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (id_to_delete,))
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_rows


# 메인 앱
def main():
    st.title("데이터베이스 관리")

    if check_password():
        tables = get_tables()
        selected_table = st.selectbox("테이블 선택", tables)

        if selected_table:
            st.subheader(f"{selected_table} 테이블 데이터")
            df = get_table_data(selected_table)

            # 데이터 편집
            edited_df = st.data_editor(df)

            if st.button("변경사항 저장"):
                update_data(selected_table, edited_df)
                st.success("데이터가 성공적으로 업데이트되었습니다.")

            # ID로 데이터 삭제
            st.subheader("ID로 데이터 삭제")
            id_to_delete = st.number_input(
                "삭제할 데이터의 ID를 입력하세요", min_value=1, step=1
            )
            delete_confirmation = st.checkbox(
                f"ID {id_to_delete}의 데이터를 삭제하시겠습니까?"
            )

            if delete_confirmation:
                if st.button("선택한 ID의 데이터 삭제", key="delete_by_id"):
                    deleted_rows = delete_by_id(selected_table, id_to_delete)
                    if deleted_rows > 0:
                        st.success(
                            f"ID {id_to_delete}의 데이터가 성공적으로 삭제되었습니다."
                        )
                    else:
                        st.warning(f"ID {id_to_delete}에 해당하는 데이터가 없습니다.")
                    st.rerun()

            # 데이터 삭제 기능
            st.subheader("모든 데이터 삭제")
            delete_all_confirmation = st.checkbox("모든 데이터를 삭제하시겠습니까?")

            if delete_all_confirmation:
                if st.button(
                    "선택한 테이블의 모든 데이터 삭제",
                    type="secondary",
                    key="delete_all",
                ):
                    conn = connect_db()
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM {selected_table}")
                    conn.commit()
                    conn.close()
                    st.success(
                        f"{selected_table} 테이블의 모든 데이터가 삭제되었습니다."
                    )
                    st.rerun()


if __name__ == "__main__":
    main()
