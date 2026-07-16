# app.py
# 한의학 기하학 구조 보조도구 v3.0
# 실행: streamlit run app.py
# 목적: 처방·약재·경혈·경락·오행·육경 등 한의학 자료를
#       기하학적 노드·모서리·축·대칭·그래프로 배치하고 검증하는 연구/교육 도구

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

from tcm_geometry_data import ACU_OVERRIDES, FORMULAS, GENETIC_CODE, MERIDIANS


st.set_page_config(
    page_title="한의학 기하학 구조 보조도구",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
<style>
.block-container{max-width:1500px;padding-top:1.1rem;padding-bottom:2rem}
h1,h2,h3{letter-spacing:-0.035em}
div[data-testid="stMetricValue"]{font-size:1.65rem}
.geom-card{border:1px solid rgba(128,128,128,.28);border-radius:14px;padding:1rem 1.1rem;margin:.25rem 0 .8rem 0}
.small-note{font-size:.92rem;opacity:.82}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 공통 유틸리티
# -----------------------------------------------------------------------------
def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def show_df(rows: Any, height: int | None = None) -> None:
    df = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if df.empty:
        st.caption("표시할 항목이 없습니다.")
        return
    df = df.apply(lambda col: col.map(clean_text))
    kwargs: Dict[str, Any] = {"width": "stretch", "hide_index": True}
    if height:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)


def polar_xy(count: int, radius: float, phase: float = math.pi / 2) -> List[Tuple[float, float]]:
    return [
        (
            radius * math.cos(phase + 2 * math.pi * i / count),
            radius * math.sin(phase + 2 * math.pi * i / count),
        )
        for i in range(count)
    ]


def exact_polygon(n: int, radius: sp.Expr = sp.Integer(1), phase: sp.Expr = sp.pi / 2) -> List[Tuple[sp.Expr, sp.Expr]]:
    return [
        (
            sp.trigsimp(radius * sp.cos(phase + 2 * sp.pi * k / n)),
            sp.trigsimp(radius * sp.sin(phase + 2 * sp.pi * k / n)),
        )
        for k in range(n)
    ]


def stringify_exact(expr: sp.Expr) -> str:
    return str(sp.simplify(sp.trigsimp(expr)))


def edge_trace(
    coords: Dict[str, Tuple[float, float]],
    edges: Sequence[Tuple[str, str]],
    name: str,
    dash: str = "solid",
    width: float = 2.0,
) -> go.Scatter:
    xs: List[float | None] = []
    ys: List[float | None] = []
    for a, b in edges:
        xa, ya = coords[a]
        xb, yb = coords[b]
        xs.extend([xa, xb, None])
        ys.extend([ya, yb, None])
    return go.Scatter(
        x=xs,
        y=ys,
        mode="lines",
        name=name,
        line={"dash": dash, "width": width},
        hoverinfo="skip",
    )


def node_trace(
    coords: Dict[str, Tuple[float, float]],
    labels: Sequence[str],
    name: str,
    hover: Dict[str, str] | None = None,
    size: int = 18,
    symbol: str = "circle",
) -> go.Scatter:
    return go.Scatter(
        x=[coords[k][0] for k in labels],
        y=[coords[k][1] for k in labels],
        mode="markers+text",
        name=name,
        text=list(labels),
        textposition="top center",
        hovertext=[hover.get(k, k) if hover else k for k in labels],
        hoverinfo="text",
        marker={"size": size, "symbol": symbol, "line": {"width": 1}},
    )


def apply_xy_layout(fig: go.Figure, title: str, height: int = 650) -> go.Figure:
    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        xaxis={"visible": False, "scaleanchor": "y", "scaleratio": 1},
        yaxis={"visible": False},
        hoverlabel={"align": "left"},
    )
    return fig


# -----------------------------------------------------------------------------
# 한의학 구조 사전
# -----------------------------------------------------------------------------
AXES: List[Dict[str, str]] = [
    {"축": "보충축", "기하 역할": "결손 노드의 가중치·반경을 보완", "한의학 자료 태그": "보기·보혈·자음·보양"},
    {"축": "소통·전환축", "기하 역할": "막힌 모서리의 연결성과 방향을 전환", "한의학 자료 태그": "소간·이기·화해·해표"},
    {"축": "수렴·안정축", "기하 역할": "외향 벡터를 중심으로 회수", "한의학 자료 태그": "안신·수렴·고삽"},
    {"축": "배출·이수축", "기하 역할": "정체 노드에서 외부로 흐름을 분기", "한의학 자료 태그": "이수·화담·사하·청열"},
    {"축": "승양·상승축", "기하 역할": "수직 성분과 상향 방향성을 표시", "한의학 자료 태그": "승양·거함·온양"},
    {"축": "완충·조화축", "기하 역할": "대립 벡터 사이의 편차를 완충", "한의학 자료 태그": "조화영위·한열조화·완급"},
]
AXIS_NAMES = [row["축"] for row in AXES]
AXIS_INDEX = {name: idx for idx, name in enumerate(AXIS_NAMES)}

FIVE_PHASES: List[Dict[str, str]] = [
    {"오행": "목", "오장": "간", "오부": "담", "방향": "전개·소통", "계절": "봄"},
    {"오행": "화", "오장": "심", "오부": "소장", "방향": "상승·확산", "계절": "여름"},
    {"오행": "토", "오장": "비", "오부": "위", "방향": "중심·변환", "계절": "장하"},
    {"오행": "금", "오장": "폐", "오부": "대장", "방향": "수렴·숙강", "계절": "가을"},
    {"오행": "수", "오장": "신", "오부": "방광", "방향": "저장·하강", "계절": "겨울"},
]
PHASE_NAMES = [row["오행"] for row in FIVE_PHASES]
PHASE_INFO = {row["오행"]: row for row in FIVE_PHASES}

# 앱 내부의 기본 연구 배속이다. 고전의 직접 문장이나 임상 인과를 뜻하지 않는다.
AXIS_PHASE_MAP: Dict[str, List[str]] = {
    "보충축": ["토", "수"],
    "소통·전환축": ["목"],
    "수렴·안정축": ["금", "수"],
    "배출·이수축": ["수", "금"],
    "승양·상승축": ["화", "목"],
    "완충·조화축": ["토"],
}

STEMS: List[Dict[str, str]] = [
    {"천간": "갑(甲)", "음양": "양", "오행": "목"},
    {"천간": "을(乙)", "음양": "음", "오행": "목"},
    {"천간": "병(丙)", "음양": "양", "오행": "화"},
    {"천간": "정(丁)", "음양": "음", "오행": "화"},
    {"천간": "무(戊)", "음양": "양", "오행": "토"},
    {"천간": "기(己)", "음양": "음", "오행": "토"},
    {"천간": "경(庚)", "음양": "양", "오행": "금"},
    {"천간": "신(辛)", "음양": "음", "오행": "금"},
    {"천간": "임(壬)", "음양": "양", "오행": "수"},
    {"천간": "계(癸)", "음양": "음", "오행": "수"},
]

PLATONIC_ROWS: List[Dict[str, Any]] = [
    {"다면체": "정4면체", "V": 4, "E": 6, "F": 4, "꼭짓점 차수": 3, "쌍대": "정4면체", "연구 역할": "최소 입체·분기 단위"},
    {"다면체": "정6면체", "V": 8, "E": 12, "F": 6, "꼭짓점 차수": 3, "쌍대": "정8면체", "연구 역할": "중심·틀·형체 안정"},
    {"다면체": "정8면체", "V": 6, "E": 12, "F": 8, "꼭짓점 차수": 4, "쌍대": "정6면체", "연구 역할": "상하좌우 방향축"},
    {"다면체": "정12면체", "V": 20, "E": 30, "F": 12, "꼭짓점 차수": 3, "쌍대": "정20면체", "연구 역할": "12경락 전체환의 배속 후보"},
    {"다면체": "정20면체", "V": 12, "E": 30, "F": 20, "꼭짓점 차수": 5, "쌍대": "정12면체", "연구 역할": "세분화된 분포·유동층"},
]

BASE_TO_BITS = {"G": "00", "A": "10", "U": "01", "C": "11"}
BITS_TO_BASE = {value: key for key, value in BASE_TO_BITS.items()}
BASE_ORDER = ["G", "A", "U", "C"]


# -----------------------------------------------------------------------------
# 원본 데이터 → 기하학 노드 인덱스
# -----------------------------------------------------------------------------
def build_acupoint_index() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for prefix, (count, meridian, region, axis_text, _meaning, _warning) in MERIDIANS.items():
        for number in range(1, count + 1):
            code = f"{prefix}{number}"
            default_name = f"{meridian} {number}"
            default_std = code
            if code in ACU_OVERRIDES:
                override = ACU_OVERRIDES[code]
                name = clean_text(override[0]) or default_name
                standard = clean_text(override[1]) or default_std
            else:
                name = default_name
                standard = default_std
            rows.append(
                {
                    "code": code,
                    "혈명": name,
                    "standard_name": standard,
                    "경락 코드": prefix,
                    "경락": meridian,
                    "순번": number,
                    "부위군": region,
                    "기하학 축 태그": axis_text,
                }
            )
    return pd.DataFrame(rows)


ACUPOINTS = build_acupoint_index()
ACU_BY_CODE = ACUPOINTS.set_index("code").to_dict(orient="index")


def formula_structural_record(name: str) -> Dict[str, Any]:
    source = FORMULAS[name]
    axes = [axis for axis in source.get("처방 방향축", []) if axis in AXIS_INDEX]
    points = [code for code in source.get("핵심 혈위", []) if code in ACU_BY_CODE or code == "Anmian"]
    return {
        "분석 대상": name,
        "문헌 분류": source.get("분류", ""),
        "문헌 변증 태그": source.get("전통 변증", ""),
        "기능 서술": source.get("처방 방향", ""),
        "약재 노드": list(source.get("구성 약재", [])),
        "6축 태그": axes,
        "연계 경혈 코드": points,
    }


def formula_state(axes: Sequence[str]) -> int:
    state = 0
    for axis in axes:
        if axis in AXIS_INDEX:
            state |= 1 << AXIS_INDEX[axis]
    return state


def state_bits_little_endian(n: int) -> str:
    return "".join(str((n >> i) & 1) for i in range(6))


def state_to_codon(n: int) -> str:
    bits = state_bits_little_endian(n)
    return "".join(BITS_TO_BASE[bits[i : i + 2]] for i in range(0, 6, 2))


def q6_neighbors(n: int) -> List[int]:
    return [n ^ (1 << i) for i in range(6)]


def h34_neighbors(codon: str) -> List[str]:
    out: List[str] = []
    chars = list(codon)
    for position in range(3):
        for base in BASE_ORDER:
            if base != chars[position]:
                changed = chars.copy()
                changed[position] = base
                out.append("".join(changed))
    return out


# -----------------------------------------------------------------------------
# 기하학 시각화
# -----------------------------------------------------------------------------
def five_phase_figure(active_phases: Sequence[str]) -> go.Figure:
    coords_list = polar_xy(5, 1.0)
    coords = {name: coords_list[i] for i, name in enumerate(PHASE_NAMES)}
    generation = [("목", "화"), ("화", "토"), ("토", "금"), ("금", "수"), ("수", "목")]
    control = [("목", "토"), ("토", "수"), ("수", "화"), ("화", "금"), ("금", "목")]
    hover = {
        phase: (
            f"오행: {phase}<br>오장: {PHASE_INFO[phase]['오장']}<br>"
            f"오부: {PHASE_INFO[phase]['오부']}<br>구조 방향: {PHASE_INFO[phase]['방향']}"
        )
        for phase in PHASE_NAMES
    }
    fig = go.Figure()
    fig.add_trace(edge_trace(coords, generation, "상생 순환", "solid", 3))
    fig.add_trace(edge_trace(coords, control, "상극 관계", "dot", 2))
    fig.add_trace(node_trace(coords, PHASE_NAMES, "오행 노드", hover, 24))
    if active_phases:
        fig.add_trace(node_trace(coords, list(active_phases), "선택 자료의 배속", hover, 38, "circle-open"))
    return apply_xy_layout(fig, "오행 정오각형: 상생 순환과 상극 대각선", 620)


def stem_decagon_figure() -> go.Figure:
    names = [row["천간"] for row in STEMS]
    coords_list = polar_xy(10, 1.0)
    coords = {name: coords_list[i] for i, name in enumerate(names)}
    edges = [(names[i], names[(i + 1) % 10]) for i in range(10)]
    opposite = [(names[i], names[(i + 5) % 10]) for i in range(5)]
    hover = {
        row["천간"]: f"천간: {row['천간']}<br>음양: {row['음양']}<br>오행: {row['오행']}"
        for row in STEMS
    }
    fig = go.Figure()
    fig.add_trace(edge_trace(coords, edges, "정10각형 경계", "solid", 3))
    fig.add_trace(edge_trace(coords, opposite, "대향축", "dot", 1.5))
    fig.add_trace(node_trace(coords, names, "십간 노드", hover, 22))
    return apply_xy_layout(fig, "십간 정10각형 배열", 620)


def meridian_wheel_figure(selected_points: Sequence[str]) -> go.Figure:
    prefixes = list(MERIDIANS.keys())
    coords_list = polar_xy(len(prefixes), 1.0)
    coords = {prefix: coords_list[i] for i, prefix in enumerate(prefixes)}
    boundary = [(prefixes[i], prefixes[(i + 1) % len(prefixes)]) for i in range(len(prefixes))]
    hover = {
        prefix: (
            f"{prefix} · {MERIDIANS[prefix][1]}<br>표준 경혈 수: {MERIDIANS[prefix][0]}<br>"
            f"부위군: {MERIDIANS[prefix][2]}<br>축 태그: {MERIDIANS[prefix][3]}"
        )
        for prefix in prefixes
    }
    selected_meridians = []
    for code in selected_points:
        prefix = "".join(ch for ch in code if ch.isalpha())
        if prefix in coords and prefix not in selected_meridians:
            selected_meridians.append(prefix)
    fig = go.Figure()
    fig.add_trace(edge_trace(coords, boundary, "14경맥 환", "solid", 2.5))
    fig.add_trace(node_trace(coords, prefixes, "경맥 노드", hover, 20))
    if selected_meridians:
        fig.add_trace(node_trace(coords, selected_meridians, "선택 자료의 연계 경맥", hover, 36, "circle-open"))
    return apply_xy_layout(fig, "14경맥 기하학 환: 12경맥 + 임맥·독맥", 630)


def formula_network(record: Dict[str, Any], custom_nodes: Sequence[str]) -> Tuple[go.Figure, pd.DataFrame, pd.DataFrame]:
    formula = record["분석 대상"]
    axes = list(record["6축 태그"])
    herbs = list(record["약재 노드"])
    points = list(record["연계 경혈 코드"])
    custom = [node for node in custom_nodes if node]

    positions: Dict[str, Tuple[float, float]] = {formula: (0.0, 0.0)}
    node_rows = [{"id": formula, "종류": "처방 자료", "표시명": formula, "계층": 0}]
    edge_rows: List[Dict[str, str]] = []

    def add_ring(items: Sequence[str], radius: float, kind: str, relation: str, phase: float) -> None:
        if not items:
            return
        ring = polar_xy(len(items), radius, phase)
        for item, xy in zip(items, ring):
            positions[item] = xy
            node_rows.append({"id": item, "종류": kind, "표시명": item, "계층": radius})
            edge_rows.append({"source": formula, "target": item, "관계": relation})

    add_ring(axes, 1.4, "6축", "축 태그", math.pi / 2)
    add_ring(herbs, 2.7, "약재", "구성", math.pi / 2 + 0.13)
    add_ring(points, 4.0, "경혈", "연계 코드", math.pi / 2 + 0.27)
    add_ring(custom, 5.2, "사용자 노드", "사용자 연결", math.pi / 2 + 0.41)

    fig = go.Figure()
    relation_groups: Dict[str, List[Tuple[str, str]]] = {}
    for edge in edge_rows:
        relation_groups.setdefault(edge["관계"], []).append((edge["source"], edge["target"]))
    for relation, edges in relation_groups.items():
        fig.add_trace(edge_trace(positions, edges, relation, "solid", 1.7))

    kinds = ["처방 자료", "6축", "약재", "경혈", "사용자 노드"]
    symbols = {"처방 자료": "diamond", "6축": "hexagon", "약재": "circle", "경혈": "square", "사용자 노드": "triangle-up"}
    sizes = {"처방 자료": 30, "6축": 23, "약재": 18, "경혈": 17, "사용자 노드": 18}
    for kind in kinds:
        ids = [row["id"] for row in node_rows if row["종류"] == kind]
        if not ids:
            continue
        hover: Dict[str, str] = {}
        for node_id in ids:
            if kind == "경혈" and node_id in ACU_BY_CODE:
                point = ACU_BY_CODE[node_id]
                hover[node_id] = f"{node_id} · {point['혈명']}<br>{point['경락']}<br>{point['부위군']}"
            else:
                hover[node_id] = f"{kind}: {node_id}"
        fig.add_trace(node_trace(positions, ids, kind, hover, sizes[kind], symbols[kind]))

    apply_xy_layout(fig, f"{formula} 구조 네트워크", 760)
    return fig, pd.DataFrame(node_rows), pd.DataFrame(edge_rows)


def q6_local_figure(state: int) -> go.Figure:
    center = f"S{state}"
    neighbor_states = q6_neighbors(state)
    labels = [f"S{n}" for n in neighbor_states]
    coords: Dict[str, Tuple[float, float]] = {center: (0.0, 0.0)}
    for label, xy in zip(labels, polar_xy(6, 1.0)):
        coords[label] = xy
    edges = [(center, label) for label in labels]
    hover = {center: f"선택 상태 {state}<br>bits={state_bits_little_endian(state)}"}
    for axis, n, label in zip(AXIS_NAMES, neighbor_states, labels):
        hover[label] = f"{axis} 반전<br>상태 {n}<br>bits={state_bits_little_endian(n)}"
    fig = go.Figure()
    fig.add_trace(edge_trace(coords, edges, "1비트 변화", "solid", 2.5))
    fig.add_trace(node_trace(coords, [center], "선택 상태", hover, 32, "diamond"))
    fig.add_trace(node_trace(coords, labels, "Q6 이웃", hover, 22))
    return apply_xy_layout(fig, "Q6 국소 구조: 선택 상태와 6개 1비트 이웃", 590)


# -----------------------------------------------------------------------------
# 정확 검증
# -----------------------------------------------------------------------------
def polygon_audit(n: int, radius: sp.Expr = sp.Integer(1)) -> Dict[str, Any]:
    pts = exact_polygon(n, radius)
    radii2 = [sp.simplify(x * x + y * y) for x, y in pts]
    edges2 = []
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        edges2.append(sp.simplify((x2 - x1) ** 2 + (y2 - y1) ** 2))
    return {
        "n": n,
        "중심합 x": sp.simplify(sum(x for x, _ in pts)),
        "중심합 y": sp.simplify(sum(y for _, y in pts)),
        "반지름²": sp.simplify(radii2[0]),
        "반지름 동일": all(sp.simplify(value - radii2[0]) == 0 for value in radii2),
        "변 길이²": sp.simplify(edges2[0]),
        "변 길이 동일": all(sp.simplify(value - edges2[0]) == 0 for value in edges2),
        "좌표": pts,
    }


@st.cache_data(show_spinner=False)
def exact_audit_rows() -> Tuple[pd.DataFrame, pd.DataFrame]:
    pent = polygon_audit(5)
    dec = polygon_audit(10)
    phi = (sp.Integer(1) + sp.sqrt(5)) / 2
    dec_side = sp.sqrt(dec["변 길이²"])

    rows = [
        {"검증": "정오각형 중심합", "정확 결과": f"({stringify_exact(pent['중심합 x'])}, {stringify_exact(pent['중심합 y'])})", "판정": pent["중심합 x"] == 0 and pent["중심합 y"] == 0},
        {"검증": "정오각형 반지름 동일", "정확 결과": stringify_exact(pent["반지름²"]), "판정": pent["반지름 동일"]},
        {"검증": "정오각형 변 길이 동일", "정확 결과": stringify_exact(pent["변 길이²"]), "판정": pent["변 길이 동일"]},
        {"검증": "정10각형 중심합", "정확 결과": f"({stringify_exact(dec['중심합 x'])}, {stringify_exact(dec['중심합 y'])})", "판정": dec["중심합 x"] == 0 and dec["중심합 y"] == 0},
        {"검증": "정10각형 반지름 동일", "정확 결과": stringify_exact(dec["반지름²"]), "판정": dec["반지름 동일"]},
        {"검증": "정10각형 변 길이 동일", "정확 결과": stringify_exact(dec["변 길이²"]), "판정": dec["변 길이 동일"]},
        {"검증": "단위원 정10각형 변 길이", "정확 결과": stringify_exact(dec_side), "판정": sp.simplify(dec_side - 1 / phi) == 0},
        {"검증": "정10각형 R/side = φ", "정확 결과": stringify_exact(1 / dec_side), "판정": sp.simplify(1 / dec_side - phi) == 0},
        {"검증": "Q6 꼭짓점·차수·모서리", "정확 결과": "64, 6, 192", "판정": 64 * 6 // 2 == 192},
        {"검증": "H(3,4) 꼭짓점·차수·모서리", "정확 결과": "64, 9, 288", "판정": (4**3) * (3 * (4 - 1)) // 2 == 288},
    ]
    euler_rows = [
        {
            "다면체": row["다면체"],
            "V-E+F": row["V"] - row["E"] + row["F"],
            "오일러 판정": row["V"] - row["E"] + row["F"] == 2,
            "쌍대": row["쌍대"],
        }
        for row in PLATONIC_ROWS
    ]
    return pd.DataFrame(rows), pd.DataFrame(euler_rows)


# -----------------------------------------------------------------------------
# 입력: 환자 입력이 아니라 구조 분석 대상 입력
# -----------------------------------------------------------------------------
st.sidebar.header("구조 분석 설정")
formula_name = st.sidebar.selectbox("분석 대상 처방 자료", list(FORMULAS.keys()), index=list(FORMULAS.keys()).index("반하사심탕") if "반하사심탕" in FORMULAS else 0)
record = formula_structural_record(formula_name)

custom_node_text = st.sidebar.text_area(
    "사용자 정의 노드",
    placeholder="예: 소양, 심하비, 승강출입\n쉼표 또는 줄바꿈으로 구분",
    height=110,
)
custom_nodes = [item.strip() for item in custom_node_text.replace("\n", ",").split(",") if item.strip()]

extra_axes = st.sidebar.multiselect("추가 6축 태그", AXIS_NAMES, default=[])
selected_axes = list(dict.fromkeys(record["6축 태그"] + extra_axes))
selected_state = formula_state(selected_axes)

st.sidebar.divider()
st.sidebar.markdown(
    """
**도구의 방향**  
한의학 자료 → 기하학적 배치·관계·대칭·상태공간 분석

이 앱은 증상 입력으로 처방을 정하는 프로그램이 아닙니다.
"""
)


# -----------------------------------------------------------------------------
# 화면
# -----------------------------------------------------------------------------
st.title("🧭 한의학 기하학 구조 보조도구")
st.caption("처방·약재·경혈·경락·오행·육경 자료를 노드·모서리·축·다면체·상태공간으로 배치하고 비교하는 연구/교육용 구조 도구")
st.info("기하학적 배속은 한의학 자료를 정리하기 위한 형식 모델입니다. 고전의 직접 문장, 생물학적 인과 또는 자동 처방 판정을 뜻하지 않습니다.")

home_tab, phase_tab, stem_tab, q6_tab, network_tab, meridian_tab, solid_tab, audit_tab = st.tabs(
    [
        "1. 한의학 구조 홈",
        "2. 오행 정오각형",
        "3. 십간 정10각형",
        "4. 6축·64상태",
        "5. 처방·약재·경혈망",
        "6. 361경혈·14경맥",
        "7. 플라토닉 구조",
        "8. 정확 기호 검증",
    ]
)

with home_tab:
    st.header("한의학 자료를 기하학 언어로 바꾸는 화면")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("약재 노드", len(record["약재 노드"]))
    c2.metric("연계 경혈 코드", len(record["연계 경혈 코드"]))
    c3.metric("활성 6축", len(selected_axes))
    c4.metric("Q6 상태", selected_state)

    st.subheader("현재 분석 대상")
    show_df(
        [
            {"항목": "처방 자료", "내용": record["분석 대상"]},
            {"항목": "문헌 분류", "내용": record["문헌 분류"]},
            {"항목": "문헌 변증 태그", "내용": record["문헌 변증 태그"]},
            {"항목": "기능 서술", "내용": record["기능 서술"]},
            {"항목": "약재 노드", "내용": ", ".join(record["약재 노드"])},
            {"항목": "6축 태그", "내용": ", ".join(selected_axes) or "없음"},
            {"항목": "연계 경혈 코드", "내용": ", ".join(record["연계 경혈 코드"]) or "없음"},
            {"항목": "사용자 노드", "내용": ", ".join(custom_nodes) or "없음"},
        ]
    )

    st.subheader("기하학 변환 규칙")
    show_df(
        [
            {"한의학 자료": "처방·약재·경혈·장부·병기 태그", "기하학 객체": "노드(Vertex)", "의미": "분석 대상의 식별 단위"},
            {"한의학 자료": "구성·소속·연계·상생·상극", "기하학 객체": "모서리(Edge)", "의미": "두 자료 사이의 관계"},
            {"한의학 자료": "보충·소통·수렴·배출·상승·조화", "기하학 객체": "6축(Axis)", "의미": "기능 방향의 메타데이터"},
            {"한의학 자료": "오행·십간·경맥 순환", "기하학 객체": "정다각형·환(Cycle)", "의미": "순환 순서와 대향 관계"},
            {"한의학 자료": "64개 조합 상태", "기하학 객체": "Q6 / H(3,4)", "의미": "이진 6축 또는 3자리 4기호 상태공간"},
            {"한의학 자료": "12경락·방향·분포", "기하학 객체": "다면체 배속", "의미": "연구자가 정한 구조적 역할 비교"},
        ]
    )

    st.subheader("6축 사전")
    show_df(AXES)

with phase_tab:
    st.header("오행을 정오각형 관계망으로 배치")
    active_phases = sorted({phase for axis in selected_axes for phase in AXIS_PHASE_MAP.get(axis, [])}, key=PHASE_NAMES.index)
    left, right = st.columns([1.65, 1])
    with left:
        st.plotly_chart(five_phase_figure(active_phases), width="stretch")
    with right:
        st.subheader("현재 자료의 배속")
        show_df(
            [
                {"활성 축": axis, "기본 오행 배속": ", ".join(AXIS_PHASE_MAP.get(axis, [])), "성격": "앱 내부 연구 규칙"}
                for axis in selected_axes
            ]
        )
        st.subheader("오행 노드 사전")
        show_df(FIVE_PHASES)
        st.caption("상생은 외곽 순환, 상극은 대각선 관계로 표시합니다. 축→오행 대응은 수정 가능한 연구 배속이며 절대적 대응표가 아닙니다.")

with stem_tab:
    st.header("십간을 정10각형으로 배치")
    left, right = st.columns([1.6, 1])
    with left:
        st.plotly_chart(stem_decagon_figure(), width="stretch")
    with right:
        show_df(STEMS)
        phi = (sp.Integer(1) + sp.sqrt(5)) / 2
        st.markdown("### 정확한 정10각형 관계")
        st.latex(r"\varphi=\frac{1+\sqrt5}{2}")
        st.latex(r"R=1\quad\Longrightarrow\quad s=2\sin\frac{\pi}{10}=\frac{1}{\varphi}")
        st.latex(r"\frac{R}{s}=\varphi")
        st.caption("십간을 10개 꼭짓점에 순서대로 배치한 구조 모델입니다. 정10각형의 황금비 관계는 기하학적 사실이며, 한의학적 배속은 별도의 연구 규칙입니다.")

with q6_tab:
    st.header("6개 기능축을 64상태 공간으로 부호화")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("선택 상태 n", selected_state)
    c2.metric("6비트", state_bits_little_endian(selected_state))
    c3.metric("상보 상태", 63 - selected_state)
    c4.metric("3자리 4기호", state_to_codon(selected_state))

    left, right = st.columns([1.45, 1])
    with left:
        st.plotly_chart(q6_local_figure(selected_state), width="stretch")
    with right:
        st.subheader("비트와 6축")
        show_df(
            [
                {
                    "비트 위치": i,
                    "축": axis,
                    "현재 값": (selected_state >> i) & 1,
                    "1비트 이웃": selected_state ^ (1 << i),
                }
                for i, axis in enumerate(AXIS_NAMES)
            ]
        )

    st.subheader("Q6와 H(3,4)는 꼭짓점 수만 같고 연결 구조는 다름")
    show_df(
        [
            {"그래프": "Q6", "꼭짓점": 64, "꼭짓점 차수": 6, "모서리": 192, "인접 규칙": "6비트 중 정확히 1비트 반전"},
            {"그래프": "H(3,4)", "꼭짓점": 64, "꼭짓점 차수": 9, "모서리": 288, "인접 규칙": "3자리 중 정확히 1자리의 4기호를 다른 값으로 변경"},
        ]
    )

    codon = state_to_codon(selected_state)
    st.subheader("H(3,4) 국소 이웃")
    show_df(
        [
            {
                "선택 부호": codon,
                "이웃 부호": neighbor,
                "달라진 자리 수": sum(a != b for a, b in zip(codon, neighbor)),
                "표준 유전암호 표기": GENETIC_CODE.get(neighbor, ""),
            }
            for neighbor in h34_neighbors(codon)
        ],
        height=350,
    )
    st.caption("G/A/U/C와 아미노산 표시는 64상태를 읽기 위한 병렬 부호화입니다. 한약·경혈이 유전자나 아미노산을 직접 조절한다는 뜻이 아닙니다.")

with network_tab:
    st.header("처방 자료를 중심으로 약재·6축·경혈 노드를 연결")
    fig, node_df, edge_df = formula_network({**record, "6축 태그": selected_axes}, custom_nodes)
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("노드 표")
        show_df(node_df, height=390)
    with right:
        st.subheader("모서리 표")
        show_df(edge_df, height=390)

    nodes_csv = node_df.to_csv(index=False).encode("utf-8-sig")
    edges_csv = edge_df.to_csv(index=False).encode("utf-8-sig")
    d1, d2 = st.columns(2)
    d1.download_button("노드 CSV 다운로드", nodes_csv, f"{formula_name}_geometry_nodes.csv", "text/csv")
    d2.download_button("모서리 CSV 다운로드", edges_csv, f"{formula_name}_geometry_edges.csv", "text/csv")

with meridian_tab:
    st.header("361 표준 경혈을 14경맥 노드 체계로 사용")
    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(meridian_wheel_figure(record["연계 경혈 코드"]), width="stretch")
    with right:
        st.subheader("현재 자료의 연계 경혈 코드")
        linked_rows: List[Dict[str, Any]] = []
        for code in record["연계 경혈 코드"]:
            if code in ACU_BY_CODE:
                linked_rows.append({"code": code, **ACU_BY_CODE[code]})
            else:
                linked_rows.append({"code": code, "혈명": code, "경락": "경외기혈", "부위군": "", "기하학 축 태그": ""})
        show_df(linked_rows)

    st.subheader("361 경혈 기하학 노드 인덱스")
    search = st.text_input("경혈 코드·혈명·경락 검색", placeholder="예: ST36, 족삼리, 위경")
    filtered = ACUPOINTS.copy()
    if search.strip():
        query = search.strip().lower()
        mask = filtered.astype(str).apply(lambda col: col.str.lower().str.contains(query, regex=False)).any(axis=1)
        filtered = filtered[mask]
    show_df(filtered, height=500)
    st.caption("이 탭은 경혈을 시술 후보로 추천하지 않고, 경맥·순번·부위군·축 태그를 가진 기하학 노드로 검색합니다.")

with solid_tab:
    st.header("플라토닉 솔리드를 한의학 구조 역할과 비교")
    st.warning("아래 순서는 표준적인 다면체 변환 정리가 아니라 연구자가 정한 배속 순서입니다. 다면체 자체의 V·E·F·쌍대성은 정확한 수학 정보로 분리해 표시합니다.")

    show_df(PLATONIC_ROWS)

    st.subheader("한의학용 구조 배속 예시")
    show_df(
        [
            {"구조 대상": "음양·한열·허실의 최소 분기", "배속 후보": "정4면체", "이유": "가장 적은 면으로 이루어진 정다면체의 분기 구조"},
            {"구조 대상": "중초·토대·중심 안정", "배속 후보": "정6면체", "이유": "서로 직교하는 세 축과 안정된 격자 구조"},
            {"구조 대상": "승강출입·상하좌우", "배속 후보": "정8면체", "이유": "세 좌표축의 양·음 방향을 6개 꼭짓점으로 표시"},
            {"구조 대상": "12경락 전체환", "배속 후보": "정12면체", "이유": "12개 면을 경락 단위에 대응시키는 연구 배속"},
            {"구조 대상": "진액·수습·세분 분포", "배속 후보": "정20면체", "이유": "20개 면의 조밀한 분포망"},
        ]
    )

    st.subheader("쌍대 관계")
    st.latex(r"\text{정6면체}\leftrightarrow\text{정8면체},\qquad \text{정12면체}\leftrightarrow\text{정20면체},\qquad \text{정4면체}\leftrightarrow\text{정4면체}")
    st.caption("쌍대성은 면과 꼭짓점을 교환하는 정확한 기하학 관계입니다. 한의학 배속은 이 관계 위에 얹는 별도의 해석층입니다.")

with audit_tab:
    st.header("소수 근사가 아닌 기호식으로 구조를 검증")
    audit_df, euler_df = exact_audit_rows()
    show_df(audit_df)
    st.subheader("플라토닉 솔리드 오일러 검증")
    show_df(euler_df)

    st.subheader("현재 선택 상태의 정확한 부호")
    show_df(
        [
            {"항목": "활성 축", "정확 결과": ", ".join(selected_axes) or "없음"},
            {"항목": "Q6 정수 상태", "정확 결과": selected_state},
            {"항목": "6비트(축 순서)", "정확 결과": state_bits_little_endian(selected_state)},
            {"항목": "상보 상태", "정확 결과": 63 - selected_state},
            {"항목": "3자리 4기호 부호", "정확 결과": state_to_codon(selected_state)},
        ]
    )

    with st.expander("정오각형·정10각형 정확 좌표 보기"):
        for n in [5, 10]:
            audit = polygon_audit(n)
            st.markdown(f"#### 정{n}각형")
            show_df(
                [
                    {"k": k, "x": stringify_exact(x), "y": stringify_exact(y)}
                    for k, (x, y) in enumerate(audit["좌표"])
                ],
                height=330,
            )

    export_record = {
        "tool": "한의학 기하학 구조 보조도구 v3.0",
        "formula_record": record,
        "selected_axes": selected_axes,
        "custom_nodes": custom_nodes,
        "q6_state": selected_state,
        "q6_bits_little_endian": state_bits_little_endian(selected_state),
        "h34_code": state_to_codon(selected_state),
        "axis_phase_mapping": AXIS_PHASE_MAP,
    }
    st.download_button(
        "현재 구조 JSON 다운로드",
        data=json.dumps(export_record, ensure_ascii=False, indent=2),
        file_name=f"{formula_name}_tcm_geometry_structure.json",
        mime="application/json",
    )

st.divider()
st.caption("한의학용 기하학 보조도구: 한의학 자료를 구조화·배치·비교·검증합니다. 진단·처방·용량·침구 시술을 자동 결정하지 않습니다.")
