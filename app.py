
import streamlit as st
import pandas as pd

# ==========================================
# 0. 페이지 기본 설정 및 필수 경고문
# ==========================================
st.set_page_config(page_title="64큐브 처방 교육·연구 대시보드", layout="wide")

st.warning(
    "**[주의]** 본 대시보드는 한의사의 변증, 처방 설명, 안전성 확인, 연구 기록을 돕기 위한 **교육·연구 보조 도구**입니다. "
    "자동 진단 또는 자동 처방 도구가 아니며, 실제 처방은 면허가 있는 의료인의 임상 판단, 환자 병력, 복용약, 검사 결과, 안전성 평가에 따라 결정되어야 합니다."
)

st.title("☯️ 64큐브 변증-처방 교육·연구 보조 대시보드")
st.markdown("전통 변증, 군신좌사 네트워크, 64큐브 생화학 벡터, 그리고 안전성 평가를 시각화합니다.")

# ==========================================
# 1. 핵심 데이터베이스 (데이터 분리 구조)
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_id": ["F001", "F002"],
        "formula_name": ["산조인탕", "평위산"],
        "indication_traditional": ["심비양허, 허번불면", "비위습탁, 복부팽만"],
        "pattern_tags": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복"],
        "caution_summary": ["간 기능 저하 주의, 과도한 진정 주의", "임산부 신중 투여, 기허 환자 주의"]
    })
    
    herbs = pd.DataFrame({
        "formula_id": ["F001", "F001", "F001", "F001", "F002", "F002", "F002", "F002"],
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "감초"],
        "role": ["군약", "신약", "좌약", "사약", "군약", "신약", "좌약", "사약"],
        "dose_range": ["15-20g", "9-12g", "6-9g", "3-6g", "10-15g", "9-12g", "9-12g", "3-6g"],
        "four_qi": ["평", "한", "온", "평", "온", "온", "온", "평"],
        "five_flavor": ["산, 감", "고, 감", "신", "감", "신, 고", "고, 신", "신, 고", "감"],
        "meridian_entry": ["심, 간, 담", "폐, 위, 신", "간, 담, 심포", "심, 폐, 비, 위", "비, 위", "비, 위, 대장", "비, 폐", "심, 폐, 비, 위"]
    })
    
    safety = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "창출", "후박", "진피", "감초"],
        "contraindication": ["실열증", "비위허한", "음허화왕, 출혈질환", "음허내열", "임산부", "기허증", "부종, 고혈압"],
        "drug_interaction_flag": ["수면제, 진정제", "", "항응고제, 항혈소판제", "", "", "", "이뇨제, 혈압약"],
        "pregnancy_flag": ["", "", "주의", "", "신중투여", "", ""],
        "liver_kidney_flag": ["대량사용시 간부담", "", "", "", "", "", "장기복용시 신장/혈압 주의"],
        "evidence_note": ["과다 복용 시 간효소 수치 상승 보고", "", "혈소판 응집 억제 작용", "", "동물실험 자궁수축", "", "위알도스테론증 유발 가능"]
    })
    
    vectors = pd.DataFrame({
        "herb_name": ["산조인", "천궁", "창출", "진피"],
        "target_gene": ["HTR1A", "PTGS2", "TNF", "IL6"],
        "functional_module": ["수면조절, 진정", "염증 완충, 혈류 순환", "위장관 운동, 습탁 제거", "면역 조절, 기행"],
        "q6_vector_type": ["보존형 변화", "완충형 변화", "급진 전환형 변화", "보존형 변화"],
        "biochemical_interpretation": ["극성(극도 긴장) -> 소수성(내부 안정) 모듈 강화", "과도한 편향을 완충하여 구조적 제약 완화", "정체된 상태(Pro)를 풀고 극성 흐름 회복", "기혈 흐름의 완만한 균형 방향 조절"]
    })
    return formulas, herbs, safety, vectors

df_formulas, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 1단계: 환자 입력 패널")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 불면증")

st.sidebar.subheader("안전성 체크리스트 (필수)")
med_sedative = st.sidebar.checkbox("수면제/항우울제 복용")
med_blood = st.sidebar.checkbox("항응고제/혈압약 복용")
cond_liver = st.sidebar.checkbox("간/신장 기능 저하")
cond_preg = st.sidebar.checkbox("임신/수유부")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("분석 및 설명자료 생성", type="primary")

# ==========================================
# 메인 화면: 데이터 분석 및 시각화
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    formula_vectors = df_vectors[df_vectors["herb_name"].isin(formula_herbs["herb_name"])]

    tab1, tab2, tab3, tab4 = st.tabs(["네트워크 패널", "64큐브 벡터 패널", "안전성 경고 패널", "환자 설명 출력"])
    
    with tab1:
        st.subheader("📌 2단계: 변증 및 처방 구조 분석")
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})")
        st.markdown("**군신좌사 (君臣佐使) 네트워크 구조**")
        st.dataframe(formula_herbs[["role", "herb_name", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        st.caption("※ 君(중심 target module), 臣(보조 pathway), 佐(과도한 편향 완충), 使(방향 정렬 및 귀경)")
        
    with tab2:
        st.subheader("🧬 3단계: 64큐브 생화학 벡터 패널")
        st.markdown("*64큐브 생화학 벡터는 처방의 효과를 직접 증명하는 것이 아니며, 네트워크 변화를 생명정보 언어로 설명하는 보조 지도입니다.*")
        for idx, row in formula_vectors.iterrows():
            st.markdown(f"**[{row['herb_name']}] 🎯 표적 기능:** {row['functional_module']}")
            st.markdown(f"- **벡터 유형:** `{row['q6_vector_type']}`")
            st.markdown(f"- **해석:** {row['biochemical_interpretation']}")
            st.divider()

    with tab3:
        st.subheader("🚨 4단계: 안전성 확인 필요")
        st.markdown("이 항목은 처방 금지가 아니라, 한의사의 추가 확인이 필요하다는 뜻입니다. 복용약, 환자 병력, 용량을 확인하십시오.")
        safety_alerts = []
        if med_sedative and any(formula_safety["drug_interaction_flag"].str.contains("수면제|진정제", na=False)):
            safety_alerts.append("⚠️ **[약물상호작용]** 수면제/진정제 병용 시 과도한 진정 작용 주의 (산조인 등 확인 요망)")
        if med_blood and any(formula_safety["drug_interaction_flag"].str.contains("항응고제|혈압약", na=False)):
            safety_alerts.append("⚠️ **[약물상호작용]** 항응고제 및 혈압약 병용 시 주의 (천궁, 감초 등 확인 요망)")
        if cond_liver and any(formula_safety["liver_kidney_flag"] != ""):
            safety_alerts.append("⚠️ **[간/신장 기능]** 간/신장 기능 저하 환자 대량/장기 사용 시 주의 요망")
        if cond_preg and any(formula_safety["pregnancy_flag"] != ""):
            safety_alerts.append("⚠️ **[임신/수유]** 임산부 신중 투여 약재 포함 (천궁, 후박 등 확인 요망)")

        if safety_alerts:
            for alert in safety_alerts:
                st.error(alert)
        else:
            st.success("✅ 현재 입력된 환자 조건에서 특이 안전성 경고가 발견되지 않았습니다. (의료인의 최종 판단 필수)")
        st.markdown("**약재별 상세 안전성 데이터**")
        st.dataframe(formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_note"]], use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("💬 5단계: 환자 설명 출력 패널")
        st.markdown("#### 👨‍⚕️ 진료기록용 요약 (Medical Chart)")
        st.code(f"""
- 처방명: {selected_formula_name}
- 환자 주증상: {patient_symp if patient_symp else '미입력'}
- 64큐브 방향성: {formula_info['pattern_tags']}
- 안전성 체크: {'경고 발생 (세부사항 추가 검토 요망)' if safety_alerts else '특이사항 없음'}
        """)
        st.markdown("#### 🗣️ 환자 설명문 예시 (환자 배포용)")
        st.info(f"이 처방({selected_formula_name})은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용해 몸의 전체적인 균형 방향을 조절하는 복합 처방입니다.\n\n현재 상태를 고려할 때, 이 처방은 급격한 변화를 주지 않고 기혈 흐름과 내부 안정을 도모하는 완만한 회복 방향으로 작용하도록 설계되었습니다.\n\n다만, 현재 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, 복용 전후의 반응을 저(한의사)와 함께 세밀하게 확인하면서 용량을 조절해 나가겠습니다.")
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '분석 및 설명자료 생성' 버튼을 눌러주세요.")
