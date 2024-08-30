from template import create_court_page, load_config

config = load_config()

# 대회 타이틀 선택 (여기서는 첫 번째 타이틀을 사용)
tournament_title = config["tournament_titles"][0]

create_court_page(tournament_title, "중화", "A")
