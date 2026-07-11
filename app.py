# app.py
# 한의사용 처방·침구·뜸 보조 대시보드 v96-safe
# 실행: streamlit run app.py
# 목적: 교육·연구·임상 설명 보조. 자동 진단, 자동 처방, 자동 침구 시술 지시가 아닙니다.

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


# ============================================================
# 0. 페이지 설정 및 공통 UI
# ============================================================

st.set_page_config(
    page_title="한의사용 처방·침구·뜸 보조 대시보드",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main .block-container {max-width: 1280px; padding-top: 2.0rem; padding-bottom: 4rem;}
    h1, h2, h3 {letter-spacing: -0.03em;}
    .safe-box {border-left: 5px solid #16a34a; background:#ecfdf5; padding:0.9rem 1rem; border-radius:0.6rem; line-height:1.75; margin:0.5rem 0 1.0rem 0;}
    .warn-box {border-left: 5px solid #f59e0b; background:#fffbeb; padding:0.9rem 1rem; border-radius:0.6rem; line-height:1.75; margin:0.5rem 0 1.0rem 0;}
    .danger-box {border-left: 5px solid #ef4444; background:#fef2f2; padding:0.9rem 1rem; border-radius:0.6rem; line-height:1.75; margin:0.5rem 0 1.0rem 0;}
    .info-box {border-left: 5px solid #3b82f6; background:#eff6ff; padding:0.9rem 1rem; border-radius:0.6rem; line-height:1.75; margin:0.5rem 0 1.0rem 0;}
    .muted {color:#64748b; font-size:0.92rem;}
    .clinical-card {border:1px solid #e5e7eb; border-radius:0.7rem; padding:1rem 1.1rem; margin:0.6rem 0; background:white;}
    .red {color:#dc2626; font-weight:700;}
    .green {color:#15803d; font-weight:700;}
    </style>
    """,
    unsafe_allow_html=True,
)


def note_box(kind: str, text: str) -> None:
    cls = {
        "safe": "safe-box",
        "warn": "warn-box",
        "danger": "danger-box",
        "info": "info-box",
    }.get(kind, "info-box")
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def clean_cell(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and pd.isna(x):
        return ""
    if isinstance(x, list):
        return ", ".join(str(i) for i in x if i is not None)
    return str(x)


def clean_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [{k: clean_cell(v) for k, v in row.items()} for row in rows]


def df_from(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(clean_rows(rows)).fillna("")


def show_df(rows_or_df: Any, hide_index: bool = True) -> None:
    if isinstance(rows_or_df, pd.DataFrame):
        df = rows_or_df.fillna("")
    else:
        df = df_from(rows_or_df)
    st.dataframe(df, use_container_width=True, hide_index=hide_index)


def show_small(rows: List[Dict[str, Any]]) -> None:
    st.table(df_from(rows))


def join_nonempty(items: List[str], sep: str = ", ") -> str:
    return sep.join([x for x in items if x])


# ============================================================
# 1. 64큐브 Q6 / H(3,4) 연구자용 매핑
# ============================================================

BASE_TO_BITS: Dict[str, str] = {"G": "00", "A": "10", "U": "01", "C": "11"}
BITS_TO_BASE: Dict[str, str] = {v: k for k, v in BASE_TO_BITS.items()}

GENETIC_CODE: Dict[str, str] = {
    "UUU": "Phe", "UUC": "Phe", "UUA": "Leu", "UUG": "Leu",
    "UCU": "Ser", "UCC": "Ser", "UCA": "Ser", "UCG": "Ser",
    "UAU": "Tyr", "UAC": "Tyr", "UAA": "Stop", "UAG": "Stop",
    "UGU": "Cys", "UGC": "Cys", "UGA": "Stop", "UGG": "Trp",
    "CUU": "Leu", "CUC": "Leu", "CUA": "Leu", "CUG": "Leu",
    "CCU": "Pro", "CCC": "Pro", "CCA": "Pro", "CCG": "Pro",
    "CAU": "His", "CAC": "His", "CAA": "Gln", "CAG": "Gln",
    "CGU": "Arg", "CGC": "Arg", "CGA": "Arg", "CGG": "Arg",
    "AUU": "Ile", "AUC": "Ile", "AUA": "Ile", "AUG": "Met",
    "ACU": "Thr", "ACC": "Thr", "ACA": "Thr", "ACG": "Thr",
    "AAU": "Asn", "AAC": "Asn", "AAA": "Lys", "AAG": "Lys",
    "AGU": "Ser", "AGC": "Ser", "AGA": "Arg", "AGG": "Arg",
    "GUU": "Val", "GUC": "Val", "GUA": "Val", "GUG": "Val",
    "GCU": "Ala", "GCC": "Ala", "GCA": "Ala", "GCG": "Ala",
    "GAU": "Asp", "GAC": "Asp", "GAA": "Glu", "GAG": "Glu",
    "GGU": "Gly", "GGC": "Gly", "GGA": "Gly", "GGG": "Gly",
}


def n_to_hyo_bits(n: int) -> str:
    return "".join(str((n >> i) & 1) for i in range(6))


def bits_to_codon(bits: str) -> str:
    return BITS_TO_BASE[bits[0:2]] + BITS_TO_BASE[bits[2:4]] + BITS_TO_BASE[bits[4:6]]


def n_to_codon(n: int) -> str:
    return bits_to_codon(n_to_hyo_bits(n))


def codon_to_n(codon: str) -> int:
    codon = codon.upper().replace("T", "U")
    bits = "".join(BASE_TO_BITS[b] for b in codon)
    value = 0
    for i, bit in enumerate(bits):
        if bit == "1":
            value += 1 << i
    return value


def q6_neighbors(n: int) -> List[int]:
    return [n ^ (1 << i) for i in range(6)]


def h34_neighbors_count() -> int:
    # codon 3 positions, each position has 3 alternatives = degree 9
    return 9


assert n_to_codon(0) == "GGG"
assert n_to_codon(9) == "AUG"
assert n_to_codon(18) == "UGA"
assert n_to_codon(63) == "CCC"
assert codon_to_n("AUG") == 9


# ============================================================
# 2. 경혈 361 DB: 기본 생성 + 핵심 혈위 임상 해설 override
# ============================================================

MERIDIAN_COUNTS: List[Dict[str, Any]] = [
    {"prefix": "LU", "경락": "수태음폐경", "count": 11, "부위군": "상지·흉부", "axis": "보충축, 소통·전환축", "default_meaning": "폐기·호흡·표증 방향 참고", "default_caution": "흉부 깊은 자침 주의"},
    {"prefix": "LI", "경락": "수양명대장경", "count": 20, "부위군": "상지·두면", "axis": "소통·전환축, 배출·이수축", "default_meaning": "두면부·표증·기기 소통 참고", "default_caution": "임신 가능성·강자극 주의"},
    {"prefix": "ST", "경락": "족양명위경", "count": 45, "부위군": "두면·흉복·하지", "axis": "보충축, 완충·조화축", "default_meaning": "비위·기혈·소화 방향 참고", "default_caution": "복부·안면부 시술 주의"},
    {"prefix": "SP", "경락": "족태음비경", "count": 21, "부위군": "하지·복부", "axis": "보충축, 수렴·안정축", "default_meaning": "비·혈·수습 조절 방향 참고", "default_caution": "임신 가능성·복부 상태 확인"},
    {"prefix": "HT", "경락": "수소음심경", "count": 9, "부위군": "상지", "axis": "수렴·안정축", "default_meaning": "심신 안정·수면 방향 참고", "default_caution": "강자극 주의"},
    {"prefix": "SI", "경락": "수태양소장경", "count": 19, "부위군": "상지·견갑·두면", "axis": "소통·전환축", "default_meaning": "견배부·두면부 소통 방향 참고", "default_caution": "견갑부·경부 시술 주의"},
    {"prefix": "BL", "경락": "족태양방광경", "count": 67, "부위군": "두항·배부·하지", "axis": "소통·전환축, 완충·조화축", "default_meaning": "배수혈·척추·후면부 조절 참고", "default_caution": "흉배부 깊은 자침 주의"},
    {"prefix": "KI", "경락": "족소음신경", "count": 27, "부위군": "하지·흉복", "axis": "보충축, 수렴·안정축", "default_meaning": "신음·신기·하초 방향 참고", "default_caution": "허열·임신 관련 상태 확인"},
    {"prefix": "PC", "경락": "수궐음심포경", "count": 9, "부위군": "상지·흉부", "axis": "수렴·안정축, 소통·전환축", "default_meaning": "흉격·심신·오심 방향 참고", "default_caution": "강자극 주의"},
    {"prefix": "TE", "경락": "수소양삼초경", "count": 23, "부위군": "상지·측두", "axis": "소통·전환축", "default_meaning": "소양·수도·측두부 방향 참고", "default_caution": "경부·두면부 시술 주의"},
    {"prefix": "GB", "경락": "족소양담경", "count": 44, "부위군": "측두·협륵·하지", "axis": "소통·전환축", "default_meaning": "소양·담·측부 긴장 방향 참고", "default_caution": "임신 가능성·두면부 시술 주의"},
    {"prefix": "LR", "경락": "족궐음간경", "count": 14, "부위군": "하지·복부·협륵", "axis": "소통·전환축, 완충·조화축", "default_meaning": "간기·혈·정서 긴장 방향 참고", "default_caution": "복부·임신 상태 확인"},
    {"prefix": "DU", "경락": "독맥", "count": 28, "부위군": "척추·두면", "axis": "승양·상승축", "default_meaning": "양기·척추·두면부 방향 참고", "default_caution": "두부·척추 시술 주의"},
    {"prefix": "CV", "경락": "임맥", "count": 24, "부위군": "전정중선·복부·흉부", "axis": "보충축, 수렴·안정축", "default_meaning": "하초·임맥·복부 방향 참고", "default_caution": "복부·임신·심혈관 상태 확인"},
]

ACU_OVERRIDES: Dict[str, Dict[str, str]] = {
    "LU1": {"혈명": "중부", "standard_name": "Zhongfu", "임상 의미": "폐기·흉부 답답함·기침 방향 참고", "주의점": "흉부 깊은 자침 주의", "왜 후보인가": "폐기와 흉부 소통을 볼 때 참고 후보"},
    "LU7": {"혈명": "열결", "standard_name": "Lieque", "임상 의미": "폐기 소통, 표증, 항강, 기침 방향 참고", "주의점": "강자극 주의", "왜 후보인가": "표증·폐기 소통이 필요할 때 참고 후보"},
    "LI4": {"혈명": "합곡", "standard_name": "Hegu", "임상 의미": "두면부, 표증, 통증, 기기 소통 방향 참고", "주의점": "임신 가능성 확인, 강자극 주의", "왜 후보인가": "표증·두면부·기체 소견이 있을 때 참고 후보"},
    "LI11": {"혈명": "곡지", "standard_name": "Quchi", "임상 의미": "열감, 피부, 표리 열 조절 방향 참고", "주의점": "허약자 강자극 주의", "왜 후보인가": "열감·피부 소견이 뚜렷할 때 참고 후보"},
    "ST25": {"혈명": "천추", "standard_name": "Tianshu", "임상 의미": "복부 팽만, 대변 이상, 장부 소통 방향 참고", "주의점": "복부 수술력·임신 상태 확인", "왜 후보인가": "복부 팽만·변비·설사와 연결될 때 참고 후보"},
    "ST36": {"혈명": "족삼리", "standard_name": "Zusanli", "임상 의미": "비위 보강, 기혈 보강, 피로·소화 방향 참고", "주의점": "실열·강자극 필요성 재검토", "왜 후보인가": "기허·비위 허약·회복 저하와 연결될 때 핵심 후보"},
    "ST40": {"혈명": "풍륭", "standard_name": "Fenglong", "임상 의미": "담음, 흉민, 어지럼, 습담 방향 참고", "주의점": "허약자 강자극 주의", "왜 후보인가": "담음·흉민·어지럼이 뚜렷할 때 참고 후보"},
    "SP3": {"혈명": "태백", "standard_name": "Taibai", "임상 의미": "비기 보강, 소화력 저하 방향 참고", "주의점": "습체·식체 동반 여부 확인", "왜 후보인가": "비허·소화력 저하가 중심일 때 참고 후보"},
    "SP6": {"혈명": "삼음교", "standard_name": "Sanyinjiao", "임상 의미": "비·간·신 조절, 혈·음·수습 조절, 하초·부인과 방향 보조", "주의점": "임신 가능성·임신 중 사용은 전문가 판단", "왜 후보인가": "음혈·수습·하초 방향을 동시에 다루는 핵심 교회혈 후보"},
    "SP9": {"혈명": "음릉천", "standard_name": "Yinlingquan", "임상 의미": "수습, 부종, 소변불리, 습담 방향 참고", "주의점": "허약자 강자극 주의", "왜 후보인가": "수습 정체·부종·소변불리와 연결될 때 참고 후보"},
    "HT7": {"혈명": "신문", "standard_name": "Shenmen", "임상 의미": "심신 안정, 불면, 불안, 건망 방향 참고", "주의점": "수면제·진정제 병용 확인", "왜 후보인가": "불면·불안·심계가 중심일 때 핵심 후보"},
    "SI3": {"혈명": "후계", "standard_name": "Houxi", "임상 의미": "독맥, 항배강, 척추 후면 소통 방향 참고", "주의점": "강자극 주의", "왜 후보인가": "항강·후면부 긴장과 연결될 때 참고 후보"},
    "BL13": {"혈명": "폐수", "standard_name": "Feishu", "임상 의미": "폐기·기침·호흡 방향 참고", "주의점": "흉배부 깊은 자침 주의", "왜 후보인가": "폐기와 호흡 문제가 동반될 때 참고 후보"},
    "BL15": {"혈명": "심수", "standard_name": "Xinshu", "임상 의미": "심신 안정, 불면, 심계 방향 참고", "주의점": "흉배부 깊은 자침 주의", "왜 후보인가": "불면·심계·정서 긴장이 있을 때 참고 후보"},
    "BL18": {"혈명": "간수", "standard_name": "Ganshu", "임상 의미": "간혈·간음 조절, 정서 긴장과 혈분 조절 보조", "주의점": "흉배부 깊은 자침 주의", "왜 후보인가": "간신음허·혈허·협륵 긴장과 연결될 때 보조 후보"},
    "BL20": {"혈명": "비수", "standard_name": "Pishu", "임상 의미": "비위 보강, 소화력 저하, 피로 방향 참고", "주의점": "흉배부 깊은 자침 주의", "왜 후보인가": "비허·소화력 저하가 중심일 때 핵심 후보"},
    "BL21": {"혈명": "위수", "standard_name": "Weishu", "임상 의미": "위기 조절, 위완부 불편, 식체 방향 참고", "주의점": "흉배부 깊은 자침 주의", "왜 후보인가": "위장 부담·식체·더부룩함이 있을 때 참고 후보"},
    "BL23": {"혈명": "신수", "standard_name": "Shenshu", "임상 의미": "신허·하초 허약 보조, 요슬산연, 만성 허약 방향", "주의점": "요부 심부 자침 위험, 신장 부위 해부학적 안전 확인", "왜 후보인가": "신허와 하초 허약을 배수혈에서 보조하기 위한 핵심 후보"},
    "BL25": {"혈명": "대장수", "standard_name": "Dachangshu", "임상 의미": "장 기능, 요부, 대변 이상 방향 참고", "주의점": "요부 시술 주의", "왜 후보인가": "대변 이상·요부 증상 동반 시 참고 후보"},
    "BL40": {"혈명": "위중", "standard_name": "Weizhong", "임상 의미": "요배부 통증, 하지 후면 긴장 방향 참고", "주의점": "혈관·피부 상태 확인", "왜 후보인가": "요배부 통증이 뚜렷할 때 참고 후보"},
    "BL52": {"혈명": "지실", "standard_name": "Zhishi", "임상 의미": "신허·요부 허약·정지 방향 보조", "주의점": "요부 심부 자침 주의", "왜 후보인가": "하초 허약·요슬산연과 연결될 때 보조 후보"},
    "BL60": {"혈명": "곤륜", "standard_name": "Kunlun", "임상 의미": "요배부, 하지 후면, 두항부 소통 방향 참고", "주의점": "임신 가능성 확인, 강자극 주의", "왜 후보인가": "요배부·후면부 긴장과 연결될 때 참고 후보"},
    "KI3": {"혈명": "태계", "standard_name": "Taixi", "임상 의미": "신음·신기 보강, 허열 완충, 요슬산연·하초 허약 방향 보조", "주의점": "허열·음허·임신 관련 상태 확인", "왜 후보인가": "자음·보신 처방에서 핵심 후보. 하초 허약과 허열 완충 방향에 맞음"},
    "KI6": {"혈명": "조해", "standard_name": "Zhaohai", "임상 의미": "음교맥, 수면·허열·음혈 부족 방향 보조", "주의점": "허열·음허 상태 확인, 강한 뜸은 신중", "왜 후보인가": "음허·허열·수면 불안정이 동반될 때 보조 후보"},
    "KI7": {"혈명": "복류", "standard_name": "Fuliu", "임상 의미": "신기 조절, 자한·도한, 수분대사 방향 참고", "주의점": "부종·소변 상태 확인", "왜 후보인가": "도한·자한·수분대사와 연결될 때 참고 후보"},
    "PC6": {"혈명": "내관", "standard_name": "Neiguan", "임상 의미": "흉민, 심계, 오심, 불안 방향 참고", "주의점": "강자극 주의", "왜 후보인가": "흉민·오심·불안이 동반될 때 핵심 후보"},
    "TE5": {"혈명": "외관", "standard_name": "Waiguan", "임상 의미": "소양, 외감, 측두부, 표리 소통 방향 참고", "주의점": "강자극 주의", "왜 후보인가": "외감·소양 긴장과 연결될 때 참고 후보"},
    "GB20": {"혈명": "풍지", "standard_name": "Fengchi", "임상 의미": "두항부 긴장, 어지럼, 풍증 방향 참고", "주의점": "경부 깊은 자침 주의", "왜 후보인가": "두항부 긴장·어지럼이 있을 때 참고 후보"},
    "GB34": {"혈명": "양릉천", "standard_name": "Yanglingquan", "임상 의미": "근·담·소양 소통, 측부 긴장 방향 참고", "주의점": "강자극 주의", "왜 후보인가": "근긴장·협륵·소양 소견이 있을 때 참고 후보"},
    "LR3": {"혈명": "태충", "standard_name": "Taichong", "임상 의미": "간기 소통, 정서 긴장, 두통·협륵 방향 참고", "주의점": "허약자 강자극 주의", "왜 후보인가": "간울·스트레스·협륵 긴장과 연결될 때 핵심 후보"},
    "LR8": {"혈명": "곡천", "standard_name": "Ququan", "임상 의미": "간혈·간음, 습열·하초 방향 참고", "주의점": "무릎 주변 시술 안전 확인", "왜 후보인가": "간혈·간음 부족과 하초 소견이 동반될 때 참고 후보"},
    "DU20": {"혈명": "백회", "standard_name": "Baihui", "임상 의미": "승양, 두정, 처짐, 정신 피로 방향 참고", "주의점": "두부 시술 안전 확인", "왜 후보인가": "중기하함·처짐·무력감과 연결될 때 참고 후보"},
    "DU14": {"혈명": "대추", "standard_name": "Dazhui", "임상 의미": "표증, 양기, 열감 방향 참고", "주의점": "실열·염증 상태 확인", "왜 후보인가": "외감·표증·양기 조절과 연결될 때 참고 후보"},
    "CV4": {"혈명": "관원", "standard_name": "Guanyuan", "임상 의미": "하초 보강, 정혈·원기 보강, 허약·냉감 방향", "주의점": "복부 수술력, 임신, 심혈관 상태 확인", "왜 후보인가": "하초 허약과 정혈 부족 방향에서 보조 후보"},
    "CV6": {"혈명": "기해", "standard_name": "Qihai", "임상 의미": "원기 보강, 기허 조절, 하복부 허약 보조", "주의점": "복부 열감, 임신, 염증 상태 확인", "왜 후보인가": "기허·피로·하복부 무력감이 동반될 때 보조 후보"},
    "CV12": {"혈명": "중완", "standard_name": "Zhongwan", "임상 의미": "위완부, 소화력, 담음·식체 방향 참고", "주의점": "복부 수술력·임신 상태 확인", "왜 후보인가": "소화불량·더부룩함·위완부 불편이 중심일 때 핵심 후보"},
    "CV17": {"혈명": "전중", "standard_name": "Danzhong", "임상 의미": "흉격, 호흡, 기울, 심계 방향 참고", "주의점": "흉부 시술 주의", "왜 후보인가": "흉민·호흡·기울 소견이 있을 때 참고 후보"},
}


def build_acupoints_361() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for meta in MERIDIAN_COUNTS:
        prefix = meta["prefix"]
        for i in range(1, int(meta["count"]) + 1):
            code = f"{prefix}{i}"
            base = {
                "code": code,
                "혈명": code,
                "standard_name": code,
                "경락": meta["경락"],
                "부위군": meta["부위군"],
                "처방 방향축": meta["axis"],
                "임상 의미": meta["default_meaning"],
                "주의점": meta["default_caution"],
                "왜 후보인가": "전체 DB 참고 항목. 처방별 핵심 후보 여부는 앞의 후보표에서 우선 확인",
            }
            if code in ACU_OVERRIDES:
                base.update(ACU_OVERRIDES[code])
            rows.append(base)
    return rows


ACUPOINT_361 = build_acupoints_361()
assert len(ACUPOINT_361) == 361


def acu(code: str) -> Dict[str, str]:
    for row in ACUPOINT_361:
        if row["code"] == code:
            return row
    return {
        "code": code,
        "혈명": code,
        "standard_name": code,
        "경락": "",
        "부위군": "",
        "처방 방향축": "",
        "임상 의미": "추가 확인 필요",
        "주의점": "한의사 확인",
        "왜 후보인가": "처방별 후보 근거 확인 필요",
    }


# ============================================================
# 3. 처방 데이터
# ============================================================

FORMULAS: Dict[str, Dict[str, Any]] = {
    "육미지황환": {
        "분류": "보음·자음 처방",
        "전통 변증": "간신음허, 허열도한, 정혈 부족, 하초 허약",
        "처방 방향": "자음, 보신, 허열 완충, 수렴·안정",
        "구성 약재": "숙지황, 산수유, 산약, 복령, 택사, 목단피",
        "잘 맞는 환자상": "요슬산연, 도한, 오심번열, 구건, 만성 피로, 음허성 열감",
        "주의 환자상": "설사, 식체, 더부룩함, 소화력 저하, 몸이 무겁고 습담이 뚜렷한 경우",
        "감별 처방": "십전대보탕, 팔미지황환, 보중익기탕, 소요산",
        "가감 방향": "허열이 뚜렷하면 청허열 방향, 소화력이 약하면 보비·화습 방향 보조 검토",
        "핵심 혈위": ["KI3", "BL23", "BL18", "SP6", "CV4", "CV6", "KI6"],
        "핵심 혈위 수": 7,
        "뜸 가능 조건": "하복부 냉감, 하초 허한, 요슬 냉통이 분명하고 열감·도한이 약할 때 제한 검토",
        "뜸 주의 조건": "도한, 오심번열, 구건, 오후 열감, 붉은 혀, 열성 피부질환이 있으면 강한 뜸 주의",
        "권장 강도": "약~중. 허열이 동반되면 보류 또는 매우 약하게 검토",
        "환자 설명": "몸 아래쪽의 허약감, 마른 열감, 도한, 입마름 같은 상태를 전통 한의학적으로 보완하는 방향에서 검토됩니다. 소화력이 약한 분은 더부룩함이나 설사가 생길 수 있어 복용 후 소화 상태를 꼭 관찰해야 합니다.",
        "동의보감": [
            {"동의보감 편제": "신(腎)·허로(虛勞)·정(精)", "연결 이유": "간신 부족, 허로, 정혈 부족 편제와 연결 가능"},
            {"동의보감 편제": "내상", "연결 이유": "소화력이 약한 경우 비위 내상 관점과 함께 재검토"},
        ],
        "황제내경": [
            {"개념": "음양", "해석": "부족한 음분과 과한 허열의 균형 확인", "한의사 질문": "실제 열인가, 부족에서 생긴 열감인가?"},
            {"개념": "장부·기혈진액", "해석": "간·신·정혈·진액의 부족과 소모 확인", "한의사 질문": "허리·무릎, 도한, 구건, 소변 상태는 어떤가?"},
            {"개념": "개합추", "해석": "수렴과 저장 기능이 약해진 상태 확인", "한의사 질문": "땀·수면·정서·소변의 새는 양상이 있는가?"},
        ],
    },
    "팔진탕": {
        "분류": "기혈쌍보 처방",
        "전통 변증": "기혈양허, 만성피로, 안색창백, 어지럼, 식욕저하",
        "처방 방향": "보기, 보혈, 기혈쌍보, 균형 보강",
        "구성 약재": "사군자탕 + 사물탕",
        "잘 맞는 환자상": "피로, 안색창백, 어지럼, 식욕저하, 회복력 저하",
        "주의 환자상": "식체, 습담, 실열, 소화력 저하가 뚜렷한 경우",
        "감별 처방": "보중익기탕, 십전대보탕, 귀비탕, 사물탕",
        "가감 방향": "소화력이 약하면 보비·화습 방향, 혈허가 뚜렷하면 보혈 방향 확인",
        "핵심 혈위": ["ST36", "SP6", "BL20", "BL17", "CV12", "CV6"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "허한·냉감·기허가 분명할 때 제한적으로 검토",
        "뜸 주의 조건": "실열, 습열, 염증성 열감, 식체가 뚜렷하면 강한 온보 자극 주의",
        "권장 강도": "약~중. 소화 부담이 있으면 복부 반응 확인",
        "환자 설명": "기운과 혈이 함께 부족한 양상을 보완하는 방향에서 검토됩니다. 식체나 더부룩함이 있으면 먼저 소화 상태를 확인해야 합니다.",
        "동의보감": [{"동의보감 편제": "허로·기혈", "연결 이유": "기혈 부족과 회복력 저하 해석에 연결"}],
        "황제내경": [{"개념": "기혈", "해석": "기와 혈의 동시 부족 확인", "한의사 질문": "피로와 혈허 소견이 함께 있는가?"}],
    },
    "십전대보탕": {
        "분류": "대보원기·기혈쌍보 처방",
        "전통 변증": "기혈양허, 허로, 허한, 수술·질병 후 회복 저하",
        "처방 방향": "대보원기, 기혈쌍보, 온보",
        "구성 약재": "팔진탕 + 황기 + 육계",
        "잘 맞는 환자상": "허약, 피로, 추위 탐, 회복 지연, 안색 저하",
        "주의 환자상": "열감, 염증, 고혈압 변동, 상열감, 소화력 저하",
        "감별 처방": "팔진탕, 보중익기탕, 귀비탕",
        "가감 방향": "열감이 있으면 온보 강도 재검토, 소화불량 시 비위 보조",
        "핵심 혈위": ["ST36", "CV6", "CV4", "BL20", "BL23", "DU20"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "허한·냉감·회복저하가 분명하고 염증성 열감이 없을 때 검토",
        "뜸 주의 조건": "상열감, 고혈압 변동, 염증성 열감, 피부 열감이 있으면 강한 뜸 주의",
        "권장 강도": "약~중. 허한이 명확해도 반응을 보며 단계적 적용",
        "환자 설명": "전반적인 기력과 회복력이 떨어진 상태를 보완하는 방향에서 검토됩니다. 열감이나 혈압 변동이 있으면 온보 방향을 신중히 봐야 합니다.",
        "동의보감": [{"동의보감 편제": "허로·기혈", "연결 이유": "큰 병 이후 회복 저하와 기혈 허약 해석에 연결"}],
        "황제내경": [{"개념": "정기", "해석": "정기 부족과 회복력 저하 확인", "한의사 질문": "허한과 회복 지연이 분명한가?"}],
    },
    "보중익기탕": {
        "분류": "보기·승양 처방",
        "전통 변증": "비위기허, 중기하함, 기허발열, 만성피로",
        "처방 방향": "보기, 승양, 중기 보강, 비위 회복",
        "구성 약재": "황기, 인삼, 백출, 감초, 당귀, 진피, 승마, 시호",
        "잘 맞는 환자상": "피로, 무력, 식욕저하, 처짐, 기단, 자한",
        "주의 환자상": "상열감, 불면, 심계, 고혈압 변동, 실열·습열",
        "감별 처방": "팔진탕, 십전대보탕, 사군자탕, 귀비탕",
        "가감 방향": "상열감이 있으면 승양 강도 재검토, 담음·식체가 있으면 이기화담 방향 보조",
        "핵심 혈위": ["ST36", "CV6", "DU20", "BL20", "CV12", "LI4"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "중기하함, 허한, 기허가 분명하고 상열감이 없을 때 검토",
        "뜸 주의 조건": "상열감, 불면, 심계, 고혈압 변동, 실열이 있으면 강한 뜸 주의",
        "권장 강도": "약. 승양 처방이므로 과한 온보는 피함",
        "환자 설명": "기운이 아래로 처지고 쉽게 지치며 식욕이 떨어지는 상태를 보완하는 방향에서 검토됩니다. 얼굴 열감, 두근거림, 불면이 있으면 반드시 알려야 합니다.",
        "동의보감": [{"동의보감 편제": "내상·비위·허로", "연결 이유": "비위기허와 중기하함 해석에 연결"}],
        "황제내경": [{"개념": "승강출입", "해석": "아래로 처진 기운을 위로 끌어올리는 방향 확인", "한의사 질문": "처짐·무력·하수감이 중심인가?"}],
    },
    "산조인탕": {
        "분류": "양혈안신 처방",
        "전통 변증": "허번불면, 혈허, 음허 내열, 심간 불안",
        "처방 방향": "수렴, 안신, 내부 안정, 허열 완충",
        "구성 약재": "산조인, 지모, 복령, 천궁, 감초",
        "잘 맞는 환자상": "잠을 깊이 못 잠, 심계, 불안, 건망, 피로, 허번",
        "주의 환자상": "실열성 흥분, 과도한 졸림, 진정제 병용, 운전·기계 조작",
        "감별 처방": "귀비탕, 천왕보심단, 온담탕",
        "가감 방향": "담음·흉민이 있으면 화담 방향, 심비양허면 귀비탕 방향 검토",
        "핵심 혈위": ["HT7", "PC6", "BL15", "SP6", "KI6", "CV17"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "불면이 허한·허약과 함께 있고 열감이 뚜렷하지 않을 때 매우 약하게 검토",
        "뜸 주의 조건": "오심번열, 불안 흥분, 얼굴 열감, 구건, 진정제 병용 시 강한 뜸 주의",
        "권장 강도": "보류~약. 안신 처방에서는 강자극보다 안정·완만한 접근",
        "환자 설명": "잠이 얕고 마음이 불안하며 피로가 동반되는 상태를 안정시키는 방향에서 검토됩니다. 수면제나 진정제를 복용 중이면 반드시 알려야 합니다.",
        "동의보감": [{"동의보감 편제": "신문·수면", "연결 이유": "불면, 심계, 불안, 정신 피로 해석에 연결"}],
        "황제내경": [{"개념": "심신", "해석": "심신 불안과 음혈 부족을 함께 확인", "한의사 질문": "불면이 허증인지 실열성 흥분인지 구분되는가?"}],
    },
    "귀비탕": {
        "분류": "심비양허·기혈보강 처방",
        "전통 변증": "심비양허, 불면, 건망, 심계, 식욕저하, 피로",
        "처방 방향": "보기, 보혈, 안신, 심비 보강",
        "구성 약재": "인삼, 황기, 백출, 복령, 산조인, 용안육, 목향, 감초 등",
        "잘 맞는 환자상": "불면, 건망, 심계, 피로, 식욕저하, 안색창백",
        "주의 환자상": "담음·식체, 실열, 소화력 저하, 과도한 졸림",
        "감별 처방": "산조인탕, 팔진탕, 보중익기탕",
        "가감 방향": "식체가 있으면 이기화담, 불면이 중심이면 안신 방향 보조",
        "핵심 혈위": ["HT7", "PC6", "ST36", "BL20", "SP6", "CV12"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "심비양허와 허한이 동반될 때 약하게 검토",
        "뜸 주의 조건": "불면이 흥분·실열성일 때, 진정제 병용 시 강자극 주의",
        "권장 강도": "약. 수면·심계 반응을 확인",
        "환자 설명": "피로와 식욕저하, 잠 문제, 두근거림처럼 기혈과 마음의 안정이 함께 약해진 양상을 보완하는 방향에서 검토됩니다.",
        "동의보감": [{"동의보감 편제": "심·비·허로", "연결 이유": "심비양허와 건망·불면 해석에 연결"}],
        "황제내경": [{"개념": "심비", "해석": "생각 과다와 소화력 저하가 함께 있는지 확인", "한의사 질문": "불면과 식욕저하가 함께 있는가?"}],
    },
    "사군자탕": {
        "분류": "보기건비 처방",
        "전통 변증": "비위기허, 식욕저하, 피로, 무력, 대변 무른 경향",
        "처방 방향": "보기, 건비, 중초 보강",
        "구성 약재": "인삼, 백출, 복령, 감초",
        "잘 맞는 환자상": "식욕저하, 피로, 무력, 묽은 변, 소화력 저하",
        "주의 환자상": "식체, 습담, 실열, 복부 팽만이 심한 경우",
        "감별 처방": "보중익기탕, 팔진탕, 이진탕, 평위산",
        "가감 방향": "담음이 뚜렷하면 이진탕, 식체가 뚜렷하면 평위산 방향 검토",
        "핵심 혈위": ["ST36", "CV12", "BL20", "SP3", "CV6"],
        "핵심 혈위 수": 5,
        "뜸 가능 조건": "복부 냉감·허한·비위기허가 분명할 때 검토",
        "뜸 주의 조건": "식체·습열·염증성 열감이 있으면 강한 뜸 주의",
        "권장 강도": "약~중. 복부 반응 확인",
        "환자 설명": "소화력과 기운이 약해 쉽게 피곤하고 식욕이 떨어지는 상태를 보완하는 방향에서 검토됩니다.",
        "동의보감": [{"동의보감 편제": "비위·내상", "연결 이유": "비위기허와 소화력 저하 해석에 연결"}],
        "황제내경": [{"개념": "중초", "해석": "중초의 운화 기능 저하 확인", "한의사 질문": "식욕·대변·피로가 함께 약한가?"}],
    },
    "사물탕": {
        "분류": "보혈조혈 처방",
        "전통 변증": "혈허, 어지럼, 안색창백, 월경량 감소, 건조",
        "처방 방향": "보혈, 조혈, 혈분 완충",
        "구성 약재": "숙지황, 당귀, 천궁, 작약",
        "잘 맞는 환자상": "혈허, 어지럼, 안색창백, 건조, 월경 관련 소견",
        "주의 환자상": "식체, 설사, 습담, 어혈 통증이 강한 경우",
        "감별 처방": "팔진탕, 귀비탕, 소요산",
        "가감 방향": "기허가 있으면 보기 보조, 어혈이 있으면 활혈 방향 확인",
        "핵심 혈위": ["SP6", "BL17", "LR8", "ST36", "BL20"],
        "핵심 혈위 수": 5,
        "뜸 가능 조건": "혈허와 냉감이 함께 있을 때 제한 검토",
        "뜸 주의 조건": "열감·염증·출혈 경향이 있으면 강한 뜸 주의",
        "권장 강도": "약. 혈허와 열감 여부를 함께 확인",
        "환자 설명": "혈이 부족해 어지럽거나 건조하고 피로한 양상을 보완하는 방향에서 검토됩니다.",
        "동의보감": [{"동의보감 편제": "혈·부인", "연결 이유": "혈허와 월경 관련 소견 해석에 연결"}],
        "황제내경": [{"개념": "혈", "해석": "혈분 부족과 건조 확인", "한의사 질문": "안색·어지럼·건조가 함께 있는가?"}],
    },
    "소요산": {
        "분류": "소간해울·건비조혈 처방",
        "전통 변증": "간울혈허, 스트레스성 흉협불편, 월경 전후 불편, 소화불량",
        "처방 방향": "소간, 해울, 건비, 조화",
        "구성 약재": "시호, 당귀, 작약, 백출, 복령, 감초, 생강, 박하",
        "잘 맞는 환자상": "스트레스성 흉협불편, 답답함, 월경 관련 불편, 소화불량",
        "주의 환자상": "허열이 심하거나 상열감이 강한 경우, 식체·담음이 중심인 경우",
        "감별 처방": "가미소요산, 귀비탕, 이진탕, 평위산",
        "가감 방향": "허열이 뚜렷하면 청허열 방향, 소화력이 약하면 건비 방향 보조",
        "핵심 혈위": ["LR3", "PC6", "SP6", "ST36", "CV12", "GB34"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "냉감·허한이 동반될 때만 제한 검토",
        "뜸 주의 조건": "상열감, 흉민, 화병 양상, 얼굴 열감이 뚜렷하면 강한 뜸 주의",
        "권장 강도": "보류~약. 소통 처방에서는 온보보다 이완·조화 우선",
        "환자 설명": "스트레스와 긴장으로 답답함이나 소화 불편이 생기는 양상을 조화시키는 방향에서 검토됩니다.",
        "동의보감": [{"동의보감 편제": "기·울·부인", "연결 이유": "간울과 월경 전후 불편 해석에 연결"}],
        "황제내경": [{"개념": "소통", "해석": "막힌 기혈과 비위 흐름 확인", "한의사 질문": "스트레스와 소화불량이 함께 움직이는가?"}],
    },
    "이진탕": {
        "분류": "화담이기 처방",
        "전통 변증": "담음정체, 오심구토, 어지럼, 흉민, 습담",
        "처방 방향": "조습, 화담, 이기, 위기 하강",
        "구성 약재": "반하, 진피, 복령, 감초, 생강, 오매",
        "잘 맞는 환자상": "가래, 오심, 더부룩함, 어지럼, 흉민, 습담",
        "주의 환자상": "음허건조, 진액 부족, 강한 열감, 임신 중 구토는 별도 확인",
        "감별 처방": "평위산, 온담탕, 소요산",
        "가감 방향": "식체가 중심이면 평위산 방향, 불안·심계가 있으면 온담탕 방향",
        "핵심 혈위": ["ST40", "PC6", "CV12", "ST36", "SP9"],
        "핵심 혈위 수": 5,
        "뜸 가능 조건": "습담과 냉감이 뚜렷할 때 제한 검토",
        "뜸 주의 조건": "구건·음허·열감·염증성 구토가 있으면 강한 뜸 주의",
        "권장 강도": "약. 담음·냉감 여부 확인 후 검토",
        "환자 설명": "몸속의 담음과 더부룩함, 오심, 어지럼 같은 양상을 정리하는 방향에서 검토됩니다.",
        "동의보감": [{"동의보감 편제": "담음·비위", "연결 이유": "담음과 위기 불화 해석에 연결"}],
        "황제내경": [{"개념": "담음", "해석": "습담과 위기 상역 확인", "한의사 질문": "오심·가래·어지럼·더부룩함이 함께 있는가?"}],
    },
    "평위산": {
        "분류": "조습화위 처방",
        "전통 변증": "비위습탁, 식체, 복부팽만, 더부룩함, 무거움",
        "처방 방향": "조습, 행기, 소도, 비위 소통",
        "구성 약재": "창출, 후박, 진피, 감초, 생강, 대조",
        "잘 맞는 환자상": "복부팽만, 더부룩함, 식체, 몸 무거움, 습담",
        "주의 환자상": "음허건조, 위음 부족, 심한 구건, 허약자",
        "감별 처방": "이진탕, 사군자탕, 보중익기탕",
        "가감 방향": "기허가 중심이면 사군자탕, 담음이 중심이면 이진탕 방향",
        "핵심 혈위": ["CV12", "ST25", "ST36", "SP9", "ST40"],
        "핵심 혈위 수": 5,
        "뜸 가능 조건": "습담·냉감·복부 냉통이 분명할 때 제한 검토",
        "뜸 주의 조건": "건조, 구건, 열감, 음허 경향이 있으면 강한 뜸 주의",
        "권장 강도": "약. 복부 반응 확인",
        "환자 설명": "더부룩함, 식체, 몸이 무거운 습담 양상을 정리하는 방향에서 검토됩니다.",
        "동의보감": [{"동의보감 편제": "비위·습", "연결 이유": "습탁과 비위 운화 장애 해석에 연결"}],
        "황제내경": [{"개념": "습", "해석": "중초 습탁과 운화 저하 확인", "한의사 질문": "무거움·더부룩함·식체가 중심인가?"}],
    },
    "오령산": {
        "분류": "이수삼습 처방",
        "전통 변증": "수습정체, 소변불리, 부종, 갈증·구토, 수분대사 장애",
        "처방 방향": "이수, 삼습, 수분대사 조절, 기화 보조",
        "구성 약재": "택사, 저령, 복령, 백출, 계지",
        "잘 맞는 환자상": "소변불리, 부종, 몸이 무거움, 갈증·구토, 수분 정체",
        "주의 환자상": "탈수, 신장 기능 저하, 전해질 이상, 이뇨제 병용",
        "감별 처방": "저령탕, 평위산, 이진탕",
        "가감 방향": "건조·탈수 소견이면 이수 강도 재검토, 습담이면 화담 방향 보조",
        "핵심 혈위": ["SP9", "CV6", "CV4", "BL23", "KI7", "ST36"],
        "핵심 혈위 수": 6,
        "뜸 가능 조건": "냉감·허한·소변불리가 함께 있을 때 제한 검토",
        "뜸 주의 조건": "탈수, 열감, 신장 기능 저하, 이뇨제 병용 시 신중",
        "권장 강도": "보류~약. 수분상태와 신장 기능 확인",
        "환자 설명": "몸의 수분 정체와 소변 상태를 전통 한의학적으로 조절하는 방향에서 검토됩니다. 신장 기능이나 이뇨제 복용 여부를 꼭 확인해야 합니다.",
        "동의보감": [{"동의보감 편제": "수종·소변", "연결 이유": "수습정체와 소변불리 해석에 연결"}],
        "황제내경": [{"개념": "수액", "해석": "수분의 정체와 기화 기능 확인", "한의사 질문": "부종·소변불리·갈증이 함께 있는가?"}],
    },
}


# 없는 BL17 override 보강
ACU_OVERRIDES.setdefault("BL17", {"혈명": "격수", "standard_name": "Geshu", "임상 의미": "혈회, 혈분 조절, 어혈·혈허 방향 참고", "주의점": "흉배부 깊은 자침 주의", "왜 후보인가": "혈허·혈분 조절이 필요할 때 핵심 후보"})
# override를 추가한 뒤 DB에 반영
ACUPOINT_361 = build_acupoints_361()


EXAMPLES: Dict[str, Dict[str, Any]] = {
    "육미지황환 테스트": {
        "formula": "육미지황환",
        "chief": "허리와 무릎이 약하고 오후에 열감이 있으며, 입마름과 도한이 있음. 피로가 오래가고 소변이 잦음.",
        "global_note": "만성피로와 회복력 저하를 주소로 내원함. 안색은 창백하고 쉽게 피로하며, 식욕저하와 가벼운 어지럼을 동반함. 맥은 허약하고 설질은 담백하고 치흔이 관찰됨.",
        "goal": "피로 회복, 허열 완충, 하초 허약 보조, 소화 부담 최소화",
        "pulse": "허맥, 세맥",
        "tongue": "건조, 소태",
        "abdomen": "하복부 무력",
        "bp": "118/76",
        "labs": "",
        "meds": "",
        "safety": ["만성 소화불량/설사"],
    },
    "보중익기탕 테스트": {
        "formula": "보중익기탕",
        "chief": "쉽게 지치고 식욕이 떨어지며 오후에 처지는 느낌이 있음. 기운이 아래로 빠지는 느낌과 자한이 있음.",
        "global_note": "비위기허와 중기하함 경향. 상열감은 크지 않으나 혈압약 복용 중.",
        "goal": "보기, 승양, 피로 회복, 식욕 개선",
        "pulse": "허맥",
        "tongue": "담백, 박태",
        "abdomen": "복부 무력",
        "bp": "132/82",
        "labs": "",
        "meds": "혈압약 복용",
        "safety": ["혈압약"],
    },
    "산조인탕 테스트": {
        "formula": "산조인탕",
        "chief": "잠을 깊게 못 자고 자주 깨며 심계와 불안이 있음. 낮에는 피로함.",
        "global_note": "허번불면, 심간 불안, 혈허 경향. 수면제 병용 여부 확인 필요.",
        "goal": "수면 안정, 불안 완화, 허열 완충",
        "pulse": "세맥",
        "tongue": "약간 건조",
        "abdomen": "특이 없음",
        "bp": "122/78",
        "labs": "",
        "meds": "",
        "safety": ["수면제/항우울제/진정제"],
    },
}

SAFETY_OPTIONS: List[str] = [
    "항응고제/항혈소판제/NSAIDs",
    "혈압약",
    "당뇨약",
    "수면제/항우울제/진정제",
    "면역억제제",
    "간·신장 기능 저하",
    "임신/수유",
    "소아/고령자/허약자",
    "만성 소화불량/설사",
    "피부 감각저하/당뇨성 말초신경병증",
    "수술/시술 예정",
    "실열/염증성 열감",
    "부종/소변불리",
    "알레르기/약물 과민반응",
    "다른 한약·건기식·보충제 병용",
]


# ============================================================
# 4. 판정/요약 함수
# ============================================================

def parse_bp(bp_text: str) -> Optional[Dict[str, int]]:
    if not bp_text:
        return None
    m = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", bp_text)
    if not m:
        return None
    return {"sbp": int(m.group(1)), "dbp": int(m.group(2))}


def safety_findings(formula_name: str, formula: Dict[str, Any], checked: List[str], bp: str, labs: str, meds: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    checked_set = set(checked)

    if "만성 소화불량/설사" in checked_set:
        rows.append({"확인 항목": "만성 소화불량/설사", "우선순위": "높음", "확인 내용": "보음·보혈·보약 처방의 위장 부담, 설사·복부팽만·식체 확인."})
    if "간·신장 기능 저하" in checked_set:
        rows.append({"확인 항목": "간·신장 기능 저하", "우선순위": "높음", "확인 내용": "장기 복용 전 AST/ALT, creatinine/eGFR 등 검사값 확인 권장."})
    if "임신/수유" in checked_set:
        rows.append({"확인 항목": "임신/수유", "우선순위": "높음", "확인 내용": "처방·침구·뜸 모두 전문가 판단 필요. SP6, LI4 등 강자극 주의."})
    if "수면제/항우울제/진정제" in checked_set:
        rows.append({"확인 항목": "진정계 약물", "우선순위": "중간~높음", "확인 내용": "산조인탕·귀비탕 등 안신 방향 처방은 졸림·반응저하를 확인."})
    if "항응고제/항혈소판제/NSAIDs" in checked_set:
        rows.append({"확인 항목": "항응고/항혈소판/NSAIDs", "우선순위": "중간~높음", "확인 내용": "출혈 경향, 멍, 침구 시술 후 지혈, 활혈 약재 포함 여부 확인."})
    if "혈압약" in checked_set:
        rows.append({"확인 항목": "혈압약", "우선순위": "중간", "확인 내용": "승양·온보 방향 처방 시 혈압 변동, 심계, 상열감 확인."})
    if "당뇨약" in checked_set:
        rows.append({"확인 항목": "당뇨약", "우선순위": "중간", "확인 내용": "혈당 변화, 식욕 변화, 말초신경병증·피부 감각저하 동반 여부 확인."})
    if "피부 감각저하/당뇨성 말초신경병증" in checked_set:
        rows.append({"확인 항목": "피부 감각저하", "우선순위": "높음", "확인 내용": "뜸·열자극 화상 위험. 온도감 확인과 보호자 안내 필요."})
    if "수술/시술 예정" in checked_set:
        rows.append({"확인 항목": "수술/시술 예정", "우선순위": "중간~높음", "확인 내용": "항응고제, NSAIDs, 침구 시술, 출혈·감염 위험 확인."})
    if not labs.strip():
        rows.append({"확인 항목": "검사값 미입력", "우선순위": "중간", "확인 내용": "장기 복용 전 AST/ALT, creatinine/eGFR 확인 권장."})
    if meds.strip():
        med_text = meds.lower()
        if any(x in med_text for x in ["aspirin", "아스피린", "와파린", "클로피도", "항응고"]):
            rows.append({"확인 항목": "복용약 출혈 관련 가능성", "우선순위": "높음", "확인 내용": "침구 시술, 활혈 약재, 수술 전후 출혈 위험 확인."})
    bpv = parse_bp(bp)
    if bpv:
        if bpv["sbp"] >= 160 or bpv["dbp"] >= 100:
            rows.append({"확인 항목": "혈압 높음", "우선순위": "높음", "확인 내용": f"입력 혈압 {bp}: 고혈압 상태 확인 후 처방·침구 자극 강도 조절."})
        elif bpv["sbp"] >= 140 or bpv["dbp"] >= 90:
            rows.append({"확인 항목": "혈압 경계/상승", "우선순위": "중간", "확인 내용": f"입력 혈압 {bp}: 승양·온보·강자극 전 재측정 권장."})
    if not rows:
        rows.append({"확인 항목": "특이 안전 신호 없음", "우선순위": "낮음", "확인 내용": "입력된 정보만으로는 큰 안전 신호가 자동 표시되지 않음. 문진·맥진·설진·검사값 재확인."})
    return rows


def safety_summary(rows: List[Dict[str, str]]) -> str:
    return "; ".join([f"{r['확인 항목']}({r['우선순위']})" for r in rows])


def core_acupoints(formula: Dict[str, Any]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for code in formula["핵심 혈위"]:
        a = acu(code)
        rows.append({
            "code": a["code"],
            "혈명": a["혈명"],
            "standard_name": a["standard_name"],
            "경락": a["경락"],
            "처방 방향축": a["처방 방향축"],
            "임상 의미": a["임상 의미"],
            "왜 후보인가": a["왜 후보인가"],
            "주의점": a["주의점"],
        })
    return rows


def moxa_point_rows(formula: Dict[str, Any]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for code in formula["핵심 혈위"]:
        a = acu(code)
        if code in ["KI3", "SP6", "KI6", "BL18"]:
            가능 = "제한적" if code in ["KI6", "BL18"] else "조건부 가능"
            강도 = "약"
            조건 = "허열·음허·구건·도한이 뚜렷하면 강한 뜸 주의"
        elif code in ["CV4", "CV6", "BL23", "ST36", "BL20", "CV12"]:
            가능 = "조건부 가능"
            강도 = "약~중"
            조건 = "하복부 냉감·허한이 분명할 때 제한 검토"
        elif code in ["DU20", "LI4", "LR3", "PC6", "GB20", "GB34"]:
            가능 = "보류 또는 매우 약하게"
            강도 = "보류~약"
            조건 = "상열감·심계·불면·고혈압 변동 시 강한 온열 자극 주의"
        else:
            가능 = "한의사 판단"
            강도 = "약"
            조건 = "환자 허실·한열·피부 상태 확인"
        rows.append({
            "code": code,
            "혈명": a["혈명"],
            "가능/보류": 가능,
            "주의 조건": 조건,
            "권장 강도": 강도,
            "시술 전 확인": a["주의점"],
        })
    return rows


def chart_note(formula_name: str, formula: Dict[str, Any], chief: str, global_note: str, goal: str, pulse: str, tongue: str, abdomen: str, bp: str, labs: str, meds: str, checked: List[str]) -> str:
    safety_rows = safety_findings(formula_name, formula, checked, bp, labs, meds)
    ac_codes = ", ".join(formula["핵심 혈위"])
    chief_line = chief.strip() or "미입력"
    goal_line = goal.strip() or "처방 방향과 안전성 확인 후 설정"
    pulse_line = join_nonempty([pulse, tongue, abdomen]) or "미입력"
    return f"""[변증 초안]
{formula['전통 변증']} 경향. 주증상("{chief_line}") 소견 시 '{formula_name}' 방향 검토.
진맥·설진·복진 입력: {pulse_line}

[처방 방향]
{formula['처방 방향']}. 단, {formula['주의 환자상']}에서는 처방 자체보다 감별·가감·안전성을 먼저 확인.
치료 목표: {goal_line}

[침구 방향]
{ac_codes} 중심. 해당 혈위는 자동 시술 지시가 아니라 처방 변증과 자주 연결되는 후보입니다.
핵심 후보: {', '.join([acu(c)['혈명'] for c in formula['핵심 혈위']])}

[뜸]
가능 조건: {formula['뜸 가능 조건']}
주의 조건: {formula['뜸 주의 조건']}
권장 강도: {formula['권장 강도']}

[안전성 및 추적]
{safety_summary(safety_rows)}
혈압: {bp or '미입력'}
검사/복용약 메모: {labs or '검사값 미입력'} / {meds or '복용약 미입력'}
추적 관찰: 소화상태, 대변 변화, 피로감 변화, 수면 변화, 소변 변화, 열감·도한, 혈압/혈당 변화

※ 이 문서는 자동 확정 처방이 아니라 한의사가 검토·수정하는 차트 초안입니다."""


def patient_explanation(formula_name: str, formula: Dict[str, Any], chief: str, checked: List[str]) -> str:
    checked_line = ", ".join(checked) if checked else "현재 특별히 체크된 안전 항목은 없습니다."
    chief_line = f"입력된 증상/메모: {chief}\n\n" if chief.strip() else ""
    return f"""{chief_line}{formula_name}은/는 전통 한의학에서 '{formula['전통 변증']}' 방향에서 검토되는 처방입니다.

쉽게 말하면, {formula['환자 설명']}

현재 이 처방은 '{formula['처방 방향']}' 방향에서 검토됩니다.

복용 전후에는 다음 항목을 관찰해 주세요.
- 소화상태, 대변 변화, 피로감 변화, 수면 변화, 소변 변화, 열감·도한, 혈압/혈당 변화

현재 안전 체크 항목:
- {checked_line}

불편감이 생기거나 기존 증상이 악화되면 임의로 계속 복용하지 말고 담당 한의사에게 알려야 합니다.

이 설명은 처방을 자동으로 정하거나 효과를 보장하는 내용이 아닙니다. 실제 복용 여부와 용량은 담당 한의사가 결정합니다."""


def bp_message(bp: str) -> str:
    bpv = parse_bp(bp)
    if not bpv:
        return "혈압 미입력 또는 형식 미확인. 예: 118/76"
    if bpv["sbp"] >= 160 or bpv["dbp"] >= 100:
        return f"입력 혈압 {bp}: 고혈압 범위 가능성이 있어 처방·침구·뜸 자극 전 재확인 권장."
    if bpv["sbp"] >= 140 or bpv["dbp"] >= 90:
        return f"입력 혈압 {bp}: 경계/상승 범위 가능성. 승양·온보·강자극 전 재측정 권장."
    return f"입력 혈압 {bp}: 입력 기준으로는 고혈압 경고가 자동 발생하지 않습니다."


# ============================================================
# 5. 기본 상태와 사이드바
# ============================================================

DEFAULTS: Dict[str, Any] = {
    "formula_name": "육미지황환",
    "chief": "",
    "global_note": "",
    "goal": "",
    "pulse": "",
    "tongue": "",
    "abdomen": "",
    "bp": "",
    "labs": "",
    "meds": "",
    "checked_safety": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

with st.sidebar:
    st.header("입력")
    ex_name = st.selectbox("테스트 예시 불러오기", list(EXAMPLES.keys()))
    if st.button("예시 적용", use_container_width=True):
        ex = EXAMPLES[ex_name]
        st.session_state["formula_name"] = ex["formula"]
        st.session_state["chief"] = ex["chief"]
        st.session_state["global_note"] = ex["global"]
        st.session_state["goal"] = ex["goal"]
        st.session_state["pulse"] = ex["pulse"]
        st.session_state["tongue"] = ex["tongue"]
        st.session_state["abdomen"] = ex["abdomen"]
        st.session_state["bp"] = ex["bp"]
        st.session_state["labs"] = ex["labs"]
        st.session_state["meds"] = ex["meds"]
        st.session_state["checked_safety"] = ex["safety"]
        st.rerun()

    st.selectbox("처방 선택", list(FORMULAS.keys()), key="formula_name")
    st.text_area("주증상 / 메모", key="chief", placeholder="예: 허리와 무릎이 약하고 오후 열감, 입마름, 도한", height=105)
    st.text_area("한의사 종합소견", key="global_note", placeholder="맥·설·복진 및 문진 종합 소견", height=120)
    st.text_area("치료 목표", key="goal", placeholder="예: 피로 회복, 허열 완충, 하초 허약 보조", height=80)

    st.subheader("진맥·설진·복진")
    st.text_input("맥상", key="pulse", placeholder="예: 허맥, 세맥")
    st.text_input("설질·설태", key="tongue", placeholder="예: 건조, 소태")
    st.text_input("복진/형태", key="abdomen", placeholder="예: 하복부 무력")

    st.subheader("검사값·복용약")
    st.text_input("혈압", key="bp", placeholder="예: 118/76")
    st.text_area("AST/ALT, creatinine/eGFR 등 검사값", key="labs", height=80)
    st.text_area("현재 복용약 상세", key="meds", height=80)

    st.subheader("환자 상태 체크 (안전성)")
    st.multiselect("해당 항목 선택", SAFETY_OPTIONS, key="checked_safety")

    st.divider()
    st.caption("교육·연구·임상 설명 보조용입니다. 자동 진단, 자동 처방, 자동 침구 시술 지시가 아닙니다.")

formula_name: str = st.session_state["formula_name"]
formula: Dict[str, Any] = FORMULAS[formula_name]
chief: str = st.session_state["chief"]
global_note: str = st.session_state["global_note"]
goal: str = st.session_state["goal"]
pulse: str = st.session_state["pulse"]
tongue: str = st.session_state["tongue"]
abdomen: str = st.session_state["abdomen"]
bp: str = st.session_state["bp"]
labs: str = st.session_state["labs"]
meds: str = st.session_state["meds"]
checked_safety: List[str] = st.session_state["checked_safety"]

safety_rows = safety_findings(formula_name, formula, checked_safety, bp, labs, meds)
ac_rows = core_acupoints(formula)


# ============================================================
# 6. 상단 요약
# ============================================================

st.title("🧭 한의사용 처방·침구·뜸 보조 대시보드")
note_box("warn", "본 대시보드는 자동 진단 또는 자동 처방 도구가 아닙니다. 실제 처방 여부와 용량, 혈위 선택, 자침 깊이, 유침 시간, 보사법, 뜸 부위와 강도는 면허가 있는 한의사가 환자 상태를 종합하여 최종 결정해야 합니다.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("선택 처방", formula_name)
m2.metric("핵심 후보 혈위", f"{len(ac_rows)}개")
m3.metric("안전 확인", f"{len(safety_rows)}건")
m4.metric("경혈 DB", f"{len(ACUPOINT_361)}개")
note_box("safe", f"현재 처방 방향: {formula['처방 방향']}")


# ============================================================
# 7. 탭 구성
# ============================================================

tabs = st.tabs([
    "1. 통합 요약",
    "2. 차트 소견서",
    "3. 361 경혈 DB",
    "4. 침구·혈위 후보",
    "5. 뜸 주의",
    "6. 진맥·설진·복진 대조",
    "7. 처방 방향 6축·감별",
    "8. 황제내경·동의보감",
    "9. 전통 처방 Core",
    "10. 안전성 확인",
    "11. 환자 설명문",
    "12. 연구자용 Q6/H(3,4)",
])

with tabs[0]:
    st.header("1. 통합 요약")
    note_box("info", "한의사가 바쁜 진료 환경에서 가장 먼저 확인해야 할 핵심 정보입니다. 정합도, 주의, 추적, 혈위 후보를 1페이지로 압축합니다.")
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("✅ 처방이 잘 맞는 환자상")
        st.write(formula["잘 맞는 환자상"])
        st.write(f"입력 소견과 처방 방향 **{formula['처방 방향']}** 의 기본 부합 여부를 확인합니다.")
        st.subheader("🔁 감별 및 가감 방향")
        st.write(f"유사 처방 감별: {formula['감별 처방']}")
        st.write(f"가감 조정: {formula['가감 방향']}")
    with right:
        st.subheader("⚠️ 주의하거나 재검토할 환자상")
        st.write(formula["주의 환자상"])
        st.write("현재 입력에서 잡힌 안전 신호")
        show_small(safety_rows)
    st.subheader("핵심 혈위 요약")
    show_df(df_from(ac_rows)[["code", "혈명", "경락", "처방 방향축", "임상 의미", "왜 후보인가"]])

with tabs[1]:
    st.header("2. 차트용 압축 소견서")
    note_box("warn", "EMR 차트에 복사해 넣기 좋게 압축한 초안입니다. 자동 확정 처방이 아니므로 한의사가 직접 검토·수정하십시오.")
    note = chart_note(formula_name, formula, chief, global_note, goal, pulse, tongue, abdomen, bp, labs, meds, checked_safety)
    st.text_area("소견서 텍스트", note, height=430)
    st.download_button("차트 소견서 다운로드", data=note, file_name=f"{formula_name}_chart_note.txt", mime="text/plain")
    st.subheader("차트형 핵심 체크")
    show_small([
        {"항목": "변증 방향", "내용": formula["전통 변증"]},
        {"항목": "처방 방향", "내용": formula["처방 방향"]},
        {"항목": "핵심 혈위", "내용": ", ".join([f"{c} {acu(c)['혈명']}" for c in formula["핵심 혈위"]])},
        {"항목": "뜸 기준", "내용": f"{formula['뜸 가능 조건']} / {formula['뜸 주의 조건']}"},
        {"항목": "안전 신호", "내용": safety_summary(safety_rows)},
    ])

with tabs[2]:
    st.header("3. 361 표준 경혈 DB")
    note_box("info", "전체 DB는 기본적으로 접어 두고, 현재 처방과 관련 높은 핵심 후보 혈위를 먼저 보여줍니다.")
    st.subheader("현재 처방 핵심 후보 먼저 보기")
    show_df(df_from(ac_rows)[["code", "혈명", "standard_name", "경락", "처방 방향축", "임상 의미", "왜 후보인가", "주의점"]])
    with st.expander("전체 361 경혈 DB 열기 / 검색", expanded=False):
        db_df = df_from(ACUPOINT_361)
        query = st.text_input("경혈 검색", placeholder="예: KI3, 태계, Taixi, 족소음신경, 보충축")
        meridians = sorted(db_df["경락"].unique().tolist())
        selected_meridians = st.multiselect("경락 필터", meridians)
        axes = sorted(set(", ".join(db_df["처방 방향축"].tolist()).replace(" ", "").split(",")))
        selected_axes = st.multiselect("처방 방향축 필터", axes)
        filtered = db_df.copy()
        if query.strip():
            q = query.strip().lower()
            mask = filtered.apply(lambda row: q in " ".join(row.astype(str).tolist()).lower(), axis=1)
            filtered = filtered[mask]
        if selected_meridians:
            filtered = filtered[filtered["경락"].isin(selected_meridians)]
        if selected_axes:
            axis_pattern = "|".join([re.escape(x) for x in selected_axes])
            filtered = filtered[filtered["처방 방향축"].str.contains(axis_pattern, na=False)]
        st.caption(f"표시: {len(filtered)} / 전체 {len(db_df)}개")
        show_df(filtered)
        st.download_button("361 경혈 DB CSV 다운로드", data=db_df.to_csv(index=False).encode("utf-8-sig"), file_name="acupoint_361_db.csv", mime="text/csv")

with tabs[3]:
    st.header("4. 처방별 침구 치료 방향 및 혈위 해설")
    note_box("safe", f"기본 침구 방향: {formula['처방 방향']}. 혈위 후보는 자동 시술 지시가 아니라 변증 방향과 자주 연결되는 후보군입니다.")
    note_box("warn", "혈위 선택, 자침 깊이, 유침 시간, 보사법, 자극 강도는 한의사가 환자 상태와 해부학적 안전성을 확인한 뒤 결정해야 합니다.")
    for code in formula["핵심 혈위"]:
        a = acu(code)
        with st.expander(f"{code} {a['혈명']} — 왜 이 혈위인가", expanded=(code == formula["핵심 혈위"][0])):
            st.markdown(f"**경락:** {a['경락']} / **표준명:** {a['standard_name']}")
            st.markdown(f"**임상 의미:** {a['임상 의미']}")
            st.markdown(f"**후보 근거:** {a['왜 후보인가']}")
            st.markdown(f"**자침·안전:** {a['주의점']}")
    st.subheader("침구 시 확인할 임상 포인트")
    st.write("- 처방 방향과 침 자극 방향이 서로 충돌하지 않는지 확인")
    st.write("- 허증 환자에게 과도한 사법·강자극을 쓰지 않도록 주의")
    st.write("- 실열·상열감 환자에게 승양·온보 자극이 과하지 않은지 확인")
    st.write("- 복부 냉감, 더부룩함, 압통, 흉협고만 등 복진과 함께 판단")

with tabs[4]:
    st.header("5. 뜸 치료 가능 여부 및 주의 조건")
    note_box("danger", "뜸은 화상, 감염, 피부 자극 위험이 있으므로 감각저하, 당뇨성 말초신경병증, 실열·상열, 임신, 피부질환을 반드시 확인해야 합니다.")
    st.subheader("처방별 뜸 조건: 가능/주의/강도")
    show_small([
        {"항목": "가능 조건", "내용": formula["뜸 가능 조건"]},
        {"항목": "주의 조건", "내용": formula["뜸 주의 조건"]},
        {"항목": "권장 강도", "내용": formula["권장 강도"]},
    ])
    st.subheader("핵심 혈위별 뜸 검토")
    show_df(moxa_point_rows(formula))
    st.subheader("강도 기준")
    show_small([
        {"강도": "보류", "의미": "열감·염증·감각저하·임신 등 위험 신호가 있거나 처방 방향상 뜸 필요성이 낮음"},
        {"강도": "약", "의미": "짧고 약한 온열 자극만 검토. 환자 반응을 즉시 확인"},
        {"강도": "약~중", "의미": "허한·냉감이 명확할 때 제한적으로 검토"},
        {"강도": "중", "의미": "허한·원기 저하가 분명하고 금기 신호가 없을 때만 전문가 판단으로 검토"},
    ])

with tabs[5]:
    st.header("6. 진맥·설진·복진 대조")
    note_box("info", "자동 판정이 아니라 선택 처방의 목표 소견과 실제 입력 소견을 대조하는 참고표입니다.")
    show_small([
        {"항목": "맥상", "입력": pulse or "미입력", "처방 적합성 대조": "허맥·세맥은 보충축·수렴축과 잘 맞을 수 있음. 현맥은 소통축 검토."},
        {"항목": "설질·설태", "입력": tongue or "미입력", "처방 적합성 대조": "건조·소태는 음허 방향 참고, 후태·황태는 습담·실열 재검토."},
        {"항목": "복진/형태", "입력": abdomen or "미입력", "처방 적합성 대조": "하복부 무력은 하초 허약 방향, 복부 긴장·팽만은 비위·담음·기체 확인."},
    ])
    st.subheader("해석 참고")
    st.write("- 맥상·설진·복진이 처방 방향과 다르면 처방 자체보다 감별·가감·침구 방향을 먼저 조정합니다.")
    st.write("- 예: 육미지황환을 보면서 후태·복부팽만·설사가 뚜렷하면 숙지황 등 보음약의 위장 부담을 확인합니다.")

with tabs[6]:
    st.header("7. 처방 방향 6축·감별")
    direction_rows = [
        {"축": "보충축", "뜻": "기·혈·음·양·정혈을 보태는 방향", "대표 소견": "피로, 무력, 안색창백, 식욕저하, 요슬산연", "현재 처방 관련성": "중심" if "보" in formula["처방 방향"] or "자음" in formula["처방 방향"] else "보조 확인"},
        {"축": "수렴·안정축", "뜻": "흩어진 기운을 안으로 모으고 안정시키는 방향", "대표 소견": "불면, 심계, 도한, 불안, 진액 소모", "현재 처방 관련성": "중심" if "수렴" in formula["처방 방향"] or "안신" in formula["처방 방향"] else "보조 확인"},
        {"축": "승양·상승축", "뜻": "아래로 처진 기운을 위로 끌어올리는 방향", "대표 소견": "처짐, 중기하함, 무력감, 기단, 하수감", "현재 처방 관련성": "중심" if "승양" in formula["처방 방향"] else "보조 확인"},
        {"축": "배출·이수축", "뜻": "정체된 수분·습담·노폐를 밖으로 빼는 방향", "대표 소견": "부종, 소변불리, 몸무거움, 습담", "현재 처방 관련성": "중심" if "이수" in formula["처방 방향"] else "보조 확인"},
        {"축": "소통·전환축", "뜻": "막힌 기혈과 비위 흐름을 돌리는 방향", "대표 소견": "흉협고만, 복부팽만, 식체, 기체, 어혈", "현재 처방 관련성": "중심" if "소" in formula["처방 방향"] or "화담" in formula["처방 방향"] else "보조 확인"},
        {"축": "완충·조화축", "뜻": "치우친 보·사·한·열을 조절하는 중간 조화 방향", "대표 소견": "보하면 체하고, 사하면 허해지는 중간형", "현재 처방 관련성": "중심" if "조화" in formula["처방 방향"] or "완충" in formula["처방 방향"] else "보조 확인"},
    ]
    show_df(direction_rows)
    st.subheader("주요 처방 비교표")
    compare_rows = []
    for name, f in FORMULAS.items():
        compare_rows.append({"처방": name, "분류": f["분류"], "전통 변증": f["전통 변증"], "핵심 방향": f["처방 방향"], "잘 맞는 환자상": f["잘 맞는 환자상"], "주의 환자상": f["주의 환자상"]})
    show_df(compare_rows)
    st.subheader("감별·가감")
    st.write(f"**감별 처방:** {formula['감별 처방']}")
    st.write(f"**가감 방향:** {formula['가감 방향']}")

with tabs[7]:
    st.header("8. 황제내경·동의보감 원전 대응 해석")
    note_box("warn", "원전을 현대 생물학적으로 증명한다는 뜻이 아니라, 입력 소견을 전통 개념과 편제에 맞춰 정리하는 주석층입니다.")
    st.subheader("황제내경 해당 개념")
    show_df(formula.get("황제내경", []))
    st.subheader("동의보감 해당 편제")
    show_df(formula.get("동의보감", []))
    st.subheader("한의사용 해석")
    note_box("info", "소견서에 입력된 증상과 변증을 음양, 장부·기혈진액, 승강출입, 표본중기, 삼음삼양 병기 등의 언어로 재정리하고, 동의보감의 병증 편제와 연결해 처방·침구·뜸 방향이 같은 치료 방향을 향하는지 확인합니다.")

with tabs[8]:
    st.header("9. 전통 처방 Core")
    show_small([
        {"항목": "처방명", "내용": formula_name},
        {"항목": "분류", "내용": formula["분류"]},
        {"항목": "전통 변증", "내용": formula["전통 변증"]},
        {"항목": "처방 방향", "내용": formula["처방 방향"]},
        {"항목": "구성 약재", "내용": formula["구성 약재"]},
        {"항목": "잘 맞는 환자상", "내용": formula["잘 맞는 환자상"]},
        {"항목": "주의 환자상", "내용": formula["주의 환자상"]},
        {"항목": "감별 처방", "내용": formula["감별 처방"]},
        {"항목": "가감 방향", "내용": formula["가감 방향"]},
    ])
    st.subheader("군신좌사·약재 방향")
    herb_rows = []
    for idx, herb in enumerate([x.strip() for x in formula["구성 약재"].replace("+", ",").split(",") if x.strip()]):
        role = "군약" if idx == 0 else ("신약" if idx <= 2 else "좌사약")
        herb_rows.append({"역할": role, "약재": herb, "전통 역할": "처방 방향을 구성하는 약재. 실제 용량·배합은 한의사 판단", "확인": "귀경·사기·오미·용량 확인"})
    show_df(herb_rows)

with tabs[9]:
    st.header("10. 안전성 확인")
    note_box("warn", "아래 항목은 금지 판정이 아니라 추가 확인이 필요한 위험 신호입니다.")
    show_df(safety_rows)
    st.subheader("혈압 해석")
    msg = bp_message(bp)
    note_box("safe" if "고혈압" not in msg and "상승" not in msg else "warn", msg)
    st.subheader("검사값·복용약 메모")
    show_small([
        {"항목": "AST/ALT 등 간기능", "입력값": labs or "미입력"},
        {"항목": "creatinine/eGFR 등 신장기능", "입력값": labs or "미입력"},
        {"항목": "혈압", "입력값": bp or "미입력"},
        {"항목": "복용약", "입력값": meds or "미입력"},
        {"항목": "체크된 안전 항목", "입력값": ", ".join(checked_safety) if checked_safety else "없음"},
    ])

with tabs[10]:
    st.header("11. 환자 설명문 패널")
    note_box("info", "환자에게 복용을 안내할 때 사용할 수 있는 쉬운 표현입니다. 실제 안내 전에는 환자 상황에 맞게 한의사가 검토해야 합니다.")
    exp = patient_explanation(formula_name, formula, chief, checked_safety)
    st.text_area("환자 설명문", exp, height=430)
    st.download_button("환자 설명문 다운로드", data=exp, file_name=f"{formula_name}_patient_explanation.txt", mime="text/plain")

with tabs[11]:
    st.header("12. 연구자용 Q6 / H(3,4) 보조 구조")
    note_box("info", "이 탭은 연구자용입니다. 한의사용 판단 화면에서는 6축·처방·혈위 해설만 보면 됩니다.")
    show_df([
        {"구조": "Q6 64큐브 Core", "vertices": 64, "undirected_edges": 192, "directed_edges": 384, "한의사용 번역": "처방 변화를 6개 방향축으로 정리하는 Core 구조"},
        {"구조": "H(3,4) Extension", "vertices": 64, "undirected_edges": 288, "directed_edges": 576, "한의사용 번역": "처방 주변 변화 가능성과 감별 지점을 넓게 보는 확장 구조"},
    ])
    codon_rows = []
    for n in [0, 9, 18, 63]:
        codon = n_to_codon(n)
        codon_rows.append({
            "n": n,
            "효 순서 비트": n_to_hyo_bits(n),
            "codon": codon,
            "amino_acid": GENETIC_CODE[codon],
            "Q6 이웃": ", ".join(map(str, q6_neighbors(n))),
            "H(3,4) 이웃 수": h34_neighbors_count(),
        })
    show_df(codon_rows)
    note_box("warn", "약재-코돈-아미노산 매핑은 약재가 실제 유전자나 아미노산을 조절한다는 뜻이 아닙니다. 전통적 작용 방향을 생명정보학적 벡터 언어로 주석화한 연구자용 해석층입니다.")

st.divider()
st.caption("교육·연구·임상 설명 보조용입니다. 자동 진단, 자동 처방, 자동 침구 시술 지시가 아닙니다. 실제 처방 여부와 용량, 혈위, 자침 깊이, 유침 시간, 보사법, 뜸 부위와 강도는 면허가 있는 한의사가 환자 상태를 종합하여 최종 결정해야 합니다.")
