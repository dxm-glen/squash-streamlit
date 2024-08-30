import streamlit as st
from template2 import create_unofficial_group_page

# config에서 그룹 이름 가져오기
group_name = "중화랭킹전"

# 페이지 생성
create_unofficial_group_page(group_name)
