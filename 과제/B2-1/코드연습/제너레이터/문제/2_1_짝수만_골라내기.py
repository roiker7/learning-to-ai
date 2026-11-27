# 설명은 개념/2단계_필요한_만큼만_꺼내기.md
def evens(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n
    


if __name__ == "__main__":
    for number in evens([1, 2, 3, 4]):
        print(number)
