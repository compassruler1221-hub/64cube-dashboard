# app.py
# 한의 임상 기하학 교육·가설 탐색 모델 v2.1-safe
# 실행: streamlit run app.py
# 목적: 전통의학 문헌 메타데이터와 정확 기하학을 분리하여 탐색하는 교육·연구용 프로토타입
# 금지 목적: 진단, 처방 선택, 약재 가감·용량 산출, 침·뜸 시술 지시, 응급도 확정

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Sequence, Tuple

import pandas as pd
import streamlit as st
import sympy as sp

st.set_page_config(
    page_title="한의 임상 기하학 교육·가설 탐색 모델",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1420px; padding-top: 1.1rem; padding-bottom: 2.5rem;}
    h1, h2, h3 {letter-spacing: -0.035em;}
    div[data-testid="stMetricValue"] {font-size: 1.55rem;}
    .safe-card {border:1px solid #d1d5db;border-radius:12px;padding:1rem 1.1rem;margin:.5rem 0;background:#fafafa;}
    </style>
    """,
    unsafe_allow_html=True,
)

FORMULAS_SAFE = {'육미지황환': {'전통 분류': '보음·자음 처방',
           '전통 변증 용어': '간신음허, 허열도한, 정혈 부족, 하초 허약',
           '구성 약재': ['숙지황', '산수유', '산약', '복령', '택사', '목단피']},
 '팔진탕': {'전통 분류': '기혈쌍보 처방',
         '전통 변증 용어': '기혈양허, 만성피로, 안색창백, 어지럼, 식욕저하',
         '구성 약재': ['인삼', '백출', '복령', '감초', '숙지황', '당귀', '천궁', '작약']},
 '십전대보탕': {'전통 분류': '대보원기·기혈쌍보 처방',
           '전통 변증 용어': '기혈양허, 허로, 허한, 수술·질병 후 회복 저하',
           '구성 약재': ['인삼', '백출', '복령', '감초', '숙지황', '당귀', '천궁', '작약', '황기', '육계']},
 '보중익기탕': {'전통 분류': '보기·승양 처방',
           '전통 변증 용어': '비위기허, 중기하함, 기허발열, 만성피로',
           '구성 약재': ['황기', '인삼', '백출', '감초', '당귀', '진피', '승마', '시호']},
 '산조인탕': {'전통 분류': '양혈안신 처방', '전통 변증 용어': '허번불면, 혈허, 음허 내열, 심간 불안', '구성 약재': ['산조인', '복령', '지모', '천궁', '감초']},
 '귀비탕': {'전통 분류': '심비양허·기혈보강 처방',
         '전통 변증 용어': '심비양허, 불면, 건망, 심계, 식욕저하, 피로',
         '구성 약재': ['인삼', '황기', '백출', '복령', '용안육', '산조인', '목향', '감초', '당귀', '원지']},
 '사물탕': {'전통 분류': '보혈조혈 처방', '전통 변증 용어': '혈허, 어지럼, 안색창백, 월경량 감소, 건조', '구성 약재': ['숙지황', '당귀', '천궁', '작약']},
 '소요산': {'전통 분류': '소간해울·건비조혈 처방',
         '전통 변증 용어': '간울, 혈허, 비허, 스트레스성 소화불량, 흉협불편',
         '구성 약재': ['시호', '당귀', '작약', '백출', '복령', '감초', '생강', '박하']},
 '이진탕': {'전통 분류': '화담이기 처방', '전통 변증 용어': '담음정체, 오심구토, 어지럼, 흉민, 습담', '구성 약재': ['반하', '진피', '복령', '감초', '생강', '오매']},
 '평위산': {'전통 분류': '조습화위 처방', '전통 변증 용어': '비위습탁, 식체, 복부팽만, 더부룩함', '구성 약재': ['창출', '후박', '진피', '감초', '생강', '대조']},
 '오령산': {'전통 분류': '이수삼습 처방', '전통 변증 용어': '수습정체, 소변불리, 부종, 갈증·구토, 수분대사 장애', '구성 약재': ['택사', '저령', '복령', '백출', '계지']},
 '반하사심탕': {'전통 분류': '신개고강·한열조화 처방',
           '전통 변증 용어': '심하비, 한열착잡, 비위불화, 위기상역, 구역',
           '구성 약재': ['반하', '황금', '황련', '건강', '인삼', '감초', '대조']},
 '소시호탕': {'전통 분류': '화해소양 처방',
          '전통 변증 용어': '소양병, 왕래한열, 흉협고만, 구고, 인건, 목현, 심번희구',
          '구성 약재': ['시호', '황금', '반하', '인삼', '감초', '생강', '대조']},
 '대시호탕': {'전통 분류': '소양양명 합병·공하겸화 처방',
          '전통 변증 용어': '흉협고만, 심하급, 변비, 구역, 실열·실증 경향',
          '구성 약재': ['시호', '황금', '반하', '작약', '지실', '대황', '생강', '대조']},
 '소함흉탕': {'전통 분류': '청열화담·개결 처방', '전통 변증 용어': '소결흉, 담열결흉, 심하비만, 흉민, 명치 답답함', '구성 약재': ['황련', '반하', '과루실']},
 '대함흉탕': {'전통 분류': '준하축수·결흉 처방', '전통 변증 용어': '결흉, 심하부 단단함과 통증, 수열결흉, 실증 급성 복증', '구성 약재': ['대황', '망초', '감수']},
 '황련해독탕': {'전통 분류': '청열해독 처방', '전통 변증 용어': '삼초실열, 번조, 상열, 염증성 열감, 출혈 경향', '구성 약재': ['황련', '황금', '황백', '치자']},
 '백호가인삼탕': {'전통 분류': '청기분열·익기생진 처방',
            '전통 변증 용어': '양명기분열, 대열, 대한, 대갈, 맥홍대, 진액 손상',
            '구성 약재': ['석고', '지모', '인삼', '감초', '갱미']},
 '계지탕': {'전통 분류': '해기조영위 처방', '전통 변증 용어': '태양중풍, 표허, 자한, 오풍, 영위불화', '구성 약재': ['계지', '작약', '생강', '대조', '감초']},
 '마황탕': {'전통 분류': '발한해표·선폐평천 처방', '전통 변증 용어': '태양상한, 무한, 오한, 신통, 맥부긴, 해수·천식', '구성 약재': ['마황', '계지', '행인', '감초']},
 '갈근탕': {'전통 분류': '해표해기·서근 처방',
         '전통 변증 용어': '태양병, 항배강, 무한 또는 표증, 경항부 긴장',
         '구성 약재': ['갈근', '마황', '계지', '작약', '생강', '대조', '감초']},
 '팔미지황환': {'전통 분류': '온보신양·보신 처방',
           '전통 변증 용어': '신양허, 하초 냉감, 요슬냉통, 소변빈삭, 부종 경향',
           '구성 약재': ['숙지황', '산수유', '산약', '복령', '택사', '목단피', '계지', '부자']},
 '온경탕': {'전통 분류': '온경산한·양혈조경 처방',
         '전통 변증 용어': '충임허한, 혈허·어혈, 월경불순, 하복부 냉감, 손발 번열 혼재',
         '구성 약재': ['오수유', '당귀', '천궁', '작약', '인삼', '계지', '아교', '목단피', '생강', '감초', '반하', '맥문동']},
 '천왕보심단': {'전통 분류': '자음양혈·안신 처방',
           '전통 변증 용어': '심신불교, 음허혈소, 심계, 불면, 건망, 구건',
           '구성 약재': ['생지황', '인삼', '현삼', '단삼', '복령', '원지', '길경', '오미자', '당귀', '천문동', '맥문동', '백자인', '산조인']},
 '가미소요산': {'전통 분류': '소간해울·청열조혈 처방',
           '전통 변증 용어': '간울혈허, 울열, 월경 전 불편, 상열감, 짜증',
           '구성 약재': ['시호', '당귀', '작약', '백출', '복령', '감초', '생강', '박하', '목단피', '치자']},
 '반하백출천마탕': {'전통 분류': '화담식풍·건비 처방',
             '전통 변증 용어': '풍담상요, 어지럼, 두중, 담음, 비위허약',
             '구성 약재': ['반하', '백출', '천마', '진피', '복령', '감초', '생강', '대조']},
 '진무탕': {'전통 분류': '온양이수 처방', '전통 변증 용어': '양허수범, 부종, 어지럼, 복통, 설사, 소변불리', '구성 약재': ['부자', '복령', '작약', '백출', '생강']},
 '소건중탕': {'전통 분류': '온중보허·완급지통 처방', '전통 변증 용어': '중초허한, 복통, 허로, 피로, 식욕저하', '구성 약재': ['계지', '작약', '생강', '대조', '감초', '교이']},
 '대건중탕': {'전통 분류': '온중산한·강역지통 처방', '전통 변증 용어': '중초한성 복통, 복부 냉감, 장관운동 저하, 허한성 통증', '구성 약재': ['촉초', '건강', '인삼', '교이']},
 '향사평위산': {'전통 분류': '행기화습·조중 처방',
           '전통 변증 용어': '비위습탁, 기체, 식체, 복부팽만, 트림',
           '구성 약재': ['창출', '후박', '진피', '감초', '향부자', '사인', '생강', '대조']},
 '곽향정기산': {'전통 분류': '화습해표·이기화중 처방',
           '전통 변증 용어': '외감풍한과 내상습체, 오심구토, 설사, 복부불편',
           '구성 약재': ['곽향', '자소엽', '백지', '대복피', '복령', '백출', '진피', '반하', '후박', '길경', '감초', '생강', '대조']}}

MERIDIANS_SAFE = {'LU': {'개수': 11, '경락명': '수태음폐경', '부위군': '상지·흉부'},
 'LI': {'개수': 20, '경락명': '수양명대장경', '부위군': '상지·면부'},
 'ST': {'개수': 45, '경락명': '족양명위경', '부위군': '두면·흉복·하지'},
 'SP': {'개수': 21, '경락명': '족태음비경', '부위군': '하지·복부'},
 'HT': {'개수': 9, '경락명': '수소음심경', '부위군': '상지'},
 'SI': {'개수': 19, '경락명': '수태양소장경', '부위군': '상지·견갑·두면'},
 'BL': {'개수': 67, '경락명': '족태양방광경', '부위군': '두항·배부·하지'},
 'KI': {'개수': 27, '경락명': '족소음신경', '부위군': '하지·흉복'},
 'PC': {'개수': 9, '경락명': '수궐음심포경', '부위군': '상지·흉부'},
 'TE': {'개수': 23, '경락명': '수소양삼초경', '부위군': '상지·두면'},
 'GB': {'개수': 44, '경락명': '족소양담경', '부위군': '두면·체측·하지'},
 'LR': {'개수': 14, '경락명': '족궐음간경', '부위군': '하지·복부'},
 'CV': {'개수': 24, '경락명': '임맥', '부위군': '전중선·복부'},
 'GV': {'개수': 28, '경락명': '독맥', '부위군': '후중선·두항'}}

ACU_NAMES_SAFE = {'KI3': {'혈명': '태계', 'standard_name': 'Taixi'},
 'BL23': {'혈명': '신수', 'standard_name': 'Shenshu'},
 'BL18': {'혈명': '간수', 'standard_name': 'Ganshu'},
 'SP6': {'혈명': '삼음교', 'standard_name': 'Sanyinjiao'},
 'CV4': {'혈명': '관원', 'standard_name': 'Guanyuan'},
 'CV6': {'혈명': '기해', 'standard_name': 'Qihai'},
 'KI6': {'혈명': '조해', 'standard_name': 'Zhaohai'},
 'ST36': {'혈명': '족삼리', 'standard_name': 'Zusanli'},
 'CV12': {'혈명': '중완', 'standard_name': 'Zhongwan'},
 'GV20': {'혈명': '백회', 'standard_name': 'Baihui'},
 'HT7': {'혈명': '신문', 'standard_name': 'Shenmen'},
 'PC6': {'혈명': '내관', 'standard_name': 'Neiguan'},
 'LR3': {'혈명': '태충', 'standard_name': 'Taichong'},
 'ST40': {'혈명': '풍륭', 'standard_name': 'Fenglong'},
 'SP9': {'혈명': '음릉천', 'standard_name': 'Yinlingquan'},
 'CV9': {'혈명': '수분', 'standard_name': 'Shuifen'},
 'BL20': {'혈명': '비수', 'standard_name': 'Pishu'},
 'BL17': {'혈명': '격수', 'standard_name': 'Geshu'},
 'BL15': {'혈명': '심수', 'standard_name': 'Xinshu'},
 'Anmian': {'혈명': '안면', 'standard_name': 'Anmian'},
 'SP3': {'혈명': '태백', 'standard_name': 'Taibai'},
 'GB34': {'혈명': '양릉천', 'standard_name': 'Yanglingquan'},
 'ST25': {'혈명': '천추', 'standard_name': 'Tianshu'},
 'BL22': {'혈명': '삼초수', 'standard_name': 'Sanjiaoshu'},
 'KI7': {'혈명': '복류', 'standard_name': 'Fuliu'},
 'GV4': {'혈명': '명문', 'standard_name': 'Mingmen'},
 'SP4': {'혈명': '공손', 'standard_name': 'Gongsun'},
 'CV13': {'혈명': '상완', 'standard_name': 'Shangwan'},
 'CV14': {'혈명': '거궐', 'standard_name': 'Juque'},
 'CV17': {'혈명': '전중', 'standard_name': 'Shanzhong'},
 'LI11': {'혈명': '곡지', 'standard_name': 'Quchi'},
 'LI4': {'혈명': '합곡', 'standard_name': 'Hegu'},
 'ST44': {'혈명': '내정', 'standard_name': 'Neiting'},
 'LU7': {'혈명': '열결', 'standard_name': 'Lieque'},
 'BL13': {'혈명': '폐수', 'standard_name': 'Feishu'},
 'LU9': {'혈명': '태연', 'standard_name': 'Taiyuan'},
 'GB20': {'혈명': '풍지', 'standard_name': 'Fengchi'},
 'BL10': {'혈명': '천주', 'standard_name': 'Tianzhu'},
 'GV14': {'혈명': '대추', 'standard_name': 'Dazhui'},
 'TE5': {'혈명': '외관', 'standard_name': 'Waiguan'}}



def clean_cell(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    text = str(value).strip()
    return "" if text.lower() in {"none", "nan", "null"} else text


def show_df(rows_or_df: Any, height: int | None = None) -> None:
    df = rows_or_df.copy() if isinstance(rows_or_df, pd.DataFrame) else pd.DataFrame(rows_or_df)
    if df.empty:
        st.caption("표시할 항목이 없습니다.")
        return
    for column in df.columns:
        df[column] = df[column].map(clean_cell)
    kwargs: Dict[str, Any] = {"use_container_width": True, "hide_index": True}
    if height:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)


def show_small(rows: List[Dict[str, Any]]) -> None:
    st.table(pd.DataFrame(rows))


# =============================================================================
# 1) 안전 게이트 — 키워드 감지는 확인 요청일 뿐 진단·응급도 확정이 아니다.
# =============================================================================
EMERGENCY_CHECKS = [
    "숨이 매우 차서 문장으로 말하기 어렵다",
    "심하거나 지속되는 흉통·가슴 압박이 있다",
    "입술·얼굴이 파래지거나 회색빛이다",
    "실신·새로운 의식 혼미·반응 저하가 있다",
    "갑작스러운 한쪽 마비·언어장애·심한 신경학적 이상이 있다",
    "멈추지 않는 심한 출혈이 있다",
]

URGENT_CHECKS = [
    "새로 발생했거나 악화되는 호흡곤란이 있다",
    "발열과 호흡곤란이 함께 있다",
    "지속되는 고열 또는 전신상태 악화가 있다",
    "심한 복통·복부 경직·반발통이 있다",
    "혈변·토혈·검은변 또는 심한 탈수 징후가 있다",
    "얼굴·혀·목 부종, 쌕쌕거림 등 심한 알레르기 반응이 의심된다",
]

KEYWORD_GROUPS: Dict[str, List[str]] = {
    "호흡곤란 표현": ["호흡곤란", "숨이 차", "숨참", "숨쉬기 어렵", "숨이 막", "질식"],
    "흉통 표현": ["흉통", "가슴 통증", "가슴이 조이", "가슴 압박"],
    "의식 변화 표현": ["의식저하", "의식 혼미", "실신", "기절", "반응이 없"],
    "청색증 표현": ["청색증", "입술이 파래", "얼굴이 파래"],
    "발열 표현": ["고열", "발열", "열이 지속", "열감"],
    "급성 복증 표현": ["심한 복통", "격심한 복통", "복부 경직", "반발통", "배가 단단"],
    "출혈 표현": ["혈변", "토혈", "검은변", "대량 출혈"],
    "중증 알레르기 표현": ["혀가 붓", "목이 붓", "얼굴이 붓", "쌕쌕", "아나필락"],
}
NEGATION_HINTS = ["없음", "없다", "없고", "없으며", "부인", "아니다", "아니며", "호소하지 않"]


def term_is_negated(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 12): min(len(text), end + 14)]
    return any(hint in window for hint in NEGATION_HINTS)


def detect_keyword_flags(text: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", clean_cell(text))
    flags: List[str] = []
    for label, terms in KEYWORD_GROUPS.items():
        hit = False
        for term in terms:
            for match in re.finditer(re.escape(term), normalized):
                if not term_is_negated(normalized, match.start(), match.end()):
                    hit = True
                    break
            if hit:
                break
        if hit:
            flags.append(label)
    return flags


def triage_state(
    emergency_selected: Sequence[str],
    urgent_selected: Sequence[str],
    keyword_flags: Sequence[str],
    keyword_reviewed: bool,
) -> Dict[str, Any]:
    if emergency_selected:
        return {
            "level": "emergency",
            "title": "즉시 응급 대응 항목이 선택되었습니다.",
            "message": "기하학·전통 문헌의 개인화 해석을 중단합니다. 대한민국에서는 119에 연락하거나 응급실로 이동하십시오.",
            "blocked": True,
        }
    if urgent_selected:
        return {
            "level": "urgent",
            "title": "신속한 대면 의료평가 항목이 선택되었습니다.",
            "message": "오늘 중 또는 가능한 한 빨리 의료기관에서 평가받으십시오. 악화되거나 응급 항목이 생기면 119를 이용하십시오.",
            "blocked": True,
        }
    if keyword_flags and not keyword_reviewed:
        return {
            "level": "review",
            "title": "자유 입력에서 안전 관련 표현이 감지되었습니다.",
            "message": "키워드 감지는 문맥을 완전히 이해하지 못합니다. 구조화된 항목을 직접 확인하고 검토 완료를 선택하십시오.",
            "blocked": True,
        }
    return {
        "level": "clear",
        "title": "구조화된 응급·긴급 항목이 선택되지 않았습니다.",
        "message": "안전 판정이나 진료 불필요 판정이 아닙니다. 본 도구는 증상을 진단하지 않습니다.",
        "blocked": False,
    }


def render_triage(state: Dict[str, Any]) -> None:
    text = f"**{state['title']}**\n\n{state['message']}"
    if state["level"] == "emergency":
        st.error(text)
    elif state["level"] in {"urgent", "review"}:
        st.warning(text)
    else:
        st.info(text)


# =============================================================================
# 2) Q6와 H(3,4) — 같은 64개 꼭짓점 수, 다른 인접구조
# =============================================================================
BASE_TO_BITS = {"G": "00", "A": "10", "U": "01", "C": "11"}
BITS_TO_BASE = {value: key for key, value in BASE_TO_BITS.items()}


def n_to_bits(n: int) -> str:
    return "".join(str((n >> i) & 1) for i in range(6))


def n_to_codon(n: int) -> str:
    bits = n_to_bits(n)
    return "".join(BITS_TO_BASE[bits[i:i + 2]] for i in range(0, 6, 2))


def q6_neighbors(n: int) -> List[int]:
    return [n ^ (1 << i) for i in range(6)]


def h34_neighbors(vertex: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
    neighbors: List[Tuple[int, int, int]] = []
    for position in range(3):
        for replacement in range(4):
            if replacement == vertex[position]:
                continue
            candidate = list(vertex)
            candidate[position] = replacement
            neighbors.append(tuple(candidate))
    return neighbors


def graph_stats() -> List[Dict[str, Any]]:
    q_vertices, q_degree = 2 ** 6, 6
    h_vertices, h_degree = 4 ** 3, 3 * (4 - 1)
    return [
        {"그래프": "Q6", "꼭짓점": q_vertices, "차수": q_degree, "모서리": q_vertices * q_degree // 2,
         "인접 정의": "6비트 중 정확히 한 비트만 다름"},
        {"그래프": "H(3,4)", "꼭짓점": h_vertices, "차수": h_degree, "모서리": h_vertices * h_degree // 2,
         "인접 정의": "3자리 중 정확히 한 자리만 다름"},
    ]


# =============================================================================
# 3) 정12면체의 5회전축 직교투영 — 정확 기호식 검증
# =============================================================================
def exact_dodecahedron_projection() -> Dict[str, Any]:
    phi = (sp.Integer(1) + sp.sqrt(5)) / 2
    vertices: List[sp.Matrix] = []

    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                vertices.append(sp.Matrix([sx, sy, sz]))
    for a in (-1, 1):
        for b in (-1, 1):
            vertices.extend([
                sp.Matrix([0, sp.Rational(a, 1) / phi, b * phi]),
                sp.Matrix([sp.Rational(a, 1) / phi, b * phi, 0]),
                sp.Matrix([b * phi, 0, sp.Rational(a, 1) / phi]),
            ])

    axis = sp.Matrix([1, 0, -phi])
    axis_norm_sq = sp.simplify(axis.dot(axis))
    radius_sq_values = [
        sp.simplify(v.dot(v) - (v.dot(axis) ** 2) / axis_norm_sq)
        for v in vertices
    ]

    inner_sq = sp.simplify(2 - 2 * sp.sqrt(5) / 5)
    outer_sq = sp.simplify(2 + 2 * sp.sqrt(5) / 5)
    counts = [
        sum(sp.simplify(value - inner_sq) == 0 for value in radius_sq_values),
        sum(sp.simplify(value - outer_sq) == 0 for value in radius_sq_values),
    ]
    radius_partition_check = all(
        sp.simplify(value - inner_sq) == 0 or sp.simplify(value - outer_sq) == 0
        for value in radius_sq_values
    )

    ratio = sp.simplify(sp.sqrt(outer_sq / inner_sq))
    ratio_check = sp.simplify(ratio - phi)

    projected_sum = sp.Matrix([0, 0, 0])
    for vertex in vertices:
        projected_sum += sp.simplify(vertex - axis * (vertex.dot(axis) / axis_norm_sq))
    projected_sum = projected_sum.applyfunc(sp.simplify)

    e1 = sp.Matrix([0, 1, 0])
    e2 = sp.Matrix([phi, 0, 1]) / sp.sqrt(phi ** 2 + 1)
    points_2d = [sp.Matrix([sp.simplify(v.dot(e1)), sp.simplify(v.dot(e2))]) for v in vertices]

    def ordered_ring(radius_sq: sp.Expr) -> List[sp.Matrix]:
        ring = [p for p in points_2d if sp.simplify(p.dot(p) - radius_sq) == 0]
        # 순환 순서를 고르는 데만 근삿값을 사용하고, 동일성 판정은 아래 정확 기호식으로 수행한다.
        return sorted(ring, key=lambda p: math.atan2(float(sp.N(p[1], 30)), float(sp.N(p[0], 30))))

    inner_ring = ordered_ring(inner_sq)
    outer_ring = ordered_ring(outer_sq)
    cos36, sin36 = sp.cos(sp.pi / 5), sp.sin(sp.pi / 5)

    def regular_decagon_check(ring: List[sp.Matrix], radius_sq: sp.Expr) -> bool:
        checks: List[bool] = []
        for i in range(10):
            p, q = ring[i], ring[(i + 1) % 10]
            dot_ratio = sp.simplify(p.dot(q) / radius_sq)
            det_ratio = sp.simplify((p[0] * q[1] - p[1] * q[0]) / radius_sq)
            checks.extend([
                sp.simplify(dot_ratio - cos36) == 0,
                sp.simplify(det_ratio - sin36) == 0,
            ])
        return all(checks)

    aligned_rays_check = all(
        sp.simplify(inner_ring[i][0] * outer_ring[i][1] - inner_ring[i][1] * outer_ring[i][0]) == 0
        for i in range(10)
    )

    return {
        "phi": phi,
        "axis": axis,
        "inner_radius_sq": inner_sq,
        "outer_radius_sq": outer_sq,
        "counts": counts,
        "radius_partition_check": radius_partition_check,
        "inner_regular_check": regular_decagon_check(inner_ring, inner_sq),
        "outer_regular_check": regular_decagon_check(outer_ring, outer_sq),
        "aligned_rays_check": aligned_rays_check,
        "radius_ratio": ratio,
        "ratio_check": ratio_check,
        "projected_sum": projected_sum,
        "vertex_count": len(vertices),
    }


def decagon_svg(inner_r: float = 92.0, outer_r: float = 149.0, size: int = 390) -> str:
    center = size / 2
    angles = [math.radians(18 + 36 * k) for k in range(10)]

    def point(radius: float, angle: float) -> Tuple[float, float]:
        return center + radius * math.cos(angle), center - radius * math.sin(angle)

    inner = [point(inner_r, angle) for angle in angles]
    outer = [point(outer_r, angle) for angle in angles]
    inner_poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in inner)
    outer_poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in outer)
    rays = "".join(
        f'<line x1="{inner[i][0]:.2f}" y1="{inner[i][1]:.2f}" x2="{outer[i][0]:.2f}" y2="{outer[i][1]:.2f}" stroke="#9ca3af" stroke-width="1" />'
        for i in range(10)
    )
    dots = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#2563eb" />' for x, y in inner)
    dots += "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#dc2626" />' for x, y in outer)
    return f"""
    <div style="display:flex;justify-content:center;">
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" role="img" aria-label="두 동심 정10각형 투영 모식도">
        <rect width="100%" height="100%" fill="#ffffff" />
        {rays}
        <polygon points="{outer_poly}" fill="none" stroke="#dc2626" stroke-width="2" />
        <polygon points="{inner_poly}" fill="none" stroke="#2563eb" stroke-width="2" />
        {dots}
        <circle cx="{center}" cy="{center}" r="3" fill="#111827" />
        <text x="{center}" y="20" text-anchor="middle" font-size="14" fill="#374151">10점 내부 고리 + 10점 외부 고리</text>
      </svg>
    </div>
    """


PLATONIC_FACTS = [
    {"정다면체": "정4면체", "면": 4, "꼭짓점": 4, "모서리": 6, "쌍대": "정4면체(자기쌍대)"},
    {"정다면체": "정6면체", "면": 6, "꼭짓점": 8, "모서리": 12, "쌍대": "정8면체"},
    {"정다면체": "정8면체", "면": 8, "꼭짓점": 6, "모서리": 12, "쌍대": "정6면체"},
    {"정다면체": "정12면체", "면": 12, "꼭짓점": 20, "모서리": 30, "쌍대": "정20면체"},
    {"정다면체": "정20면체", "면": 20, "꼭짓점": 12, "모서리": 30, "쌍대": "정12면체"},
]

GEOMETRY_OPERATORS = [
    {"연산": "쌍대화", "정의": "면 중심을 새 꼭짓점으로 하여 면과 꼭짓점을 교환", "필수 명시": "중심·스케일·정규화"},
    {"연산": "절단", "정의": "모든 꼭짓점을 일정 비율로 잘라 새 면을 생성", "필수 명시": "절단 비율"},
    {"연산": "정류", "정의": "모서리 중점을 새 꼭짓점으로 사용", "필수 명시": "중점 연산"},
    {"연산": "직교투영", "정의": "지정 축에 수직인 평면으로 선형 투영", "필수 명시": "축·기저·투영행렬"},
    {"연산": "상사축소", "정의": "중심 기준으로 모든 좌표를 동일 비율로 축소", "필수 명시": "중심·스케일 인자"},
]

ALLOWED_USE_ROWS = [
    {"구분": "가능", "내용": "정확한 좌표·그래프·투영·대칭·비율을 교육·연구 목적으로 표시"},
    {"구분": "가능", "내용": "전통 방제·경혈의 최소 문헌 메타데이터를 출처 검증 전제로 열람"},
    {"구분": "가능", "내용": "기호식 증명과 표시용 근삿값을 구분"},
    {"구분": "금지", "내용": "증상 입력으로 처방·가감·용량·혈위·뜸 강도를 자동 추천"},
    {"구분": "금지", "내용": "벡터 합·황금비·다면체 위치를 정상·병리·치료효과로 해석"},
]


def build_acupoint_index() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for prefix, meta in MERIDIANS_SAFE.items():
        for number in range(1, meta["개수"] + 1):
            code = f"{prefix}{number}"
            override = ACU_NAMES_SAFE.get(code, {})
            rows.append({
                "code": code,
                "혈명": override.get("혈명", ""),
                "standard_name": override.get("standard_name", ""),
                "경락": meta["경락명"],
                "부위군": meta["부위군"],
            })
    assert len(rows) == 361
    return pd.DataFrame(rows)


ACUPOINT_INDEX = build_acupoint_index()


# =============================================================================
# 화면
# =============================================================================
DEFAULT_NOTE = "5일 전부터 오한과 열감이 있었고 현재 숨이 차다는 표현이 포함된 안전 게이트 예시입니다."
st.session_state.setdefault("research_ack", False)
st.session_state.setdefault("formula_name", "반하사심탕")
st.session_state.setdefault("research_note", DEFAULT_NOTE)
st.session_state.setdefault("emergency_checks", [])
st.session_state.setdefault("urgent_checks", [])
st.session_state.setdefault("keyword_reviewed", False)

with st.sidebar:
    st.header("연구 설정")
    st.checkbox("연구·교육용이며 진단·처방·시술 지시로 사용하지 않음에 동의", key="research_ack")
    st.selectbox("열람할 전통 방제 문헌 항목", list(FORMULAS_SAFE.keys()), key="formula_name")
    st.text_area(
        "안전 게이트용 자유 입력",
        key="research_note",
        height=150,
        help="처방 적합도를 계산하지 않으며 안전 관련 표현을 확인하는 데만 사용됩니다.",
    )
    st.multiselect("즉시 응급 확인 항목", EMERGENCY_CHECKS, key="emergency_checks")
    st.multiselect("신속 진료 확인 항목", URGENT_CHECKS, key="urgent_checks")
    st.checkbox("자동 감지 표현의 문맥을 직접 검토 완료", key="keyword_reviewed")

formula_name = st.session_state["formula_name"]
formula = FORMULAS_SAFE[formula_name]
research_note = clean_cell(st.session_state["research_note"])
keyword_flags = detect_keyword_flags(research_note)
triage = triage_state(
    st.session_state["emergency_checks"],
    st.session_state["urgent_checks"],
    keyword_flags,
    st.session_state["keyword_reviewed"],
)

st.title("🧭 한의 임상 기하학 교육·가설 탐색 모델")
st.caption("v2.1-safe · 원본의 임상 추천 필드를 제거하고 최소 문헌 메타데이터와 정확 기하학만 남긴 재작성본")
render_triage(triage)

if not st.session_state["research_ack"]:
    st.warning("사이드바의 연구·교육용 사용 동의를 확인해야 자료 탭을 열 수 있습니다.")

tabs = st.tabs([
    "1. 대문·면책",
    "2. 안전 게이트",
    "3. 전통 방제 문헌 DB",
    "4. 경혈 최소 인덱스",
    "5. Q6와 H(3,4)",
    "6. 플라토닉 연산",
    "7. 황금비 투영 검증",
    "8. 감사·내보내기",
])

with tabs[0]:
    st.header("연구·교육용 도구의 사용 범위")
    st.markdown(
        """
        <div class="safe-card">
        <b>본 도구는 전통의학 문헌 메타데이터와 이산·다면체 기하학을 분리하여 탐색하는 연구·교육용 프로토타입입니다.</b><br><br>
        출력되는 도형, 좌표, 그래프, 대칭 및 비율은 진단, 처방 선택, 약재 가감, 용량 결정,
        침·뜸 시술 또는 치료효과 예측을 위한 임상 지표가 아닙니다. 기하학적 유사성은 의학적 인과관계를 뜻하지 않습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_df(ALLOWED_USE_ROWS)
    st.subheader("원본에서 코드 수준으로 제거한 항목")
    st.markdown(
        """
        - ‘잘 맞는 환자상’, 처방 적합성, 감별·가감 자동 출력
        - 방제별 핵심 혈위, 뜸 가능 여부와 권장 강도
        - 황금비·면적비를 군신좌사 비율 또는 약재 용량으로 환산하는 로직
        - 벡터 합 `{0,0}`을 건강·정상 상태로 해석하는 로직
        - Q6와 H(3,4)를 같은 그래프로 취급하는 설명
        - 연산자가 없는 정다면체 임의 순환
        """
    )
    st.info("면책문만 추가한 것이 아니라, 임상 추천에 사용될 수 있는 데이터 필드와 출력 경로 자체를 제거했습니다.")

with tabs[1]:
    st.header("안전 게이트")
    show_small([
        {"항목": "감지된 표현", "내용": ", ".join(keyword_flags) if keyword_flags else "감지 없음"},
        {"항목": "직접 선택한 응급 항목", "내용": ", ".join(st.session_state["emergency_checks"]) or "없음"},
        {"항목": "직접 선택한 신속 진료 항목", "내용": ", ".join(st.session_state["urgent_checks"]) or "없음"},
        {"항목": "현재 게이트", "내용": triage["level"]},
    ])
    if keyword_flags:
        st.warning("키워드 감지는 문맥 오류가 있을 수 있습니다. 구조화된 항목을 직접 확인해야 합니다.")
    show_df([
        {"단계": "응급", "조건": "중증 호흡곤란·심한 흉통·청색증·의식 변화 등 직접 선택", "동작": "119/응급실 안내"},
        {"단계": "신속 진료", "조건": "새로운 호흡곤란·발열 동반 호흡곤란·고열 지속 등 직접 선택", "동작": "신속한 대면 평가 안내"},
        {"단계": "문맥 검토", "조건": "관련 표현 감지, 검토 미완료", "동작": "확인 요청"},
        {"단계": "일반", "조건": "구조화된 위험 항목 없음", "동작": "연구 자료 열람만 허용"},
    ])

with tabs[2]:
    st.header("전통 방제 최소 문헌 메타데이터")
    if not st.session_state["research_ack"]:
        st.warning("연구용 사용 동의를 먼저 확인하십시오.")
    else:
        st.warning("원본 파일에 원전·공정서·제품설명서의 항목별 출처가 첨부되지 않았습니다. 연구 사용 전 출처와 판본을 검증하십시오.")
        show_small([
            {"항목": "방제명", "내용": formula_name},
            {"항목": "전통 분류", "내용": formula["전통 분류"]},
            {"항목": "전통 변증 용어", "내용": formula["전통 변증 용어"]},
            {"항목": "구성 약재", "내용": ", ".join(formula["구성 약재"])},
        ])
        st.info("증상 입력과 방제 항목 사이의 적합성·추천·점수·가감·용량은 계산하지 않습니다.")

with tabs[3]:
    st.header("361 경혈 최소 인덱스")
    if not st.session_state["research_ack"]:
        st.warning("연구용 사용 동의를 먼저 확인하십시오.")
    else:
        query = st.text_input("경혈 코드·이름·경락 검색", key="acu_query")
        filtered = ACUPOINT_INDEX.copy()
        if query.strip():
            mask = filtered.astype(str).apply(
                lambda column: column.str.contains(query.strip(), case=False, na=False)
            ).any(axis=1)
            filtered = filtered[mask]
        show_df(filtered, height=520)
        st.caption("임상 의미, 후보 근거, 자침·뜸 방법과 강도 데이터는 코드에서 제거했습니다.")

with tabs[4]:
    st.header("Q6와 H(3,4)는 그래프 동형이 아닙니다")
    show_df(graph_stats())
    st.error("Q6의 차수는 6, H(3,4)의 차수는 9이므로 두 그래프는 동형일 수 없습니다.")
    st.markdown(
        """
        H(3,4)는 3개 위치마다 4개 값을 갖는 코돈 공간과 자연스럽게 대응합니다.
        Q6에 2비트 부호화를 적용하면 꼭짓점 사이의 전단사를 만들 수 있지만 인접관계는 보존되지 않습니다.
        """
    )
    rows: List[Dict[str, Any]] = []
    for n in [0, 1, 9, 18, 27, 36, 45, 54, 63]:
        codon = n_to_codon(n)
        h_vertex = tuple("GAUC".index(base) for base in codon)
        rows.append({
            "Q6 인덱스": n,
            "6비트": n_to_bits(n),
            "선택한 부호화의 코돈": codon,
            "Q6 이웃 수": len(q6_neighbors(n)),
            "H(3,4) 이웃 수": len(h34_neighbors(h_vertex)),
            "63-n": 63 - n,
        })
    show_df(rows, height=360)
    st.warning("n↔63−n은 선택한 비트 부호화의 보수 관계일 뿐 생물학적 상보 염기나 의학적 음양을 뜻하지 않습니다.")

with tabs[5]:
    st.header("플라토닉 솔리드: 화살표마다 연산자를 명시")
    show_df(PLATONIC_FACTS)
    st.latex(r"T^*=T,\qquad C^*=O,\qquad D^*=I")
    show_df(GEOMETRY_OPERATORS)
    st.warning("‘정12면체→정6면체→정4면체→정8면체→정20면체’는 각 화살표의 연산이 없으면 표준 수학적 순환이 아닙니다.")
    st.write("각 단계에 입력 좌표, 중심, 연산자, 파라미터, 출력 꼭짓점·모서리 집합, 정확한 동일성 판정을 기록해야 합니다.")

with tabs[6]:
    st.header("정12면체 5회전축 직교투영 — 정확 검증")
    proof = exact_dodecahedron_projection()
    c1, c2, c3 = st.columns(3)
    c1.metric("꼭짓점", str(proof["vertex_count"]))
    c2.metric("방위", "10")
    c3.metric("동심 고리", "2")
    st.markdown(decagon_svg(), unsafe_allow_html=True)
    show_df([
        {"검증": "내부 고리 반지름²", "정확 결과": sp.sstr(proof["inner_radius_sq"]), "확인": proof["counts"][0]},
        {"검증": "외부 고리 반지름²", "정확 결과": sp.sstr(proof["outer_radius_sq"]), "확인": proof["counts"][1]},
        {"검증": "두 반지름으로 완전 분할", "정확 결과": str(proof["radius_partition_check"]), "확인": "True"},
        {"검증": "내부/외부 정10각형", "정확 결과": f"{proof['inner_regular_check']} / {proof['outer_regular_check']}", "확인": "각 36°"},
        {"검증": "두 고리 방위 정렬", "정확 결과": str(proof["aligned_rays_check"]), "확인": "True"},
        {"검증": "외부/내부 반지름", "정확 결과": sp.sstr(proof["radius_ratio"]), "확인": "φ"},
        {"검증": "반지름비−φ", "정확 결과": sp.sstr(proof["ratio_check"]), "확인": "0"},
        {"검증": "투영벡터 합", "정확 결과": str(list(proof["projected_sum"])), "확인": "중심대칭"},
    ])
    st.success("표준 좌표와 축 a=(1,0,−φ)에서 20개 꼭짓점은 두 동심 정10각형을 이루며 외부/내부 반지름 비는 정확히 φ입니다.")
    st.warning("벡터 합 0은 중심대칭의 기하학적 항등식일 뿐 건강·정상·치료 성공을 뜻하지 않습니다. 투영 그림만으로 3D 인접성도 추론할 수 없습니다.")
    with st.expander("표시용 근삿값 — 증명에 사용하지 않음"):
        show_small([
            {"항목": "φ", "근삿값": str(sp.N(proof["phi"], 12))},
            {"항목": "내부 반지름", "근삿값": str(sp.N(sp.sqrt(proof["inner_radius_sq"]), 12))},
            {"항목": "외부 반지름", "근삿값": str(sp.N(sp.sqrt(proof["outer_radius_sq"]), 12))},
        ])

with tabs[7]:
    st.header("감사 기록과 내보내기")
    audit_rows = [
        {"항목": "앱 목적", "상태": "연구·교육용"},
        {"항목": "진단·처방·용량 산출", "상태": "코드에서 제거"},
        {"항목": "침·뜸 개인화 필드", "상태": "코드에서 제거"},
        {"항목": "안전 게이트", "상태": triage["level"]},
        {"항목": "Q6/H(3,4)", "상태": "비동형 명시"},
        {"항목": "정12면체 투영", "상태": "두 동심 정10각형·반지름비 φ"},
        {"항목": "기호/수치", "상태": "기호식=증명, 근삿값=표시"},
        {"항목": "문헌 DB 출처", "상태": "미첨부·외부 검증 필요"},
    ]
    show_df(audit_rows)
    audit_text = f"""[연구 모델 감사 기록]
버전: v2.1-safe
열람 문헌 항목: {formula_name}
안전 게이트: {triage['level']}
감지 표현: {', '.join(keyword_flags) if keyword_flags else '없음'}
직접 선택 응급 항목: {', '.join(st.session_state['emergency_checks']) or '없음'}
직접 선택 신속 진료 항목: {', '.join(st.session_state['urgent_checks']) or '없음'}

교정 완료:
- 임상 의사결정, 처방 적합성, 가감·용량, 혈위·뜸 추천 데이터와 출력 제거
- Q6 degree=6, edges=192 / H(3,4) degree=9, edges=288로 분리
- 정다면체 관계에 연산자 요구
- 정12면체 투영을 두 동심 정10각형으로 정확 검증
- 벡터 합 0과 임상 정상 상태 분리
- 기호식과 표시용 근삿값 분리

주의: 환자 식별정보를 입력하거나 이 기록에 포함해 외부 공유하지 마십시오.
"""
    st.text_area("감사 기록", audit_text, height=310)
    st.download_button("감사 기록 다운로드", audit_text, "geometry_research_audit.txt", "text/plain")
    st.markdown(
        """
        - 응급 상황에서는 대한민국 119 또는 응급의료기관을 이용합니다.
        - 진단·치료·예후 관찰·치료 예측·모니터링 목적의 소프트웨어는 기능과 의도된 사용 목적에 따라 규제 검토가 필요할 수 있습니다.
        - 실제 배포 전 의료·법률·개인정보보호·소프트웨어 품질 전문가의 검토가 필요합니다.
        """
    )

st.divider()
st.caption(
    "연구·교육용 프로토타입입니다. 진단, 처방 선택, 약재 가감·용량, 침·뜸 시술, 응급도 확정에 사용하지 마십시오. "
    "전통의학 문헌 메타데이터는 원전·공정서·제품설명서와 대조해야 합니다."
)
