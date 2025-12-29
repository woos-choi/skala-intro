# password.py
# 요구사항:
# - 알파벳, 숫자, 특수문자가 각각 1개 이상 포함
# - 최소 6자리 이상
# - 정규표현식 사용

import re

# 특수문자는 "문자/숫자/언더바"가 아닌 것(= \W) 또는 "_" 포함으로 처리
#  - \W: [^a-zA-Z0-9_]
#  - 여기에 "_"도 특수문자로 인정하려면 [_\W]로 검사
PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[_\W]).{6,}$")

def is_valid_password(pw: str) -> bool:
    return bool(PATTERN.match(pw))

def main():
    print("비밀번호를 입력하세요.")
    print("조건: 6자 이상, 알파벳/숫자/특수문자를 각각 1개 이상 포함")
    pw = input("> ")

    if is_valid_password(pw):
        print("✅ 사용 가능한 비밀번호입니다.")
    else:
        print("❌ 조건을 만족하지 않습니다.")
        # 상세 피드백(정규식으로 개별 확인)
        if len(pw) < 6:
            print("- 길이가 6자 이상이어야 합니다.")
        if not re.search(r"[A-Za-z]", pw):
            print("- 알파벳이 최소 1개 포함되어야 합니다.")
        if not re.search(r"\d", pw):
            print("- 숫자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"[_\W]", pw):
            print("- 특수문자가 최소 1개 포함되어야 합니다. (예: !@#$%^&* 등)")

if __name__ == "__main__":
    main()
