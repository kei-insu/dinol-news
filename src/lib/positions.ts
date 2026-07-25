// 직무 ID → 한글 라벨. 라벨 변경은 이 맵 1줄만 수정한다(카드 데이터 불변).
// 맵에 없는 ID 는 화면에 렌더하지 않고 console.warn 한다(docs/detail-page-schema.md §4).
export const POSITIONS: Record<string, string> = {
  'ux-designer': 'UX디자이너',
  'ui-designer': 'UI디자이너',
  'product-designer': '프로덕트디자이너',
  'service-designer': '서비스디자이너',
  'brand-designer': '브랜드디자이너',
  'bx-designer': 'BX디자이너',
  'graphic-designer': '그래픽디자이너',
  'editorial-designer': '편집디자이너',
  'motion-designer': '모션디자이너',
  'video-designer': '영상디자이너',
  'illustrator': '일러스트레이터',
  'art-director': '아트디렉터',
  'industrial-designer': '제품디자이너',
  'space-designer': '공간디자이너',
  'architect': '건축가',
  'package-designer': '패키지디자이너',
  'typographer': '타이포그래퍼',
  'fashion-designer': '패션디자이너',
  'design-lead': '디자인리드',
  'design-manager': '디자인매니저',
};

// 유효 직무 칩이 하나도 없을 때 표시하는 기본 칩 라벨/툴팁.
// positions: [] 의 의미(특정 직무 없음)를 JSON 을 건드리지 않고 화면에서만 보완한다.
export const FALLBACK_POSITION_LABEL = '공통 참고';
export const FALLBACK_POSITION_TITLE = '특정 디자인 직무에 한정되지 않는 공통 참고 콘텐츠';
