---
layout: post
title: "Pikchr Editor 소개 - Pikchr 다이어그램 작성을 돕는 웹 기반 비주얼 에디터"
categories: it
---

# Pikchr Editor: Pikchr 다이어그램 작성을 돕는 웹 기반 비주얼 에디터

기술 문서나 블로그를 작성할 때 다이어그램을 코드로 표현하는 도구로 Mermaid, PlantUML, Graphviz 등이 주로 사용됩니다. 그중 SQLite와 Fossil VCS의 개발자인 D. Richard Hipp이 만든 [Pikchr](https://pikchr.org)(픽처)는 텍스트 마크업을 통해 간결하고 정교한 SVG 벡터 다이어그램을 생성할 수 있는 도구입니다.

다만 Pikchr를 사용할 때 다음과 같은 불편이 있습니다:

1. **문법 습득의 장벽**: 지원되는 도형 키워드, 위치 속성(`at`, `with`), 연결자(`then`, `from`, `to`), 앵커 포인트(`.e`, `.nw`, `.c`) 등의 구문 규칙을 매번 확인해야 합니다.
2. **수정 위치 식별의 번거로움**: 코드가 길어지면 캔버스에 렌더링된 요소가 코드의 어느 문장에 해당하는지, 혹은 수정하려는 코드가 캔버스의 어느 위치에 반영되는지 빠르게 찾기 어렵습니다.

이러한 점을 보완하여 Pikchr 문법 작성을 보조하고 문장 단위의 식별을 돕기 위해 오픈소스 웹 에디터인 [Pikchr Editor (pikchr-editor)](https://pikchr-editor.vercel.app)를 개발했습니다.

---

## 프로젝트 목표

Pikchr Editor는 텍스트 에디터와 미리보기 뷰어를 결합하고, 문장(Statement) 단위의 인터랙션을 제공하는 데 초점을 맞추었습니다.

1. **Pikchr 문법 입력 보조**
   - 문맥 인식 자동완성(Context-Aware Autocomplete)을 통해 키워드, 속성, 앵커 목록 제안
   - 속성 인스펙터(Visual Inspector)를 통해 폼 입력 방식으로 속성 값 수정 지원
2. **문장 식별 지원 (Statement Identification)**
   - 캔버스 도형 ↔ 코드 문장 ↔ 우측 문장 목록 간 하이라이트 동기화
   - 세미콜론/개행으로 구분된 문장 식별 지원

---

## UI 레이아웃 구성

Pikchr Editor는 작업 영역을 4개 패널로 구분하고 모바일 화면을 위한 반응형 레이아웃을 제공합니다.

```
+-----------------------------------------------------------------------------------+
| 상단 메뉴바: 파일, 편집, 공식 예제, 뷰, 다국어(KO/EN/JA), 테마, SVG/PNG 내보내기      |
+--------------------+------------------------------------+-------------------------+
| 좌측 사이드바      | 센터 스테이지                      | 우측 사이드바           |
| (팔레트 및 정의)   | (SVG 캔버스)                       | (문장 목록 및 속성)     |
|                    |                                    |                         |
| - 기본 도형 팔레트 | - 실시간 SVG 렌더링                | [STATEMENTS]            |
|   (Box, Circle...) | - 캔버스 줌 / 이동 (Zoom/Pan)      | - 문장 목록 트리        |
| - 템플릿 스니펫    | - 요소 선택 하이라이트 및 앵커 표시 | [PROPERTY]              |
| - 변수 / 매크로    |                                    | - 객체별 속성 입력 폼   |
+--------------------+------------------------------------+-------------------------+
| 하단 패널: 코드 에디터 (Code View)                                                |
| - 문맥 자동완성, 문장 시각적 하이라이트 오버레이, 라인 번호, 컴파일 상태 표시      |
+-----------------------------------------------------------------------------------+
```

---

## 주요 기능

### 1. 문장 단위 시각적 식별 
- **캔버스 클릭을 통한 식별**: 렌더링된 SVG 내 특정 도형을 클릭하면, 하단 에디터의 해당 문장이 오버레이로 표시되고 우측 문장 목록에서도 해당 항목이 포커스됩니다.
- **문장 목록 클릭을 통한 식별**: 우측 `STATEMENTS` 목록에서 객체를 선택하면 캔버스의 도형과 코드 에디터의 해당 문장이 함께 강조됩니다.
- **인라인 다중 문장 분리**: 한 라인에 세미콜론으로 여러 문장이 작성된 경우(`box; arrow; circle;`)에도 문자 오프셋을 계산하여 선택된 문장만 구분하여 표시합니다.

### 2. 문맥 인식 키워드 자동완성 
- 입력 위치의 문맥을 분석하여 추천 항목을 표시합니다:
  - 도형 키워드 선언 후: 크기(`width`, `height`), 색상(`fill`, `color`), 텍스트 라벨
  - 연결선(`arrow`, `line`): 경로 분기(`then`, `from`, `to`, `until`), 두께(`thick`), 스타일(`dashed`)
  - 점 표기법(`.`) 입력 시: 객체 앵커(`.n`, `.s`, `.e`, `.w`, `.ne`, `.nw`, `.center` 등)
  - 방향 지시어(`right`, `down`, `left`, `up`) 및 거리 표현
- 팝오버는 뷰포트 하단을 벗어날 경우 위쪽으로 위치가 전환되며, 필요한 경우 체크박스로 기능을 끌 수 있습니다.

### 3. 객체별 속성 인스펙터 
- 우측 인스펙터를 통해 선택된 객체의 속성을 폼 형태로 수정할 수 있습니다:
  - **`box`, `cylinder`, `diamond`**: 너비, 높이, 모서리 곡률(`radius`), 채우기 색상, 테두리 두께, fit 모드
  - **`circle`, `dot`**: 반지름, 지름, 색상, 채우기
  - **`arrow`, `line`, `spline`**: 화살표 머리 형태(`->`, `<-`, `<->`), 방향, 길이, 출발/도착점
  - **`text`**: 글자 크기(`big`, `small`), 스타일(`bold`, `italic`, `mono`), 정렬(`ljust`, `rjust`, `center`)
- 인스펙터에서 수정된 값은 소스 코드와 캔버스에 함께 반영됩니다.

### 4. 캔버스 뷰 및 내보내기
- **WebAssembly 컴파일**: WebAssembly 기반 컴파일러(`pikchr-js`)를 탑재하여 브라우저 환경에서 직접 SVG를 렌더링합니다.
- **배경 모드**:
  - `Paper-White`: 기본 다이어그램용 화이트 시트
  - `Paper-Dark`: Pikchr 고유 다크 모드 플래그(`flags: 2`)가 적용된 다크 캔버스
  - `Transparent`: 모눈 그리드 투명 캔버스
- **내보내기**: 상단 메뉴를 통해 SVG 및 PNG 파일로 내보내거나 코드를 클립보드로 복사할 수 있습니다.

### 5. 반응형 인터페이스 및 레이아웃 조절
- 데스크톱에서는 패널 경계선을 드래그하여 사이드바와 하단 에디터의 크기를 조절할 수 있으며, 조절된 크기는 브라우저 `localStorage`에 저장됩니다.
- 모바일 환경에서는 탭 전환 버튼을 통해 캔버스와 코드 뷰를 전환할 수 있으며, 키 입력 시 커서 위치로 화면이 자동 스크롤됩니다.

---

## 기술 스택

| 영역 | 사용 기술 |
| :--- | :--- |
| **Frontend Framework** | React 18, TypeScript, Vite |
| **Styling** | Tailwind CSS v4, Lucide React Icons |
| **Pikchr Engine** | WebAssembly (`pikchr-js`) |
| **Parser & AST Engine** | 자체 구현 토큰/문장 파서 (`statementDetector`, `contextAnalyzer`) |
| **Testing** | Vitest (50여 개 단위 및 통합 테스트) |

---

## 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/OnionStar0325/pikchr-editor.git
cd pikchr-editor

# 2. 의존성 패키지 설치
npm install

# 3. 개발 서버 실행
npm run dev
```

브라우저에서 `http://localhost:3000`으로 접속하여 실행할 수 있으며, 상단 메뉴의 `Examples`에서 공식 예제 다이어그램을 불러올 수 있습니다.

---

## 링크

- **GitHub 저장소**: [https://github.com/OnionStar0325/pikchr-editor](https://github.com/OnionStar0325/pikchr-editor)
- **Pikchr Editor**: [https://pikchr-editor.vercel.app](https://pikchr-editor.vercel.app)
- **라이선스**: MIT License
