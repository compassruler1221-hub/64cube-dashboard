import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 0. 64큐브 매핑 무결성 검산 (Assertion)
# ==========================================
def n_to_codon(n):
    bases = {0: 'G', 1: 'A', 2: 'U', 3: 'C'}
    b1 = n % 4
    b2 = (n // 4) % 4
    b3 = (n // 16) % 4
    return bases[b1] + bases[b2] + bases[b3]

def codon_to_aa(codon):
    genetic_code = {
        'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
        'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
        'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met',
        'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
        'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
        'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
        'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
        'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
        'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'Stop', 'UAG': 'Stop',
        'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
        'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
        'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
        'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'Stop', 'UGG': 'Trp',
        'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
        'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
        'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
    }
    return genetic_code.get(codon, "Unknown")

assert n_to_codon(0) == "GGG"
assert codon_to_aa(n_to_codon(0)) == "Gly"

# ==========================================
# 1. 페이지 설정 및 필수 방어 가이드라인
# ==========================================
st.set_page_config(page_title="한의 임상 의사결정 지원 대시보드", layout="wide")

st.warning(
    "**[주의] 본 대시보드에서 한의학 처방 분석은 전통 처방의 생리적 효과를 자동으로 증명하거나 예측하는 시스템이 아닙니다.**\n\n"
    "- 이 시스템의 약재-코돈 매핑은 약재가 실제 유전암호를 조절한다는 뜻이 아닙니다.\n"
    "- 실제 처방은 면허가 있는 한의사의 변증, 환자 병력, 검사 결과, 안전성 평가를 바탕으로 결정되어야 합니다."
)

st.title("☯️ 한의 임상 의사결정 지원 대시보드 (CDSS)")
st.markdown("### 처방 해석 구조 = 전통 처방 구조 + 동의보감 병증 해석 + 진맥·설진 대조 + 침구 방향 + 뜸 주의 + 주변 변화 가능성 + 안전성 확인")

with st.expander("🔬 연구자용 공식 보기 (Click to Expand)"):
    st.caption("Formula_Vector = Traditional_Core + Donguibogam_Layer + Mac_Tongue_Sync + Acu_Moxa_Layer + H(3,4)_Extension + Polyhedron_Balance + Safety_Filter + Q6_Core_Annotation")

st.markdown(
    "전통 처방 구조와 동의보감 병증 해석을 **중심 설명층**으로 두고, "
    "Q6·H(3,4)·다면체 구조는 이를 보조적으로 주석화하는 해석층으로 사용합니다."
)

# ==========================================
# 2. 데이터베이스 세팅 (처방 라인업 1차 확장)
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_id": ["F001", "F002", "F003", "F004", "F005", "F006", "F007"],
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환", "귀비탕", "십전대보탕", "이진탕"],
        "indication_traditional": ["심비양허, 허번불면", "비위습탁, 복부팽만", "비위기허, 중기하함", "간신음허, 허열도한", "심비양허, 기혈양허, 불면", "기혈양허, 허로", "습담, 오심구토, 현훈"],
        "pattern_tags": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복", "승양, 익기, 에너지부스팅", "자음, 보신, 구조물질보충", "보기, 보혈, 안신", "대보원기, 온양", "조습, 화담, 이기"],
        "q6_core_vector": ["보존형 변화 및 수렴형 완충 주도", "급진 전환형 변화 주도", "발산/상승 및 전환형 변화 주도", "보존형 변화 및 수렴형 완충 방향 주도", "Level 3 매핑 진행 중", "Level 3 매핑 진행 중", "Level 3 매핑 진행 중"],
        "trad_interpret": [
            "혈(血)을 기르고 심(心)을 안정시키며 허열을 수렴하는 방향",
            "비위의 습탁을 건조하게 하고 기체의 흐름을 회복하는 방향",
            "아래로 처진 기를 끌어올리고 비위의 운화 및 전신 기력을 회복하는 방향",
            "소모된 바탕을 보충하고 허열과 수분 정체를 함께 조절하는 삼보삼사(三補三瀉) 방향",
            "심비(心脾)를 보익하여 기혈을 생성하고 정신을 안정시키는 방향",
            "기(氣)와 혈(血)을 전면적으로 보충하여 극도의 허로 상태를 회복하는 방향",
            "비장(脾臟)의 습(濕)을 말리고 담(痰)을 삭여 체내 비정상적 수분 정체를 해소하는 방향"
        ]
    })

    donguibogam = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환", "귀비탕", "십전대보탕", "이진탕"],
        "db_chapter": ["신형(身形), 몽(夢)", "내경편 비위(脾胃)", "내경편 기(氣), 내상(內傷)", "내경편 신(腎), 소아(小兒)", "내경편 신(神), 몽(夢)", "내경편 허로(虛勞)", "내경편 담음(痰飮)"],
        "db_pattern": ["허번불면(虛煩不眠), 심담허겁(心膽虛怯)", "식적(食積), 담음(痰飮), 비위 불화", "노권상(勞倦傷), 음식상(飮食傷), 기허발열(氣虛發熱)", "신수(腎水) 부족, 진음(眞陰) 고갈", "사려과다(思慮過多), 건망, 정충", "기혈양허(氣血兩虛), 구병(久病)", "담음(痰飮), 위기불화(胃氣不和)"],
        "db_interpret": [
            "과도한 사려(思慮)로 심비(心脾)가 상하여 발생하는 수면 장애와 정서 불안을 다스리는 방향성을 제시합니다.",
            "비위의 운화 기능이 떨어져 습(濕)이 정체된 병증에 대해 덥히고 말려 기기를 소통시키는 병리적 주석을 제공합니다.",
            "과도한 피로와 섭생 불량으로 중기가 무너져 열이 위로 뜨는 허열을 내리고 맑은 양기를 끌어올리는 승양의 지혜를 담고 있습니다.",
            "선천적 바탕이 부족하거나 극심한 소모로 정(精)이 고갈된 상태를 채워 체액의 고갈을 막는 근본적인 보음(補陰)의 원리입니다.",
            "생각을 너무 많이 하여 심(心)과 비(脾)가 상해 잠을 못 자고 가슴이 두근거리는 것을 치료하는 보익(補益) 원리입니다.",
            "음양기혈(陰陽氣血)이 모두 허해진 상태를 크게 보(大補)하여 몸의 근본 바탕을 재건하는 원리입니다.",
            "모든 담음(痰飮) 병증의 기본 방제로, 비위를 다스려 담이 생성되는 근본 원인을 제거하는 이치입니다."
        ]
    })
    
    clinical = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환", "귀비탕", "십전대보탕", "이진탕"],
        "clinic_pattern": [
            "간신음허, 허번불면, 도한 동반 가능성",
            "비위습탁, 기체, 소화불량 및 복부 팽만 동반 가능성",
            "비위기허, 중기하함, 만성 피로 및 기력 저하 동반 가능성",
            "간신음허, 정혈 부족, 허열, 수분 정체 동반 가능성",
            "심비양허, 수면장애, 불안, 식욕부진 동반 가능성",
            "기혈양허, 극심한 피로, 냉증 동반 가능성",
            "담음 정체, 오심, 구토, 어지럼증 동반 가능성"
        ],
        "clinic_structure": [
            "- 핵심 해석: 소모된 진액을 보충하고 허열을 진정시키는 수렴형 처방",
            "- 핵심 해석: 정체된 습탁을 제거하고 기운을 강하게 돌리는 배출/전환형 처방",
            "- 핵심 해석: 아래로 처진 기운을 강하게 위로 끌어올리는 발산/상승형 처방",
            "- 핵심 해석: 보충축과 배출·완충축이 함께 배치된 삼보삼사 균형형 처방",
            "- 핵심 해석: 비위를 보하여 혈을 낳게 하고 심신을 안정시키는 보기보혈 안신 처방",
            "- 핵심 해석: 사군자탕과 사물탕에 황기, 육계를 더해 기혈을 강력하게 온보하는 처방",
            "- 핵심 해석: 습을 말리고 기운을 소통시켜 담음을 제거하는 조습화담 처방"
        ],
        "clinic_direction": [
            "- 보사: 영혈 보충과 허열 제어가 중심\n- 승강: 수렴 및 하행 안정 방향 우세",
            "- 보사: 사(瀉)법 위주 (제습, 행기)\n- 승강: 탁한 것을 내리고 기운을 소통시킴",
            "- 보사: 기혈 보충 중심\n- 승강: 강력한 상승(승양) 방향 우세",
            "- 보사: 보충이 중심이나, 수습 조절과 허열 완충이 함께 배치됨\n- 승강: 저장·수렴·하행 안정 방향 우세",
            "- 보사: 보기·보혈 동시 진행\n- 승강: 중심을 채우고 심(心)으로 안정화",
            "- 보사: 강력한 보(補)법 위주\n- 승강: 기혈을 전신으로 순환시키고 데움",
            "- 보사: 사(瀉)법 위주 (화담)\n- 승강: 위기(胃氣)를 하강시켜 오심을 진정"
        ],
        "clinic_caution": [
            "- 졸음, 무기력, 진정제 병용 시 확인",
            "- 임산부 및 심한 기허 환자 신중 투여",
            "- 고혈압, 상열감, 혈당 변동성 주의",
            "- 소화불량·설사 경향 환자는 숙지황 위장 부담 확인\n- 항응고제 병용 시 목단피 주의",
            "- 점액질 약재로 인한 소화 부담 확인",
            "- 실열(實熱) 환자, 염증기 환자 절대 주의 (육계 등 온열지제 부담)",
            "- 진액이 고갈된 음허(陰虛) 환자, 마른기침 환자 주의 (조습 작용)"
        ],
        "clinic_followup": [
            "- 수면의 질, 주간 피로도, 두근거림",
            "- 복부 팽만감, 대변 상태, 소화력",
            "- 만성 피로 회복 여부, 혈압, 혈당",
            "- 부종 변화, 도한, 수면 변화, 소화 상태",
            "- 식욕, 수면 시간, 정서적 불안도",
            "- 체력 회복, 상열감 발생 여부, 소화 상태",
            "- 오심/구토 호전 여부, 입마름 발생 여부"
        ]
    })

    polyhedrons = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "octahedron": ["보존/수렴 강함, 완충 중간, 배출/발산 낮음", "배출/전환 강함, 완충 중간, 보존 낮음", "발산/상승 및 전환축 강함, 수렴/배출 낮음", "보존/보충/수렴 강함, 완충 중간, 급진전환 낮음"],
        "ve_axis": ["U-base (Phe, Tyr, Trp) 축 중심 분포", "C-base (Leu, Pro, His) 축 중심 분포", "A-base (Met, Ile, Asn) 축 중심 분포", "G-base (Val, Ala, Asp, Gly) 축 중심 분포"],
        "rd_plane": [
            "[안정화 구조] 진정 방향의 단일면 기하학적 안정화 시각화",
            "[안정화 구조] 기행 방향의 동적 완충면 형성 시각화",
            "[안정화 구조] 기력 회복 및 에너지 대사 관련 해석축을 지지하는 넓은 상승 평형면 시각화",
            "**[RD 균형도 = 3:3 대칭 균형]**\n\n▶ **보존/보충 3축 (三補):** 숙지황·산약·산수유\n▶ **배출/완충 3축 (三瀉):** 복령·택사·목단피\n\n*보존·보충 중심축과 수습·허열 완충축이 마주 보며 완벽한 대칭적 쌍대(Dual) 구조를 형성함.*"
        ]
    })
    
    neijing = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "zang_fu": ["심(心) · 간(肝)", "비(脾) · 위(胃)", "비(脾) · 폐(肺)", "간(肝) · 신(腎)"],
        "qi_blood": ["음혈 소모 · 허번", "습탁 정체 · 기기 불통", "기허 · 중기하함", "음혈 · 정(精) · 구조물질 소모"],
        "wuxing": ["木/水 평형 보조", "土 중심, 金 행기 보조", "土 중심, 木/火 상승 보조", "水 중심, 木 보조"],
        "interpretation": [
            "심간(心肝)의 혈을 기르고 안신(安神)하는 전통 해석을 병렬 매핑",
            "비위(脾胃)의 조습(燥濕) 및 운화(運化) 기능을 정보기하학 언어로 병렬 매핑",
            "중기(中氣)를 승양(升陽)하는 전통 방향성을 상승 벡터로 병렬 매핑",
            "간신(肝腎) 자음보신(滋陰補腎)의 삼보삼사 구조를 RD 대칭 모델로 병렬 매핑"
        ]
    })
    
    # 핵심 약재 일부만 등록 (시연용)
    herbs = pd.DataFrame({
        "formula_id": ["F001", "F002", "F003", "F003", "F004", "F004", "F005", "F006", "F007"],
        "herb_name": ["산조인", "창출", "황기", "인삼", "숙지황", "산약", "용안육", "육계", "반하"],
        "role": ["군약", "군약", "군약", "신약", "군약", "신약", "군약", "신약", "군약"],
        "dose_range": ["15g", "10g", "15g", "9g", "20g", "10g", "9g", "3g", "9g"],
        "trad_role_desc": ["수렴 안신", "조습 건비", "승양", "건비", "보신", "보비", "안신", "온양", "화담"],
        "four_qi": ["평", "온", "미온", "미온", "미온", "평", "온", "대열", "온"],
        "five_flavor": ["감", "신", "감", "감", "감", "감", "감", "신", "신"],
        "meridian_entry": ["심, 간", "비, 위", "비, 폐", "비, 폐", "간, 신", "비, 신", "심, 비", "신, 비", "비, 위"]
    })
    
    vectors = pd.DataFrame({
        "herb_name": ["산조인", "창출", "황기", "숙지황", "산약"],
        "codon": ["UUU (U-U-U)", "CUU (C-U-U)", "AUG (A-U-G)", "GUU (G-U-U)", "GAU (G-A-U)"],
        "amino_acid": ["Phe", "Leu", "Met", "Val", "Asp"],
        "q6_coord": [0, 11, 42, 40, 36],
        "q6_axis": ["보존형 변화", "급진 전환", "비정상 연장", "구조 안정", "보존형 완충"]
    })

    safety = pd.DataFrame({
        "herb_name": ["산조인", "창출", "황기", "숙지황", "용안육", "육계", "반하"],
        "drug_interaction_flag": ["수면제", "해당없음", "면역억제제", "해당없음", "해당없음", "해당없음", "해당없음"],
        "pregnancy_flag": ["특이 주의 제한", "특이 주의 제한", "특이 주의 제한", "특이 주의 제한", "특이 주의 제한", "신중투여", "신중투여"],
        "liver_kidney_flag": ["간부담", "특이사항 없음", "특이사항 없음", "소화기계 부담", "특이사항 없음", "특이사항 없음", "특이사항 없음"],
        "evidence_level": ["임상확인", "일반안전", "이론주의", "전통주의", "일반안전", "주의권고", "주의권고"],
        "evidence_note": ["간효소 수치 상승", "음허내열 주의", "면역계 자극", "소화불량", "일반적 안전", "상열감", "조습 진액소모"]
    })
    
    return formulas, polyhedrons, neijing, donguibogam, clinical, herbs, safety, vectors

df_formulas, df_polyhedrons, df_neijing, df_donguibogam, df_clinical, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 환자 임상 정보 입력")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 피로, 소화불량, 불면")

st.sidebar.subheader("진맥·설진 및 복진 입력")
mac_force = st.sidebar.selectbox("맥력 (Pulse Strength)", ["선택 안함", "허(虛)", "실(實)"])
tongue_coat = st.sidebar.selectbox("설태 (Tongue Coating)", ["선택 안함", "박(薄)", "후(厚)", "백(白)", "황(黃)", "니(膩)", "무태(無苔)"])

st.sidebar.subheader("안전성 체크리스트: [복용약]")
med_anti_coag = st.sidebar.checkbox("항응고제/항혈소판제/NSAIDs")
med_bp = st.sidebar.checkbox("혈압약")
med_diab = st.sidebar.checkbox("당뇨약/인슐린")
med_sedative = st.sidebar.checkbox("수면제/항우울제/진정제")

st.sidebar.subheader("안전성 체크리스트: [환자 상태]")
cond_liver = st.sidebar.checkbox("간 기능 저하 또는 간질환 병력")
cond_kidney = st.sidebar.checkbox("신장 기능 저하 또는 신장질환 병력")
cond_bp_var = st.sidebar.checkbox("고혈압 또는 저혈압 변동")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사/위장장애")
cond_surgery = st.sidebar.checkbox("수술/시술/치과치료 예정")

st.sidebar.subheader("임상 검사값 및 특이사항 입력")
lab_ast_alt = st.sidebar.text_input("AST/ALT:", value="45 / 52 (U/L)")
lab_bp = st.sidebar.text_input("혈압 (mmHg):", value="145 / 90")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 한의학 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("처방 분석 및 리포트 생성", type="primary")

# ==========================================
# 메인 화면: 12단계 모듈 분석
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    db_info = df_donguibogam[df_donguibogam["formula_name"] == selected_formula_name].iloc[0]
    clinical_info = df_clinical[df_clinical["formula_name"] == selected_formula_name].iloc[0]
    
    # 예외 처리: 데이터가 없는 신규 처방은 빈 시리즈 반환
    poly_info = df_polyhedrons[df_polyhedrons["formula_name"] == selected_formula_name]
    poly_info = poly_info.iloc[0] if not poly_info.empty else pd.Series()
    
    nj_info = df_neijing[df_neijing["formula_name"] == selected_formula_name]
    nj_info = nj_info.iloc[0] if not nj_info.empty else pd.Series()

    selected_id = formula_info["formula_id"]
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    merged_herbs_vectors = pd.merge(formula_herbs, df_vectors, on="herb_name", how="left").fillna("미고정")

    tabs = st.tabs([
        "1. 한의사용 통합 요약 및 감별", 
        "2. 전통 처방 Core 패널", 
        "3. 동의보감 병렬 해석",
        "4. 진맥·설진 대조", 
        "5. 침구 치료 방향", 
        "6. 뜸 치료 방향", 
        "7. 처방 주변 변화 가능성", 
        "8. 보사·승강출입 균형", 
        "9. Q6 64큐브 Core 주석", 
        "10. 황제내경 병렬 해석", 
        "11. 안전성 확인", 
        "12. 환자 설명문"
    ])
    
    # ------------------------------------------
    with tabs[0]:
        st.subheader(f"🧑‍⚕️ 1. [{selected_formula_name}] 한의사용 통합 요약")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']}\n\n**해석:** {formula_info['trad_interpret']}")
        with col2:
            st.warning(f"**복용 후 추적 관찰:**\n\n{clinical_info['clinic_followup']}")

        # 처방 정합도 점검
        matches, cautions = [], []
        if patient_symp: matches.append(f"입력 증상('{patient_symp}') 기준, {formula_info['pattern_tags']} 방향과 정합성 검토")
        else: matches.append("증상 미입력 (전반적 방향성 검토 요망)")
        
        if mac_force == "허(虛)": matches.append("맥 허(虛) → 보(補) 방향 처방과 정합")
        elif mac_force == "실(實)": cautions.append("맥 실(實) → 보약 계열(보중익기, 육미 등) 처방 시 부담 재검토")
        
        if cond_dig: cautions.append("만성 소화불량 → 숙지황, 용안육 등 점액질/숙지황 위장 부담 확인")
        if med_anti_coag: cautions.append("항응고제 복용 → 출혈 경향 약재 병용 주의")
        if cond_surgery: cautions.append("수술 예정 → 복용 중단 여부 및 출혈 경향 전문가 판단 필요")

        st.markdown("#### 🚨 처방 정합도 점검표")
        st.success("**✅ 정합 (맞는 부분)**\n" + "\n".join([f"- {m}" for m in matches]))
        if cautions:
            st.error("**⚠️ 주의 및 재검토 (어긋날 수 있는 부분)**\n" + "\n".join([f"- {c}" for c in cautions]))

        st.divider()
        st.markdown("### 📊 처방 감별 비교 패널 (Differential Diagnosis)")
        st.caption("선택한 처방과 임상에서 자주 감별되는 유사 처방들의 방향성을 비교합니다.")
        
        diff_df = pd.DataFrame([
            {"처방": "육미지황환", "중심 변증": "간신음허·허열", "강한 방향": "자음·보신·수렴", "주의 환자": "소화불량, 설사, 항응고제"},
            {"처방": "보중익기탕", "중심 변증": "비위기허·중기하함", "강한 방향": "보기·승양", "주의 환자": "고혈압, 불면, 심계"},
            {"처방": "귀비탕", "중심 변증": "심비양허·불면·건망", "강한 방향": "보기·보혈·안신", "주의 환자": "소화 부담, 주간 졸림"},
            {"처방": "십전대보탕", "중심 변증": "기혈양허·허로", "강한 방향": "대보원기·온양", "주의 환자": "열감, 고혈압, 실열증"},
            {"처방": "평위산", "중심 변증": "습체·비위불화", "강한 방향": "조습·화위", "주의 환자": "건조·음허 환자 주의"},
            {"처방": "이진탕", "중심 변증": "담음 정체·오심", "강한 방향": "조습·화담", "주의 환자": "진액 고갈 환자 주의"},
        ])
        
        # Highlight selected formula
        def highlight_selected(row):
            if row['처방'] == selected_formula_name:
                return ['background-color: #d1e7dd'] * len(row)
            return [''] * len(row)
            
        st.dataframe(diff_df.style.apply(highlight_selected, axis=1), use_container_width=True, hide_index=True)

    # ------------------------------------------
    with tabs[1]:
        st.subheader("📌 2. 전통 처방 Core 패널")
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})")
        if not formula_herbs.empty:
            st.dataframe(formula_herbs[["role", "herb_name", "trad_role_desc", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        else:
            st.warning("해당 처방의 약재 상세 데이터는 업데이트 중입니다.")

    with tabs[2]:
        st.subheader("📖 3. 동의보감 병렬 해석 패널")
        st.markdown(f"#### 1. {selected_formula_name} 문헌적 병증 해석")
        st.markdown(f"- 📜 **동의보감 편제:** `{db_info['db_chapter']}`")
        st.markdown(f"- 🤒 **핵심 적응증 및 병리:** `{db_info['db_pattern']}`")
        st.markdown("#### 2. 양생(養生) 및 병리 조절 방향성")
        st.info(db_info['db_interpret'])

    # ------------------------------------------
    with tabs[3]:
        st.subheader("📊 4. 진맥·설진 대조 패널")
        st.info("진맥·설진 정보는 대시보드가 자동 판정하는 값이 아니라, 한의사가 직접 확인한 소견을 입력하여 선택 처방의 변증 방향과 정합성을 대조하기 위한 참고 정보입니다.")
        
        st.markdown("#### 정합 소견 예시")
        st.success(clinical_info['clinic_direction']) # Using this as a proxy for pattern fit

    with tabs[4]:
        st.subheader("📍 5. 침구 치료 방향 패널")
        st.info("본 패널은 침 치료를 자동으로 처방하는 기능이 아니라, 선택 처방의 변증 방향에 따라 한의사가 검토할 수 있는 치료 원칙과 주의점을 정리하는 보조 설명층입니다.")
        st.markdown("#### 침 치료 방향 및 검토 가능한 혈위군")
        st.markdown(clinical_info['clinic_structure']) # Proxy for acu strategy

    with tabs[5]:
        st.subheader("🔥 6. 뜸 치료 방향 패널")
        st.warning("**[주의]** 뜸 치료는 화상, 알레르기, 피부 감염 등의 이상 반응 위험이 있으므로 뜸 가능성 검토와 주의조건(당뇨성 말초신경병증 등) 확인이 필수입니다.")
        
        if "열" in formula_info['indication_traditional'] or "음허" in formula_info['indication_traditional']:
            st.error("🔴 **뜸 주의:** 실열, 허열(오심번열, 도한) 양상이 뚜렷할 경우 강한 온열 자극 주의 요망.")
        else:
            st.success("🟢 **뜸 검토 가능:** 허한성, 냉감 동반, 양허성 피로 시 완만한 온보 방향 검토.")

    # ------------------------------------------
    with tabs[6]:
        st.subheader("🌐 7. 처방 주변 변화 가능성 패널")
        st.caption("연구자용 구조명: H(3,4) 생물정보 확장층")
        st.markdown("처방의 중심 방향에서 벗어날 수 있는 주변 변화 가능성을 변증·안전성 언어로 번역한 보조 설명층입니다.")
        st.markdown(clinical_info['clinic_caution'])

    with tabs[7]:
        st.subheader("💎 8. 보사·승강출입 균형 패널")
        st.caption("연구자용 구조명: 다면체 방향성 시각화")
        
        if not poly_info.empty:
            st.success("핵심 해석: " + poly_info['octahedron'])
            st.markdown(poly_info['rd_plane'])
        else:
            st.warning("이 처방의 다면체 구조(Octahedron, VE, RD, TO) 매핑은 데이터 수집 및 연구 진행 중입니다. (Level 1/2 임상 정보 우선 제공)")

    # ------------------------------------------
    with tabs[8]:
        st.subheader("🧬 9. Q6 64큐브 Core 주석 패널")
        if "Level 3" in formula_info['q6_core_vector']:
            st.warning("이 처방의 64큐브 코돈-아미노산 벡터 매핑은 현재 수학적 검증 및 연구 진행 중입니다. (Level 3 데이터)")
        else:
            st.success(f"**💡 Q6 64큐브 핵심 변화 방향:** `{formula_info['q6_core_vector']}`")
            for idx, row in merged_herbs_vectors.iterrows():
                st.markdown(f"**[{row['herb_name']}]** | Q6 주석: `{row['codon']} ➔ {row['amino_acid']}` | 해석축: {row['q6_axis']}")

    with tabs[9]:
        st.subheader("📚 10. 황제내경 병렬 해석 패널")
        if not nj_info.empty:
            st.markdown(f"- **장부축 매핑:** `{nj_info['zang_fu']}`\n- **오행 작용 벡터:** `{nj_info['wuxing']}`")
            st.info(nj_info['interpretation'])
        else:
            st.warning("황제내경 생명론 기반의 정보기하학적 병렬 매핑이 진행 중입니다.")

    # ------------------------------------------
    with tabs[10]:
        st.subheader("🚨 11. 안전성 확인 패널")
        if not formula_safety.empty:
            display_safety = formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_note"]].copy()
            display_safety.columns = ["약재명", "약물 병용 주의", "임신·수유 관련", "간·신장 관련", "주의 근거/확인 사항"]
            st.dataframe(display_safety, use_container_width=True, hide_index=True)
        else:
            st.warning("이 처방을 구성하는 개별 약재의 세부 안전성 DB가 업데이트 중입니다. 전반적인 처방 주의사항(Tab 1)을 참고하십시오.")

    with tabs[11]:
        st.subheader("💬 12. 환자 설명문 패널")
        patient_html_generic = f"""
        <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
            <b>{selected_formula_name}</b>은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 균형 방향을 조절하는 복합 처방입니다.<br><br>
            이 처방은 몸의 부족한 기운을 보충하고, 소화력과 피로 상태를 함께 살피는 방향의 처방입니다. 복용 전후에는 소화 상태, 피로감, 혈압, 혈당, 두근거림, 수면 변화를 확인해야 합니다.<br><br>
            복용 중 특이 반응이 나타나면 담당 한의사의 진료 과정에서 세밀하게 조절해야 합니다.
        </div>
        """
        st.markdown(patient_html_generic, unsafe_allow_html=True)
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 리포트 생성' 버튼을 눌러주세요.")
