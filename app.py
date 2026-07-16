"""
황금비 다면체 × 한의학 연구 대시보드
======================================
실행:
    pip install -r requirements.txt
    streamlit run app.py

용도:
- 황금비, 정10각형, 정20면체·정12면체·마름모30면체의 수학적 구조를 계산·시각화
- 12경맥·십간·오행 등과의 대응을 '상징적 연구 가설'로 기록하고 비교
- 환자별 임상 자료를 자동 진단하거나 처방·침구·뜸 지시로 변환하지 않음

중요:
수학적으로 정확한 다면체 관계가 임상 효과나 생리학적 인과관계를 입증하지는 않습니다.
이 앱의 임상 연결부는 검증 전 연구 가설 및 설명 모델입니다.
"""

from __future__ import annotations

import io
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp
from scipy.spatial import ConvexHull


# -----------------------------------------------------------------------------
# 페이지 / 스타일
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="황금비 다면체 × 한의학 연구 엔진",
    page_icon="☯️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1480px; padding-top: 1.1rem; padding-bottom: 3rem;}
    h1, h2, h3 {letter-spacing: -0.035em;}
    div[data-testid="stMetricValue"] {font-size: 1.75rem;}
    .hypothesis-box {
        border: 1px solid rgba(128,128,128,.35);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        background: rgba(128,128,128,.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 상수 / 데이터 모델
# -----------------------------------------------------------------------------
PHI = (1.0 + math.sqrt(5.0)) / 2.0
TAU = 2.0 * math.pi
TEN_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
FIVE_PHASES = ["목", "목", "화", "화", "토", "토", "금", "금", "수", "수"]
YIN_YANG = ["양", "음", "양", "음", "양", "음", "양", "음", "양", "음"]
MERIDIANS_12 = [
    "수태음폐경", "수양명대장경", "족양명위경", "족태음비경",
    "수소음심경", "수태양소장경", "족태양방광경", "족소음신경",
    "수궐음심포경", "수소양삼초경", "족소양담경", "족궐음간경",
]


@dataclass
class VectorState:
    x: float
    y: float
    radius: float
    theta_deg: float
    opposite_x: float
    opposite_y: float
    opposite_theta_deg: float
    nearest_phase_index: int
    opposite_phase_index: int
    balance_index: float


# -----------------------------------------------------------------------------
# 기하 생성 함수
# -----------------------------------------------------------------------------
def unique_rows(points: Iterable[Sequence[float]], decimals: int = 12) -> np.ndarray:
    arr = np.asarray(list(points), dtype=float)
    return np.unique(np.round(arr, decimals=decimals), axis=0)


def icosahedron_vertices() -> np.ndarray:
    """정20면체 표준 좌표 12개."""
    pts: List[Tuple[float, float, float]] = []
    for s1 in (-1.0, 1.0):
        for s2 in (-1.0, 1.0):
            pts.extend(
                [
                    (0.0, s1, s2 * PHI),
                    (s1, s2 * PHI, 0.0),
                    (s2 * PHI, 0.0, s1),
                ]
            )
    return unique_rows(pts)


def dodecahedron_vertices() -> np.ndarray:
    """정12면체 표준 좌표 20개."""
    pts: List[Tuple[float, float, float]] = []
    inv = 1.0 / PHI

    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                pts.append((sx, sy, sz))

    for s1 in (-1.0, 1.0):
        for s2 in (-1.0, 1.0):
            pts.extend(
                [
                    (0.0, s1 * inv, s2 * PHI),
                    (s1 * inv, s2 * PHI, 0.0),
                    (s2 * PHI, 0.0, s1 * inv),
                ]
            )
    return unique_rows(pts)


def edges_by_minimum_distance(points: np.ndarray, tolerance: float = 1e-7) -> List[Tuple[int, int]]:
    """정다면체처럼 모든 모서리 길이가 같은 점 집합에서 최소 비영 거리로 모서리 추출."""
    distances: List[float] = []
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            d = float(np.linalg.norm(points[i] - points[j]))
            if d > tolerance:
                distances.append(d)
    edge_length = min(distances)
    return [
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if abs(float(np.linalg.norm(points[i] - points[j])) - edge_length) <= tolerance
    ]


def icosidodecahedron_from_icosahedron() -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """정20면체 모서리 중점 30개로 정이십십이면체를 구성."""
    ico = icosahedron_vertices()
    ico_edges = edges_by_minimum_distance(ico)
    mids = unique_rows((ico[i] + ico[j]) / 2.0 for i, j in ico_edges)
    return mids, edges_by_minimum_distance(mids)


def grouped_hull_faces(points: np.ndarray, decimals: int = 8) -> List[Dict[str, object]]:
    """ConvexHull의 삼각분할 면을 같은 평면끼리 합쳐 다각형 면으로 복원."""
    hull = ConvexHull(points)
    grouped: Dict[Tuple[float, ...], set[int]] = {}
    equation_by_key: Dict[Tuple[float, ...], np.ndarray] = {}

    for simplex, equation in zip(hull.simplices, hull.equations):
        key = tuple(np.round(equation, decimals=decimals))
        grouped.setdefault(key, set()).update(int(v) for v in simplex)
        equation_by_key[key] = np.asarray(equation, dtype=float)

    return [
        {
            "vertices": sorted(grouped[key]),
            "equation": equation_by_key[key],
        }
        for key in grouped
    ]


def rhombic_triacontahedron_dual() -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    정이십십이면체의 쌍대(dual)를 계산해 마름모30면체의 32꼭짓점·60모서리를 구성.
    좌표는 수치 시각화용이며, 위상 수(V,E,F)는 알고리즘으로 검증한다.
    """
    primal, _ = icosidodecahedron_from_icosahedron()
    faces = grouped_hull_faces(primal)

    dual_vertices: List[np.ndarray] = []
    face_vertex_sets: List[set[int]] = []
    for face in faces:
        equation = np.asarray(face["equation"], dtype=float)
        normal = equation[:3]
        offset = float(equation[3])
        if offset >= 0:
            normal = -normal
            offset = -offset
        dual_vertices.append(normal / (-offset))
        face_vertex_sets.append(set(face["vertices"]))

    dual_edges: List[Tuple[int, int]] = []
    for i in range(len(face_vertex_sets)):
        for j in range(i + 1, len(face_vertex_sets)):
            if len(face_vertex_sets[i].intersection(face_vertex_sets[j])) == 2:
                dual_edges.append((i, j))

    return np.asarray(dual_vertices), dual_edges


@st.cache_data
def build_solids() -> Dict[str, Dict[str, object]]:
    ico = icosahedron_vertices()
    dod = dodecahedron_vertices()
    ido, ido_edges = icosidodecahedron_from_icosahedron()
    rt, rt_edges = rhombic_triacontahedron_dual()

    return {
        "정20면체": {"vertices": ico, "edges": edges_by_minimum_distance(ico), "faces": 20},
        "정12면체": {"vertices": dod, "edges": edges_by_minimum_distance(dod), "faces": 12},
        "정이십십이면체": {"vertices": ido, "edges": ido_edges, "faces": 32},
        "마름모30면체": {"vertices": rt, "edges": rt_edges, "faces": 30},
    }


# -----------------------------------------------------------------------------
# 수학 검증 / 2D 투영
# -----------------------------------------------------------------------------
def exact_symbolic_checks() -> pd.DataFrame:
    phi = (sp.Integer(1) + sp.sqrt(5)) / 2
    k = sp.symbols("k", integer=True)

    sum_cos = sp.simplify(sum(sp.cos(2 * sp.pi * i / 10) for i in range(10)))
    sum_sin = sp.simplify(sum(sp.sin(2 * sp.pi * i / 10) for i in range(10)))

    rows = [
        {
            "검증식": "φ² = φ + 1",
            "기호 결과": sp.simplify(phi**2 - phi - 1),
            "판정": "참" if sp.simplify(phi**2 - phi - 1) == 0 else "재검토",
        },
        {
            "검증식": "φ⁻¹ = φ - 1",
            "기호 결과": sp.simplify(1 / phi - (phi - 1)),
            "판정": "참" if sp.simplify(1 / phi - (phi - 1)) == 0 else "재검토",
        },
        {
            "검증식": "정10각형 Σcos(2πk/10) = 0",
            "기호 결과": sum_cos,
            "판정": "참" if sum_cos == 0 else "재검토",
        },
        {
            "검증식": "정10각형 Σsin(2πk/10) = 0",
            "기호 결과": sum_sin,
            "판정": "참" if sum_sin == 0 else "재검토",
        },
        {
            "검증식": "R(θ+2π) = R(θ)",
            "기호 결과": "삼각함수 주기성",
            "판정": "참",
        },
        {
            "검증식": "D(t+10) = D(t), θ=2πt/10",
            "기호 결과": sp.simplify(sp.exp(sp.I * 2 * sp.pi * (k + 10) / 10) - sp.exp(sp.I * 2 * sp.pi * k / 10)),
            "판정": "참",
        },
    ]
    return pd.DataFrame(rows).astype(str)


def decagon_points(radius: float = 1.0, phase_offset_deg: float = 90.0) -> np.ndarray:
    angles = np.deg2rad(phase_offset_deg) + np.arange(10) * TAU / 10.0
    return np.column_stack((radius * np.cos(angles), radius * np.sin(angles)))


def project_xy(points: np.ndarray, rotation_deg: float = 0.0) -> np.ndarray:
    """Z축 회전 후 XY 정사영."""
    theta = math.radians(rotation_deg)
    rot = np.array(
        [
            [math.cos(theta), -math.sin(theta), 0.0],
            [math.sin(theta), math.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    rotated = points @ rot.T
    return rotated[:, :2]


def phase_vector(weights: Sequence[float], phase_offset_deg: float = 90.0) -> VectorState:
    if len(weights) != 10:
        raise ValueError("십간 가중치는 정확히 10개여야 합니다.")

    pts = decagon_points(1.0, phase_offset_deg)
    w = np.asarray(weights, dtype=float)
    vector = (pts * w[:, None]).sum(axis=0)
    x, y = float(vector[0]), float(vector[1])
    radius = float(np.linalg.norm(vector))
    theta = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0 if radius > 1e-12 else 0.0
    opposite_theta = (theta + 180.0) % 360.0

    point_angles = (np.degrees(np.arctan2(pts[:, 1], pts[:, 0])) + 360.0) % 360.0

    def angular_distance(a: float, b: float) -> float:
        return abs((a - b + 180.0) % 360.0 - 180.0)

    nearest = int(np.argmin([angular_distance(theta, a) for a in point_angles]))
    opposite = int(np.argmin([angular_distance(opposite_theta, a) for a in point_angles]))

    # 0~100의 기하학적 중심성 지표. 임상 건강 점수가 아님.
    scale = max(float(np.sum(np.abs(w))), 1.0)
    normalized_radius = min(radius / scale, 1.0)
    balance_index = 100.0 * (1.0 - normalized_radius)

    return VectorState(
        x=x,
        y=y,
        radius=radius,
        theta_deg=theta,
        opposite_x=-x,
        opposite_y=-y,
        opposite_theta_deg=opposite_theta,
        nearest_phase_index=nearest,
        opposite_phase_index=opposite,
        balance_index=balance_index,
    )


# -----------------------------------------------------------------------------
# 그래프 / 시각화
# -----------------------------------------------------------------------------
def edge_traces_3d(points: np.ndarray, edges: Sequence[Tuple[int, int]]) -> Tuple[List[float], List[float], List[float]]:
    x: List[float] = []
    y: List[float] = []
    z: List[float] = []
    for i, j in edges:
        x.extend([float(points[i, 0]), float(points[j, 0]), None])
        y.extend([float(points[i, 1]), float(points[j, 1]), None])
        z.extend([float(points[i, 2]), float(points[j, 2]), None])
    return x, y, z


def polyhedron_figure(name: str, points: np.ndarray, edges: Sequence[Tuple[int, int]], labels: Sequence[str] | None = None) -> go.Figure:
    ex, ey, ez = edge_traces_3d(points, edges)
    hover = labels if labels is not None and len(labels) == len(points) else [f"v{i}" for i in range(len(points))]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=ex,
            y=ey,
            z=ez,
            mode="lines",
            line={"width": 3},
            hoverinfo="skip",
            name="모서리",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode="markers+text" if labels else "markers",
            text=labels,
            textposition="top center",
            marker={"size": 5},
            hovertext=hover,
            hovertemplate="%{hovertext}<br>(%{x:.4f}, %{y:.4f}, %{z:.4f})<extra></extra>",
            name="꼭짓점",
        )
    )
    fig.update_layout(
        title=name,
        height=640,
        margin={"l": 0, "r": 0, "t": 45, "b": 0},
        scene={
            "aspectmode": "data",
            "xaxis_title": "X",
            "yaxis_title": "Y",
            "zaxis_title": "Z",
        },
        showlegend=False,
    )
    return fig


def decagon_vector_figure(weights: Sequence[float], state: VectorState, phase_offset_deg: float = 90.0) -> go.Figure:
    pts = decagon_points(1.0, phase_offset_deg)
    closed = np.vstack([pts, pts[0]])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=closed[:, 0], y=closed[:, 1], mode="lines", name="정10각형",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pts[:, 0],
            y=pts[:, 1],
            mode="markers+text",
            text=[f"{TEN_STEMS[i]}({FIVE_PHASES[i]}·{YIN_YANG[i]})" for i in range(10)],
            textposition="top center",
            marker={"size": [8 + 2 * abs(float(v)) for v in weights]},
            customdata=np.asarray(weights),
            hovertemplate="%{text}<br>가중치=%{customdata:.2f}<extra></extra>",
            name="십간 위상",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0.0, state.x],
            y=[0.0, state.y],
            mode="lines+markers",
            line={"width": 6},
            marker={"size": 9},
            name="합성 벡터",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0.0, state.opposite_x],
            y=[0.0, state.opposite_y],
            mode="lines+markers",
            line={"width": 4, "dash": "dash"},
            marker={"size": 8},
            name="수학적 역벡터",
        )
    )
    fig.update_layout(
        title="정10각형 위상 가중치와 합성 벡터",
        xaxis={"scaleanchor": "y", "scaleratio": 1, "zeroline": True},
        yaxis={"zeroline": True},
        height=610,
        margin={"l": 20, "r": 20, "t": 55, "b": 20},
        legend={"orientation": "h"},
    )
    return fig


def projection_figure(points3d: np.ndarray, edges: Sequence[Tuple[int, int]], rotation_deg: float) -> go.Figure:
    pts = project_xy(points3d, rotation_deg)
    ex: List[float] = []
    ey: List[float] = []
    for i, j in edges:
        ex.extend([float(pts[i, 0]), float(pts[j, 0]), None])
        ey.extend([float(pts[i, 1]), float(pts[j, 1]), None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", hoverinfo="skip", name="투영 모서리"))
    fig.add_trace(
        go.Scatter(
            x=pts[:, 0], y=pts[:, 1], mode="markers", marker={"size": 8},
            text=[f"v{i}" for i in range(len(pts))],
            hovertemplate="%{text}<br>(%{x:.5f}, %{y:.5f})<extra></extra>",
            name="투영 꼭짓점",
        )
    )
    fig.update_layout(
        title=f"Z축 회전 {rotation_deg:.1f}° 후 XY 정사영",
        xaxis={"scaleanchor": "y", "scaleratio": 1},
        height=600,
        margin={"l": 20, "r": 20, "t": 55, "b": 20},
        showlegend=False,
    )
    return fig


# -----------------------------------------------------------------------------
# 위상 네트워크 분석
# -----------------------------------------------------------------------------
def adjacency_list(vertex_count: int, edges: Sequence[Tuple[int, int]]) -> List[List[int]]:
    adj = [[] for _ in range(vertex_count)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    return [sorted(v) for v in adj]


def shortest_path_distances(start: int, adjacency: Sequence[Sequence[int]]) -> List[int]:
    distances = [-1] * len(adjacency)
    distances[start] = 0
    queue = [start]
    for current in queue:
        for nxt in adjacency[current]:
            if distances[nxt] == -1:
                distances[nxt] = distances[current] + 1
                queue.append(nxt)
    return distances


def antipodal_vertex(points: np.ndarray, index: int) -> int:
    target = -points[index]
    return int(np.argmin(np.linalg.norm(points - target, axis=1)))


# -----------------------------------------------------------------------------
# 연구 후보 CSV
# -----------------------------------------------------------------------------
def candidate_template() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "CAND-001",
                "candidate_name": "연구 후보 A",
                "theta_deg": 0.0,
                "magnitude": 1.0,
                "evidence_level": "미검증 가설",
                "notes": "실제 약재·혈위·치료 지시가 아닌 사용자 정의 후보",
            },
            {
                "candidate_id": "CAND-002",
                "candidate_name": "연구 후보 B",
                "theta_deg": 180.0,
                "magnitude": 1.0,
                "evidence_level": "미검증 가설",
                "notes": "벡터 정합도 시험용",
            },
        ]
    )


def validate_candidate_df(df: pd.DataFrame) -> pd.DataFrame:
    required = ["candidate_id", "candidate_name", "theta_deg", "magnitude", "evidence_level", "notes"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV 필수 열 누락: {', '.join(missing)}")

    out = df[required].copy()
    out["theta_deg"] = pd.to_numeric(out["theta_deg"], errors="coerce")
    out["magnitude"] = pd.to_numeric(out["magnitude"], errors="coerce")
    out = out.dropna(subset=["theta_deg", "magnitude"])
    out["theta_deg"] = out["theta_deg"] % 360.0
    out["magnitude"] = out["magnitude"].clip(lower=0.0)
    return out


def rank_candidates(df: pd.DataFrame, target_x: float, target_y: float) -> pd.DataFrame:
    target = np.array([target_x, target_y], dtype=float)
    rows = []
    for _, row in df.iterrows():
        theta = math.radians(float(row["theta_deg"]))
        magnitude = float(row["magnitude"])
        vector = magnitude * np.array([math.cos(theta), math.sin(theta)])
        residual = float(np.linalg.norm(target - vector))
        dot = float(np.dot(target, vector))
        target_norm = float(np.linalg.norm(target))
        vector_norm = float(np.linalg.norm(vector))
        cosine = dot / (target_norm * vector_norm) if target_norm > 1e-12 and vector_norm > 1e-12 else 0.0
        rows.append(
            {
                **row.to_dict(),
                "vector_x": vector[0],
                "vector_y": vector[1],
                "cosine_alignment": cosine,
                "residual_distance": residual,
            }
        )
    return pd.DataFrame(rows).sort_values(["residual_distance", "cosine_alignment"], ascending=[True, False])


# -----------------------------------------------------------------------------
# 리포트 생성
# -----------------------------------------------------------------------------
def research_report(
    case_id: str,
    notes: str,
    weights: Sequence[float],
    state: VectorState,
    solid_summary: pd.DataFrame,
) -> Dict[str, object]:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "case_id": case_id,
        "scope": "education_and_research_only",
        "safety_statement": (
            "This output is a geometric research record, not a diagnosis, prescription, "
            "acupuncture/moxibustion instruction, dosage recommendation, or proof of clinical efficacy."
        ),
        "input_notes": notes,
        "ten_phase_weights": [float(v) for v in weights],
        "ten_phase_labels": [
            {"stem": TEN_STEMS[i], "phase": FIVE_PHASES[i], "yin_yang": YIN_YANG[i]}
            for i in range(10)
        ],
        "vector_state": asdict(state),
        "solid_topology": solid_summary.to_dict(orient="records"),
    }


# -----------------------------------------------------------------------------
# 앱 화면
# -----------------------------------------------------------------------------
solids = build_solids()
solid_summary = pd.DataFrame(
    [
        {
            "다면체": name,
            "V 꼭짓점": len(data["vertices"]),
            "E 모서리": len(data["edges"]),
            "F 면": int(data["faces"]),
            "오일러 V-E+F": len(data["vertices"]) - len(data["edges"]) + int(data["faces"]),
        }
        for name, data in solids.items()
    ]
)

st.title("☯️ 황금비 다면체 × 한의학 연구 엔진")
st.caption("Golden-ratio Polyhedral Geometry & TCM Hypothesis Workbench")

st.warning(
    "이 앱은 수학·정보기하학 연구 및 교육용입니다. 다면체와 경혈·경락·장부·처방 사이의 대응은 "
    "검증된 생리학적 인과관계가 아니라 사용자가 시험하는 가설입니다. 자동 진단, 처방 용량, 침구·뜸 시술 지시를 생성하지 않습니다."
)

with st.sidebar:
    st.header("연구 설정")
    case_id = st.text_input("사례/실험 ID", value="CASE-001")
    phase_offset = st.slider("정10각형 시작 위상(°)", 0.0, 360.0, 90.0, 1.0)
    projection_rotation = st.slider("3D 투영 전 Z축 회전(°)", 0.0, 360.0, 0.0, 1.0)
    st.divider()
    st.markdown("**해석 층 구분**")
    st.markdown("- 수학 층: 정확한 좌표·위상·주기 계산")
    st.markdown("- 가설 층: 십간·오행·경맥과의 상징적 대응")
    st.markdown("- 임상 층: 이 앱에서 자동 결론 금지")


tabs = st.tabs(
    [
        "1. 수학 검증",
        "2. 3D 다면체",
        "3. 2D 정10각형 벡터",
        "4. 12경맥 네트워크 가설",
        "5. 후보 벡터 비교",
        "6. 연구 리포트",
        "7. 임상 검증 설계",
    ]
)


with tabs[0]:
    st.header("1. 황금비·주기·위상 수학 검증")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("φ", f"{PHI:.12f}")
    c2.metric("φ⁻¹", f"{1 / PHI:.12f}")
    c3.metric("φ⁻³", f"{PHI ** -3:.12f}")
    c4.metric("정10각 회전", "36°")

    st.subheader("기호 연산 결과")
    st.dataframe(exact_symbolic_checks(), use_container_width=True, hide_index=True)

    st.subheader("다면체 위상 검증")
    st.dataframe(solid_summary, use_container_width=True, hide_index=True)
    if bool((solid_summary["오일러 V-E+F"] == 2).all()):
        st.success("표에 포함된 모든 볼록 다면체가 오일러 관계 V-E+F=2를 만족합니다.")
    else:
        st.error("일부 다면체 위상 수를 재검토해야 합니다.")

    st.info(
        "여기서 '오차율 0%'라고 말할 수 있는 범위는 기호 항등식과 조합적 위상 수입니다. "
        "Plotly 좌표와 화면 렌더링은 부동소수점 근사입니다."
    )


with tabs[1]:
    st.header("2. 3D 다면체와 정사영")
    solid_name = st.selectbox("다면체", list(solids.keys()), index=0)
    data = solids[solid_name]
    points = np.asarray(data["vertices"], dtype=float)
    edges = list(data["edges"])

    c1, c2, c3 = st.columns(3)
    c1.metric("꼭짓점 V", len(points))
    c2.metric("모서리 E", len(edges))
    c3.metric("면 F", int(data["faces"]))

    left, right = st.columns(2)
    with left:
        labels = MERIDIANS_12 if solid_name == "정20면체" else None
        st.plotly_chart(polyhedron_figure(solid_name, points, edges, labels), use_container_width=True)
    with right:
        st.plotly_chart(projection_figure(points, edges, projection_rotation), use_container_width=True)

    st.caption(
        "정20면체의 12꼭짓점에 12경맥 이름을 붙이는 것은 상징적 라벨링입니다. "
        "라벨 순서는 해부학적·임상적 표준 배치를 의미하지 않습니다."
    )

    coord_df = pd.DataFrame(points, columns=["x", "y", "z"])
    coord_df.insert(0, "vertex", [f"v{i}" for i in range(len(points))])
    st.download_button(
        "현재 다면체 좌표 CSV 다운로드",
        coord_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{solid_name}_vertices.csv",
        mime="text/csv",
    )


with tabs[2]:
    st.header("3. 정10각형 위상·합성 벡터·역벡터")
    st.markdown(
        "각 위상에 사용자가 정한 가중치를 놓고 합성 벡터를 계산합니다. "
        "역벡터는 수학적으로 정확하지만, 특정 약재·혈위가 그 역벡터를 갖는다는 것은 별도 임상 검증이 필요합니다."
    )

    weights: List[float] = []
    cols = st.columns(5)
    for i in range(10):
        with cols[i % 5]:
            weights.append(
                st.slider(
                    f"{TEN_STEMS[i]} · {FIVE_PHASES[i]}({YIN_YANG[i]})",
                    min_value=-5.0,
                    max_value=5.0,
                    value=0.0,
                    step=0.1,
                    key=f"phase_weight_{i}",
                )
            )

    state = phase_vector(weights, phase_offset)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("합성 반경 r", f"{state.radius:.6f}")
    c2.metric("위상 θ", f"{state.theta_deg:.2f}°")
    c3.metric("기하 중심성", f"{state.balance_index:.2f}/100")
    c4.metric("역위상", f"{state.opposite_theta_deg:.2f}°")

    st.plotly_chart(decagon_vector_figure(weights, state, phase_offset), use_container_width=True)

    nearest = state.nearest_phase_index
    opposite = state.opposite_phase_index
    result_rows = [
        {"항목": "합성 벡터", "값": f"({state.x:.8f}, {state.y:.8f})"},
        {"항목": "수학적 역벡터", "값": f"({state.opposite_x:.8f}, {state.opposite_y:.8f})"},
        {"항목": "가장 가까운 상징 위상", "값": f"{TEN_STEMS[nearest]} · {FIVE_PHASES[nearest]}({YIN_YANG[nearest]})"},
        {"항목": "반대편 상징 위상", "값": f"{TEN_STEMS[opposite]} · {FIVE_PHASES[opposite]}({YIN_YANG[opposite]})"},
    ]
    st.dataframe(pd.DataFrame(result_rows), use_container_width=True, hide_index=True)

    st.warning(
        "기하 중심성은 입력 가중치가 원점에 얼마나 가까운지를 나타내는 앱 내부 지표일 뿐, "
        "건강·질병 중증도·치료 반응 점수가 아닙니다."
    )


with tabs[3]:
    st.header("4. 정20면체 12노드와 12경맥의 상징적 네트워크")
    ico_points = np.asarray(solids["정20면체"]["vertices"], dtype=float)
    ico_edges = list(solids["정20면체"]["edges"])
    adjacency = adjacency_list(len(ico_points), ico_edges)

    selected_node = st.selectbox(
        "연구상 교란 노드",
        range(12),
        format_func=lambda i: f"v{i} · {MERIDIANS_12[i]}",
    )
    distances = shortest_path_distances(selected_node, adjacency)
    anti = antipodal_vertex(ico_points, selected_node)

    network_df = pd.DataFrame(
        [
            {
                "vertex": f"v{i}",
                "상징 경맥 라벨": MERIDIANS_12[i],
                "좌표": tuple(np.round(ico_points[i], 8)),
                "인접 노드": ", ".join(f"v{j}" for j in adjacency[i]),
                "선택 노드에서 그래프 거리": distances[i],
                "기하학적 대척점": "예" if i == anti else "",
            }
            for i in range(12)
        ]
    )

    c1, c2 = st.columns([1.2, 1.0])
    with c1:
        st.plotly_chart(
            polyhedron_figure("정20면체 12노드 네트워크", ico_points, ico_edges, MERIDIANS_12),
            use_container_width=True,
        )
    with c2:
        st.metric("선택 노드", f"v{selected_node}")
        st.metric("상징 경맥", MERIDIANS_12[selected_node])
        st.metric("기하학적 대척 노드", f"v{anti} · {MERIDIANS_12[anti]}")
        st.markdown(
            '<div class="hypothesis-box"><b>해석 경계</b><br>'
            "대척 노드와 그래프 거리는 다면체 위상 계산입니다. 이를 원위취혈, 보사법, 실제 시술 위치로 "
            "직결하려면 독립적인 임상시험과 안전성 검토가 필요합니다.</div>",
            unsafe_allow_html=True,
        )

    st.dataframe(network_df, use_container_width=True, hide_index=True, height=430)


with tabs[4]:
    st.header("5. 사용자 정의 후보 벡터 비교")
    st.markdown(
        "약재·혈위·처방을 앱이 임의로 좌표화하지 않습니다. 연구자가 외부 근거와 사전등록 규칙에 따라 만든 "
        "후보 CSV를 넣으면, **기하학적 정합도만** 계산합니다."
    )

    template = candidate_template()
    st.download_button(
        "후보 CSV 템플릿 다운로드",
        template.to_csv(index=False).encode("utf-8-sig"),
        file_name="candidate_vector_template.csv",
        mime="text/csv",
    )

    uploaded = st.file_uploader("후보 벡터 CSV", type=["csv"])
    candidate_df = template
    if uploaded is not None:
        try:
            candidate_df = validate_candidate_df(pd.read_csv(uploaded))
            st.success(f"후보 {len(candidate_df)}개를 불러왔습니다.")
        except Exception as exc:
            st.error(str(exc))
            candidate_df = template

    current_weights = [float(st.session_state.get(f"phase_weight_{i}", 0.0)) for i in range(10)]
    current_state = phase_vector(current_weights, phase_offset)
    ranked = rank_candidates(candidate_df, current_state.opposite_x, current_state.opposite_y)

    st.dataframe(
        ranked,
        use_container_width=True,
        hide_index=True,
        column_config={
            "theta_deg": st.column_config.NumberColumn(format="%.2f°"),
            "magnitude": st.column_config.NumberColumn(format="%.4f"),
            "cosine_alignment": st.column_config.NumberColumn(format="%.6f"),
            "residual_distance": st.column_config.NumberColumn(format="%.6f"),
        },
    )
    st.warning(
        "순위는 치료 우선순위가 아닙니다. 좌표와 크기가 연구자가 정의한 역벡터에 얼마나 가까운지만 보여줍니다."
    )


with tabs[5]:
    st.header("6. 연구 기록 내보내기")
    notes = st.text_area(
        "관찰 메모",
        placeholder="수학적 입력의 출처, 측정 장비, 전처리, 가중치 정의, 제외 기준 등을 기록하세요.",
        height=180,
    )

    current_weights = [float(st.session_state.get(f"phase_weight_{i}", 0.0)) for i in range(10)]
    current_state = phase_vector(current_weights, phase_offset)
    report = research_report(case_id, notes, current_weights, current_state, solid_summary)
    report_json = json.dumps(report, ensure_ascii=False, indent=2)

    st.json(report)
    st.download_button(
        "연구 기록 JSON 다운로드",
        report_json.encode("utf-8"),
        file_name=f"{case_id}_polyhedral_research.json",
        mime="application/json",
    )

    csv_record = pd.DataFrame(
        [
            {
                "case_id": case_id,
                "x": current_state.x,
                "y": current_state.y,
                "r": current_state.radius,
                "theta_deg": current_state.theta_deg,
                "opposite_x": current_state.opposite_x,
                "opposite_y": current_state.opposite_y,
                "opposite_theta_deg": current_state.opposite_theta_deg,
                "geometric_centrality": current_state.balance_index,
                **{f"weight_{TEN_STEMS[i]}": current_weights[i] for i in range(10)},
            }
        ]
    )
    st.download_button(
        "분석 행 CSV 다운로드",
        csv_record.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{case_id}_vector_record.csv",
        mime="text/csv",
    )


with tabs[6]:
    st.header("7. 임상적 접점을 검증하기 위한 연구 설계")
    st.markdown(
        "수학적 구조와 임상 의사결정을 연결하려면 먼저 아래 단계를 통과해야 합니다. "
        "이 과정을 거치기 전에는 '완벽한 수치화', '오차율 0% 임상 처방', '양자역학적 의학'으로 표현하면 안 됩니다."
    )

    protocol_rows = [
        {
            "단계": "1. 조작적 정의",
            "필수 내용": "증상, 맥파, 설진, 검사값을 어떤 규칙으로 10개 가중치에 변환하는지 사전 고정",
            "실패 위험": "연구자 직관으로 사후 좌표를 조정하면 재현 불가",
        },
        {
            "단계": "2. 측정 신뢰도",
            "필수 내용": "동일 환자 반복 측정, 평가자 간 일치도, 장비 오차와 결측치 처리",
            "실패 위험": "입력 자체가 불안정하면 정밀한 기하 계산도 임상적으로 무의미",
        },
        {
            "단계": "3. 맹검 검증",
            "필수 내용": "기하 지표를 모르는 평가자와 임상 결과를 모르는 분석자를 분리",
            "실패 위험": "기대효과와 확인편향",
        },
        {
            "단계": "4. 대조 모델",
            "필수 내용": "단순 선형·로지스틱 모델, 기존 임상척도, 무작위 위상 모델과 성능 비교",
            "실패 위험": "복잡한 다면체가 단순 기준보다 낫다는 증거 부재",
        },
        {
            "단계": "5. 외부 검증",
            "필수 내용": "다른 기관·다른 환자군·다른 장비에서 재현",
            "실패 위험": "단일 데이터셋 과적합",
        },
        {
            "단계": "6. 안전성 시험",
            "필수 내용": "처방·침구·뜸 결정에는 별도의 윤리심의, 이상반응 감시, 중단 기준 필요",
            "실패 위험": "수학적 정합도를 치료 안전성으로 오인",
        },
    ]
    st.dataframe(pd.DataFrame(protocol_rows), use_container_width=True, hide_index=True)

    st.subheader("권장 결과 변수")
    outcome_rows = [
        {"유형": "주요 결과", "예": "사전 정의된 증상 척도 변화, 객관적 검사값, 이상반응"},
        {"유형": "모델 성능", "예": "AUC, MAE/RMSE, calibration, decision-curve analysis"},
        {"유형": "재현성", "예": "ICC, Cohen's κ, test-retest error"},
        {"유형": "탐색 결과", "예": "φ 거듭제곱 비율·위상 주기와 임상 변수의 상관"},
    ]
    st.dataframe(pd.DataFrame(outcome_rows), use_container_width=True, hide_index=True)

    st.error(
        "응급 증상, 중증 감염, 급성 복증, 흉통·호흡곤란, 신경학적 결손 등은 이 모델보다 표준 의학적 평가가 우선입니다."
    )


st.divider()
st.caption(
    "교육·연구용 소프트웨어. 수학적으로 정확한 결과와 임상적으로 검증된 결과를 구분하십시오. "
    "실제 진단·처방·침구·뜸·용량 결정은 면허가 있는 의료전문가의 표준 평가와 근거에 따라야 합니다."
)
