# 설명은 개념/3단계_CSV_쓰기.md
import csv
import json
def jsonl_to_csv(jsonl_path, csv_path, fields):
    with open(jsonl_path, encoding="utf-8") as file_j, open(csv_path,"w", encoding="utf-8-sig", newline="") as file_c:   # 두 파일을 한 번에
       
        # writer 만들기
        writer = csv.writer(file_c)
        
        # 헤더(fields) 한 번 쓰기          ← fields는 이미 리스트, 그대로 writerow
        writer.writerow(fields)
        
        cnt = 0
        for line in file_j:
            # 빈 줄 건너뛰기
            if line.strip()=='':
                continue
            
            # record = 한 줄을 딕셔너리로
            a = json.loads(line)
            
            # values = fields 순서대로 record에서 값 꺼내 담기   ← 앞의 student 예시
            values = []
            for key in fields:
                values.append(a[key])
            # values를 한 줄로 쓰기
            writer.writerow( values )

            cnt += 1
    return cnt                               # 다 끝난 뒤 한 번

if __name__ == "__main__":
    from pathlib import Path
    data = Path(__file__).resolve().parent.parent / "예시자료"
    import tempfile
    out = Path(tempfile.mkdtemp()) / "영화.csv"
    print(jsonl_to_csv(data / "영화.jsonl", out, ["title", "score"]), "건")
    print(out.read_text(encoding="utf-8-sig"))
