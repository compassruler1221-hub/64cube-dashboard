import streamlit as st
import pandas as pd

# ==========================================
# 0. 페이지 설정 및 필수 가이드라인
# ==========================================
st.set_page_config(page_title="64큐브-황제내경 통합 대시보드", layout="wide")

st.warning(
    "**[주의] 본 대시보드는 한의사의 변증, 처방 설명, 안전성 확인, 연구 기록을 돕기 위한 교육·연구 보조 도구입니다.**\n\n"
    "자동 진단 또는 자동 처방 도구가 아니며, 실제 처방은 면허가 있는 의료인의 임상 판단에 따라 결정되어야 합니다."
)

st.title("☯️ 64큐브-다면체-황제내경 통합 처방 분석 대시보드")
st.markdown("64큐브 상태공간(원본 지도)과 다면체 압축 평형, 그리고 황제내경의 생명 균형론을 하나의 해석 체계 안에 병렬 배치한 교육·연구 보조 모델입니다.")

# ==========================================
# 1. 완벽하게 통합된 빅데이터 베이스
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_id": ["F001", "F002", "F003", "F004"],
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "indication_traditional": ["심비양허, 허번불면", "비위습탁, 복부팽만", "비위기허, 중기하함", "간신음허, 허열도한"],
        "pattern_tags": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복", "승양, 익기, 에너지부스팅", "자음, 보신, 구조물질보충"],
        "q6_core_vector": ["보존형 및 완충형 변화 주도", "급진 전환형 변화 주도", "비정상 연장형 및 상승형 전환 주도", "보존형 변화 및 수렴형 완충 주도"],
        "caution_summary": ["간 기능 저하 주의, 과도한 진정", "임산부 신중 투여, 기허 환자", "고혈압, 상열감, 급성염증 주의", "소화장애, 설사 환자 주의"]
    })
    
    polyhedrons = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "octahedron": [
            "보존: 85 | 수렴: 80 | 완충: 70 | 전환: 30 | 발산: 20 | 배출: 15\n\n*(보존/수렴 강함, 완충 중간, 배출/발산 낮음)*",
            "배출: 85 | 전환: 80 | 발산: 65 | 완충: 60 | 보존: 20 | 수렴: 15\n\n*(배출/전환 강함, 완충 중간, 보존 낮음)*",
            "발산(상승): 90 | 전환: 85 | 보충: 70 | 완충: 40 | 수렴: 20 | 배출: 10\n\n*(발산/상승 및 전환축 강함, 수렴/배출 낮음. 다면체 대칭 안정화보다는 정팔면체 상의 특정 벡터 편향성이 두드러지는 보기·승양형 구조)*",
            "보존: 90 | 보충: 85 | 수렴: 80 | 완충: 70 | 배출: 55 | 급진전환: 20\n\n*(보존/보충/수렴 강함, 완충 중간, 급진전환 낮음)*"
        ],
        "ve_axis": [
            "U-base (Phe, Tyr, Trp) 축 중심 분포",
            "C-base (Leu, Pro, His) 축 중심 분포",
            "A-base (Met, Ile, Asn) 축 중심 분포",
            "G-base (Val, Ala, Asp, Gly) 중심\n\n*12 position-base 축 전반의 입체적 물질 보충 및 구조 안정화*"
        ],
        "rd_plane": [
            "[안정화 구조] 진정 방향의 단일면 기하학적 안정화 해석",
            "[안정화 구조] 기행 방향의 동적 완충면 형성 해석",
            "[안정화 구조] 기력 회복 및 에너지 대사 관련 해석축을 지지하는 넓은 상승 평형면",
            "**[RD 균형도 = 3:3 대칭 균형]**\n\n▶ **보존/보충 3축 (三補):** 숙지황·산약·산수유\n▶ **배출/완충 3축 (三瀉):** 복령·택사·목단피\n\n*보존·보충 중심축과 수습·허열 완충축이 마주 보며 완벽한 대칭적 쌍대(Dual) 구조를 형성함.*"
        ]
    })
    
    # [신규 추가] 황제내경 해석 레이어 데이터베이스 생성
    neijing = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "zang_fu": ["심(心) · 간(肝) · 담(膽)", "비(脾) · 위(胃) · 대장(大腸)", "비(脾) · 폐(肺) · 심(心)", "간(肝) · 신(腎)"],
        "qi_blood": ["심비양허 · 허번 · 영혈소모", "비위습탁 · 기체 · 운화정체", "기허 · 중기하함 · 승양기능 저하", "음혈 · 정(精) · 진액 · 구조물질 보충"],
        "wuxing": ["木/水 평형 보조", "土 중심, 金 행기 보조", "土 중심, 木/火 상승 보조", "水 중심, 木 보조"],
        "direction": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복", "보기, 승양, 발산, 전환", "저장, 보존, 자음, 허열 완충"],
        "q6_connect": ["보존형 및 완충형 변화", "급진 전환형 변화 주도", "발산/상승 벡터 및 전환형 변화", "보존형 변화 및 수렴형 완충 (RD 3:3)"],
        "interpretation": [
            "산조인탕은 전통적 안신 방향을 소수성 모듈로 표현한 해석적 매핑 대상입니다. 영혈 소모로 인한 내부 허열을 수렴하여 다면체 구조 상의 급격한 전이를 완충하는 기하학적 평형 모델로 설명할 수 있습니다.",
            "평위산은 전통적으로 비위습탁과 운화 정체 상태에서 습을 말리고 기를 돌리는 방향에서 검토됩니다. 정체된 대사 국면을 깨고 흐름을 빠르게 회복시키는 동적 전환형 벡터 구조로 해석할 수 있습니다.",
            "보중익기탕은 전통적으로 비위기허와 중기하함의 방향에서 검토되는 처방입니다. 아래로 처진 기의 방향성을 끌어올리고 비위의 운화와 전신 기력 회복을 돕는 해석축을 지니며, 64큐브 다면체 해석에서는 보존형 안정화보다 발산/상승과 전환축이 강하게 나타나는 보기·승양형 처방으로 설명할 수 있습니다.",
            "육미지황환은 전통적으로 소모된 바탕을 보충하고 허열과 수습 정체를 함께 조절하는 방향에서 검토됩니다. 신(腎)과 간(肝)의 정혈을 윤택하게 하는 자음 구조물질 보충축을 지니며, 64큐브 다면체 해석에서는 보존·보충 중심축과 수습·허열 완충축이 대칭 균형을 이루는 RD 안정화 구조로 설명할 수 있습니다."
        ]
    })
    
    herbs = pd.DataFrame({
        "formula_id": [
            "F001", "F001", "F001", "F001", "F002", "F002", "F002", "F002",
            "F003", "F003", "F003", "F003", "F003", "F003", "F003", "F003",
            "F004", "F004", "F004", "F004", "F004", "F004"
        ],
        "herb_name": [
            "산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "감초",
            "황기", "인삼", "백출", "감초", "당귀", "진피", "승마", "시호",
            "숙지황", "산수유", "산약", "복령", "목단피", "택사"
        ],
        "role": [
            "군약", "신약", "좌약", "사약", "군약", "신약", "좌약", "사약",
            "군약", "신약", "신약", "사약", "좌약", "좌약", "사약", "사약",
            "군약", "신약", "신약", "좌약", "사약", "사약"
        ],
        "dose_range": ["15-20g", "9-12g", "6-9g", "3-6g", "10-15g", "9-12g", "9-12g", "3-6g", "15-20g", "9-12g", "9-12g", "3-6g", "6-9g", "3-6g", "3-6g", "3-6g", "20-25g", "10-15g", "10-15g", "9-12g", "9-12g", "9-12g"],
        "four_qi": ["평", "한", "온", "평", "온", "온", "온", "평", "미온", "미온", "온", "평", "온", "온", "미한", "미한", "미온", "미온", "평", "평", "미한", "한"],
        "five_flavor": ["감, 산", "고, 감", "신", "감", "신, 고", "고, 신", "신, 고", "감", "감", "감, 미고", "감, 고", "감", "감, 신", "신, 고", "신, 감", "고, 신", "감", "산, 삽", "감", "감, 담", "고, 신", "감, 담"],
        "meridian_entry": ["심, 간, 담", "폐, 위, 신", "간, 담, 심포", "심, 폐, 비, 위", "비, 위", "비, 위, 대장", "비, 폐", "심, 폐, 비, 위", "비, 폐", "비, 폐, 심", "비, 위", "심, 폐, 비, 위", "심, 간, 비", "비, 폐", "폐, 비, 위", "간, 담", "간, 신", "간, 신", "비, 폐, 신", "심, 비, 신", "심, 간, 신", "신, 방광"]
    })
    
    safety = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "drug_interaction_flag": ["수면제, 진정제", "해당없음", "항응고제, 항혈소판제", "이뇨제, 혈압약", "해당없음", "해당없음", "해당없음", "면역관련 약물", "혈당관련 약물, 혈압약", "해당없음", "항응고제", "해당없음", "해당없음", "해당없음", "해당없음", "혈당관련 약물(시너지)", "이뇨제(시너지)", "항응고제", "이뇨제(시너지)"],
        "pregnancy_flag": ["안전", "안전", "주의권고", "안전", "안전", "신중투여", "안전", "안전", "안전", "안전", "주의권고", "안전", "안전", "안전", "안전", "안전", "안전", "금기추정", "안전"],
        "liver_kidney_flag": ["대량사용시 간부담", "특이사항 없음", "특이사항 없음", "장기복용시 신장/혈압 주의", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 간효소 주의", "소화기계 부담(위장장애)", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 신장 주의"],
        "evidence_level": ["임상확인필요", "일반안전", "문헌보고", "문헌보고", "일반안전", "주의권고", "일반안전", "이론적주의", "문헌보고", "일반안전", "전통주의", "일반안전", "임상확인필요", "전통주의", "일반안전", "이론적주의", "일반안전", "문헌보고", "임상확인필요"],
        "evidence_note": ["과다 복용 시 간효소 수치 상승", "일반적 용량 내 안전", "혈소판 응집 억제 작용", "위알도스테론증 유발 가능", "음허내열 환자 주의", "동물실험 자궁수축", "일반적 용량 내 안전", "면역계 자극 가능성 검토", "과량 복용 시 두근거림/혈압상승", "일반적 용량 내 안전", "자궁 수축 및 출혈 경향", "상열감 환자 주의", "특이 체질 간부담", "점액질로 인한 소화불량/설사", "일반적 용량 내 안전", "혈당 변동 가능성 관련 확인", "수분 대사 보조", "혈류 순환 관련 확인", "신장 배설 부담 가능성"]
    })
    
    vectors = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "codon": ["UUU (U-U-U)", "UCU (U-C-U)", "UAU (U-A-U)", "UGG (U-G-G)", "CUU (C-U-U)", "CCU (C-C-U)", "CAU (C-A-U)", "AUG (A-U-G)", "CGU (C-G-U)", "AUU (A-U-U)", "ACU (A-C-U)", "AAU (A-A-U)", "AGU (A-G-U)", "GUU (G-U-U)", "GCU (G-C-U)", "GAU (G-A-U)", "GGU (G-G-U)", "UGU (U-G-U)", "CAA (C-A-A)"],
        "amino_acid": ["Phe (페닐알라닌)", "Ser (세린)", "Tyr (티로신)", "Trp (트립토판)", "Leu (류신)", "Pro (프롤린)", "His (히스티딘)", "Met (메티오닌)", "Arg (아르기닌)", "Ile (이소류신)", "Thr (트레오닌)", "Asn (아스파라긴)", "Ser (세린)", "Val (발린)", "Ala (알라닌)", "Asp (아스파르트산)", "Gly (글리신)", "Cys (시스테인)", "Gln (글루타민)"],
        "functional_module": ["소수성 안정화 경향 축", "친수성 열 완충 경향 축", "방향족 고리 구조 완충축", "복합 처방 내 다양한 작용축을 완충하는 상징적 주석", "소수성 드라이브 경향 축", "단백질 구조적 특성을 활용한 상징적 주석", "전하 결합을 활용한 해석적 주석 축", "전통적 보기 방향을 가리키는 에너지 대사 해석축의 시작 신호", "전통적 기력 회복 및 대사 관련 해석축", "소수성 코어 형성 경향 축", "친수성 수소결합 유지 경향 축", "극성 아미노산 기반 면역 관련 해석축", "유연성 중심의 완충 해석축", "구조 단백질 보존 경향 축", "비극성 메틸기 완충 경향 축", "음전하 기반 수분 포획 경향 축", "분자구조 유연성 경향 축", "순환 촉진 관련 해석적 주석 축", "측사슬 극성 배출 경향 축"],
        "q6_vector_type": ["보존형 변화 (소수성)", "수렴형 완충 (친수성)", "완충형 변화", "수렴형 조화", "급진 전환형 변화", "완충형 전환", "보존형 변화", "비정상 연장형 변화", "급진 전환형 변화", "보존형 강화", "보존형 변화", "상승형 전환", "완충형 변화", "보존형 변화", "수렴형 완충", "보존형 완충", "전환형 배출", "완충형 변화", "급진 전환형 배출"],
        "biochemical_interpretation": ["전통적 안신 방향을 소수성 모듈로 표현한 해석적 매핑", "열성 편향을 친수성 수소결합 구조로 완충하는 모델 주석", "방향족 구조의 전자를 활용해 과도한 편향을 기술하는 해석축", "방향족 잔기 이미지로, 복합 처방 내 다양한 작용축을 완충하는 상징적 주석", "정체된 전통 상태를 소수성 반발력으로 가시화한 해석축", "단백질 2차 구조의 유연성을 통해 기체 상태를 기술하는 주석", "전하 매핑을 통해 처방의 흐름 균형을 기술하는 도구", "전통적 보기 방향을 현대 생명정보 언어로 번역한 에너지 대사 해석축", "전통적 기력 회복 과정을 대변하는 에너지 대사 모델 주석", "소화기 구조의 안정적 보존 상태를 대변하는 해석적 매핑", "유효 성분의 친수성 수화 상태를 가시화하는 주석", "전통적 승양 방향을 상부 극성 벡터로 가정한 해석축", "처방 내 과부하 상태를 유연하게 분산하는 기하학적 모델 주석", "물질 손실을 막고 구조적 안정성을 가정한 보존 모델", "비극성 장벽을 통해 체액 보존 방향을 설명하는 매핑", "음전하 속성을 통해 점막 안정 경향을 설명하는 해석축", "공간적 제약 없이 수분 평형 경로를 설명하는 해석 모델", "순환 정체 해소 경향을 설명하는 해석적 주석", "삼투압 변동 메커니즘을 통해 배출 평형을 설명하는 매핑"]
    })
    return formulas, polyhedrons, neijing, herbs, safety, vectors

df_formulas, df_polyhedrons, df_neijing, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 1단계: 환자 입력 패널")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 소화불량, 황반변성, 디스크")

st.sidebar.subheader("안전성 체크리스트 (필수)")
med_sedative = st.sidebar.checkbox("수면제/항우울제 복용")
med_blood = st.sidebar.checkbox("항응고제/혈압약 복용")
med_diab = st.sidebar.checkbox("당뇨약 복용")
cond_liver = st.sidebar.checkbox("간/신장 기능 저하")
cond_preg = st.sidebar.checkbox("임신/수유부")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("분석 및 리포트 생성", type="primary")

# ==========================================
# 메인 화면: 데이터 분석 및 시각화
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    poly_info = df_polyhedrons[df_polyhedrons["formula_name"] == selected_formula_name].iloc[0]
    nj_info = df_neijing[df_neijing["formula_name"] == selected_formula_name].iloc[0]
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    formula_vectors = df_vectors[df_vectors["herb_name"].isin(formula_herbs["herb_name"])]

    # [대망의 6대 패널 확장 구조화]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "네트워크 패널", "유전암호-64큐브 패널", "다면체 균형 패널", "황제내경 해석 패널", "안전성 경고 패널", "환자 설명 출력"
    ])
    
    # ------------------------------------------
    with tab1:
        st.subheader("📌 2단계: 변증 및 처방 구조 분석")
        if patient_symp:
            st.error(
                f"**⚠️ [임상 정합도 확인 알림]**\n\n"
                f"입력된 주증상/현대 진단명(**'{patient_symp}'**)과 선택 처방의 전통 변증 방향(**'{formula_info['indication_traditional']}'**)이 직접 일치하지 않을 수 있습니다. "
                f"본 처방은 특정 병명 자체보다 환자의 전신 변증, 허실, 한열, 소화력, 동반 증상을 종합한 한의사의 임상적 판단을 기준으로 최종 검토해야 합니다."
            )
            
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})")
        st.markdown("**군신좌사 (君臣佐使) 네트워크 구조**")
        st.dataframe(formula_herbs[["role", "herb_name", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        st.caption("※ 君(중심 target module), 臣(보조 pathway), 佐(과도한 편향 완충), 使(방향 정렬 및 귀경)")
        
    # ------------------------------------------
    with tab2:
        st.subheader("🧬 3단계: 유전암호 및 64큐브 생화학 벡터 매핑")
        st.error("**[해석 주의] 약재-코돈-아미노산 매핑은 약재가 실제 유전암호를 직접 변화시킨다는 뜻이 아니라, 약재의 전통적 작용 방향을 64큐브 생화학 벡터 언어로 주석화한 해석 모델입니다.**")
        
        st.success(f"""
        **💡 64큐브 방향성 요약 ({selected_formula_name} 기준)**
        - **주요 방향:** {formula_info['pattern_tags']}
        - **64큐브 핵심 변화 유형:** `{formula_info['q6_core_vector']}`
        """)
        
        for idx, row in formula_vectors.iterrows():
            st.markdown(f"### **[{row['herb_name']}]**")
            st.markdown(f"- 🧬 **유전암호 매핑:** `코돈: {row['codon']}` ➔ **`아미노산: {row['amino_acid']}`**")
            st.markdown(f"- 🎯 **표적 기능:** {row['functional_module']}")
            st.markdown(f"- 🧭 **벡터 유형:** `{row['q6_vector_type']}`")
            st.markdown(f"- 💡 **생화학적 해석:** {row['biochemical_interpretation']}")
            st.divider()

    # ------------------------------------------
    with tab3:
        st.subheader("💎 4단계: 다면체 균형 및 구조화 패널")
        st.warning("**다면체 분석은 처방 효과를 증명하는 것이 아니라, 처방의 복합 방향성을 구조적으로 시각화하는 정보기하학적 보조 도구입니다.**")
        
        st.markdown("#### 1. Q6 (64차원 하이퍼큐브) 원본 상태공간")
        st.info("64상태(코돈/괘)와 384방향성 변화(효사/코돈 변이)가 그물처럼 연결된 원본 생화학 지도입니다. 처방은 이 공간을 가로지르는 복합 벡터로 해석됩니다.")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2. Octahedron (정팔면체) : 6대 방향 벡터")
            st.markdown("*처방의 중심 방향성을 6대 축(보존, 완충, 전환, 수렴, 발산, 배출)으로 압축하여 정량화된 점수로 표시합니다.*")
            st.success(f"**[{selected_formula_name} 6방향 요약]**\n\n{poly_info['octahedron']}")
            
            st.markdown("#### 3. VE (벡터 평형체) : 12 Position-Base 축")
            st.markdown("*12개의 꼭짓점 축(3코돈 위치 × 4염기) 위에 약재별 코돈-아미노산 주석을 배치합니다.*")
            st.success(f"**[{selected_formula_name} VE 12축 배치]**\n\n{poly_info['ve_axis']}")

        with col2:
            st.markdown("#### 4. RD (마름모십이면체) : 안정화와 완충면")
            st.markdown("*VE의 쌍대 구조로서, VE가 미는 방향축들이 모여 형성하는 '균형 공간'과 '완충면'을 해석합니다.*")
            st.success(f"**[{selected_formula_name} RD 안정화 해석]**\n\n{poly_info['rd_plane']}")
            
            st.markdown("#### 5. TO (깎은 정팔면체) : 전신 네트워크 확산")
            st.markdown("*단일 처방 모듈이 인체라는 거대 공간을 채워나갈 때(공간충전), 어긋남 없이 안정적으로 확장되는 균형 셀 모델입니다.*")
            st.info("처방의 장기적 투여 시 전신적 평형(Homeostasis) 유지력을 대변합니다.")

    # ------------------------------------------
    # [신규 탑재] 황제내경 해석 패널! 원장님의 핵심 이론층 가시화
    # ------------------------------------------
    with tab4:
        st.subheader("📚 5단계: 황제내경(黃帝內經) 동적평형 해석 패널")
        st.error("**[해석 주의] 본 패널은 처방 효과를 증명하기 위한 것이 아니라, 전통 한의학의 음양·오행·장부·기혈 언어를 64큐브의 상태공간 해석과 연결하기 위한 설명층입니다.**")
        
        st.info(
            "“64큐브에서 하나의 처방은 단일 표적을 때리는 약물이 아니라, 몸의 여러 방향 벡터를 동시에 조절하는 복합 개입으로 해석됩니다. "
            "황제내경적 관점에서는 이를 음양의 치우침, 장부 기능의 허실, 기혈진액의 승강출입 변화로 매핑할 수 있습니다.”"
        )
        
        col_nj1, col_nj2 = st.columns(2)
        with col_nj1:
            st.markdown("#### 1. 음양(陰陽) 동적평형과 상태공간")
            st.markdown(
                "인체는 고정된 실체가 아니라 음양의 승강·출입·소장 변화 속에서 동적 균형을 유지하는 생명 시스템입니다. "
                "**64큐브의 6비트 부호 변화는 음양 변화 방향을 정보기하학적 공간으로 시각화한 원본 지도** 역할을 수행합니다."
            )
            
            st.markdown("#### 2. 오행(五行)의 동적 작용 방향 벡터 주석")
            st.markdown(
                "- 🪵 **木 (목):** 소통, 발산, 작용축 조절 경향\\\n"
                "- 🔥 **火 (화):** 대사 활성, 열, 반응성 가속 경향\\\n"
                "- ⛰️ **土 (토):** 중심 유지, 운화, 구조적 안정화 경향\\\n"
                "- 🪙 **金 (금):** 수렴, 경계 획정, 과잉 절제 경향\\\n"
                "- 💧 **水 (수):** 깊은 저장, 정(精)의 응축, 물질 보존 경향"
            )
            
            st.markdown("#### 3. 치미병(治未病) 및 예방의학적 해석")
            st.success(
                "**[치미병의 64큐브적 정의]**\\\n"
                "이미 고착화된 특정 병명에 개입하는 것이 아니라, 기혈·장부의 불균형이 파국에 이르기 전에 "
                "**'위험한 급진 전환 국면'을 선제적으로 감지하고 완충형 및 보존형 변화 벡터를 유도**하는 정밀 방향성 제어로 해석됩니다."
            )

        with col_nj2:
            st.markdown(f"### 🎯 [{selected_formula_name}] 황제내경 지문 분석")
            st.markdown(f"- 🏛️ **장부축 매핑:** `{nj_info['zang_fu']}`")
            st.markdown(f"- 🩸 **기혈진액 변증축:** `{nj_info['qi_blood']}`")
            st.markdown(f"- ☯️ **오행 작용 벡터:** `{nj_info['wuxing']}`")
            st.markdown(f"- 🧭 **승강출입 방향성:** `{nj_info['direction']}`")
            st.markdown(f"- 🧬 **64큐브 다면체 연결:** `{nj_info['q6_connect']}`")
            st.divider()
            st.markdown("#### 📝 종합 평형 해석")
            st.info(nj_info['interpretation'])

    # ------------------------------------------
    with tab5:
        st.subheader("🚨 6단계: 임상 안전성 확인 필요")
        st.info("**이 경고는 처방 금지가 아니라, 한의사의 추가 확인이 필요하다는 뜻입니다.**\n\n복용약, 병력, 용량, 복용 기간을 확인하십시오.")
        
        high_alerts = []
        med_alerts = []
        notice_alerts = []

        if med_sedative and any(formula_safety["drug_interaction_flag"].str.contains("수면제|진정제", na=False)):
            high_alerts.append("🔴 **[약물상호작용: 높음]** 수면제/진정제 병용 시 과도한 진정 작용 유발 가능성 검토")
        if med_blood and any(formula_safety["drug_interaction_flag"].str.contains("항응고제|혈압약", na=False)):
            high_alerts.append("🔴 **[약물상호작용: 높음]** 항응고제 및 혈압약 병용 시 출혈 및 혈압 변동 경향 검토")
        if med_diab and any(formula_safety["drug_interaction_flag"].str.contains("혈당", na=False)):
            high_alerts.append("🔴 **[약물상호작용: 높음]** 당뇨약 병용 시 혈당 변동성(인삼 등 영향) 검토 요망")
        if cond_liver and any(formula_safety["liver_kidney_flag"].str.contains("간|신장", na=False)):
            high_alerts.append("🔴 **[임상기저치: 높음]** 간/신장 기능 저하 환자 대량/장기 사용 시 신장 배설 부담 및 간효소 추이 검토 요망")

        if cond_dig and any(formula_safety["liver_kidney_flag"].str.contains("소화", na=False)):
             med_alerts.append("🟡 **[소화기계: 중간]** 만성 소화불량 환자 복용 시 점액질 성분(숙지황 등)으로 인한 위장 부담 검토")

        if cond_preg and any(formula_safety["pregnancy_flag"].str.contains("주의|신중|금기", na=False)):
            notice_alerts.append("🟢 **[특수조건: 주의]** 임산부 주의/금기 약재 포함 여부 및 투여 타당성 확인 요망")
        notice_alerts.append("🟢 **[용량주의: 일반]** 장기 복용 및 대량 복용 시 환자의 복용 전후 전신 반응을 주기적으로 확인해야 합니다.")

        if high_alerts:
            st.markdown("### **[우선순위: 높음 (High)]**")
            for alert in high_alerts: st.error(alert)
        if med_alerts:
            st.markdown("### **[우선순위: 중간 (Medium)]**")
            for alert in med_alerts: st.warning(alert)
        if notice_alerts:
            st.markdown("### **[우선순위: 주의 (Notice)]**")
            for alert in notice_alerts: st.info(alert)
            
        if not high_alerts and not med_alerts and len(notice_alerts) <= 1:
            st.success("✅ 현재 입력된 환자 조건에서 특이 안전성 경고가 발견되지 않았습니다. (의료인의 최종 판단 필수)")
            
        st.markdown("---")
        st.markdown("**약재별 상세 안전성 데이터**")
        st.dataframe(formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_level", "evidence_note"]], use_container_width=True, hide_index=True)

    # ------------------------------------------
    with tab6:
        st.subheader("💬 7단계: 환자 설명 출력 패널")
        st.error("**[방어문] 본 대시보드의 유전암호 및 다면체 분석은 처방 효과를 단정하거나 증명하는 것이 아니며, 전통 처방 구조의 복합 방향성을 가시화하는 보조 도구입니다.**")
        
        st.markdown("#### 📝 진료기록용 요약 생성 (Medical Chart)")
        
        rd_plane_raw = poly_info.get("rd_plane", "")
        if "대칭 균형" in rd_plane_raw:
            rd_plane_clean = "RD 균형도 = 3:3 대칭 균형\n  - [보존/보충 3축]: 숙지황·산약·산수유\n  - [배출/완충 3축]: 복령·택사·목단피"
        else:
            rd_plane_clean = rd_plane_raw.replace('**', '').replace('▶ ', '').replace('\n', ' ')

        chart_summary = f"""
- 처방명: {selected_formula_name}
- 환자 주증상: {patient_symp if patient_symp else '미입력'}
- 전통 변증 방향: {formula_info['indication_traditional']}
- 64큐브 핵심 변화: {formula_info['q6_core_vector']}
- 다면체 안정성(RD): \n  {rd_plane_clean}
- 황제내경 해석축: 장부({nj_info['zang_fu']}) | 오행({nj_info['wuxing']})
- 안전성 체크: 최고 위험도 등급(High/Medium) 발생 여부 검토 필함
"""
        st.code(chart_summary)
        
        st.markdown("#### 🗣️ 환자 설명문 생성 (환자 배포용)")
        
        if selected_formula_name == "육미지황환":
            symptom_warnings = []
            if med_diab: symptom_warnings.append("복용 전후 혈당 변동 가능성")
            if cond_dig: symptom_warnings.append("소화 상태 및 설사 여부")
            if cond_liver: symptom_warnings.append("피로감 및 부종 여부")
            
            warning_text = ""
            if symptom_warnings:
                warning_text = f"다만, 현재 입력된 정보(당뇨약 복용, 만성 소화불량, 간/신장 저하 등)가 체크되어 있으므로, 진료 과정에서 <b>{', '.join(symptom_warnings)}</b>를 세밀하게 확인해야 합니다."
            else:
                warning_text = "다만, 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, 복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서 조절해야 합니다."

            patient_html = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                이 처방, <b>육미지황환</b>은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 소모된 바탕을 보충하고 과도한 열감과 수분 정체를 함께 조절하는 복합 처방으로 설명할 수 있습니다.<br><br>
                전통 한의학적 해석에서는 자음, 보신, 구조물질 보충의 방향으로 해석할 수 있으며, 64큐브 다면체 해석에서는 숙지황·산약·산수유의 보존/보충 중심축과 복령·택사·목단피의 수습/허열 완충축이 3:3으로 마주 보는 RD 안정화 구조로 해석됩니다.<br><br>
                {warning_text}
            </div>
            """
            st.markdown(patient_html, unsafe_allow_html=True)
            
        elif selected_formula_name == "보중익기탕":
            symptom_warnings = []
            if med_diab: symptom_warnings.append("복용 전후 혈당 변동 가능성")
            if cond_liver: symptom_warnings.append("기력 상태 및 피로도 추이")
            
            warning_text = ""
            if symptom_warnings:
                warning_text = f"다만, 현재 입력된 정보(당뇨약 복용, 기저질환 등)가 체크되어 있으므로, 진료 과정에서 <b>{', '.join(symptom_warnings)}</b>를 세밀하게 확인해야 합니다."
            else:
                warning_text = "다만, 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, 복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서 조절해야 합니다."

            patient_html_bj = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                이 처방, <b>보중익기탕</b>은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 소모된 바탕을 보충하고 기력을 끌어올리는 복합 처방으로 설명할 수 있습니다.<br><br>
                전통 한의학적 해석에서는 승양, 익기, 에너지 부스팅 방향으로 해석할 수 있으며, 64큐브 다면체 해석에서는 보존형 안정화 처방이라기보다, Octahedron 6방향 벡터 중 <b>발산/상승과 전환축이 강하게 나타나는 보기·승양형 처방으로 해석</b>됩니다.<br><br>
                {warning_text}
            </div>
            """
            st.markdown(patient_html_bj, unsafe_allow_html=True)
            
        else:
            patient_html_generic = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                이 처방(<b>{selected_formula_name}</b>)은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 균형 방향을 조절하는 복합 처방으로 설명할 수 있습니다.<br><br>
                전통 한의학적 해석에서는 <b>{formula_info['pattern_tags']}</b>의 방향성으로 해석할 수 있으며, 64큐브 다면체 해석에서는 <b>{formula_info['q6_core_vector']}</b>의 평형 구조로 해석됩니다.<br><br>
                다만, 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, 복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서 조절해야 합니다.
            </div>
            """
            st.markdown(patient_html_generic, unsafe_allow_html=True)
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '분석 및 리포트 생성' 버튼을 눌러주세요.")
