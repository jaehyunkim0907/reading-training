# 매일 비문학 문해력 훈련 (GitHub Pages)

- 28개 완전 독창적 비문학 독서 지문 (3문단 이상, 약 740~850자) 및 5지선다 140문항 내장
- 긴 지문을 읽고 5문제를 **전부 푼 뒤 제출하여 한꺼번에 채점**, 100점 만점/해설
- 매일 KST 날짜에 맞춰 다른 문제은행 글 자동 배정, 동일 날짜 재방문 시 학습 기록 유지
- [선택] OpenAI API + GitHub Actions 설정 시 **매일 새로운 4~5문단/900~1250자 수준의 지문과 문제를 실제 생성**, HTML은 생성된 JSON을 자동 표시
- HTML에 API 키를 넣지 않음. 학습 기록은 브라우저 localStorage에 저장.

## 빠른 교체 (API 키 없이 무료 시작)

1. 저장소 `jaehyunkim0907/reading-training`의 기존 `index.html`을 이 압축파일의 `index.html`로 **교체하여 Commit**합니다.
2. `https://jaehyunkim0907.github.io/reading-training/`을 새로고침합니다. 캐시가 남으면 `Ctrl+F5`.
3. 이 단계만으로 28개 주제의 장문 독해 시험이 날짜별로 자동 배정되고, **제출 후 채점**됩니다. 고정 문제은행이므로 29일 후에는 주제가 재순환됩니다.

## 진짜 매일 AI 신규 출제까지 설정하기

1. 다음 파일도 저장소의 동일한 상대 경로에 추가합니다.
   - `.github/workflows/daily-reading.yml`
   - `scripts/generate_daily.py`
   - `data/daily/.gitkeep` (빈 폴더를 위한 자리표시자, 선택)
2. [OpenAI 플랫폼](https://platform.openai.com/api-keys)에서 **API 키를 생성**합니다. ChatGPT 구독료와 별도의 API 사용 요금이 발생할 수 있습니다.
3. GitHub 저장소에서 `Settings → Secrets and variables → Actions → New repository secret`을 눌러 **Name: `OPENAI_API_KEY`** 로 키를 추가합니다. HTML 파일, README, 채팅, Git 커밋에 키를 올리지 마세요.
4. `Settings → Pages → Source`를 `GitHub Actions`로 변경합니다. *(기존 `Deploy from a branch`에서 변경해야 같은 작업 내 신규 출제/배포가 보장됩니다.)*
5. `Actions → Daily Reading Exam and GitHub Pages → Run workflow`를 **처음 한 번 수동 실행**합니다. 초록색 체크로 완료되는지 확인합니다.
6. 이후 기본 설정상 매일 **한국 시간 오전 5:17**에 실행되어 오늘 날짜의 신규 지문 JSON을 만들고 Pages를 다시 배포합니다. GitHub 자체 일정 실행에는 지연·누락이 있을 수 있으며, 작업이 실패하면 사이트는 내장 문제은행으로 동작합니다.

## 주의사항

- EBS의 기존 지문과 문항을 가져오거나 복제하지 않았습니다. EBS 링크는 웹 환경에서 직접 내용을 확인할 수 없어 일반적 독서 평가 유형을 참고하여 자체 제작했습니다.
- AI 출제는 구조 검증(문단 수, 글자 수, 문제/선택지 수 등)을 거치지만 **논리적 정확성은 완전히 보장되지 않습니다.** 중요한 교육 콘텐츠는 정답과 해설을 검토해 주세요.
- GitHub public 저장소의 `data/daily/*.json`은 누구나 볼 수 있으므로 정답 키도 숨겨지지 않습니다. API 키는 GitHub Actions Secrets에만 보관됩니다.
- 기존 버전의 브라우저 학습 기록은 새 버전에서 자동으로 이전되지 않습니다.
- `data/daily/YYYY-MM-DD.json` 포맷: `{ "category", "title", "passage", "questions": [{ "type", "q", "options": [5개], "correct": 0..4, "explain" }] }`.
