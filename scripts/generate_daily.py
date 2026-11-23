#!/usr/bin/env python3
"""매일 KST 날짜의 한국어 비문학 독해 시험을 생성하여 정적 JSON 파일로 저장.
GitHub Actions에서 실행. API 키는 Actions Secrets만 사용하고 웹 페이지에 노출하지 않음.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parents[1]
DAY=dt.datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
TARGET=ROOT/'data'/'daily'/f'{DAY}.json'
KEY=os.getenv('OPENAI_API_KEY','').strip()
MODEL=os.getenv('OPENAI_MODEL','gpt-4o').strip()
CATEGORIES=[
 '언어학·의미 변화','경제·게임 이론','물리학·에너지','생명과학·진화','윤리학·공정성',
 '법과 사회 제도','역사학·사료 비판','현대 철학·인식론','예술·미학','정보 과학·압축',
 '통계학·인과 추론','환경·생태계','도시 계획·교통','지구 과학·기후','인지 심리·기억',
 '정치철학·숙의','공공 정책·평가','금융·할인율','천문학·관측','과학 방법론',
 '문화 인류학·의례','문학 이론·독서','재료 과학·반도체','의사 결정·위험 분석',
 '기술 윤리·AI','의학 통계·검사','지리·지도 해석','교육·학습 과학'
]

def schema():
    q={"type":"object","additionalProperties":False,"required":["type","q","options","correct","explain"],"properties":{
      "type":{"type":"string"},"q":{"type":"string"},"options":{"type":"array","items":{"type":"string"}},
      "correct":{"type":"integer"},"explain":{"type":"string"}
    }}
    return {"type":"object","additionalProperties":False,"required":["category","title","passage","questions"],"properties":{
      "category":{"type":"string"},"title":{"type":"string"},"passage":{"type":"string"},
      "questions":{"type":"array","items":q}
    }}

def check(data):
    if not isinstance(data,dict) or not all(k in data for k in ['title','category','passage','questions']):raise ValueError('필수 필드 누락')
    passages=[p.strip() for p in data['passage'].split('\n\n') if p.strip()]
    length=len(''.join(c for c in data['passage'] if not c.isspace()))
    if not 3<=len(passages)<=5 or not 720<=length<=2000:raise ValueError(f'지문 분량/문단 수 확인 필요: {length}자, {len(passages)}문단')
    if not isinstance(data['questions'],list) or len(data['questions'])!=5:raise ValueError('문항 5개 필요')
    prompts=set()
    for i,q in enumerate(data['questions']):
        if not isinstance(q.get('q'),str) or len(q['q'].strip())<10:raise ValueError(f'{i+1}번 질문 너무 짧음')
        if q['q'] in prompts:raise ValueError('중복 질문')
        prompts.add(q['q'])
        opts=q.get('options');ans=q.get('correct')
        if not isinstance(opts,list) or len(opts)!=5 or len(set(opts))!=5:raise ValueError(f'{i+1}번 선택지 오류')
        if any(not isinstance(o,str) or len(o.strip())<5 for o in opts):raise ValueError(f'{i+1}번 선택지 분량 부족')
        if type(ans)!=int or not(0<=ans<=4):raise ValueError(f'{i+1}번 정답 인덱스 오류')
        if len(q.get('explain',''))<25:raise ValueError(f'{i+1}번 해설 분량 부족')
    return data

def request(prompt):
    payload={
       'model':MODEL,
       'instructions': '당신은 한국어 수능 국어 독서/비문학 전문 출제자다. 문제는 실제 시험 문제와 지문을 복제하지 않고 새롭게 창작한다. 다섯 문제에는 각각 논리적으로 유일한 정답이 있어야 한다. 오답도 그럴듯하되 글로 반박 가능해야 한다. JSON 스키마를 엄격히 따른다.',
       'input':prompt,
       'text':{'format':{'type':'json_schema','name':'daily_reading_exam','strict':True,'schema':schema()}},
       'max_output_tokens':5500,
       'store':False,
    }
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),headers={'Authorization':f'Bearer {KEY}','Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=100) as res:response=json.load(res)
    parts=[]
    for item in response.get('output',[]):
        if item.get('type')=='message':
            for c in item.get('content',[]):
                if c.get('type')=='output_text':parts.append(c.get('text',''))
    if not parts:raise ValueError(f'응답 본문 누락: {response.get("status")}')
    return json.loads(''.join(parts))

def main():
    if TARGET.exists():
        print('기존 일일 시험이 이미 있습니다:',TARGET.relative_to(ROOT));return
    if not KEY:
        raise SystemExit('OPENAI_API_KEY secret이 없습니다. GitHub Settings → Secrets and variables → Actions에서 추가해 주세요.')
    start=dt.date(2026,11,23)
    ix=(dt.date.fromisoformat(DAY)-start).days % len(CATEGORIES)
    recent=[]
    for f in sorted((ROOT/'data'/'daily').glob('*.json'))[-20:]:
        try:recent.append(json.loads(f.read_text(encoding='utf8'))['title'])
        except (KeyError,ValueError):pass
    prompt=f'''오늘은 {DAY} (한국 시간)이다.
주제 영역: {CATEGORIES[ix]}. 최근 출제 제목: {', '.join(recent) or '없음'}.
이전 제목과 관점이 다른, 독창적인 고급 독서 지문 1편과 객관식 5문항을 JSON으로 만들어라.
지문 조건: 띄어쓰기 제외 한국어 약 900~1250자(최소 720자); 4~5개 문단을 빈 줄(\\n\\n)로 분리하라. 개념 정의→원리 설명→구체적 적용 또는 반례→한계·종합적 판단을 갖춘 논증형 글로 작성하라. 필요하면 현실과 혼동하지 않도록 가상 사례임을 명시하라. 모호하거나 논쟁적인 사실을 단정하지 말라.
문항 조건: 'type'을 내용 일치, 중심 주장, 추론, 조건·수리 적용, 논증 평가, 반론·한계, 개념 비교 등에서 다양하게 구성하되 5문항의 사고 영역이 최대한 중복되지 않도록 하라. 5지선다, 정답 인덱스는 0~4, 정답 위치를 고르게 분배하라. 지문을 읽어야 풀 수 있도록 지문 속 구체적 조건·개념을 활용하라. 오답은 분명히 틀리지만 과도하게 엉뚱하지 않게 작성하라. 해설은 한국어 2~3문장으로 정답의 근거와 대표 오답의 논리적 한계를 설명하라. 오류 없는 JSON만 출력하라.'''
    for attempt in range(1,4):
        try:
            exam=check(request(prompt))
            if exam['title'] in recent:raise ValueError('최근 제목 중복')
            TARGET.parent.mkdir(parents=True,exist_ok=True)
            TARGET.write_text(json.dumps(exam,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            print(f'Created {TARGET.relative_to(ROOT)}; {len(exam["passage"])} chars, 5 questions')
            return
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,json.JSONDecodeError) as exc:
            if isinstance(exc,urllib.error.HTTPError):
                print('API 에러 코드:',exc.code,'본문:',exc.read().decode('utf-8','replace')[:1200],file=sys.stderr)
                if exc.code in (400,401,403,429):raise
            print(f'생성 시도 {attempt}/3 실패: {exc}',file=sys.stderr)
            prompt+=' 이전 응답이 형식이나 난이도 조건을 충족하지 못했으므로 요구 조건을 더 엄격하게 지키라.'
            if attempt<3:time.sleep(attempt*3)
    raise SystemExit('시험 생성에 실패했습니다. Actions에서 다시 실행해 주세요.')

if __name__=='__main__':main()
