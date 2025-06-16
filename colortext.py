def color_text(text, color):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m"
    }
    color_code = colors.get(color.lower())
    if color_code:
        return f"{color_code}{text}\033[0m"
    else:
        return text  # 지원하지 않는 색이면 원본 텍스트 반환

# 사용 예시
print(color_text("이건 빨강입니다", "red"))
print(color_text("이건 초록입니다", "green"))
print(color_text("이건 노랑입니다", "yellow"))
print(color_text("이건 파랑입니다", "blue"))
print(color_text("이건 마젠타입니다", "magenta"))
print(color_text("이건 시안입니다", "cyan"))
