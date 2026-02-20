# SCSS `sass:color` 함수 정리

이 문서는 Dart Sass 기준으로 색상 관련 함수를 학습용으로 정리한 자료입니다.
특히 기존 `lighten()`, `darken()` 경고를 `sass:color` 모듈 방식으로 바꾸는 데 초점을 맞춥니다.

---

## 1. 시작: 모듈 임포트

```scss
@use 'sass:color';
```

`sass:color`를 임포트한 뒤 `color.함수명(...)` 형태로 사용합니다.

---

## 2. 왜 바꿔야 하나?

기존 전역 함수(`lighten`, `darken`, `transparentize` 등)는 deprecation 대상입니다.
앞으로는 `color.adjust`, `color.scale`, `color.change` 같은 모듈 함수를 쓰는 것이 권장됩니다.

---

## 3. 가장 자주 쓰는 함수 3개

### 3.1 `color.adjust()` - 현재 값에 더하고/빼기

- 의미: 채널 값을 "증감"합니다.
- 예: 20% 어둡게, 알파를 0.2 줄이기

```scss
color.adjust($color_gray, $lightness: -20%, $space: hsl);
color.adjust($color_white, $alpha: -0.7);
```

### 3.2 `color.scale()` - 남은 범위를 비율로 조정

- 의미: 현재값을 절대값으로 빼는 것이 아니라, 가능한 범위 대비 비율로 변경합니다.
- 예: 밝기를 20% 줄이기(상대 비율)

```scss
color.scale($color_gray, $lightness: -20%);
```

### 3.3 `color.change()` - 값을 정확히 지정

- 의미: 채널을 "절대값"으로 설정합니다.
- 예: 알파를 정확히 0.9로 설정

```scss
color.change($color_gray, $alpha: 0.9);
```

---

## 4. `adjust`와 `change` 차이

- `adjust`: 현재 값 기준으로 증감 (`+/-`)
- `change`: 목표 값을 직접 지정

예를 들어 "`$color_gray`를 20% 어둡게"는 보통 아래가 더 간단합니다.

```scss
color.adjust($color_gray, $lightness: -20%, $space: hsl);
```

`change`로 하려면 현재 lightness를 읽어서 계산해야 합니다.

```scss
$l: color.channel($color_gray, 'lightness', $space: hsl);
$darker: color.change($color_gray, $lightness: $l - 20%, $space: hsl);
```

---

## 5. `adjust()`/`change()` 주요 매개변수

두 함수 모두 비슷한 채널 인자를 받습니다.

- RGB: `$red`, `$green`, `$blue`
- HSL: `$hue`, `$saturation`, `$lightness`
- HWB: `$whiteness`, `$blackness`
- Lab/XYZ/Oklch 계열: `$x`, `$y`, `$z`, `$chroma` (색공간별 채널 인자 사용 가능)
- 공통: `$alpha`, `$space`

주의:

- `$darken` 같은 인자는 없습니다.
- `darken` 의도를 표현하려면 `$lightness: -...`를 사용하세요.

---

## 6. 실전 변환 예시 (`lighten`/`darken` 대체)

기존:

```scss
background: lighten($color_red, 35%);
color: darken($color_red, 15%);
```

권장:

```scss
background: color.adjust($color_red, $lightness: 35%, $space: hsl);
color: color.adjust($color_red, $lightness: -15%, $space: hsl);
```

---

## 7. 자주 하는 실수

1. `change`를 증감 함수처럼 사용
   - `change`는 절대값 설정 함수
2. 알파를 착각
   - `adjust($alpha: -0.9)`는 "0.9 감소"
   - `change($alpha: 0.9)`는 "0.9로 설정"

---

## 8. 짧은 치트시트

```scss
@use 'sass:color';

// 20% 어둡게(증감)
$c1: color.adjust($color_gray, $lightness: -20%, $space: hsl);

// 20% 밝게(증감)
$c2: color.adjust($color_gray, $lightness: 20%, $space: hsl);

// 알파 0.2 줄이기
$c3: color.adjust($color_gray, $alpha: -0.2);

// 알파를 0.9로 고정
$c4: color.change($color_gray, $alpha: 0.9);

// 상대 비율로 밝기 감소
$c5: color.scale($color_gray, $lightness: -20%);
```
