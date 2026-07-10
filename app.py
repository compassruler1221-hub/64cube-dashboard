import streamlit as st
import pandas as pd

# ==========================================
# 0. 64큐브 매핑 무결성 검산 (Assertion)
# ==========================================
def n_to_codon(n):
    bases = {0: 'G', 1: 'A', 2: 'U', 3: 'C'}
    b1 = n % 4; b2 = (n // 4) % 4; b3 = (n // 16) % 4
    return bases[b1] + bases[b2] + bases[b3]

def codon_to_aa(codon):
    genetic_code = {'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu', 'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu', 'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met', 'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val', 'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser', 'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro', 'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr', 'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala', 'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'Stop', 'UAG': 'Stop', 'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln', 'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys', 'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu', 'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'Stop', 'UGG': 'Trp', 'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg', 'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg', 'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'}
    return genetic_code.get(codon, "Unknown")

assert n_to_codon(0) == "GGG" and codon_to_aa("GGG") == "Gly"
assert n_to_codon(9) == "AUG" and codon_to_aa("AUG") == "Met"
assert n_to_codon(18) == "UGA" and codon_to_aa("UGA") == "Stop"
assert n_to_codon(63) == "CCC" and codon_to_aa("CCC") == "Pro"

# ==========================================
# 1. 데이터베이스 세팅
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_id": ["F001", "F002", "F003", "F004"],
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "indication_traditional": ["심비양허, 허번불면", "비위습탁, 복부팽만", "비위기허, 중기하함", "간신음허, 허열도한"],
        "pattern_tags": ["수렴, 안신, 내부안정", "조습, 행기, 흐름회복", "승양, 익기, 에너지부스팅", "자음, 보신, 구조물질보충"],
        "q6_core_vector": ["보존형 변화 및 수렴형 완충 주도", "급진 전환형 변화 주도", "발산/상승 및 전환형 변화 주도", "보존형 변화 및 수렴형 완충 방향 주도"],
        "trad_interpret": ["혈을 기르고 심을 안정시키며 허열을 수렴하는 방향", "비위의 습탁을 건조하게 하고 기체의 흐름을 회복하는 방향", "아래로 처진 기를 끌어올리고 비위의 운화 및 전신 기력을 회복하는 방향", "소모된 바탕을 보충하고 허열과 수분 정체를 함께 조절하는 삼보삼사 방향"]
    })

    donguibogam = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "db_chapter": ["신형(身形), 몽(夢)", "내경편 비위(脾胃)", "내경편 기(氣), 내상(內傷)", "내경편 신(腎), 소아(小兒)"],
        "db_pattern": ["허번불면(虛煩不眠), 심담허겁(心膽虛怯)", "식적(食積), 담음(痰飮), 비위 불화", "노권상(勞倦傷), 음식상(飮食傷), 기허발열(氣虛發열)", "신수(腎水) 부족, 진음(眞陰) 고갈"],
        "db_interpret": ["과도한 사려로 심비가 상하여 발생하는 수면 장애와 정서 불안을 다스리는 양생적 조절 방향성을 제시합니다.", "비위의 운화 기능이 떨어져 습이 정체된 병증에 대해 덥히고 말려 기기를 소통시키는 병리적 주석을 제공합니다.", "과도한 피로와 섭생 불량으로 중기가 무너져 열이 위로 뜨는 허열을 내리고 맑은 양기를 위로 끌어올리는 승양의 지혜를 담고 있습니다.", "선천적 바탕이 부족하거나 극심한 소모로 정이 고갈된 상태를 채워 체액의 고갈을 막는 근본적인 보음의 원리를 설명합니다."]
    })
    
    clinical = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "clinic_pattern": ["심비양허, 허번불면, 영혈 소모 동반", "비위습탁, 기체, 소화불량 및 복부 팽만", "비위기허, 중기하함, 만성 피로 및 기력 저하", "간신음허, 정혈 부족, 허열, 수분 정체"],
        "clinic_structure": ["- 삼보/삼사: 수렴·안신 약재 중심\n- 해석: 소모된 진액을 보충하고 허열을 진정시키는 수렴형 처방", "- 삼보/삼사: 조습·행기 약재 중심\n- 해석: 정체된 습탁을 제거하고 기운을 돌리는 배출/전환형 처방", "- 삼보/삼사: 보기·승양 약재 중심\n- 해석: 처진 기운을 위로 끌어올리는 발산/상승형 처방", "- 삼보/삼사: 보충축과 배출·완충축의 균형형 처방"],
        "clinic_direction": ["- 보사: 보혈/수렴 중심\n- 승강: 수렴/하행\n- 출입: 저장/안신", "- 보사: 사(瀉)법 위주\n- 승강: 하행/소통\n- 출입: 배출/발산", "- 보사: 보기 위주\n- 승강: 상승/발산\n- 출입: 에너지 확산", "- 보사: 보충+완충 균형\n- 승강: 저장/수렴/하행\n- 출입: 보존/수절"],
        "clinic_caution": ["주간 졸음 주의, 진정제 병용 시 과도한 진정 가능성", "임산부 및 심한 기허 신중, 장기 복용 시 진액 소모", "고혈압·상열감 환자 주의, 혈당 변동성 모니터링", "소화불량·설사 환자 위장 부담, 항응고제/당뇨약/이뇨제 병용 주의"],
        "clinic_followup": ["수면 질, 피로도, 두근거림", "복부 팽만감, 대변 상태, 입마름", "만성 피로 회복도, 식욕, 혈압/혈당", "소화 상태, 부종 변화, 피로감, 혈당/간·신장 검사값"]
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
    
    vectors = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "codon": ["UUU (U-U-U)", "UCU (U-C-U)", "미고정", "UGG (U-G-G)", "CUU (C-U-U)", "CCU (C-C-U)", "CAU (C-A-U)", "AUG (A-U-G)", "CGU (C-G-U)", "AUU (A-U-U)", "ACU (A-C-U)", "미고정", "AGU (A-G-U)", "GUU (G-U-U)", "GCU (G-C-U)", "GAU (G-A-U)", "GGU (G-G-U)", "UGU (U-G-U)", "CAA (C-A-A)"],
        "amino_acid": ["Phe (페닐알라닌)", "Ser (세린)", "미고정", "Trp (트립토판)", "Leu (류신)", "Pro (프롤린)", "His (히스티딘)", "Met (메티오닌)", "Arg (아르기닌)", "Ile (이소류신)", "Thr (트레오닌)", "미고정", "Ser (세린)", "Val (발린)", "Ala (알라닌)", "Asp (아스파르트산)", "Gly (글리신)", "Cys (시스테인)", "Gln (글루타민)"],
        "q6_coord": [0, 16, "미고정", 42, 11, 15, 7, 42, 35, 41, 45, "미고정", 33, 40, 44, 36, 32, 34, 23],
        "q6_axis": ["보존형 변화 (소수성)", "수렴형 완충 (친수성)", "추후 고정 필요", "수렴형 조화", "급진 전환형 변화", "완충형 전환", "보존형 변화", "비정상 연장형 변화", "급진 전환형 변화", "보존형 강화", "보존형 변화", "추후 고정 필요", "완충형 변화", "구조 안정성 / 보존형 변화", "수렴형 완충", "보존형 완충", "전환형 배출", "완충형 변화", "급진 전환형 배출"]
    })

    safety = pd.DataFrame({
        "herb_name": ["산조인", "지모", "천궁", "감초", "창출", "후박", "진피", "황기", "인삼", "백출", "당귀", "승마", "시호", "숙지황", "산수유", "산약", "복령", "목단피", "택사"],
        "drug_interaction_flag": ["수면제, 진정제", "해당없음", "항응고제, 항혈소판제, 아스피린", "이뇨제, 혈압약", "해당없음", "해당없음", "해당없음", "면역억제제", "당뇨약/인슐린, 혈압약", "해당없음", "항응고제, 항혈소판제", "해당없음", "해당없음", "해당없음", "해당없음", "당뇨약/인슐린(시너지)", "이뇨제(시너지)", "항응고제, 항혈소판제", "이뇨제(시너지)"],
        "pregnancy_flag": ["안전", "안전", "주의권고", "안전", "안전", "신중투여", "안전", "안전", "안전", "안전", "주의권고", "안전", "안전", "안전", "안전", "안전", "안전", "금기추정", "안전"],
        "liver_kidney_flag": ["대량사용시 간부담", "특이사항 없음", "특이사항 없음", "장기복용시 신장/혈압 주의", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 간효소 주의", "소화기계 부담(위장장애)", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 신장 주의"],
        "evidence_level": ["임상확인필요", "일반안전", "문헌보고", "문헌보고", "일반안전", "주의권고", "일반안전", "이론적주의", "문헌보고", "일반안전", "전통주의", "일반안전", "임상확인필요", "전통주의", "일반안전", "이론적주의", "일반안전", "문헌보고", "임상확인필요"],
        "evidence_note": ["과다 복용 시 간효소 수치 상승", "일반적 용량 내 안전", "혈소판 응집 억제 작용", "위알도스테론증 유발 가능", "음허내열 환자 주의", "동물실험 자궁수축", "일반적 용량 내 안전", "면역계 자극 가능성 검토", "과량 복용 시 두근거림/혈압상승", "일반적 용량 내 안전", "자궁 수축 및 출혈 경향", "상열감 환자 주의", "특이 체질 간부담", "점액질로 인한 소화불량/설사", "일반적 용량 내 안전", "혈당 변동 가능성 관련 확인", "수분 대사 보조", "혈류 순환 관련 확인", "신장 배설 부담 가능성"]
    })
    
    return formulas, polyhedrons, neijing, donguibogam, clinical, herbs, safety, vectors

df_formulas, df_polyhedrons, df_neijing, df_donguibogam, df_clinical, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 환자 임상 정보 입력")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 소화불량, 황반변성, 디스크")

st.sidebar.subheader("안전성 체크리스트: [복용약]")
med_anti_coag = st.sidebar.checkbox("항응고제/항혈소판제/아스피린/NSAIDs")
med_bp = st.sidebar.checkbox("혈압약")
med_diab = st.sidebar.checkbox("당뇨약/인슐린")
med_diuretic = st.sidebar.checkbox("이뇨제")
med_sedative = st.sidebar.checkbox("수면제/진정제")
med_psych = st.sidebar.checkbox("항우울제/항불안제/정신과 약")
med_immuno = st.sidebar.checkbox("스테로이드/면역억제제")
med_cancer = st.sidebar.checkbox("항암제/표적치료제/호르몬제")
med_antibio = st.sidebar.checkbox("항생제/항바이러스제")
med_suppl = st.sidebar.checkbox("다른 한약·건기식·보충제 병용")

st.sidebar.subheader("안전성 체크리스트: [환자 상태]")
cond_preg = st.sidebar.checkbox("임신/수유 중")
cond_frail = st.sidebar.checkbox("소아/고령자/허약자")
cond_liver = st.sidebar.checkbox("간 기능 저하 또는 간질환 병력")
cond_kidney = st.sidebar.checkbox("신장 기능 저하 또는 신장질환 병력")
cond_cardio = st.sidebar.checkbox("심혈관 질환/부정맥/심부전")
cond_bp_var = st.sidebar.checkbox("고혈압 또는 저혈압 변동")
cond_diab_var = st.sidebar.checkbox("당뇨/저혈당 병력")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사/위장장애")
cond_allergy = st.sidebar.checkbox("알레르기/약물 과민반응 병력")
cond_autoimm = st.sidebar.checkbox("자가면역질환")
cond_cancer = st.sidebar.checkbox("암 치료 중 또는 치료 직후")
cond_surgery = st.sidebar.checkbox("수술/시술/치과치료 예정")
cond_alcohol = st.sidebar.checkbox("음주량 많음")
cond_lab = st.sidebar.checkbox("최근 검사 이상 (간/신장/혈액)")

st.sidebar.subheader("임상 검사값 및 특이사항 입력")
lab_ast_alt = st.sidebar.text_input("AST/ALT:", value="45 / 52 (U/L)")
lab_creatinine = st.sidebar.text_input("Creatinine/eGFR:", value="1.2 mg/dL / 58")
lab_pt_inr = st.sidebar.text_input("PT/INR:", value="1.0 / 1.1")
lab_hba1c = st.sidebar.text_input("공복혈당/HbA1c:", value="126 mg/dL / 6.8%")
lab_bp = st.sidebar.text_input("혈압 (mmHg):", value="145 / 90")
lab_current_meds = st.sidebar.text_area("현재 복용약 상세:", value="아스피린 장용정 100mg\n로사르탄 50mg")
lab_allergy_hist = st.sidebar.text_input("알레르기 상세:", value="특이사항 없음")
lab_surgery_date = st.sidebar.text_input("수술/시술 예정일:", value="2026-08-15 (임플란트 시술)")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 한의학 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("처방 분석 및 리포트 생성", type="primary")

# ==========================================
# 메인 화면: 9단계 모듈 분석
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    poly_info = df_polyhedrons[df_polyhedrons["formula_name"] == selected_formula_name].iloc[0]
    nj_info = df_neijing[df_neijing["formula_name"] == selected_formula_name].iloc[0]
    db_info = df_donguibogam[df_donguibogam["formula_name"] == selected_formula_name].iloc[0]
    clinical_info = df_clinical[df_clinical["formula_name"] == selected_formula_name].iloc[0]
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    merged_herbs_vectors = pd.merge(formula_herbs, df_vectors, on="herb_name", how="left")

    tabs = st.tabs([
        "1. 전통 처방 Core 패널", 
        "2. 동의보감 병렬 해석 패널",
        "3. 한의사용 임상 요약 패널",
        "4. 처방 주변 변화 가능성 패널",
        "5. 보사·승강출입 균형 패널",
        "6. Q6 64큐브 Core 주석 패널",
        "7. 황제내경 병렬 해석 패널",
        "8. 안전성 확인 패널", 
        "9. 환자 설명문 패널"
    ])
    
    # ------------------------------------------
    with tabs[0]: # 전통 처방 Core
        st.subheader("📌 1. 전통 처방 Core 패널")
        if patient_symp:
            st.error(f"**⚠️ [임상 정합도 확인 알림]**\n\n입력된 주증상/현대 진단명(**'{patient_symp}'**)과 선택 처방의 전통 변증 방향(**'{formula_info['indication_traditional']}'**)이 직접 일치하지 않을 수 있습니다. 임상적 판단을 기준으로 최종 검토하십시오.")
            
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']} ({formula_info['pattern_tags']})\n\n**전통 처방 해석:** {formula_info['trad_interpret']}")
        st.markdown("#### 군신좌사(君臣佐使) 네트워크")
        st.dataframe(formula_herbs[["role", "herb_name", "trad_role_desc", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        
    # ------------------------------------------
    with tabs[1]: # 동의보감
        st.subheader("📖 2. 동의보감 병렬 해석 패널")
        st.error("**[해석 주의] 본 패널은 한국 한의학 원전 맥락에서 정리하는 원전 주석층입니다. 현대 유전암호 해석을 대체하는 것이 아니라 전통 한의학적 해석을 보강합니다.**")
        st.markdown(f"- 📜 **동의보감 편제:** `{db_info['db_chapter']}`")
        st.markdown(f"- 🤒 **핵심 적응증 및 병리:** `{db_info['db_pattern']}`")
        st.info(db_info['db_interpret'])

    # ------------------------------------------
    with tabs[2]: # 한의사용 임상 요약
        st.subheader("🧑‍⚕️ 3. 한의사용 임상 요약 패널")
        st.warning("본 패널은 Q6, H(3,4), 다면체 분석 결과를 한의학적 변증·보사 언어로 번역한 설명층입니다.")
        st.subheader("1. 변증 요약")
        st.info(clinical_info['clinic_pattern'])
        st.subheader("2. 처방 구조 요약")
        st.markdown(clinical_info['clinic_structure'])
        st.subheader("3. 보사·승강출입 해석")
        st.markdown(clinical_info['clinic_direction'])
        st.subheader("4. 임상 주의 포인트")
        st.markdown(clinical_info['clinic_caution'])
        st.subheader("5. 추적 관찰 항목")
        st.markdown(clinical_info['clinic_followup'])

    # ------------------------------------------
    with tabs[3]: # 처방 주변 변화 가능성 (구 H34)
        st.subheader("🌐 4. 처방 주변 변화 가능성 패널")
        st.caption("연구자용 구조명: H(3,4) 생물정보 확장층")
        st.warning("본 패널은 처방의 중심 방향에서 벗어날 수 있는 주변 변화 가능성을 한의학적으로 정리한 보조 설명층입니다.")
        st.markdown("""
        ### 한의사용 해석
        H(3,4) Extension은 **처방의 중심 변증 방향 주변에서 어떤 주의점이 생길 수 있는지 보는 확장 지도**입니다.
        - **Q6 Core**: 처방의 중심 변증 방향
        - **H(3,4) Extension**: 중심 방향 주변의 변증 전환 가능성
        - **Diagonal edge**: 기본 방향에서 벗어나는 주변 주의축
        """)
        # 처방별 상세 변화 가능성
        st.info(f"중심 방향: {formula_info['indication_traditional']}")
        # (여기에 각 처방별 로직을 상세화해서 넣으면 됩니다)

    # ------------------------------------------
    with tabs[4]: # 보사·승강출입 균형 (구 다면체)
        st.subheader("💎 5. 보사·승강출입 균형 패널")
        st.caption("연구자용 구조명: 다면체 방향성 시각화")
        st.info("본 패널은 처방의 보사·승강출입·수렴발산·한열허실 방향을 구조적으로 정리한 보조 설명층입니다.")
        st.markdown("""
        ### 한의사용 해석
        다면체 분석은 도형을 보라는 뜻이 아니라, **처방이 어느 방향으로 치우치고, 어느 축에서 균형을 잡는지**를 보는 설명 방식입니다.
        - **보사·승강출입**: 보존·보충·수렴·완충·발산·배출의 기본 방향성
        - **RD 3:3 안정화**: 삼보와 삼사가 서로 균형을 이루는 구조
        """)
        # 상세 다면체 내용 삽입

    # ------------------------------------------
    with tabs[5]: # Q6 Core 주석
        st.subheader("🧬 6. Q6 64큐브 Core 주석 패널")
        st.info("Q6 layer는 처방의 전통적 방향성을 6비트 상태공간의 언어로 주석화한 정보기하학적 해석층입니다.")
        st.success(f"**💡 Q6 64큐브 핵심 변화 방향:** `{formula_info['q6_core_vector']}`")
        # 상세 약재별 코드 삽입...

    # ------------------------------------------
    with tabs[6]: # 황제내경
        st.subheader("📚 7. 황제내경 병렬 해석 패널")
        st.error("**[해석 주의] 원전 개념을 병렬 해석하는 교육·연구 보조 층입니다.**")
        st.markdown(f"- 🏛️ **장부축 매핑:** `{nj_info['zang_fu']}`")
        st.markdown(f"- 🩸 **기혈진액 변증축:** `{nj_info['qi_blood']}`")
        st.markdown(f"- ☯️ **오행 작용 벡터:** `{nj_info['wuxing']}`")
        st.info(nj_info['interpretation'])

    # ------------------------------------------
    with tabs[7]: # 안전성
        st.subheader("🚨 8. 안전성 확인 패널")
        # (안전성 필터 로직 동일)

    # ------------------------------------------
    with tabs[8]: # 환자 설명문
        st.subheader("💬 9. 환자 설명문 패널")
        st.markdown("이 대시보드는 처방 주변에서 나타날 수 있는 반응 가능성과 주의점을 함께 보여줍니다. 이는 약재가 유전자를 조절한다는 뜻이 아니라, 복용 전후 관찰해야 할 항목을 정리한 것입니다.")
        # 환자 설명문 상세 문구 삽입...

else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 리포트 생성' 버튼을 눌러주세요.")
