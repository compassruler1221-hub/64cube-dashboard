import streamlit as st
import pandas as pd

# ==========================================
# 0. 페이지 설정 및 규제 맞춤형 경고문
# ==========================================
st.set_page_config(page_title="64큐브 처방 교육·연구 대시보드", layout="wide")

st.warning(
    "**[주의] 본 대시보드는 한의사의 변증, 처방 설명, 안전성 확인, 연구 기록을 돕기 위한 교육·연구 보조 도구입니다.**\n\n"
    "자동 진단 또는 자동 처방 도구가 아니며, 실제 처방은 면허가 있는 의료인의 임상 판단에 따라 결정되어야 합니다."
)

st.title("☯️ 64큐브 변증-처방 네트워크 설명 대시보드")
st.markdown("전통 처방 구조와 현대 생명정보 해석을 병렬로 제시하여 안전성 확인을 시각화합니다.")

# ==========================================
# 1. 꽉 찬 100% 빅데이터 베이스 (기미, 귀경 완벽 복구)
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_id": ["F001", "F002", "F003", "F004"],
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "indication_traditional": ["심비양허, 허번불면", "비위습탁, 복부팽만", "비위기허, 중기하함", "간신음허, 허열도한"],
        "pattern_tags": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복", "승양, 익기, 에너지부스팅", "자음, 보신, 구조물질보충"],
        "caution_summary": ["간 기능 저하 주의, 과도한 진정", "임산부 신중 투여, 기허 환자", "고혈압, 상열감, 급성염증 주의", "소화장애, 설사 환자 주의"]
    })
    
    # 22개 모든 약재의 기미, 귀경 데이터 꽉꽉 채움!
    herbs = pd.DataFrame({
        "formula_id": [
            "F001", "F001", "F001", "F001", 
            "F002", "F002", "F002", "F002",
            "F003", "F003", "F003", "F003", "F003", "F003", "F003", "F003",
            "F004", "F004", "F004", "F004", "F004", "F004"
        ],
        "herb_name": [
            "산조인", "지모", "천궁", "감초", 
            "창출", "후박", "진피", "감초",
            "황기", "인삼", "백출", "감초", "당귀", "진피", "승마", "시호",
            "숙지황", "산수유", "산약", "복령", "목단피", "택사"
        ],
        "role": [
            "군약", "신약", "좌약", "사약", 
            "군약", "신약", "좌약", "사약",
            "군약", "신약", "신약", "사약", "좌약", "좌약", "사약", "사약",
            "군약", "신약", "신약", "좌약", "사약", "사약"
        ],
        "dose_range": [
            "15-20g", "9-12g", "6-9g", "3-6g", 
            "10-15g", "9-12g", "9-12g", "3-6g",
            "15-20g", "9-12g", "9-12g", "3-6g", "6-9g", "3-6g", "3-6g", "3-6g",
            "20-25g", "10-15g", "10-15g", "9-12g", "9-12g", "9-12g"
        ],
        "four_qi": [
            "평", "한", "온", "평", "온", "온", "온", "평",
            "미온", "미온", "온", "평", "온", "온", "미한", "미한",
            "미온", "미온", "평", "평", "미한", "한"
        ],
        "five_flavor": [
            "감, 산", "고, 감", "신", "감", "신, 고", "고, 신", "신, 고", "감",
            "감", "감, 미고", "감, 고", "감", "감, 신", "신, 고", "신, 감", "고, 신",
            "감", "산, 삽", "감", "감, 담", "고, 신", "감, 담"
        ],
        "meridian_entry": [
            "심, 간, 담", "폐, 위, 신", "간, 담, 심포", "심, 폐, 비, 위", "비, 위", "비, 위, 대장", "비, 폐", "심, 폐, 비, 위",
            "비, 폐", "비, 폐, 심", "비, 위", "심, 폐, 비, 위", "심, 간, 비", "비, 폐", "폐, 비, 위", "간, 담",
            "간, 신", "간, 신", "비, 폐, 신", "심, 비, 신", "심, 간, 신", "신, 방광"
        ]
    })
    
    # 표가 비어보이지 않도록 모든 약재의 안전성 데이터를 빠짐없이 기록
    safety = pd.DataFrame({
        "herb_name": [
            "산조인", "지모", "천궁", "감초", "창출", "후박", "진피", 
            "황기", "인삼", "백출", "당귀", "승마", "시호", 
            "숙지황", "산수유", "산약", "복령", "목단피", "택사"
        ],
        "drug_interaction_flag": [
            "수면제, 진정제", "해당없음", "항응고제, 항혈소판제", "이뇨제, 혈압약", "해당없음", "해당없음", "해당없음",
            "면역억제제", "혈당강하제, 혈압약", "해당없음", "항응고제", "해당없음", "해당없음",
            "해당없음", "해당없음", "혈당강하제(시너지)", "이뇨제(시너지)", "항응고제", "이뇨제(시너지)"
        ],
        "pregnancy_flag": [
            "안전", "안전", "주의권고", "안전", "안전", "신중투여", "안전",
            "안전", "안전", "안전", "주의권고", "안전", "안전",
            "안전", "안전", "안전", "안전", "금기추정", "안전"
        ],
        "liver_kidney_flag": [
            "대량사용시 간부담", "특이사항 없음", "특이사항 없음", "장기복용시 신장/혈압 주의", "특이사항 없음", "특이사항 없음", "특이사항 없음",
            "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 간효소 주의",
            "소화기계 부담(위장장애)", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 신장 주의"
        ],
        "evidence_level": [
            "임상확인필요", "일반안전", "문헌보고", "문헌보고", "일반안전", "주의권고", "일반안전",
            "이론적주의", "문헌보고", "일반안전", "전통주의", "일반안전", "임상확인필요",
            "전통주의", "일반안전", "이론적주의", "일반안전", "문헌보고", "임상확인필요"
        ],
        "evidence_note": [
            "과다 복용 시 간효소 수치 상승", "일반적 용량 내 안전", "혈소판 응집 억제 작용", "위알도스테론증 유발 가능", "음허내열 환자 주의", "동물실험 자궁수축", "일반적 용량 내 안전",
            "면역계 자극 가능성", "과량 복용 시 두근거림/혈압상승", "일반적 용량 내 안전", "자궁 수축 및 출혈 경향", "상열감 환자 주의", "특이 체질 간부담",
            "점액질로 인한 소화불량/설사", "일반적 용량 내 안전", "혈당 강하 작용 보조", "이뇨 작용 보조", "혈류 순환 촉진", "신장 배설 부담 가능성"
        ]
    })
    
    # 64큐브 벡터 데이터도 모든 약재를 매핑하여 꽉 차게 출력!
    vectors = pd.DataFrame({
        "herb_name": [
            "산조인", "지모", "천궁", "감초", "창출", "후박", "진피",
            "황기", "인삼", "백출", "당귀", "승마", "시호",
            "숙지황", "산수유", "산약", "복령", "목단피", "택사"
        ],
        "functional_module": [
            "수면조절, 진정", "해열, 점막 보호", "염증 완충, 혈류 순환", "전신 조화, 점막 완충", "위장관 운동, 습탁 제거", "평활근 이완, 기체 해소", "장관 운동 촉진, 기행",
            "대사 경로 활성화", "ATP 생성 촉진", "위장관 대사 촉진", "조혈 작용, 혈류 순환", "상부 면역 활성화", "간 해독 및 스트레스 반응 조절",
            "구조 단백질 합성/보존", "체액 손실 방지", "소화기계 점막 재생", "수분 대사 및 이뇨", "말초 혈관 순환 촉진", "삼투압 조절 및 수분 배출"
        ],
        "q6_vector_type": [
            "보존형 변화", "수렴형 완충", "완충형 변화", "수렴형 조화", "급진 전환형 변화", "완충형 전환", "보존형 변화",
            "비정상 연장형 변화", "급진 전환형 변화", "보존형 강화", "보존형 변화", "상승형 전환", "완충형 변화",
            "보존형 변화", "수렴형 완충", "보존형 완충", "전환형 배출", "완충형 변화", "급진 전환형 배출"
        ],
        "biochemical_interpretation": [
            "극도 긴장을 완화하고 내부 안정 모듈 강화", "열성 편향을 소수성 장벽으로 완충", "과도한 편향을 완충하여 제약 완화", "각기 다른 벡터들의 충돌을 무극성으로 중화", "정체된 상태를 풀고 흐름 회복", "과도한 수축(긴장)을 물리적으로 이완", "기혈 흐름의 완만한 균형 방향 조절",
            "기저 대사량을 끌어올려 에너지 상태 연장", "미토콘드리아 대사 사이클 가속", "소화기 구조의 에너지 흡수율 보존", "혈액 내 유효 물질의 농도 유지", "방어 기전을 상부로 끌어올림", "간 대사 효소계의 과부하 완충",
            "세포 내 물질 손실을 막고 구조적 안정성 확보", "체액 증발을 막는 물리적 장벽 강화", "위장관 점막의 물리적 손상 복구", "세포 간질액의 잉여 수분을 배출 경로로 유도", "미세 혈관의 노폐물 정체를 해소", "신장 여과압을 조절하여 빠른 배출 유도"
        ]
    })
    return formulas, herbs, safety, vectors

df_formulas, df_herbs, df_safety, df_vectors = load_data()

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
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    formula_vectors = df_vectors[df_vectors["herb_name"].isin(formula_herbs["herb_name"])]

    tab1, tab2, tab3, tab4 = st.tabs(["네트워크 패널", "64큐브 벡터 패널", "안전성 경고 패널", "환자 설명 출력"])
    
    # ------------------------------------------
    with tab1:
        st.subheader("📌 2단계: 변증 및 처방 구조 분석")
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})")
        st.markdown("**군신좌사 (君臣佐使) 네트워크 구조**")
        # 기미, 귀경 컬럼이 모두 포함된 꽉 찬 데이터 표출!
        st.dataframe(formula_herbs[["role", "herb_name", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        st.caption("※ 君(중심 target module), 臣(보조 pathway), 佐(과도한 편향 완충), 使(방향 정렬 및 귀경)")
        
    # ------------------------------------------
    with tab2:
        st.subheader("🧬 3단계: 64큐브 생화학 벡터 패널")
        st.success(f"""
        **💡 64큐브 방향성 요약 ({selected_formula_name} 기준)**
        - **주요 방향:** {formula_info['pattern_tags']}
        - **주의 방향:** {formula_info['caution_summary']}
        """)
        
        st.markdown("*64큐브 생화학 벡터는 처방의 효과를 단정하는 것이 아니며, 전통 처방 네트워크의 방향성을 생명정보 언어로 설명하는 보조 지도입니다.*")
        # 모든 약재의 벡터 데이터가 꽉 차게 출력됨!
        for idx, row in formula_vectors.iterrows():
            st.markdown(f"**[{row['herb_name']}] 🎯 표적 기능:** {row['functional_module']}")
            st.markdown(f"- **벡터 유형:** `{row['q6_vector_type']}`")
            st.markdown(f"- **해석:** {row['biochemical_interpretation']}")
            st.divider()

    # ------------------------------------------
    with tab3:
        st.subheader("🚨 4단계: 안전성 확인 필요")
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
        # 표가 텅 비지 않도록 모든 약재의 안전성 정보가 표출됨!
        st.dataframe(formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_level", "evidence_note"]], use_container_width=True, hide_index=True)

    # ------------------------------------------
    with tab4:
        st.subheader("💬 5단계: 환자 설명 출력 패널")
        st.markdown("#### 📝 진료기록용 요약 생성 (Medical Chart)")
        st.code(f"""
- 처방명: {selected_formula_name}
- 환자 주증상: {patient_symp if patient_symp else '미입력'}
- 전통 변증 방향: {formula_info['indication_traditional']}
- 64큐브 방향성: {formula_info['pattern_tags']}
- 안전성 체크: {'관련 주의 및 추가 검토 필요' if safety_alerts else '특이사항 없음'}
        """)
        
        st.markdown("#### 🗣️ 환자 설명문 생성 (환자 배포용)")
        st.info(
            f"이 처방({selected_formula_name})은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, "
            f"여러 약재가 함께 작용하여 몸의 균형 방향을 조절하는 복합 처방입니다.\n\n"
            f"현재 상태를 고려할 때, 이 처방은 급격한 변화를 주지 않고 **{formula_info['pattern_tags']}**의 방향으로 몸을 회복시키도록 설계되었습니다.\n\n"
            f"다만, 복용 중이신 약물이나 기저질환과 관련하여 안전성 확인이 필요할 수 있으므로, "
            f"**복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서** 용량을 조절해 나가겠습니다."
        )
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '분석 및 설명자료 생성' 버튼을 눌러주세요.")
