# Python 3: 문장을 반복 입력/출력, !quit 입력 시 종료

while True:
    s = input("문장을 입력하세요(!quit을 입력 시 종료) : ")
    if s == "!quit":
        print("프로그램을 종료합니다.")
        break
    print(s)
