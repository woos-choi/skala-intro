# echo.py
import re
from password import is_valid_password

def main():
    print("echo 프로그램입니다.")
    print("- 문장을 입력하면 그대로 출력합니다.")
    print("- 종료: !quit")
    print("- 비밀번호 검사: !pw <비밀번호>  (예: !pw Abc!123)")
    print()

    while True:
        s = input("> ").rstrip("\n")

        if s == "!quit":
            print("프로그램을 종료합니다.")
            break

        m = re.match(r"^!pw\s+(.+)$", s)
        if m:
            pw = m.group(1)
            if is_valid_password(pw):
                print("✅ 비밀번호 조건 통과")
            else:
                print("❌ 비밀번호 조건 불만족 (6자 이상 + 알파벳/숫자/특수문자 각각 1개 이상)")
            continue

        print(s)

if __name__ == "__main__":
    main()
