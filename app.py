import streamlit as st
import pandas as pd

# ==========================================
# 0. 64큐브 매핑 무결성 검산 (Assertion)
# ==========================================
# 본 대시보드의 수학적 정합성을 서버 기동 시 자동 검증합니다.
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

# 핵심 공리 고정 검산
assert n_to_codon(0) == "GGG"
assert codon_to_aa(n_to_codon(0)) == "Gly"
assert n_to_codon(9) == "AUG"
assert codon_to_aa(n_to_codon(9)) == "Met"
assert n_to_codon(18) == "UGA"
assert codon_to_aa(n_to_codon(18)) == "Stop"
assert n_to_codon(63) == "CCC"
assert codon_to_aa(n_to_codon(63)) == "Pro"

# ==========================================
# 1. 페이지 설정 및 필수 방어 가이드라인
# ==========================================
st.set_page_config(page_title="64큐브-다면체 처방 대시보드", layout="wide")

st.warning(
    "**[주의] 본 대시보드에서 한의학 처방 분석은 전통 처방의 생리적 효과를 자동으로 증명하거나 예측하는 시스템이 아닙니다.**\n\n"
    "- 이 시스템의 약재-코돈 매핑은 약재가 실제 유전암호를 조절한다는 뜻이 아닙니다.\n"
    "- 전통 처방 Core가 중심이며, Q6 64큐브는 해석(Core)층, H(3,4)는 생물정보 확장(Extension)층입니다.\n"
    "- 실제 처방은 면허가 있는 한의사의 변증, 환자 병력, 검사 결과, 안전성 평가를 바탕으로 결정되어야 합니다."
)

st.title("☯️ 64큐브-다면체 기반 코돈·아미노산 벡터 처방 해석 대시보드")
st.markdown(
    "**Formula_Vector = Traditional_Core + Q6_Core_Annotation + Polyhedron_Visualization + H(3,4)_Biochemical_Extension + Safety_Filter**\n\n"
    "전통 처방 구조를 최상위 Core Layer로 두고, 이를 64큐브 상태공간과 H(3,4) 생물정보망, 다면체 동적평형 구조로 주석화(Annotation)하는 융합 해석 모델입니다."
)

# ==========================================
# 2. 데이터베이스 세팅 (좌표 미고정 로직 반영)
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_id": ["F001", "F002", "F003", "F004"],
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "indication_traditional": ["심비양허, 허번불면", "비위습탁, 복부팽만", "비위기허, 중기하함", "간신음허, 허열도한"],
        "pattern_tags": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복", "승양, 익기, 에너지부스팅", "자음, 보신, 구조물질보충"],
        "q6_core_vector": ["보존형 변화 및 수렴형 완충 주도", "급진 전환형 변화 주도", "발산/상승 및 전환형 변화 주도", "보존형 변화 및 수렴형 완충 방향 주도"],
        "trad_interpret": [
            "혈(血)을 기르고 심(心)을 안정시키며 허열을 수렴하는 방향",
            "비위의 습탁을 건조하게 하고 기체의 흐름을 회복하는 방향",
            "아래로 처진 기를 끌어올리고 비위의 운화 및 전신 기력을 회복하는 방향",
            "소모된 바탕을 보충하고 허열과 수분 정체를 함께 조절하는 삼보삼사(三補三瀉) 방향"
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
            "심간(心肝)의 혈을 기르고 안신(安神)하는 전통 해석을 64큐브 상태공간과 병렬 매핑",
            "비위(脾胃)의 조습(燥濕) 및 운화(運化) 기능을 정보기하학적 동적평형 언어로 병렬 매핑",
            "비폐(脾肺)의 기허를 보강하고 중기(中氣)를 승양(升陽)하는 전통 방향성을 상승 벡터로 병렬 매핑",
            "간신(肝腎)의 자음보신(滋陰補腎)이라는 삼보삼사 구조를 RD 다면체의 3:3 대칭 안정화 모델로 병렬 매핑"
        ]
    })
    
    herbs = pd.DataFrame({
        "formula_id": ["F001", "F001", "F001", "F001", "F002", "F002", "F002", "F002", "F003", "F003", "F003", "F003", "F003", "F003", "F003", "F003", "F004", "F004", "F004", "F004", "F004", "F004"],
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "감초", "황기", "인삼", "백출", "감초", "당귀", "진피", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "role": ["군약", "신약", "좌약", "사약", "군약", "신약", "좌약", "사약", "군약", "신약", "신약", "사약", "좌약", "좌약", "사약", "사약", "군약", "신약", "신약", "좌약", "사약", "사약"],
        "dose_range": ["15-20g", "9-12g", "6-9g", "3-6g", "10-15g", "9-12g", "9-12g", "3-6g", "15-20g", "9-12g", "9-12g", "3-6g", "6-9g", "3-6g", "3-6g", "3-6g", "20-25g", "10-15g", "10-15g", "9-12g", "9-12g", "9-12g"],
        "trad_role_desc": ["수렴 안신", "자음 강화", "행기 활혈", "조화 제약", "조습 건비", "행기 화위", "이기 조중", "조화 제약", "보외기 승양", "보내기 생진", "건비 조습", "조화 제약", "보혈 화혈", "이기 건비", "승양 투진", "소간 해울", "자음 보신 정혈", "보익 간신 수렴", "보비 위 익폐 신", "이수 삼습 건비", "청열 량혈 활혈", "이수 삼습 사열"],
        "four_qi": ["평", "한", "온", "평", "온", "온", "온", "평", "미온", "미온", "온", "평", "온", "온", "미한", "미한", "미온", "미온", "평", "평", "미한", "한"],
        "five_flavor": ["감, 산", "고, 감", "신", "감", "신, 고", "고, 신", "신, 고", "감", "감", "감, 미고", "감, 고", "감", "감, 신", "신, 고", "신, 감", "고, 신", "감", "산, 삽", "감", "감, 담", "고, 신", "감, 담"],
        "meridian_entry": ["심, 간, 담", "폐, 위, 신", "간, 담, 심포", "심, 폐, 비, 위", "비, 위", "비, 위, 대장", "비, 폐", "심, 폐, 비, 위", "비, 폐", "비, 폐, 심", "비, 위", "심, 폐, 비, 위", "심, 간, 비", "비, 폐", "폐, 비, 위", "간, 담", "간, 신", "간, 신", "비, 폐, 신", "심, 비, 신", "심, 간, 신", "신, 방광"]
    })
    
    # 일부 약재(천궁, 승마 등)는 공격 방지를 위해 의도적으로 "좌표 미고정" 처리
    vectors = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "codon": ["UUU (U-U-U)", "UCU (U-C-U)", "미고정", "UGG (U-G-G)", "CUU (C-U-U)", "CCU (C-C-U)", "CAU (C-A-U)", "AUG (A-U-G)", "CGU (C-G-U)", "AUU (A-U-U)", "ACU (A-C-U)", "미고정", "AGU (A-G-U)", "GUU (G-U-U)", "GCU (G-C-U)", "GAU (G-A-U)", "GGU (G-G-U)", "UGU (U-G-U)", "CAA (C-A-A)"],
        "amino_acid": ["Phe (페닐알라닌)", "Ser (세린)", "미고정", "Trp (트립토판)", "Leu (류신)", "Pro (프롤린)", "His (히스티딘)", "Met (메티오닌)", "Arg (아르기닌)", "Ile (이소류신)", "Thr (트레오닌)", "미고정", "Ser (세린)", "Val (발린)", "Ala (알라닌)", "Asp (아스파르트산)", "Gly (글리신)", "Cys (시스테인)", "Gln (글루타민)"],
        "q6_coord": [0, 16, "미고정", 42, 11, 15, 7, 42, 35, 41, 45, "미고정", 33, 40, 44, 36, 32, 34, 23],
        "q6_axis": ["보존형 변화 (소수성)", "수렴형 완충 (친수성)", "추후 고정 필요", "수렴형 조화", "급진 전환형 변화", "완충형 전환", "보존형 변화", "비정상 연장형 변화", "급진 전환형 변화", "보존형 강화", "보존형 변화", "추후 고정 필요", "완충형 변화", "구조 안정성 / 보존형 변화", "수렴형 완충", "보존형 완충", "전환형 배출", "완충형 변화", "급진 전환형 배출"]
    })

    safety = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "drug_interaction_flag": ["수면제, 진정제", "해당없음", "항응고제, 항혈소판제", "이뇨제, 혈압약", "해당없음", "해당없음", "해당없음", "면역관련 약물", "혈당관련 약물, 혈압약", "해당없음", "항응고제", "해당없음", "해당없음", "해당없음", "해당없음", "혈당관련 약물(시너지)", "이뇨제(시너지)", "항응고제", "이뇨제(시너지)"],
        "pregnancy_flag": ["안전", "안전", "주의권고", "안전", "안전", "신중투여", "안전", "안전", "안전", "안전", "주의권고", "안전", "안전", "안전", "안전", "안전", "안전", "금기추정", "안전"],
        "liver_kidney_flag": ["대량사용시 간부담", "특이사항 없음", "특이사항 없음", "장기복용시 신장/혈압 주의", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 간효소 주의", "소화기계 부담(위장장애)", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 신장 주의"],
        "evidence_level": ["임상확인필요", "일반안전", "문헌보고", "문헌보고", "일반안전", "주의권고", "일반안전", "이론적주의", "문헌보고", "일반안전", "전통주의", "일반안전", "임상확인필요", "전통주의", "일반안전", "이론적주의", "일반안전", "문헌보고", "임상확인필요"],
        "evidence_note": ["과다 복용 시 간효소 수치 상승", "일반적 용량 내 안전", "혈소판 응집 억제 작용", "위알도스테론증 유발 가능", "음허내열 환자 주의", "동물실험 자궁수축", "일반적 용량 내 안전", "면역계 자극 가능성 검토", "과량 복용 시 두근거림/혈압상승", "일반적 용량 내 안전", "자궁 수축 및 출혈 경향", "상열감 환자 주의", "특이 체질 간부담", "점액질로 인한 소화불량/설사", "일반적 용량 내 안전", "혈당 변동 가능성 관련 확인", "수분 대사 보조", "혈류 순환 관련 확인", "신장 배설 부담 가능성"]
    })
    
    return formulas, polyhedrons, neijing, herbs, safety, vectors

df_formulas, df_polyhedrons, df_neijing, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 환자 입력 및 조건")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 소화불량, 황반변성, 디스크")

st.sidebar.subheader("안전성 체크리스트 (필수)")
med_sedative = st.sidebar.checkbox("수면제/항우울제 복용")
med_blood = st.sidebar.checkbox("항응고제/혈압약 복용")
med_diab = st.sidebar.checkbox("당뇨약 복용")
cond_liver = st.sidebar.checkbox("간/신장 기능 저하")
cond_preg = st.sidebar.checkbox("임신/수유부")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 한의학 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("처방 분석 및 리포트 생성", type="primary")

# ==========================================
# 메인 화면: 7단계 모듈 분석
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    poly_info = df_polyhedrons[df_polyhedrons["formula_name"] == selected_formula_name].iloc[0]
    nj_info = df_neijing[df_neijing["formula_name"] == selected_formula_name].iloc[0]
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    merged_herbs_vectors = pd.merge(formula_herbs, df_vectors, on="herb_name", how="left")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "전통 처방 Core 패널", 
        "Q6 64큐브 Core 주석 패널", 
        "H(3,4) 생물정보 확장 패널", 
        "다면체 방향성 시각화 패널", 
        "황제내경 병렬 해석 패널", 
        "안전성 확인 패널", 
        "환자 설명문 패널"
    ])
    
    # ------------------------------------------
    with tab1:
        st.subheader("📌 1. 전통 처방 Core 패널")
        if patient_symp:
            st.error(
                f"**⚠️ [임상 정합도 확인 알림]**\n\n"
                f"입력된 주증상/현대 진단명(**'{patient_symp}'**)과 선택 처방의 전통 변증 방향(**'{formula_info['indication_traditional']}'**)이 직접 일치하지 않을 수 있습니다. "
                f"본 처방은 특정 병명 자체보다 환자의 전신 변증, 허실, 한열, 소화력, 동반 증상을 종합한 한의사의 임상적 판단을 기준으로 최종 검토해야 합니다."
            )
            
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})\n\n**전통 처방 해석:** {formula_info['trad_interpret']}")
        st.markdown("#### 군신좌사(君臣佐使) 네트워크")
        st.dataframe(formula_herbs[["role", "herb_name", "trad_role_desc", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        
    # ------------------------------------------
    with tab2:
        st.subheader("🧬 2. Q6 64큐브 Core 주석 패널")
        st.info("Q6 layer는 64괘·64코돈·384효사·384 directed bit-flip mutation을 병렬 배치하는 정보기하학적 해석층으로, 처방의 전통적 방향성을 6비트 상태공간의 언어로 주석화(Annotation)합니다.")
        st.success(f"**💡 Q6 64큐브 핵심 변화 방향:** `{formula_info['q6_core_vector']}`")
        
        for idx, row in merged_herbs_vectors.iterrows():
            st.markdown(f"### **[약재: {row['herb_name']}]**")
            st.markdown(f"- 🏛️ **전통 역할:** {row['role']} / {row['trad_role_desc']}")
            
            # 미고정 약재에 대한 안전 처리
            if str(row['q6_coord']) == "미고정":
                st.markdown(f"- 🧬 **Q6 Core 주석:** `좌표 미고정 / 추후 고정 필요` | **해석축:** {row['q6_axis']}")
            else:
                st.markdown(f"- 🧬 **Q6 Core 주석:** `{row['codon']} ➔ {row['amino_acid']}` | **64큐브 좌표:** n={row['q6_coord']} | **해석축:** {row['q6_axis']}")
                
            st.markdown(f"- ⚠️ **[해석 주의]:** 이 매핑은 {row['herb_name']}이(가) 실제 유전암호를 직접 조절한다는 뜻이 아니라, 전통적 작용 방향을 코돈-아미노산 물성 벡터 언어로 주석화한 것입니다.")
            st.divider()

    # ------------------------------------------
    with tab3:
        st.subheader("🌐 3. H(3,4) 생물정보 확장 패널")
        st.warning("**H(3,4) Extension Layer는 Q6 뼈대에 포함되지 않는 전체 코돈 단일염기 치환(대각 엣지 포함)을 포괄하는 생물정보학적 확장층입니다.**")
        
        st.markdown(
            "본 패널은 Q6의 192개 무방향 엣지를 넘어, 각 코돈당 9방향의 변화를 모두 반영한 288개 무방향 엣지의 해밍 그래프 $H(3,4)$ 구조를 다룹니다.\n\n"
            "이 생물학 Extension 층은 **약재가 실제 유전암호를 조절한다는 뜻이 아니라, 선택된 코돈-아미노산 좌표 주변의 전체 단일염기 치환망과 물리화학적 물성 변화 가능성을 별도로 분석하고 검증하는 보조 정보층**입니다."
        )
        
        st.info(f"**[{selected_formula_name}] H(3,4) 확장 검토 지침**\n\n해당 처방을 구성하는 각 약재의 Q6 코돈 좌표를 중심으로, $H(3,4)$ 전체 치환망에서의 아미노산 물성 거리에 따른 가중치(Transition/Transversion 비율 등)를 결합하여 추가적인 기하학적 평형성을 탐색합니다.")

    # ------------------------------------------
    with tab4:
        st.subheader("💎 4. 다면체 방향성 시각화 패널")
        st.info("다면체는 처방 효과를 증명하는 도구가 아니라, 처방의 복합 방향성을 구조적으로 시각화하는 정보기하학적 보조 모델입니다.")
        
        st.markdown("#### 1. 정팔면체 (Octahedron) : 6대 방향 벡터 시각화")
        st.success(poly_info['octahedron'])
        
        st.markdown("#### 2. 벡터 평형체 (VE) : 12 Position-Base 시각화")
        st.success(poly_info['ve_axis'])

        st.markdown("#### 3. 마름모십이면체 (RD) : 안정화 구조 시각화")
        st.success(poly_info['rd_plane'])
        
        st.markdown("#### 4. 깎은 정팔면체 (TO) : 전신 네트워크 확산 시각화")
        st.info("단일 처방 모듈이 인체라는 거대 공간을 채워나갈 때(공간충전), 어긋남 없이 안정적으로 확장되는 장기적 전신적 평형(Homeostasis) 유지력을 대변합니다.")

    # ------------------------------------------
    with tab5:
        st.subheader("📚 5. 황제내경 병렬 해석 패널")
        st.error("**[해석 주의] 본 패널은 황제내경 원문을 직접적인 생물학적 증명 자료로 사용하는 것이 아니라, 전통 생명론의 핵심 개념을 정보기하학 언어로 병렬 해석하는 교육·연구 보조 층입니다.**")
        
        st.markdown("#### 1. 황제내경 해석축 (Neijing Axis)")
        st.markdown(f"- 🏛️ **장부축 매핑:** `{nj_info['zang_fu']}`")
        st.markdown(f"- 🩸 **기혈진액 변증축:** `{nj_info['qi_blood']}`")
        st.markdown(f"- ☯️ **오행 작용 벡터:** `{nj_info['wuxing']}`")
        
        st.markdown("#### 2. 64큐브 - 황제내경 병렬 매핑 결론")
        st.info(nj_info['interpretation'])

    # ------------------------------------------
    with tab6:
        st.subheader("🚨 6. 안전성 확인 패널")
        st.info("**이 경고는 처방 금지가 아니라, 한의사의 임상적 추가 확인 필요성을 의미합니다.**")
        
        high_alerts, med_alerts, notice_alerts = [], [], []

        if med_sedative and any(formula_safety["drug_interaction_flag"].str.contains("수면제|진정제", na=False)): high_alerts.append("🔴 **[약물상호작용: 높음]** 수면제/진정제 병용 시 과도한 진정 작용 유발 가능성 검토")
        if med_blood and any(formula_safety["drug_interaction_flag"].str.contains("항응고제|혈압약", na=False)): high_alerts.append("🔴 **[약물상호작용: 높음]** 항응고제 및 혈압약 병용 시 출혈 및 혈압 변동 경향 검토")
        if med_diab and any(formula_safety["drug_interaction_flag"].str.contains("혈당", na=False)): high_alerts.append("🔴 **[약물상호작용: 높음]** 당뇨약 병용 시 혈당 변동성 검토 요망")
        if cond_liver and any(formula_safety["liver_kidney_flag"].str.contains("간|신장", na=False)): high_alerts.append("🔴 **[임상기저치: 높음]** 간/신장 기능 저하 환자 장기 사용 시 배설 부담 추이 검토 요망")
        if cond_dig and any(formula_safety["liver_kidney_flag"].str.contains("소화", na=False)): med_alerts.append("🟡 **[소화기계: 중간]** 만성 소화불량 환자 복용 시 위장 부담 검토")
        if cond_preg and any(formula_safety["pregnancy_flag"].str.contains("주의|신중|금기", na=False)): notice_alerts.append("🟢 **[특수조건: 주의]** 임산부 주의 약재 포함 여부 및 투여 타당성 확인 요망")
        
        notice_alerts.append("🟢 **[일반주의]** 복용 전후 전신 반응 주기적 확인 요망.")

        if high_alerts:
            for alert in high_alerts: st.error(alert)
        if med_alerts:
            for alert in med_alerts: st.warning(alert)
        if notice_alerts:
            for alert in notice_alerts: st.info(alert)
            
        st.markdown("---")
        st.dataframe(formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_note"]], use_container_width=True, hide_index=True)

    # ------------------------------------------
    with tab7:
        st.subheader("💬 7. 환자 설명문 패널")
        
        if selected_formula_name == "육미지황환":
            symptom_warnings = [w for w, cond in zip(["혈당 변동", "소화 및 설사", "피로감/부종"], [med_diab, cond_dig, cond_liver]) if cond]
            warning_text = f"다만, 현재 입력된 정보가 체크되어 있으므로, 진료 과정에서 <b>{', '.join(symptom_warnings)}</b> 여부를 세밀하게 확인해야 합니다." if symptom_warnings else "복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서 조절해야 합니다."

            patient_html = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                <b>육미지황환</b>은 숙지황·산수유·산약의 삼보(三補)와 복령·택사·목단피의 삼사(三瀉)로 구성된 처방입니다. 전통적으로 자음·보신·허열 완충 방향에서 해석됩니다.<br><br>
                본 대시보드에서는 이 삼보삼사 구조를 Q6 64큐브 Core 층에서 보존형 변화와 수렴형 완충 방향으로 주석화하고, 다면체 층에서는 RD 3:3 안정화 구조로 시각화합니다.<br><br>
                H(3,4) 생물학 Extension 층은 약재가 실제 유전암호를 조절한다는 뜻이 아니라, 선택된 코돈-아미노산 좌표 주변의 전체 단일염기 치환망과 물성 변화 가능성을 별도 분석하는 보조 정보층입니다.<br><br>
                {warning_text}
            </div>
            """
            st.markdown(patient_html, unsafe_allow_html=True)
            
        else:
            patient_html_generic = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                <b>{selected_formula_name}</b>은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 균형 방향을 조절하는 복합 처방입니다.<br><br>
                본 대시보드는 <b>{formula_info['indication_traditional']}</b>이라는 전통적 작용 방향을 Q6 64큐브 Core 층의 기하학적 언어로 주석화하고 시각화하여 처방의 이해를 돕습니다.<br><br>
                약재가 실제 유전암호를 조절한다는 뜻이 아니며, 복용 전후의 반응을 한의사의 진료 과정에서 세밀하게 확인하고 조절해야 합니다.
            </div>
            """
            st.markdown(patient_html_generic, unsafe_allow_html=True)
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 리포트 생성' 버튼을 눌러주세요.")
