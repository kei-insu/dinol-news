# fortune-schema.md — 디자이너 별자리 운세 데이터 스키마 (fortune.json)

| 작성일 | 상태 |
|---|---|
| 2026-07-13 | 스키마 확정(개발순서 1). 다음: GitHub Action → fortune.html → 루틴 지침 |

> 코너명: **오늘의 디자이너 별자리** (헤더 영문 `Today's Designer Zodiac`). 디놀 하위 코너.
> 데이터 흐름: Action이 freehoroscopeapi에서 원본 수집 → `horoscope_raw.json` → 루틴이 번역·재해석 → **`fortune.json`** → `fortune.html`이 렌더.
> 이 문서는 `fortune.json`의 단일 기준. 예시 = `fortune.example.json`(2별자리 채움).

---

## 1. 최상위 구조

```
{
  "date":  "YYYYMMDD",          // 발행 날짜(GMT+9)
  "source":"freehoroscopeapi.com daily",  // 출처 표기용(고정)
  "signs": [ …12개… ]           // 별자리 순서(양자리→물고기자리), 순위 없음
}
```

- `signs`는 **정확히 12개**, **별자리 순서 고정**(아래 표). ⚠️ 순위(랭킹) 개념 없음.
- "재미로 보는 운세" 문구는 `fortune.html`에 고정 표기(데이터에 안 넣음).

## 2. 별자리 순서·이름·기호 (고정)

| 순서 | sign | nameKo | symbol |
|---|---|---|---|
| 1 | `aries` | 양자리 | ♈ |
| 2 | `taurus` | 황소자리 | ♉ |
| 3 | `gemini` | 쌍둥이자리 | ♊ |
| 4 | `cancer` | 게자리 | ♋ |
| 5 | `leo` | 사자자리 | ♌ |
| 6 | `virgo` | 처녀자리 | ♍ |
| 7 | `libra` | 천칭자리 | ♎ |
| 8 | `scorpio` | 전갈자리 | ♏ |
| 9 | `sagittarius` | 사수자리 | ♐ |
| 10 | `capricorn` | 염소자리 | ♑ |
| 11 | `aquarius` | 물병자리 | ♒ |
| 12 | `pisces` | 물고기자리 | ♓ |

`sign`은 freehoroscopeapi의 sign 파라미터와 동일(영문 소문자).

## 3. 별자리 객체 필드

### 기본 카드 (실제 운세)
| 필드 | 타입 | 설명 |
|---|---|---|
| `sign` | string | 영문 id(위 표) |
| `nameKo` | string | 한글 별자리명 |
| `symbol` | string | 유니코드 기호 |
| `score` | int 1~5 | **총운 별점.** 루틴이 원본 운세의 긍정도(감성)로 산정 |
| `message` | string | **번역된 실제 운세**(한국어 2~4문장). 원문 그대로 재게시 금지 → 번역+가벼운 정리(변형저작물) |

### 팝업 (디자이너 재해석) — `designer` 객체
| 필드 | 타입 | 설명 |
|---|---|---|
| `designer.probs` | array[6] | 확률 6종(순서·label·icon **고정**, pct·quip만 생성) |
| `designer.matches` | array[6] | 궁합 6종(순서·name·emoji **고정**, stars·quip만 생성) |
| `designer.luckyColor` | object | `{ "hex":"#RRGGBB", "name":"한국어 색이름(창작)" }` |
| `designer.luckyFont` | string | 아래 폰트풀 10종 중 하나(**정확한 구글폰트 패밀리명**) |

#### 확률 6종 (probs) — 순서·label·icon 고정
| 순서 | label | icon | 필드 |
|---|---|---|---|
| 1 | 야근 | 🌙 | `pct`(0~100 int), `quip`(≤40자) |
| 2 | 외주 | 💼 | 〃 |
| 3 | 한번에 통과 | ✅ | 〃 |
| 4 | 3회+ 수정 | 🔁 | 〃 |
| 5 | 주목/채택 | 🌟 | 〃 |
| 6 | 리젝 | ❌ | 〃 |

각 원소: `{ "label":"야근", "icon":"🌙", "pct":30, "quip":"…" }`

#### 궁합 6종 (matches) — 순서·name·emoji 고정
| 순서 | name | emoji | 필드 |
|---|---|---|---|
| 1 | 팀장 | 👔 | `stars`(1~5 int), `quip`(≤40자) |
| 2 | 동료 디자이너 | 🎨 | 〃 |
| 3 | 기획자 | 📋 | 〃 |
| 4 | 개발자 | 💻 | 〃 |
| 5 | 대표 | 🏢 | 〃 |
| 6 | 클라이언트 | 🤝 | 〃 |

각 원소: `{ "name":"개발자", "emoji":"💻", "stars":5, "quip":"…" }`

## 4. 행운의 폰트 풀 (10종 · 구글폰트 패밀리명 정확히)

`Noto Serif KR` · `Song Myung` · `Jua` · `Do Hyeon` · `Black Han Sans` · `Gaegu` · `Nanum Pen Script` · `Nanum Brush Script` · `Gamja Flower` · `Hi Melody`

- ⚠️ `luckyFont` 값은 위 문자열과 **정확히 일치**해야 렌더됨(불일치 시 기본체 폴백).
- `fortune.html`은 이 10종을 **전부 `<link>`로 로드**해 둔다(어느 별자리에 뭐가 배정돼도 렌더되게).
- 팝업 타이틀(별자리명)을 그 별자리의 `luckyFont` + `luckyColor.hex`로 꾸민다 ← 시그니처.

## 5. 콘텐츠 가드레일 (운세)

- 직군 비하 금지 — 애정 어린 티키타카. 부정 항목(야근·리젝)도 유머로 승화.
- 순위/적중 주장 금지(신뢰 리스크). 총운 `score`는 "오늘 기운" 표현이지 순위 아님.
- 원문 운세 그대로 재게시 금지 → 번역+재해석.
- `quip`은 짧고 가볍게(한 줄). 별자리 특성과 실무 상황을 엮어 재미 위주로.

## 6. 남은 개발 순서

2. **GitHub Action** `.github/workflows/horoscope.yml` — cron으로 12별자리 fetch → `horoscope_raw.json` 커밋(Action은 외부 fetch 가능).
3. **fortune.html** — `fortune.json` 읽어 12카드 리스트 + 팝업 렌더(폰트 10종 로드, 팝업 타이틀 폰트·색 적용).
4. **루틴 지침** — `horoscope_raw.json` 읽고 번역·별점·확률·궁합·색·폰트 생성 → `fortune.json` 작성 단계 추가.
