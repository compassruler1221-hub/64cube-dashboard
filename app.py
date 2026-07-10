# app.py
# 64큐브-다면체 한의학 Core 기반 처방 분석 대시보드
# 실행: streamlit run app.py

import itertools
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


# ============================================================
# 0. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="64큐브-다면체 처방 해석 대시보드",
    page_icon="🧭",
    layout="wide",
)


# ============================================================
# 1. 64큐브 Q6 / 코돈 매핑 공리
# ============================================================

BASE_TO_BITS: Dict[str, str] = {
    "G": "00",
    "A": "10",
    "U": "01",
    "C": "11",
}
BITS_TO_BASE: Dict[str, str] = {v: k for k, v in BASE_TO_BITS.items()}

BASE_ORDER = ["G", "A", "U", "C"]  # 00, 10, 01, 11
HYO_NAMES = {
    0: "초효",
    1: "2효",
    2: "3효",
    3: "4효",
    4: "5효",
    5: "상효",
}

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

AA_PROPERTIES: Dict[str, Dict[str, object]] = {
    "Ala": {"hydropathy": 1.8, "charge": "neutral", "group": "nonpolar"},
    "Arg": {"hydropathy": -4.5, "charge": "positive", "group": "basic"},
    "Asn": {"hydropathy": -3.5, "charge": "neutral", "group": "polar"},
    "Asp": {"hydropathy": -3.5, "charge": "negative", "group": "acidic"},
    "Cys": {"hydropathy": 2.5, "charge": "neutral", "group": "polar"},
    "Gln": {"hydropathy": -3.5, "charge": "neutral", "group": "polar"},
    "Glu": {"hydropathy": -3.5, "charge": "negative", "group": "acidic"},
    "Gly": {"hydropathy": -0.4, "charge": "neutral", "group": "special"},
    "His": {"hydropathy": -3.2, "charge": "positive", "group": "basic"},
    "Ile": {"hydropathy": 4.5, "charge": "neutral", "group": "nonpolar"},
    "Leu": {"hydropathy": 3.8, "charge": "neutral", "group": "nonpolar"},
    "Lys": {"hydropathy": -3.9, "charge": "positive", "group": "basic"},
    "Met": {"hydropathy": 1.9, "charge": "neutral", "group": "nonpolar"},
    "Phe": {"hydropathy": 2.8, "charge": "neutral", "group": "aromatic"},
    "Pro": {"hydropathy": -1.6, "charge": "neutral", "group": "special"},
    "Ser": {"hydropathy": -0.8, "charge": "neutral", "group": "polar"},
    "Thr": {"hydropathy": -0.7, "charge": "neutral", "group": "polar"},
    "Trp": {"hydropathy": -0.9, "charge": "neutral", "group": "aromatic"},
    "Tyr": {"hydropathy": -1.3, "charge": "neutral", "group": "aromatic"},
    "Val": {"hydropathy": 4.2, "charge": "neutral", "group": "nonpolar"},
    "Stop": {"hydropathy": None, "charge": "stop", "group": "stop"},
}


def n_to_hyo_bits(n: int) -> str:
    """초효(bit0)부터 상효(bit5)까지의 6비트 문자열."""
    return "".join(str((n >> i) & 1) for i in range(6))


def hyo_bits_to_n(bits: str) -> int:
    return sum(int(bits[i]) * (2 ** i) for i in range(6))


def n_to_codon(n: int) -> str:
    bits = n_to_hyo_bits(n)
    return (
        BITS_TO_BASE[bits[0:2]]
        + BITS_TO_BASE[bits[2:4]]
        + BITS_TO_BASE[bits[4:6]]
    )


def codon_to_n(codon: str) -> int:
    bits = "".join(BASE_TO_BITS[base] for base in codon)
    return hyo_bits_to_n(bits)


def codon_to_aa(codon: str) -> str:
    return GENETIC_CODE[codon]


def q6_neighbors(n: int) -> List[Dict[str, object]]:
    rows = []
    src_codon = n_to_codon(n)
    src_aa = codon_to_aa(src_codon)
    for bit in range(6):
        m = n ^ (1 << bit)
        codon = n_to_codon(m)
        aa = codon_to_aa(codon)
        rows.append({
            "layer": "Q6 Core",
            "from_n": n,
            "from_codon": src_codon,
            "from_aa": src_aa,
            "to_n": m,
            "to_codon": codon,
            "to_aa": aa,
            "changed_position": (bit // 2) + 1,
            "bit": bit,
            "hyo": HYO_NAMES[bit],
            "edge_type": "single-bit flip",
        })
    return rows


def h34_neighbors(n: int) -> List[Dict[str, object]]:
    rows = []
    src_codon = n_to_codon(n)
    src_aa = codon_to_aa(src_codon)

    q6_to = {row["to_n"] for row in q6_neighbors(n)}

    for pos in range(3):
        original = src_codon[pos]
        for base in BASE_ORDER:
            if base == original:
                continue
            new_codon = src_codon[:pos] + base + src_codon[pos + 1:]
            m = codon_to_n(new_codon)
            aa = codon_to_aa(new_codon)
            is_q6 = m in q6_to
            rows.append({
                "layer": "Q6 Core" if is_q6 else "H(3,4) Extension",
                "from_n": n,
                "from_codon": src_codon,
                "from_aa": src_aa,
                "to_n": m,
                "to_codon": new_codon,
                "to_aa": aa,
                "changed_position": pos + 1,
                "bit": "" if not is_q6 else "Q6 bit",
                "hyo": "" if not is_q6 else "Q6 edge",
                "edge_type": "Q6 single-bit" if is_q6 else "diagonal substitution",
            })
    return rows


# 핵심 검산
assert n_to_codon(0) == "GGG"
assert codon_to_aa(n_to_codon(0)) == "Gly"
assert n_to_codon(9) == "AUG"
assert codon_to_aa(n_to_codon(9)) == "Met"
assert n_to_codon(18) == "UGA"
assert codon_to_aa(n_to_codon(18)) == "Stop"
assert n_to_codon(63) == "CCC"
assert codon_to_aa(n_to_codon(63)) == "Pro"


# ============================================================
# 2. 처방 데이터
# ============================================================

FORMULAS = {
    "육미지황환": {
        "traditional_direction": "자음·보신·허열 완충 방향",
        "core_summary": "숙지황·산수유·산약의 삼보와 복령·택사·목단피의 삼사로 구성된 처방 구조",
        "q6_summary": "보존형 변화와 수렴형 완충 방향으로 주석화",
        "rd_summary": "RD 3:3 안정화 구조: 보존/보충 3축과 배출/완충 3축의 상보적 배치",
        "poly_scores": {
            "보존": 90,
            "보충": 85,
            "수렴": 80,
            "완충": 70,
            "배출": 55,
            "급진전환": 20,
        },
        "huangdi": {
            "장부축": "간(肝) · 신(腎)",
            "기혈진액축": "음혈 · 정(精) · 진액 · 구조물질 보존",
            "오행축": "水 중심, 木 보조",
            "승강출입": "저장 · 보존 · 자음 · 허열 완충",
        },
        "herbs": [
            {
                "name": "숙지황",
                "role": "군약",
                "traditional": "자음·보신·정혈 보존 방향",
                "codon": "GUU",
                "axis": "구조 안정성 / 보존형 변화",
                "poly": "RD 보존/보충 축",
                "note": "전통적 보존·보충 방향을 GUU-Val 축으로 주석화",
            },
            {
                "name": "산수유",
                "role": "신약",
                "traditional": "수렴·보존 방향",
                "codon": "GCU",
                "axis": "비극성 완충 / 수렴형 완충",
                "poly": "RD 보존/수렴 축",
                "note": "전통적 수렴 방향을 GCU-Ala 축으로 주석화",
            },
            {
                "name": "산약",
                "role": "신약",
                "traditional": "보비·보신·진액 보존 방향",
                "codon": "GAU",
                "axis": "음전하 기반 수분 포획 / 보존형 완충",
                "poly": "RD 보존/완충 축",
                "note": "전통적 진액 보존 방향을 GAU-Asp 축으로 주석화",
            },
            {
                "name": "복령",
                "role": "좌약",
                "traditional": "수습 조절·완충 방향",
                "codon": "GGU",
                "axis": "구조 유연성 / 전환형 배출",
                "poly": "RD 배출/완충 축",
                "note": "전통적 수습 조절 방향을 GGU-Gly 축으로 주석화",
            },
            {
                "name": "택사",
                "role": "좌약",
                "traditional": "수습 배출·하행 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "RD 배출 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "목단피",
                "role": "사약",
                "traditional": "허열 완충·혈분 조절 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "RD 완충 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
        ],
        "safety": [
            ("항응고제/항혈소판제", "목단피 등 혈류 관련 약재가 포함될 수 있어 복용약 확인이 필요합니다."),
            ("당뇨약", "산약 등과 관련하여 혈당 변화 가능성을 확인해야 합니다."),
            ("간·신장 기능 저하", "장기 복용 또는 고용량 사용 전 간·신장 관련 확인이 필요합니다."),
            ("만성 소화불량/설사", "숙지황 등 점액질 성분으로 인한 소화 부담 가능성을 확인해야 합니다."),
        ],
    },

    "보중익기탕": {
        "traditional_direction": "비위기허·중기하함·승양 방향",
        "core_summary": "황기·인삼·백출·감초를 중심으로 보기·승양 방향을 구성하는 처방 구조",
        "q6_summary": "발산·상승 및 전환 방향으로 주석화",
        "rd_summary": "대칭 안정화보다 특정 상승 벡터 편향성이 두드러지는 구조",
        "poly_scores": {
            "발산": 90,
            "전환": 85,
            "보충": 70,
            "완충": 40,
            "수렴": 20,
            "배출": 10,
        },
        "huangdi": {
            "장부축": "비(脾) · 폐(肺)",
            "기혈진액축": "기(氣) · 중기 · 운화",
            "오행축": "土 중심, 木/火 보조",
            "승강출입": "상승 · 발산 · 중기 회복 방향",
        },
        "herbs": [
            {
                "name": "황기",
                "role": "군약",
                "traditional": "보기·승양 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "Octahedron 발산/상승 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "인삼",
                "role": "신약",
                "traditional": "보기·중초 보충 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "보충 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "백출",
                "role": "신약",
                "traditional": "비위 운화·보충 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "보충/전환 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "승마",
                "role": "사약",
                "traditional": "승양·상행 방향",
                "codon": "AAU",
                "axis": "극성 아미노산 기반 상승형 전환",
                "poly": "Octahedron 상승 축",
                "note": "전통적 승양 방향을 AAU-Asn 축으로 주석화",
            },
            {
                "name": "시호",
                "role": "사약",
                "traditional": "소통·상승·완충 방향",
                "codon": "AGU",
                "axis": "유연성 중심 완충형 변화",
                "poly": "발산/완충 축",
                "note": "전통적 소통 방향을 AGU-Ser 축으로 주석화",
            },
        ],
        "safety": [
            ("혈압약", "감초·인삼·황기 등과 관련하여 혈압 변화 가능성 확인이 필요합니다."),
            ("당뇨약", "인삼 등과 관련하여 혈당 변화 가능성을 확인해야 합니다."),
            ("면역억제제", "황기 등 면역 관련 약재 사용 시 복용약 확인이 필요합니다."),
            ("간·신장 기능 저하", "장기 복용 또는 병용약이 있는 경우 간·신장 관련 확인이 필요합니다."),
        ],
    },

    "산조인탕": {
        "traditional_direction": "허번불면·수렴·안신·내부 안정 방향",
        "core_summary": "산조인을 중심으로 지모·천궁·감초가 수렴과 내부 안정 방향을 구성하는 처방 구조",
        "q6_summary": "수렴형 완충과 내부 안정 방향으로 주석화",
        "rd_summary": "수렴·완충 중심의 내부 안정화 구조",
        "poly_scores": {
            "수렴": 90,
            "완충": 80,
            "보존": 60,
            "보충": 45,
            "전환": 25,
            "발산": 15,
        },
        "huangdi": {
            "장부축": "심(心) · 간(肝) · 담(膽)",
            "기혈진액축": "혈 · 음 · 정신 안정 방향",
            "오행축": "木/火 조절, 水 보조",
            "승강출입": "수렴 · 안정 · 내부 조절 방향",
        },
        "herbs": [
            {
                "name": "산조인",
                "role": "군약",
                "traditional": "수렴·안신 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "수렴/완충 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "지모",
                "role": "신약",
                "traditional": "허열 완충·자음 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "완충 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "천궁",
                "role": "좌약",
                "traditional": "소통·혈행 조절 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "전환/소통 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
            {
                "name": "감초",
                "role": "사약",
                "traditional": "조화·완충 방향",
                "codon": None,
                "axis": "좌표 미고정 / 대시보드에서 추후 고정 필요",
                "poly": "완충 축",
                "note": "현재 버전에서는 전통 방향성만 표시",
            },
        ],
        "safety": [
            ("수면제/항우울제", "진정 관련 복용약과 병용 시 졸림·반응 저하 가능성을 확인해야 합니다."),
            ("항응고제/항혈소판제", "천궁 등 혈류 관련 약재가 포함될 수 있어 복용약 확인이 필요합니다."),
            ("간·신장 기능 저하", "장기 복용 또는 병용약이 있는 경우 간·신장 관련 확인이 필요합니다."),
        ],
    },
}


# ============================================================
# 3. UI helper
# ============================================================

def warning_box() -> None:
    st.warning(
        "본 대시보드는 자동 진단 또는 자동 처방 도구가 아닙니다. "
        "약재-코돈-아미노산 매핑은 약재가 실제 유전암호를 조절한다는 뜻이 아니라, "
        "전통적 작용 방향을 64큐브 코돈-아미노산 물성 벡터 언어로 주석화한 교육·연구 보조 해석입니다. "
        "실제 처방 여부와 용량은 면허가 있는 한의사의 변증, 환자 병력, 복용약, 검사 결과, 안전성 평가를 바탕으로 결정되어야 합니다."
    )


def herb_to_row(herb: Dict[str, object]) -> Dict[str, object]:
    codon = herb.get("codon")
    if codon:
        n = codon_to_n(codon)
        aa = codon_to_aa(codon)
        prop = AA_PROPERTIES[aa]
        codon_display = f"{codon} ({'-'.join(codon)}) → {aa}"
        n_display = n
        hydro = prop["hydropathy"]
        charge = prop["charge"]
        group = prop["group"]
    else:
        codon_display = "좌표 미고정"
        n_display = "—"
        aa = "—"
        hydro = "—"
        charge = "—"
        group = "—"

    return {
        "약재": herb["name"],
        "전통 역할": herb["role"],
        "전통 Core 방향": herb["traditional"],
        "Q6 좌표 n": n_display,
        "코돈-아미노산 주석": codon_display,
        "물성 그룹": group,
        "Hydropathy": hydro,
        "Charge": charge,
        "해석축": herb["axis"],
        "다면체 주석": herb["poly"],
    }


def selected_herb_options(formula: Dict[str, object]) -> List[str]:
    return [h["name"] for h in formula["herbs"]]


def find_herb(formula: Dict[str, object], herb_name: str) -> Dict[str, object]:
    for herb in formula["herbs"]:
        if herb["name"] == herb_name:
            return herb
    raise KeyError(herb_name)


def patient_explanation(formula_name: str, formula: Dict[str, object], checked: List[str]) -> str:
    caution_text = ""
    if checked:
        caution_text = (
            "\n\n현재 입력된 안전성 확인 항목에는 "
            + ", ".join(checked)
            + "이 포함되어 있습니다. 실제 복용 여부와 용량은 담당 한의사가 환자의 증상, 병력, 복용 중인 약, 검사 결과와 안전성을 함께 확인해 결정해야 합니다."
        )
    else:
        caution_text = (
            "\n\n현재 안전성 확인 항목이 선택되지 않았더라도, 실제 복용 전에는 환자 상태와 복용약 확인이 필요합니다."
        )

    return (
        f"{formula_name}은 전통 한의학에서 {formula['traditional_direction']}에서 설명되는 처방입니다. "
        f"이 대시보드는 {formula_name}의 전통 처방 구조를 먼저 정리하고, 이를 Q6 64큐브와 다면체 구조로 시각화해 이해를 돕는 보조 도구입니다.\n\n"
        "이 화면은 처방을 자동으로 정하거나 특정 결과를 보장하는 도구가 아닙니다. "
        "약재와 코돈·아미노산의 연결은 실제 유전암호 조절을 뜻하지 않고, 전통적 작용 방향을 생명정보 벡터 언어로 주석화한 설명 방식입니다."
        + caution_text
    )


# ============================================================
# 4. Sidebar
# ============================================================

st.title("🧭 64큐브-다면체 한의학 Core 기반 처방 분석 대시보드")

warning_box()

with st.sidebar:
    st.header("입력")
    formula_name = st.selectbox("처방 선택", list(FORMULAS.keys()))
    formula = FORMULAS[formula_name]

    chief_complaint = st.text_input("주증상 / 메모", placeholder="예: 피로, 소화불량, 수면 문제 등")

    st.subheader("안전성 확인 항목")
    safety_options = sorted({item for f in FORMULAS.values() for item, _ in f["safety"]})
    checked_safety = []
    for opt in safety_options:
        if st.checkbox(opt, value=False):
            checked_safety.append(opt)

    st.divider()
    st.caption("이 입력은 교육·연구 보조 설명 생성을 위한 것이며, 진단 또는 처방 결정을 대체하지 않습니다.")


# ============================================================
# 5. Top summary
# ============================================================

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("선택 처방", formula_name)
with col2:
    st.metric("Q6 구조", "64 vertices / 192 edges")
with col3:
    st.metric("H(3,4) 구조", "64 vertices / 288 edges")

st.markdown(
    f"""
### 현재 해석 요약

- **전통 처방 Core:** {formula["core_summary"]}
- **전통 방향:** {formula["traditional_direction"]}
- **Q6 Core 주석:** {formula["q6_summary"]}
- **다면체 주석:** {formula["rd_summary"]}
"""
)


# ============================================================
# 6. Tabs
# ============================================================

tabs = st.tabs([
    "1. 전통 처방 Core",
    "2. Q6 64큐브 Core",
    "3. H(3,4) 확장망",
    "4. 다면체 방향성",
    "5. 황제내경 병렬 해석",
    "6. 안전성 확인",
    "7. 환자 설명문",
])


# ------------------------------------------------------------
# Tab 1. Traditional Core
# ------------------------------------------------------------
with tabs[0]:
    st.header("1. 전통 처방 Core 패널")
    st.markdown(
        """
전통 처방 Core layer는 64큐브나 유전암호에 종속되지 않습니다.  
이 층에서는 처방의 군신좌사, 전통 방향, 귀경·변증·승강출입을 먼저 정리합니다.
"""
    )

    herb_df = pd.DataFrame([herb_to_row(h) for h in formula["herbs"]])
    st.dataframe(herb_df, use_container_width=True, hide_index=True)

    st.info(
        "이 표의 코돈-아미노산 항목은 전통적 작용 방향을 주석화하기 위한 해석축입니다. "
        "약재가 실제 코돈이나 아미노산을 직접 조절한다는 뜻이 아닙니다."
    )


# ------------------------------------------------------------
# Tab 2. Q6 Core
# ------------------------------------------------------------
with tabs[1]:
    st.header("2. Q6 64큐브 Core 주석 패널")
    st.markdown(
        """
Q6 layer는 64개 정점을 갖는 6차원 하이퍼큐브입니다.  
각 정점은 하나의 코돈 좌표로 주석화되며, 각 정점은 6개의 단일비트 이웃을 갖습니다.  
따라서 Q6는 192개 무방향 edge와 384개 방향성 edge를 가집니다.
"""
    )

    mapped_herbs = [h for h in formula["herbs"] if h.get("codon")]
    if not mapped_herbs:
        st.info("현재 선택한 처방에는 Q6 좌표가 고정된 약재가 없습니다.")
    else:
        selected_herb = st.selectbox(
            "Q6 이웃을 볼 약재 선택",
            [h["name"] for h in mapped_herbs],
            key="q6_herb",
        )
        herb = find_herb(formula, selected_herb)
        codon = herb["codon"]
        n = codon_to_n(codon)
        aa = codon_to_aa(codon)

        st.subheader(f"{selected_herb}: n={n}, {codon} ({'-'.join(codon)}) → {aa}")
        st.caption(herb["note"])

        q6_df = pd.DataFrame(q6_neighbors(n))
        st.dataframe(
            q6_df[["hyo", "bit", "changed_position", "from_codon", "from_aa", "to_n", "to_codon", "to_aa", "edge_type"]],
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "Q6 Core edge는 384효사와 병렬 배치되는 단일비트 변화입니다. "
            "이는 전체 생물학적 단일염기 치환망을 대체하지 않고, H(3,4) 확장층과 함께 해석됩니다."
        )


# ------------------------------------------------------------
# Tab 3. H(3,4) Extension
# ------------------------------------------------------------
with tabs[2]:
    st.header("3. H(3,4) 생물정보 확장 패널")
    st.markdown(
        """
H(3,4)는 실제 코돈 단일염기 치환 전체를 표현하는 확장망입니다.  
각 코돈은 세 염기 위치마다 다른 세 염기로 바뀔 수 있으므로 9개의 단일염기 이웃을 갖습니다.

- Q6 Core: 192개 무방향 edge / 384개 방향성 edge
- H(3,4): 288개 무방향 edge / 576개 방향성 edge
- H(3,4) - Q6: 96개 diagonal edge / 192개 방향성 diagonal 변화
"""
    )

    mapped_herbs = [h for h in formula["herbs"] if h.get("codon")]
    if not mapped_herbs:
        st.info("현재 선택한 처방에는 H(3,4) 확장망을 표시할 Q6 좌표가 고정된 약재가 없습니다.")
    else:
        selected_herb_h = st.selectbox(
            "H(3,4) 이웃을 볼 약재 선택",
            [h["name"] for h in mapped_herbs],
            key="h34_herb",
        )
        herb = find_herb(formula, selected_herb_h)
        codon = herb["codon"]
        n = codon_to_n(codon)
        h34_df = pd.DataFrame(h34_neighbors(n))

        st.subheader(f"{selected_herb_h}: n={n}, {codon} ({'-'.join(codon)}) → {codon_to_aa(codon)}")
        st.dataframe(
            h34_df[["layer", "changed_position", "from_codon", "from_aa", "to_n", "to_codon", "to_aa", "edge_type"]],
            use_container_width=True,
            hide_index=True,
        )

        counts = h34_df["layer"].value_counts().rename_axis("Layer").reset_index(name="Count")
        st.bar_chart(counts.set_index("Layer"))

        st.info(
            "H(3,4) Extension은 약재가 생물학적 변이를 유발한다는 뜻이 아닙니다. "
            "선택된 코돈 좌표 주변의 전체 단일염기 치환망을 참고용으로 보여주는 생물정보학적 확장층입니다."
        )


# ------------------------------------------------------------
# Tab 4. Polyhedron
# ------------------------------------------------------------
with tabs[3]:
    st.header("4. 다면체 방향성 시각화 패널")
    st.markdown(
        """
다면체 layer는 처방의 복합 방향성을 시각화하는 보조 구조입니다.  
처방 결과를 증명하는 도구가 아니라, 전통 처방 Core의 방향성을 정보기하학적으로 정리하는 주석층입니다.
"""
    )

    score_df = pd.DataFrame(
        [{"방향": k, "주석 점수": v} for k, v in formula["poly_scores"].items()]
    )
    st.bar_chart(score_df.set_index("방향"))

    st.markdown(
        f"""
#### 다면체 해석 요약

- **Octahedron:** 6대 방향 벡터의 압축 표현
- **VE:** 12 position-base 축의 중간 균형 구조
- **RD:** 안정화·완충 구조
- **TO:** 확장 네트워크 구조

**현재 처방 주석:** {formula["rd_summary"]}
"""
    )
    st.caption("주석 점수는 대시보드 내부 설명값이며, 임상적 결과 점수가 아닙니다.")


# ------------------------------------------------------------
# Tab 5. Huangdi Neijing
# ------------------------------------------------------------
with tabs[4]:
    st.header("5. 황제내경 병렬 해석 패널")
    st.markdown(
        """
이 패널은 황제내경이 DNA나 유전암호를 직접 설명한다는 뜻이 아닙니다.  
황제내경의 음양·오행·장부·기혈진액·승강출입·치미병 개념을 전신 동적평형의 언어로 정리하고,  
이를 Q6 상태공간 해석과 병렬로 배치하는 교육·연구 보조 층입니다.
"""
    )

    hd_df = pd.DataFrame(
        [{"축": k, "해석": v} for k, v in formula["huangdi"].items()]
    )
    st.dataframe(hd_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
#### 공통 해석축

- **음양:** 상반된 방향성의 동적 균형
- **오행:** 木·火·土·金·水의 작용 방향
- **장부:** 처방 방향이 놓이는 전통 장부축
- **기혈진액:** 기·혈·진액·정의 보존과 소통
- **승강출입:** 상승·하강·내수렴·외발산
- **치미병:** 불균형이 커지기 전 방향성 검토
"""
    )


# ------------------------------------------------------------
# Tab 6. Safety
# ------------------------------------------------------------
with tabs[5]:
    st.header("6. 안전성 확인 패널")
    st.markdown(
        """
안전성 확인은 처방 금지 판정이 아니라, 추가 확인이 필요한 항목을 표시하는 절차입니다.  
실제 판단은 한의사의 변증, 환자 병력, 복용약, 검사 결과와 함께 이루어져야 합니다.
"""
    )

    relevant_warnings = []
    for issue, text in formula["safety"]:
        if issue in checked_safety:
            relevant_warnings.append({"확인 항목": issue, "주의 문구": text})

    if relevant_warnings:
        st.error("선택된 안전성 확인 항목이 있습니다. 실제 사용 전 전문가 확인이 필요합니다.")
        st.dataframe(pd.DataFrame(relevant_warnings), use_container_width=True, hide_index=True)
    else:
        st.success("선택된 안전성 확인 항목이 없습니다.")
        st.info("선택 항목이 없더라도 실제 사용 전에는 병력, 복용약, 검사 결과 확인이 필요합니다.")

    with st.expander("처방별 기본 안전성 확인 문구 보기"):
        st.dataframe(
            pd.DataFrame([{"확인 항목": i, "주의 문구": t} for i, t in formula["safety"]]),
            use_container_width=True,
            hide_index=True,
        )


# ------------------------------------------------------------
# Tab 7. Patient explanation
# ------------------------------------------------------------
with tabs[6]:
    st.header("7. 환자 설명문 패널")
    st.markdown(
        "아래 문구는 환자에게 설명할 때 사용할 수 있는 쉬운 표현입니다. 실제 안내 전에는 환자 상황에 맞게 한의사가 검토해야 합니다."
    )

    explanation = patient_explanation(formula_name, formula, checked_safety)

    if chief_complaint:
        explanation = f"입력된 주증상/메모: {chief_complaint}\n\n" + explanation

    st.text_area("환자 설명문", explanation, height=300)

    st.download_button(
        "환자 설명문 다운로드",
        data=explanation,
        file_name=f"{formula_name}_patient_explanation.txt",
        mime="text/plain",
    )


# ============================================================
# 7. Footer
# ============================================================

st.divider()
st.caption(
    "64큐브 Q6는 384효사와 병렬 배치되는 Core layer이고, H(3,4)는 전체 코돈 단일염기 치환망을 포함하는 Extension layer입니다. "
    "전통 처방 Core가 중심이며, Q6·H(3,4)·다면체는 주석과 시각화를 위한 보조 구조입니다."
)
