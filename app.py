import streamlit as st
import pandas as pd

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
assert n_to_codon(9) == "AUG"
assert codon_to_aa(n_to_codon(9)) == "Met"
assert n_to_codon(18) == "UGA"
assert codon_to_aa(n_to_codon(18)) == "Stop"
assert n_to_codon(63) == "CCC"
assert codon_to_aa(n_to_codon(63)) == "Pro"

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
    "본 대시보드는 전통 처방과 동의보감 병증 해석을 중심으로, "
    "환자의 안전성 확인과 치료 방향 정합도를 점검하는 **임상 보조 시스템**입니다."
)

# ==========================================
# 2. 데이터베이스 세팅
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

    donguibogam = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "db_chapter": ["신형(身形), 몽(夢)", "내경편 비위(脾胃)", "내경편 기(氣), 내상(內傷)", "내경편 신(腎), 소아(小兒)"],
        "db_pattern": ["허번불면(虛煩不眠), 심담허겁(心膽虛怯)", "식적(食積), 담음(痰飮), 비위 불화", "노권상(勞倦傷), 음식상(飮食傷), 기허발열(氣虛發열)", "신수(腎水) 부족, 진음(眞陰) 고갈"],
        "db_interpret": [
            "과도한 사려(思慮)로 심비(心脾)가 상하여 발생하는 수면 장애와 정서 불안을 다스리는 양생적 조절 방향성을 제시합니다.",
            "비위의 운화 기능이 떨어져 습(濕)이 정체된 병증에 대해 덥히고 말려 기기를 소통시키는 병리적 주석을 제공합니다.",
            "과도한 피로와 섭생 불량으로 중기가 무너져 열이 위로 뜨는 허열(虛熱)을 내리고 맑은 양기를 위로 끌어올리는 승양(升陽)의 지혜를 담고 있습니다.",
            "선천적 바탕이 부족하거나 극심한 소모로 정(精)이 고갈된 상태를 채워 체액의 고갈을 막는 근본적인 보음(補陰)의 원리를 설명합니다."
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
        "pregnancy_flag": ["일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "주의권고", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "신중투여", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "주의권고", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "일반 용량 내 특이 주의 제한", "금기추정", "일반 용량 내 특이 주의 제한"],
        "liver_kidney_flag": ["대량사용시 간부담", "특이사항 없음", "특이사항 없음", "장기복용시 신장/혈압 주의", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 간효소 주의", "소화기계 부담(위장장애)", "특이사항 없음", "특이사항 없음", "특이사항 없음", "특이사항 없음", "장기 복용시 신장 주의"],
        "evidence_level": ["임상확인필요", "일반안전", "문헌보고", "문헌보고", "일반안전", "주의권고", "일반안전", "이론적주의", "문헌보고", "일반안전", "전통주의", "일반안전", "임상확인필요", "전통주의", "일반안전", "이론적주의", "일반안전", "문헌보고", "임상확인필요"],
        "evidence_note": ["과다 복용 시 간효소 수치 상승", "일반적 용량 내 특이 주의 제한", "혈소판 응집 억제 작용", "위알도스테론증 유발 가능", "음허내열 환자 주의", "동물실험 자궁수축", "일반적 용량 내 특이 주의 제한", "면역계 자극 가능성 검토", "과량 복용 시 두근거림/혈압상승", "일반적 용량 내 특이 주의 제한", "자궁 수축 및 출혈 경향", "상열감 환자 주의", "특이 체질 간부담", "점액질로 인한 소화불량/설사", "일반적 용량 내 특이 주의 제한", "혈당 변동 가능성 관련 확인", "수분 대사 보조", "혈류 순환 관련 확인", "신장 배설 부담 가능성"]
    })
    
    return formulas, donguibogam, herbs, safety, vectors

df_formulas, df_donguibogam, df_herbs, df_safety, df_vectors = load_data()

# ==========================================
# 패널 1: 환자 입력 패널 (Sidebar)
# ==========================================
st.sidebar.header("📝 환자 임상 정보 입력")
patient_symp = st.sidebar.text_input("주증상 및 현대 진단명", placeholder="예: 소화불량, 황반변성, 피로")

st.sidebar.subheader("진맥·설진 및 복진 입력")
mac_pos = st.sidebar.selectbox("맥위 (Pulse Depth)", ["선택 안함", "부(浮)", "중(中)", "침(沈)"])
mac_rate = st.sidebar.selectbox("맥속 (Pulse Rate)", ["선택 안함", "지(遲)", "평(平)", "삭(數)"])
mac_force = st.sidebar.selectbox("맥력 (Pulse Strength)", ["선택 안함", "허(虛)", "실(實)"])
mac_shape = st.sidebar.selectbox("맥형 (Pulse Shape)", ["선택 안함", "현(弦)", "활(滑)", "세(細)", "약(弱)", "긴(緊)", "완(緩)", "대(大)", "결(結)", "대맥(代)"])
tongue_body = st.sidebar.selectbox("설질 (Tongue Body)", ["선택 안함", "담(淡)", "홍(紅)", "암(暗)", "자(紫)", "반점"])
tongue_coat = st.sidebar.selectbox("설태 (Tongue Coating)", ["선택 안함", "박(薄)", "후(厚)", "백(白)", "황(黃)", "니(膩)", "무태(無苔)"])
fluid_status = st.sidebar.selectbox("진액 (Moisture)", ["선택 안함", "건조", "윤택", "치흔", "부종감"])

st.sidebar.subheader("안전성 체크리스트: [복용약]")
med_anti_coag = st.sidebar.checkbox("항응고제/항혈소판제/아스피린/NSAIDs")
med_bp = st.sidebar.checkbox("혈압약")
med_diab = st.sidebar.checkbox("당뇨약/인슐린")
med_diuretic = st.sidebar.checkbox("이뇨제")
med_sedative = st.sidebar.checkbox("수면제/진정제")
med_psych = st.sidebar.checkbox("항우울제/항불안제/정신과 약")
med_immuno = st.sidebar.checkbox("스테로이드/면역억제제")
med_cancer = st.sidebar.checkbox("항암제/표적치료제/호르몬제")

st.sidebar.subheader("안전성 체크리스트: [환자 상태]")
cond_preg = st.sidebar.checkbox("임신/수유 중")
cond_frail = st.sidebar.checkbox("소아/고령자/허약자")
cond_liver = st.sidebar.checkbox("간/신장 기능 저하 또는 질환 병력")
cond_cardio = st.sidebar.checkbox("심혈관 질환/부정맥/심부전")
cond_bp_var = st.sidebar.checkbox("고혈압/저혈압 변동")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사/위장장애")
cond_surgery = st.sidebar.checkbox("수술/시술/치과치료 예정")

st.sidebar.subheader("임상 검사값 및 특이사항 입력")
lab_ast_alt = st.sidebar.text_input("AST/ALT:", value="45 / 52 (U/L)")
lab_creatinine = st.sidebar.text_input("Creatinine/eGFR:", value="1.2 mg/dL / 58")
lab_bp = st.sidebar.text_input("혈압 (mmHg):", value="145 / 90")
lab_current_meds = st.sidebar.text_area("현재 복용약 상세:", value="아스피린 장용정 100mg\n로사르탄 50mg")

st.sidebar.divider()
selected_formula_name = st.sidebar.selectbox("분석할 한의학 처방 선택", df_formulas["formula_name"])
analyze_btn = st.sidebar.button("처방 분석 및 정합도 확인", type="primary")

# ==========================================
# 메인 화면: 12단계 모듈 (한의사 1열 최적화)
# ==========================================
if analyze_btn:
    formula_info = df_formulas[df_formulas["formula_name"] == selected_formula_name].iloc[0]
    db_info = df_donguibogam[df_donguibogam["formula_name"] == selected_formula_name].iloc[0]
    selected_id = formula_info["formula_id"]
    
    formula_herbs = df_herbs[df_herbs["formula_id"] == selected_id]
    formula_safety = df_safety[df_safety["herb_name"].isin(formula_herbs["herb_name"])]
    merged_herbs_vectors = pd.merge(formula_herbs, df_vectors, on="herb_name", how="left")

    tabs = st.tabs([
        "1. 한의사용 통합 요약",
        "2. 전통 처방 Core", 
        "3. 동의보감 병렬 해석",
        "4. 진맥·설진 대조",
        "5. 침구 치료 방향",
        "6. 뜸 치료 방향",
        "7. 처방 주변 변화 가능성", 
        "8. 보사·승강출입 균형", 
        "9. Q6 64큐브 주석", 
        "10. 황제내경 해석",
        "11. 안전성 세부 확인", 
        "12. 환자 설명문"
    ])
    
    # ------------------------------------------
    with tabs[0]:
        st.subheader(f"🧑‍⚕️ 1. [{selected_formula_name}] 한의사용 통합 요약 패널")
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']}\n\n**해석:** {formula_info['trad_interpret']}")
        
        # [NEW] 처방 정합도 점검표 동적 생성
        matches, cautions, followups = [], [], []
        if cond_surgery: cautions.append("수술 예정 → 출혈 관련 약재 및 복용 중단 여부 전문가 판단 필요")

        if selected_formula_name == "보중익기탕":
            matches.append("피로, 기허, 식욕저하 등 보기(補氣) 방향과 정합 가능성")
            if mac_force == "허(虛)" or mac_shape in ["약(弱)", "완(緩)"]: matches.append("맥상(허/약/완) → 보기 방향과 정합")
            if tongue_body == "담(淡)" or fluid_status == "치흔": matches.append("설상(담/치흔) → 기허 방향과 정합")
            
            if med_bp or cond_bp_var: cautions.append("혈압 변동/혈압약 복용 → 승양(상승) 방향 과잉 반응(두근거림 등) 확인")
            if med_diab: cautions.append("당뇨약 복용 → 인삼, 감초 관련 혈당 변화 확인")
            if cond_cardio: cautions.append("심혈관/부정맥 → 심계 반응 확인")
            if cond_dig: cautions.append("만성 소화불량 → 습담·식적 뚜렷할 경우 처방 방향 재검토")
            followups = ["혈압", "두근거림", "불면", "혈당", "소화상태", "피로감", "상열감"]

        elif selected_formula_name == "육미지황환":
            matches.append("피로, 소모성 상태, 간신음허·정혈 부족 방향과 정합 가능성")
            if mac_force == "허(虛)" or mac_pos == "침(沈)" or mac_shape == "세(細)": matches.append("맥상(침/세/허) → 자음보신 방향과 정합")
            
            if cond_dig: cautions.append("만성 소화불량/설사 → 숙지황으로 인한 위장 부담(점액질) 확인 필요")
            if med_anti_coag: cautions.append("항응고제 복용 → 목단피 관련 출혈 경향 확인 필요")
            if med_diab: cautions.append("당뇨약 복용 → 산약 등 관련 혈당 변화 확인")
            followups = ["소화불량/설사 발생 여부", "부종 변화", "열감·도한 변화", "피로감 변화", "혈당 변화", "간/신장 검사수치 (장기 복용 시)"]
            
        elif selected_formula_name == "산조인탕":
            matches.append("불면, 불안, 심계 등 허번불면 방향과 정합 가능성")
            if mac_shape in ["현(弦)", "세(細)"]: matches.append("맥상(현/세) → 간혈 부족 방향과 정합")
            
            if med_sedative or med_psych: cautions.append("수면제/항우울제 복용 → 과도한 진정 작용 및 주간 졸림 확인")
            if cond_dig: cautions.append("소화불량/설사 → 위장 부담 확인")
            if med_anti_coag: cautions.append("항응고제 복용 → 천궁 등 활혈 약재 관련 확인")
            followups = ["수면의 질 및 시간", "주간 무기력/졸음 여부", "두근거림/불안감 변화", "소화 상태"]

        elif selected_formula_name == "평위산":
            matches.append("소화불량, 식적, 가스 팽만 등 비위습탁 방향과 정합 가능성")
            if tongue_coat in ["후(厚)", "니(膩)", "백(白)"]: matches.append("설태(후/니/백) → 습탁 방향과 정합")
            
            if cond_preg: cautions.append("임신/수유 중 → 신중투여 요망 (자궁수축 주의)")
            if fluid_status == "건조" or tongue_coat == "무태(無苔)": cautions.append("진액 고갈/음허 양상 → 조습(燥濕) 작용으로 인한 진액 손상 우려")
            followups = ["복부 팽만감 감소 여부", "가스/대변 상태", "소화력 회복 여부", "입마름 발생 여부"]

        st.markdown("### 🚨 처방 정합도 점검표")
        
        st.markdown("#### ✅ 정합 (입력된 환자 정보와 맞는 부분)")
        for m in (matches if matches else ["입력된 정보로 판별된 뚜렷한 정합 포인트 없음"]): st.success(f"- {m}")
        
        st.markdown("#### ⚠️ 주의 (입력된 환자 정보와 어긋나거나 확인이 필요한 부분)")
        for c in (cautions if cautions else ["특이 주의사항 없음"]): st.warning(f"- {c}")
            
        st.markdown("#### 🔍 추적 관찰 (복용 후 추적해야 할 항목)")
        st.info("- " + "\n- ".join(followups))
        
        st.divider()
        st.markdown("#### 🧭 침구·뜸 방향 요약")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**침 치료 방향**")
            if selected_formula_name == "보중익기탕": st.markdown("- 비위기허 및 중기하함 보강\n- 보기·승양 방향 검토")
            elif selected_formula_name == "육미지황환": st.markdown("- 간신음허 보강 및 허열 완충\n- 보법 또는 평보평사 검토")
            else: st.markdown("- 변증에 따른 평보평사 위주")
        with col2:
            st.markdown("**뜸 치료 방향**")
            if selected_formula_name == "보중익기탕": st.markdown("- 기허 뚜렷 시 온보 검토\n- 고혈압/상열감 환자 온열 자극 주의")
            elif selected_formula_name == "육미지황환": st.markdown("- 하복부 냉감 시 검토\n- 허열/도한/당뇨성 감각저하 시 강한 온열 주의")
            else: st.markdown("- 냉증 동반 시 검토\n- 실열 양상 시 주의")

    # ------------------------------------------
    with tabs[1]:
        st.subheader("📌 2. 전통 처방 Core 패널")
        st.info(f"**전통 변증 방향:** {formula_info['indication_traditional']}\n\n**전통 처방 해석:** {formula_info['trad_interpret']}")
        st.markdown("#### 군신좌사(君臣佐使) 네트워크")
        st.dataframe(formula_herbs[["role", "herb_name", "trad_role_desc", "dose_range", "four_qi", "five_flavor", "meridian_entry"]], use_container_width=True, hide_index=True)
        
    # ------------------------------------------
    with tabs[2]:
        st.subheader("📖 3. 동의보감 병렬 해석 패널")
        st.error("**[해석 주의] 이 패널은 처방의 병증 이해와 양생론을 한국 한의학 원전 맥락에서 정리하는 층입니다.**")
        st.markdown(f"#### 1. {selected_formula_name} 문헌적 병증 해석")
        st.markdown(f"- 📜 **동의보감 편제:** `{db_info['db_chapter']}`")
        st.markdown(f"- 🤒 **핵심 적응증 및 병리:** `{db_info['db_pattern']}`")
        st.markdown("#### 2. 양생(養生) 및 병리 조절 방향성")
        st.info(db_info['db_interpret'])

    # ------------------------------------------
    with tabs[3]:
        st.subheader("📊 4. 진맥·설진 대조 패널")
        st.info("진맥·설진 정보는 대시보드가 자동 판정하는 값이 아니라, 한의사가 직접 확인한 소견을 입력하여 선택 처방의 변증 방향과 정합성을 대조하기 위한 참고 정보입니다.")
        
        st.markdown(f"**입력된 환자 소견:** 맥[{mac_pos}, {mac_rate}, {mac_force}, {mac_shape}] | 설[{tongue_body}, {tongue_coat}, {fluid_status}]")
        
        if selected_formula_name == "육미지황환":
            st.success("**[정합 소견]**\n- 맥: 침(沈), 세(細), 삭(數), 약(弱) 경향\n- 설: 홍(紅) 또는 담홍(淡紅), 소태(少苔) 경향\n- 증상: 도한, 오심번열, 요슬산연")
            st.warning("**[주의 소견]**\n- 설태가 후니(厚膩)함 (식체·습담)\n- 복부 냉감 및 잦은 설사 (위장 허약)")
            st.error("**[재검토 요망 소견]**\n- 실열·습열 소견이 뚜렷함\n- 맥이 실·활·삭하고 열상이 강함")
        elif selected_formula_name == "보중익기탕":
            st.success("**[정합 소견]**\n- 맥: 허(虛), 약(弱), 완(緩) 경향\n- 설: 담(淡), 치흔(齒痕), 백태 경향\n- 증상: 기단, 식욕저하, 내장하수감")
            st.warning("**[주의 소견]**\n- 상열감, 고혈압, 심계, 불면")
            st.error("**[재검토 요망 소견]**\n- 실열, 습열, 뚜렷한 식적이나 담음")
        elif selected_formula_name == "산조인탕":
            st.success("**[정합 소견]**\n- 맥: 세(細), 약(弱), 현세(弦細) 경향\n- 설: 담홍 또는 홍, 소태\n- 증상: 허번불면, 심계, 피로")
            st.warning("**[주의 소견]**\n- 주간 졸림, 진정제 병용, 간·신장 기능 저하")
            st.error("**[재검토 요망 소견]**\n- 실열성 불면, 담열이 뚜렷한 불면")
        else:
            st.markdown("- 선택 처방에 대한 일반 변증 정합성 대조 필요")

    # ------------------------------------------
    with tabs[4]:
        st.subheader("📍 5. 침구 치료 방향 패널 (Acupuncture)")
        st.info("본 패널은 침 치료를 자동으로 처방하는 기능이 아니라, 선택 처방의 변증 방향에 따라 한의사가 검토할 수 있는 치료 원칙과 주의점을 정리하는 보조 설명층입니다.")
        
        if selected_formula_name == "육미지황환":
            st.markdown("""
            **[침 치료 방향]**
            - 간·신 축 보강 및 정혈·진액 부족 방향 확인
            - 보법 또는 평보평사 중심 검토
            - 허열이 동반되면 강자극 주의
            - 수습 정체가 있으면 이수·건비 방향 병행 검토

            **[검토 가능한 혈위군]**
            - 신·간·비 경락축
            - 자음·보신 축 / 허열 완충 축
            
            **[주의]** 실열, 습열, 식체가 뚜렷하면 단순 보법 중심으로 가면 안 됩니다.
            """)
        elif selected_formula_name == "보중익기탕":
            st.markdown("""
            **[침 치료 방향]**
            - 비위기허·중기하함 확인 및 보기·승양 방향
            - 평보평사 또는 보법 중심 검토
            - 상열감, 고혈압, 심계, 불면이 있으면 승양 과잉 반응 확인

            **[검토 가능한 혈위군]**
            - 비·위 경락축
            - 중기 보강 축 / 승양 축
            """)

    # ------------------------------------------
    with tabs[5]:
        st.subheader("🔥 6. 뜸 치료 방향 패널 (Moxibustion)")
        st.warning("**[주의]** 뜸 치료는 화상, 알레르기, 피부 감염 등의 이상 반응 위험이 있으므로 뜸 가능성 검토와 주의조건(당뇨성 말초신경병증 등) 확인이 필수입니다.")
        
        if selected_formula_name == "육미지황환":
            st.markdown("""
            **육미지황환은 자음·허열 완충 방향이므로, 무조건 온열 자극을 강하게 주는 뜸 방향으로 해석하면 안 됩니다.**
            
            **🟢 뜸 검토 가능:** 하복부 냉감, 허한 동반, 소화력 저하와 양허가 함께 있을 때
            
            **🔴 뜸 주의/재검토:** 
            - 오심번열, 도한, 구건, 실열 양상
            - 당뇨성 말초신경병증, 피부 감각 저하
            - 피부질환, 상처, 화상 위험군
            """)
        elif selected_formula_name == "보중익기탕":
            st.markdown("""
            **🟢 뜸 검토 가능:** 비위허한, 복부 냉감, 기허 피로, 중기하함
            
            **🔴 뜸 주의/재검토:** 상열감, 고혈압, 심계, 불면, 안면홍조 등 상승 기운이 이미 뚜렷한 경우
            """)

    # ------------------------------------------
    with tabs[6]:
        st.subheader("🌐 7. 처방 주변 변화 가능성 패널")
        st.caption("연구자용 구조명: H(3,4) Extension")

        st.warning("이 패널은 처방의 중심 방향에서 벗어날 수 있는 주변 변화 가능성을 한의학적으로 정리한 보조 지도입니다. 약재가 실제 유전암호를 조절한다는 뜻이 아닙니다.")

        st.markdown("""
        ### 🔑 한의사용 해석
        H(3,4) Extension은 **처방의 중심 변증 방향 주변에서 환자 체질, 병증, 복용약에 따라 어느 쪽으로 해석이 흔들릴 수 있는지(변증 전환 가능성) 보는 확장 지도**입니다.
        """)

        if selected_formula_name == "보중익기탕":
            st.info("중심 방향: 비위기허, 중기하함, 보기, 승양")
            st.markdown("""
            #### 1. 승양 과잉 방향
            - 상열감, 두근거림, 불면, 안면홍조, 혈압 상승 경향 확인
            - 고혈압 또는 심계가 있는 환자는 반응 관찰 필요
            #### 2. 보익 과잉 방향
            - 식체, 더부룩함, 복부 팽만, 소화불량 확인
            #### 3. 약물 병용 주의 방향
            - 감초: 이뇨제·혈압약 병용 확인
            - 당귀: 항응고제 병용 확인
            - 인삼: 혈당 변화 관찰
            """)
        elif selected_formula_name == "육미지황환":
            st.info("중심 방향: 간신음허, 정혈 부족, 허열, 자음, 보신")
            st.markdown("""
            #### 1. 보음·보신 부담 방향
            - 소화불량, 더부룩함, 설사 경향 확인 (숙지황 부담)
            #### 2. 수습 조절 방향
            - 부종, 소변 상태, 몸이 무거운 느낌 확인
            #### 3. 약물 병용 주의 방향
            - 목단피: 항응고제 병용 확인
            - 당뇨약 복용 시 혈당 변화 및 간·신장 기능 확인
            """)

    # ------------------------------------------
    with tabs[7]:
        st.subheader("💎 8. 보사·승강출입 균형 패널")
        st.caption("연구자용 구조명: 다면체 방향성 시각화")

        st.info("본 패널은 처방 효과를 증명하는 도구가 아니라, 처방의 보사·승강출입·수렴발산·한열허실 방향을 구조적으로 정리한 보조 설명층입니다.")

        st.markdown("""
        ### 🔑 한의사용 해석
        다면체 분석은 도형 자체를 보라는 뜻이 아니라, **처방이 보충 중심인지, 배출 중심인지, 수렴·완충 중심인지 확인하는 균형 지도**입니다.
        - **정팔면체 Octahedron** → 6대 기본 방향성 (보존·보충·수렴·완충·발산·배출)
        - **마름모십이면체 RD** → 삼보삼사 등 보충-배출 축의 대칭 균형
        """)

        if selected_formula_name == "육미지황환":
            st.success("핵심 해석: 삼보와 삼사가 함께 배치된 보충-배출 균형형 처방")
            st.markdown("""
            #### 1. 보사 균형 (RD 3:3 대칭)
            - **보충축:** 숙지황·산수유·산약
            - **배출·완충축:** 복령·택사·목단피
            - 해석: 보음만 강조되는 처방이 아니라, 수습 조절과 허열 완충이 함께 배치됨
            #### 2. 승강출입
            - 저장·수렴·보존 방향이 강하며, 급격한 발산이나 공하 방향은 낮음
            #### 3. 한열허실
            - 허증 중심, 허열 완충 방향. (수습 정체가 동반되는지 병행 확인)
            """)

    # ------------------------------------------
    with tabs[8]:
        st.subheader("🧬 9. Q6 64큐브 Core 주석 패널")
        st.info("Q6 layer는 처방의 전통적 방향성을 6비트 상태공간의 기하학적 언어로 주석화(Annotation)하는 연구자용 해석층입니다.")
        st.success(f"**💡 Q6 64큐브 핵심 변화 방향:** `{formula_info['q6_core_vector']}`")
        for idx, row in merged_herbs_vectors.iterrows():
            st.markdown(f"**[{row['herb_name']}]** 전통 역할: {row['role']} | Q6 축: {row['q6_axis']}")

    # ------------------------------------------
    with tabs[9]:
        st.subheader("📚 10. 황제내경 병렬 해석 패널")
        st.error("**[해석 주의] 전통 생명론의 핵심 개념을 정보기하학 언어로 병렬 해석하는 연구 보조 층입니다.**")
        st.markdown(f"- **장부축 매핑:** `{nj_info['zang_fu']}`\n- **기혈진액 변증축:** `{nj_info['qi_blood']}`\n- **오행 작용 벡터:** `{nj_info['wuxing']}`")

    # ------------------------------------------
    with tabs[10]:
        st.subheader("🚨 11. 안전성 확인 패널 (Safety Filter)")
        st.markdown("**약재별 상세 안전성 데이터**")
        display_safety = formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_note"]].copy()
        display_safety.columns = ["약재명", "약물 병용 주의", "임신·수유 관련", "간·신장 관련", "주의 근거/확인 사항"]
        st.dataframe(display_safety, use_container_width=True, hide_index=True)

    # ------------------------------------------
    with tabs[11]:
        st.subheader("💬 12. 환자 설명문 패널")
        patient_html = f"""
        <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
            <b>{selected_formula_name}</b>은 몸의 부족한 기운을 보충하고, 전반적인 신체 상태를 함께 살피는 방향의 처방입니다.<br><br>
            이 대시보드는 처방 주변에서 나타날 수 있는 반응 가능성과 주의점을 함께 보여줍니다. 복용 전후에는 소화 상태, 피로감, 혈압, 혈당, 두근거림, 수면 변화 같은 항목을 확인해야 합니다.<br><br>
            복용 중 특이 반응이 나타나면 담당 한의사의 진료 과정에서 세밀하게 조절해야 합니다.
        </div>
        """
        st.markdown(patient_html, unsafe_allow_html=True)
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 정합도 확인' 버튼을 눌러주세요.")
