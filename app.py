import streamlit as st
import pandas as pd

# ==========================================
# 0. 페이지 설정 및 필수 경고문
# ==========================================
st.set_page_config(page_title="64큐브-다면체 처방 대시보드", layout="wide")

st.warning(
    "**[주의] 본 대시보드는 한의사의 변증, 처방 설명, 안전성 확인, 연구 기록을 돕기 위한 교육·연구 보조 도구입니다.**\n\n"
    "자동 진단 또는 자동 처방 도구가 아니며, 실제 처방은 면허가 있는 의료인의 임상 판단에 따라 결정되어야 합니다."
)

st.title("☯️ 유전암호-다면체 처방 네트워크 대시보드")
st.markdown("64큐브 상태공간을 다면체(Octahedron, VE, RD)로 압축하여 처방의 복합 방향성을 구조적으로 시각화하는 정보기하학적 분석 모델입니다.")

# ==========================================
# 1. 빅데이터 베이스 (정량화 데이터 추가)
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
    
    # [정량화 업데이트] 다면체 점수 및 3:3 대칭 구조 반영
    polyhedrons = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "octahedron": [
            "보존: 85 | 수렴: 80 | 완충: 70 | 전환: 30 | 발산: 20 | 배출: 15\n\n*(보존/수렴 강함, 완충 중간, 배출/발산 낮음)*",
            "배출: 85 | 전환: 80 | 발산: 65 | 완충: 60 | 보존: 20 | 수렴: 15\n\n*(배출/전환 강함, 완충 중간, 보존 낮음)*",
            "발산(상승): 90 | 전환: 85 | 보충: 70 | 완충: 40 | 수렴: 20 | 배출: 10\n\n*(발산/상승 강함, 전환 강함, 수렴/배출 낮음)*",
            "보존: 90 | 보충: 85 | 수렴: 80 | 완충: 70 | 배출: 55 | 급진전환: 20\n\n*(보존/보충/수렴 강함, 완충 중간, 급진전환 낮음)*"
        ],
        "ve_axis": [
            "U-base (Phe, Tyr, Trp) 축 중심 분포",
            "C-base (Leu, Pro, His) 축 중심 분포",
            "A-base (Met, Ile, Asn) 축 중심 분포",
            "G-base (Val, Ala, Asp, Gly) 중심\n\n*12 position-base 축 전반의 입체적 물질 보충 및 구조 안정화*"
        ],
        "rd_plane": [
            "[안정화 구조] 수면/진정 방향의 단일면 강력 안정화",
            "[안정화 구조] 습탁 제거 및 기행 방향의 동적 완충면 형성",
            "[안정화 구조] 상부 면역 및 ATP 생성 축을 지지하는 넓은 상승 안정면",
            "**[RD 균형도 = 3:3 대칭 균형]**\n\n▶ **보존/보충 3축 (三補):** 숙지황·산약·산수유\n▶ **배출/완충 3축 (三瀉):** 복령·택사·목단피\n\n*보존·보충 중심축과 수습·허열 완충축이 마주 보며 완벽한 대칭적 쌍대(Dual) 구조를 형성함.*"
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
        "drug_interaction_flag": ["수면제, 진정제", "해당없음", "항응고제, 항혈소판제", "이뇨제, 혈압약", "해당없음", "해당없음", "해당없음", "면역억제제", "혈당강하제, 혈압약", "해당없음", "항응고제", "해당없음", "해당없음", "해당없음", "해당없음", "혈당강하제(시너지)", "이뇨제(시너지)", "항응고제", "이뇨제(시너지)"],
        "pregnancy_flag": ["안전", "안전", "주의권고", "안전", "안전", "신중투여", "안전", "안전", "안전", "안전", "주의권고", "안전", "안전", "안전", "안전", "안전", "안전", "금기추정", "안전"],
        "liver_kidney_flag": ["대량사용시 간부담", "특이사항 없음", "특이사항 없음", "장기복용시 신장/혈압 주의", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 간효소 주의", "소화기계 부담(위장장애)", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 신장 주의"],
        "evidence_level": ["임상확인필요", "일반안전", "문헌보고", "문헌보고", "일반안전", "주의권고", "일반안전", "이론적주의", "문헌보고", "일반안전", "전통주의", "일반안전", "임상확인필요", "전통주의", "일반안전", "이론적주의", "일반안전", "문헌보고", "임상확인필요"],
        "evidence_note": ["과다 복용 시 간효소 수치 상승", "일반적 용량 내 안전", "혈소판 응집 억제 작용", "위알도스테론증 유발 가능", "음허내열 환자 주의", "동물실험 자궁수축", "일반적 용량 내 안전", "면역계 자극 가능성", "과량 복용 시 두근거림/혈압상승", "일반적 용량 내 안전", "자궁 수축 및 출혈 경향", "상열감 환자 주의", "특이 체질 간부담", "점액질로 인한 소화불량/설사", "일반적 용량 내 안전", "혈당 강하 작용 보조", "이뇨 작용 보조", "혈류 순환 촉진", "신장 배설 부담 가능성"]
    })
    
    vectors = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "codon": ["UUU (Uracil-Uracil-Uracil)", "UCU (Uracil-Cytosine-Uracil)", "UAU (Uracil-Adenine-Uracil)", "UGG (Uracil-Guanine-Guanine)", "CUU (Cytosine-Uracil-Uracil)", "CCU (Cytosine-Cytosine-Uracil)", "CAU (Cytosine-Adenine-Uracil)", "AUG (Adenine-Uracil-Guanine)", "CGU (Cytosine-Guanine-Uracil)", "AUU (Adenine-Uracil-Uracil)", "ACU (Adenine-Cytosine-Uracil)", "AAU (Adenine-Adenine-Uracil)", "AGU (Adenine-Guanine-Uracil)", "GUU (Guanine-Uracil-Uracil)", "GCU (Guanine-Cytosine-Uracil)", "GAU (Guanine-Adenine-Uracil)", "GGU (Guanine-Guanine-Uracil)", "UGU (Uracil-Guanine-Uracil)", "CAA (Cytosine-Adenine-Adenine)"],
        "amino_acid": ["Phe (페닐알라닌)", "Ser (세린)", "Tyr (티로신)", "Trp (트립토판)", "Leu (류신)", "Pro (프롤린)", "His (히스티딘)", "Met (메티오닌)", "Arg (아르기닌)", "Ile (이소류신)", "Thr (트레오닌)", "Asn (아스파라긴)", "Ser (세린)", "Val (발린)", "Ala (알라닌)", "Asp (아스파르트산)", "Gly (글리신)", "Cys (시스테인)", "Gln (글루타민)"],
        "functional_module": ["소수성 안정화 (수면조절)", "친수성 열 완충 (해열)", "방향족 고리 구조 완충 (혈류)", "거대 복합 모듈 중화 (전신 조화)", "강력한 소수성 드라이브 (습탁 제거)", "구조적 꺾임(Kink) 유도 (기체 해소)", "양전하 결합 활성화 (기행)", "대사 경로의 시작(Start) 신호", "산화질소(NO) 및 ATP 생성 촉진", "소수성 코어 형성 (위장관 보존)", "친수성 수소결합 유지 (혈류 보존)", "극성 아미노산 네트워크 (면역 활성)", "효소 활성부위 유연성 제공", "강력한 구조 단백질 뼈대 (자음)", "비극성 메틸기 완충 (체액 보존)", "음전하 기반 수분 포획 (점막 재생)", "가장 작은 분자구조 유연성 (수분 대사)", "이황화 결합(S-S) 조절 (순환 촉진)", "친수성 측사슬 극성 배출 (이뇨)"],
        "q6_vector_type": ["보존형 변화 (소수성)", "수렴형 완충 (친수성)", "완충형 변화", "수렴형 조화", "급진 전환형 변화", "완충형 전환", "보존형 변화", "비정상 연장형 변화 (Start)", "급진 전환형 변화", "보존형 강화", "보존형 변화", "상승형 전환", "완충형 변화", "보존형 변화 (구조형성)", "수렴형 완충", "보존형 완충", "전환형 배출", "완충형 변화", "급진 전환형 배출"],
        "biochemical_interpretation": ["극도 긴장을 완화하고 소수성(안정) 모듈 강화", "열성 편향을 친수성 수소결합 장벽으로 완충", "방향족 구조의 전자를 활용해 과도한 편향 완충", "다양한 아미노산들의 충돌을 거대 분자로 중화", "정체된 상태를 강력한 소수성 반발력으로 회복", "단백질 2차 구조의 꺾임을 통해 과도한 수축 이완", "양전하를 띤 표면 구조를 통해 완만한 균형 조절", "단백질 합성의 시작을 알리며 기저 대사량을 끌어올림", "혈관 확장 신호전달을 통해 미토콘드리아 대사 가속", "세포막 내부의 에너지 흡수율 및 구조 보존", "혈액 내 유효 물질의 수화(Hydration) 상태 유지", "수용성 방어 기전을 전신(상부)으로 활성화", "간 대사 효소계의 과부하를 유연하게 완충", "세포 내 물리적 뼈대를 형성하여 물질 손실 방지", "비극성 장벽을 통해 체액 증발을 막는 물리적 장벽 강화", "음전하를 띠어 위장관 점막의 수분을 강하게 포획", "공간적 제약 없이 잉여 수분을 배출 경로로 유도", "말초 혈관 내 단백질 결합을 풀어 순환 정체 해소", "강한 친수성 삼투압을 통해 신장 여과압 조절"]
    })
    return formulas, polyhedrons, herbs, safety, vectors

df_formulas, df_polyhedrons, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 1단계: 환자 입력 패널")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 만성피로, 소화불량")

st.sidebar.subheader("안전성 체크리스트 (필수)")
med_sedative = st.sidebar.checkbox("수면제/항우울제 복용")
med_blood = st.sidebar.checkbox("항응고제/혈압약 복용")
med_diab = st.sidebar.checkbox("당뇨약 복용")
cond_liver = st.sidebar.checkbox("간/신장 기능 저하")
cond_preg = st.sidebar.checkbox("임신/수유부")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("분석 및 설명자료 생성", type="primary")

# ==========================================
# 메인 화면: 데이터 분석 및 시각화
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    poly_info = df_polyhedrons[df_polyhedrons["formula_name"] == selected_formula_name].iloc[0]
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    formula_vectors = df_vectors[df_vectors["herb_name"].isin(formula_herbs["herb_name"])]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["네트워크 패널", "유전암호-64큐브 패널", "다면체 균형 패널", "안전성 경고 패널", "환자 설명 출력"])
    
    # ------------------------------------------
    with tab1:
        st.subheader("📌 2단계: 변증 및 처방 구조 분석")
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})")
        st.markdown("**군신좌사 (君臣佐使) 네트워크 구조**")
        st.dataframe(formula_herbs[["role", "herb_name", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        st.caption("※ 君(중심 target module), 臣(보조 pathway), 佐(과도한 편향 완충), 使(방향 정렬 및 귀경)")
        
    # ------------------------------------------
    with tab2:
        st.subheader("🧬 3단계: 유전암호 및 64큐브 생화학 벡터 매핑")
        
        # [핵심 방어선 구축]
        st.error("**[해석 주의] 약재-코돈-아미노산 매핑은 약재가 실제 유전암호를 직접 바꾼다는 뜻이 아니라, 약재의 전통적 작용 방향을 64큐브 코돈-아미노산 물성 벡터로 주석화한 생명정보학적 해석 모델입니다.**")
        
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
    with tab4:
        st.subheader("🚨 5단계: 안전성 확인 필요")
        st.info("**이 경고는 처방 금지가 아니라, 한의사의 추가 확인이 필요하다는 뜻입니다.**\n\n복용약, 병력, 용량, 복용 기간을 확인하십시오.")
        
        safety_alerts = []
        if med_sedative and any(formula_safety["drug_interaction_flag"].str.contains("수면제|진정제", na=False)):
            safety_alerts.append("⚠️ **[약물상호작용]** 수면제/진정제 병용 시 과도한 진정 작용 주의")
        if med_blood and any(formula_safety["drug_interaction_flag"].str.contains("항응고제|혈압약", na=False)):
            safety_alerts.append("⚠️ **[약물상호작용]** 항응고제 및 혈압약 병용 시 출혈 및 혈압 변동 주의")
        if med_diab and any(formula_safety["drug_interaction_flag"].str.contains("혈당강하제", na=False)):
            safety_alerts.append("⚠️ **[약물상호작용]** 당뇨약 병용 시 혈당 변동성(인삼 등) 확인 요망")
        if cond_liver and any(formula_safety["liver_kidney_flag"].str.contains("간|신장", na=False)):
            safety_alerts.append("⚠️ **[간/신장 기능]** 간/신장 기능 저하 환자 대량/장기 사용 시 주의 요망")
        if cond_preg and any(formula_safety["pregnancy_flag"].str.contains("주의|신중|금기", na=False)):
            safety_alerts.append("⚠️ **[임신/수유]** 임산부 주의/금기 약재 포함 확인 요망")
        if cond_dig and any(formula_safety["liver_kidney_flag"].str.contains("소화", na=False)):
             safety_alerts.append("⚠️ **[소화기계]** 만성 소화불량 환자 복용 시 위장 장애(숙지황 등) 주의")

        if safety_alerts:
            for alert in safety_alerts:
                st.error(alert)
        else:
            st.success("✅ 현재 입력된 환자 조건에서 특이 안전성 경고가 발견되지 않았습니다. (의료인의 최종 판단 필수)")
            
        st.markdown("**약재별 상세 안전성 데이터**")
        st.dataframe(formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_level", "evidence_note"]], use_container_width=True, hide_index=True)

    # ------------------------------------------
    with tab5:
        st.subheader("💬 6단계: 환자 설명 출력 패널")
        st.markdown("#### 📝 진료기록용 요약 생성 (Medical Chart)")
        st.code(f"""
- 처방명: {selected_formula_name}
- 환자 주증상: {patient_symp if patient_symp else '미입력'}
- 64큐브 핵심 변화: {formula_info['q6_core_vector']}
- 다면체 안정성(RD): {poly_info['rd_plane'].replace('**','').replace('▶ ','').replace('\n',' ')}
- 안전성 체크: {'관련 주의 및 추가 검토 필요' if safety_alerts else '특이사항 없음'}
        """)
        
        st.markdown("#### 🗣️ 환자 설명문 생성 (환자 배포용)")
        
        # [육미지황환 맞춤형 고도화 설명 로직]
        if selected_formula_name == "육미지황환":
            symptom_warnings = []
            if med_diab: symptom_warnings.append("혈당 변화")
            if cond_dig: symptom_warnings.append("소화 상태 및 설사 여부")
            if cond_liver: symptom_warnings.append("피로감 및 부종 여부")
            
            warning_text = ""
            if symptom_warnings:
                warning_text = f"다만, 현재 입력된 정보(당뇨약 복용, 만성 소화불량, 간/신장 저하 등)가 체크되어 있으므로, 복용 전후 **{', '.join(symptom_warnings)}**를 진료 과정에서 세밀하게 확인해야 합니다."
            else:
                warning_text = "다만, 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, 복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서 용량을 조절해 나가겠습니다."

            st.info(
                f"이 처방({selected_formula_name})은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 소모된 바탕을 보충하고 과도한 열감과 수분 정체를 함께 조절하는 복합 처방으로 설명할 수 있습니다.\n\n"
                f"전통 한의학적으로는 자음, 보신, 구조물질 보충의 방향을 가지며, 64큐브 다면체 해석에서는 **보존·보충 중심축(숙지황, 산약, 산수유)**과 **수습·허열 완충축(복령, 택사, 목단피)**이 서로 완벽한 대칭 균형을 이루는 RD 안정화 구조로 볼 수 있습니다.\n\n"
                f"{warning_text}"
            )
        else:
            st.info(
                f"이 처방({selected_formula_name})은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, "
                f"여러 약재가 함께 작용하여 몸의 균형 방향을 조절하는 복합 처방입니다.\n\n"
                f"현재 상태를 고려할 때, 이 처방은 급격한 변화를 주지 않고 **{formula_info['pattern_tags']}**의 방향으로 몸을 회복시키도록 설계되었습니다.\n\n"
                f"다만, 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, "
                f"**복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서** 용량을 조절해 나가겠습니다."
            )
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '분석 및 설명자료 생성' 버튼을 눌러주세요.")
