# 설명은 개념/1단계_yield와_next.md
def colors():
    yield "빨강"
    yield "노랑"
    yield "파랑"



if __name__ == "__main__":
    for color in colors():
        print(color)
