# 설명은 개념/4단계_제너레이터_연결하기.md
def read_temps(path):
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.strip() == '':
                continue          
            a = float(line)
            yield a

def hot_days(temps, limit):
    for i in temps:
        if i >= limit:
            yield i

def first_n(temps, n):
    a = 0
    for i in temps:
        if a >= n:
            return 
        yield i
        a+=1

if __name__ == "__main__":
    print("python3 채점.py 종합 으로 확인하세요")
