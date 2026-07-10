import streamlit as st
import pandas as pd

# ==========================================
# 1. 페이지 설정 및 방어 가이드라인
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
    st.caption("Formula_Vector = Traditional_Core + Donguibogam_Layer + Q6_Core + H(3,4)_Extension + Polyhedron_Layer + Safety_Filter")

st.markdown(
    "전통 처방 구조와 동의보감 병증 해석을 **중심 설명층**으로 두고, "
    "Q6·H(3,4)·다면체 구조는 이를 보조적으로 주석화하는 해석층으로 사용합니다."
)

# ==========================================
# 2. 데이터베이스 세팅 (12개 처방 꽉 채움)
# ==========================================
@st.cache_data
def load_data():
    formulas = pd.DataFrame({
        "formula_name": [
            "육미지황환", "보중익기탕", "산조인탕", "평위산", 
            "귀비탕", "십전대보탕", "팔진탕", "사물탕", 
            "사군자탕", "소요산", "이진탕", "오령산"
        ],
        "indication_traditional": [
            "간신음허, 허열도한", "비위기허, 중기하함", "심비양허, 허번불면", "비위습탁, 복부팽만",
            "심비양허, 기혈양허, 불면", "기혈양허, 극심한 허로", "기혈양허, 만성피로", "영혈부족, 혈허",
            "비위기허, 기단무력", "간울비허, 흉협고만", "습담정체, 오심구토", "방광기화불리, 수습정체"
        ],
        "pattern_tags": [
            "자음, 보신, 구조물질보충", "승양, 익기, 에너지부스팅", "수렴, 안신, 내부안정", "조습, 행기, 흐름회복",
            "보기, 보혈, 안신", "대보원기, 온양", "기혈쌍보", "보혈, 화혈",
            "익기, 건비", "소간, 해울, 건비", "조습, 화담", "이수, 삼습, 온양"
        ],
        "level": [3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1] # 3: 풀데이터, 1: 기본데이터
    })

    clinical = pd.DataFrame({
        "formula_name": formulas["formula_name"],
        "clinic_pattern": formulas["indication_traditional"],
        "clinic_structure": [
            "- **삼보:** 숙지황·산수유·산약\n- **삼사:** 복령·택사·목단피\n- **핵심 해석:** 보충축과 배출·완충축이 함께 배치된 삼보삼사 균형형 처방",
            "- 승양·보기: 황기, 승마, 시호\n- 건비·익기: 인삼, 백출\n- 핵심 해석: 아래로 처진 기운을 위로 끌어올리는 상승형 처방",
            "- 수렴·안신: 산조인\n- 자음·청열: 지모\n- 핵심 해석: 소모된 진액을 보충하고 허열을 진정시키는 수렴형 처방",
            "- 조습·건비: 창출\n- 행기·제만: 후박\n- 핵심 해석: 정체된 습탁을 제거하고 기운을 돌리는 배출/전환형 처방",
            "보기(사군자탕 류) + 안신(용안육, 산조인) 구조. 심과 비를 동시에 보함",
            "기혈쌍보(팔진탕) + 온양(황기, 육계) 구조. 강력한 온보 처방",
            "사군자탕 + 사물탕. 기와 혈을 동시에 보충",
            "당귀, 천궁, 백작약, 숙지황. 보혈 및 혈액순환의 기본 처방",
            "인삼, 백출, 복령, 감초. 비위 기운 보충의 기본 처방",
            "시호(소간) + 당귀/백작약(보혈) + 백출/복령(건비). 스트레스성 소화불량 조절",
            "반하, 진피, 복령, 감초. 조습화담의 기본 처방",
            "택사, 복령, 저령, 백출, 육계. 수분 대사 촉진 및 배출"
        ],
        "clinic_direction": [
            "- **보사:** 보충 중심이나, 수습 조절과 허열 완충 배치\n- **승강:** 수렴·하행 안정 우세\n- **한열:** 허열 완충\n- **허실:** 허증 중심 (수습 정체 확인 요망)",
            "- **보사:** 기혈 보충 중심\n- **승강:** 강력한 상승(승양) 우세\n- **한열:** 기허 허열 조절\n- **허실:** 기허, 중기하함",
            "- 보사: 영혈 보충 중심\n- 승강: 수렴 하행 우세\n- 한열: 청열 완충\n- 허실: 음혈 허증",
            "- 보사: 사(瀉)법 위주\n- 승강: 하강 및 소통 우세\n- 한열: 조습을 통한 냉습 제어\n- 허실: 위장관 실증(습탁)",
            "- 보사: 보기·보혈 동시 진행\n- 승강: 중심을 채우고 심(心)으로 안정화",
            "- 보사: 강력한 보(補)법 위주\n- 승강: 기혈을 전신으로 순환시키고 데움",
            "- 보사: 기혈 쌍보 중심\n- 승강: 전신 기혈 순환 보조",
            "- 보사: 보혈 중심\n- 출입: 혈맥 소통 및 영양 공급",
            "- 보사: 보기 중심\n- 승강: 중기(中氣) 안정화",
            "- 보사: 소간(사)과 건비(보)의 조화\n- 승강: 간기 울결을 풀고 비위 하강 보조",
            "- 보사: 사(瀉)법(화담) 위주\n- 승강: 위기 하강으로 오심 진정",
            "- 보사: 사(瀉)법(이수) 위주\n- 승강: 수분 하강 및 배출"
        ],
        "clinic_caution": [
            "- 소화불량·설사 환자는 숙지황 위장 부담 확인\n- 당뇨약/이뇨제/항응고제 복용 환자 모니터링",
            "- 고혈압, 상열감, 급성 염증 환자 주의\n- 혈당 변동성 모니터링",
            "- 주간 졸음, 진정제 병용 시 과도한 진정 확인",
            "- 임산부, 심한 기허 환자, 음허 환자 주의",
            "- 점액질 약재로 인한 소화 부담 확인",
            "- 실열(實熱) 환자, 염증기 환자 절대 주의 (온열지제 부담)",
            "- 소화 장애 및 상열감 발생 여부 확인",
            "- 소화불량 환자 숙지황/당귀 주의",
            "- 건조함이 심한 환자 주의",
            "- 기허가 극심한 환자는 시호 성분 주의",
            "- 진액이 고갈된 음허(陰虛) 환자, 마른기침 환자 주의",
            "- 탈수, 음허 환자 주의"
        ],
        "clinic_followup": [
            "- 소화 상태, 설사 여부, 부종, 피로감, 열감, 혈당",
            "- 혈압/혈당 변동, 두근거림, 상열감, 소화 상태",
            "- 수면 질, 주간 피로도, 소화 상태",
            "- 복부 팽만감, 소화력, 갈증 상태",
            "- 식욕, 수면 시간, 정서적 불안도",
            "- 체력 회복, 상열감 발생 여부",
            "- 전반적 피로도, 안색, 소화 상태",
            "- 어지럼증, 생리 상태, 소화력",
            "- 피로감, 식욕, 대변 상태",
            "- 스트레스 반응, 가슴 답답함, 소화 상태",
            "- 오심/구토 호전 여부, 입마름 발생",
            "- 소변량, 부종 증감, 갈증 여부"
        ]
    })
    
    # 처방 감별 비교표용 데이터
    diff_df = pd.DataFrame([
        {"처방": "육미지황환", "중심 변증": "간신음허·허열", "강한 방향": "자음·보신·수렴", "주의 환자": "소화불량, 설사, 항응고제"},
        {"처방": "보중익기탕", "중심 변증": "비위기허·중기하함", "강한 방향": "보기·승양", "주의 환자": "고혈압, 불면, 심계"},
        {"처방": "귀비탕", "중심 변증": "심비양허·불면·건망", "강한 방향": "보기·보혈·안신", "주의 환자": "소화 부담, 주간 졸림"},
        {"처방": "십전대보탕", "중심 변증": "기혈양허·극심한 허로", "강한 방향": "대보원기·온양", "주의 환자": "열감, 고혈압, 실열증"},
        {"처방": "평위산", "중심 변증": "습체·비위불화", "강한 방향": "조습·화위", "주의 환자": "건조·음허 환자 주의"},
        {"처방": "소요산", "중심 변증": "간울비허·스트레스", "강한 방향": "소간·해울·건비", "주의 환자": "극심한 기허 환자"},
        {"처방": "이진탕", "중심 변증": "담음 정체·오심", "강한 방향": "조습·화담", "주의 환자": "진액 고갈 환자 주의"},
    ])

    return formulas, clinical, diff_df

formulas_df, clinical_df, diff_df = load_data()

# ==========================================
# 패널 1: 사이드바 - 초정밀 임상/안전성 입력칸 (부활!)
# ==========================================
st.sidebar.header("📝 환자 임상 정보 입력")
patient_symp = st.sidebar.text_input("주증상 및 진단명", placeholder="예: 소화불량, 만성피로, 황반변성")

# [NEW] 진맥/설진/복진 상세 입력 (정합도 판정에 사용됨)
st.sidebar.subheader("🤚 진맥·설진·복진 소견")
col_m1, col_m2 = st.sidebar.columns(2)
with col_m1:
    mac_depth = st.selectbox("맥위(Depth)", ["선택안함", "부(浮)맥", "중(中)맥", "침(沈)맥"])
    mac_speed = st.selectbox("맥속(Speed)", ["선택안함", "지(遲)맥", "평(平)맥", "삭(數)맥"])
    mac_force = st.selectbox("맥력(Force)", ["선택안함", "허(虛)맥", "실(實)맥", "약(弱)맥"])
with col_m2:
    mac_shape = st.selectbox("맥형(Shape)", ["선택안함", "현(弦)", "활(滑)", "세(細)", "긴(緊)", "완(緩)", "대(大)"])
    tongue_color = st.selectbox("설질(Color)", ["선택안함", "담(淡)", "홍(紅)", "암(暗)", "자(紫)", "반점"])
    tongue_coat = st.selectbox("설태(Coat)", ["선택안함", "박태(薄)", "후태(厚)", "백태(白)", "황니태(黃膩)", "소태/무태"])

col_t1, col_t2 = st.sidebar.columns(2)
with col_t1:
    tongue_fluid = st.selectbox("진액/형태", ["선택안함", "건조(乾燥)", "윤택(潤澤)", "치흔(齒痕)", "부종감"])
with col_t2:
    abd_exam = st.selectbox("복진(Abd)", ["선택안함", "복부 냉감", "압통/저항", "더부룩함/가스", "복직근 긴장"])

st.sidebar.subheader("🚨 안전성 체크리스트: [복용약]")
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

st.sidebar.subheader("🚨 안전성 체크리스트: [환자 상태]")
cond_preg = st.sidebar.checkbox("임신/수유 중")
cond_frail = st.sidebar.checkbox("소아/고령자/허약자")
cond_liver = st.sidebar.checkbox("간 기능 저하 또는 간질환 병력")
cond_kidney = st.sidebar.checkbox("신장 기능 저하 또는 신장질환 병력")
cond_bp_high = st.sidebar.checkbox("고혈압/상열감/심계")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사/위장장애")
cond_allergy = st.sidebar.checkbox("알레르기/약물 과민반응 병력")
cond_autoimm = st.sidebar.checkbox("자가면역질환")
cond_cancer = st.sidebar.checkbox("암 치료 중 또는 치료 직후")
cond_surgery = st.sidebar.checkbox("수술/시술/치과치료 예정")
cond_alcohol = st.sidebar.checkbox("음주량 많음")
cond_lab = st.sidebar.checkbox("최근 검사 이상 (간/신장/혈액)")

st.sidebar.subheader("🧪 임상 검사값 및 특이사항 입력")
lab_ast_alt = st.sidebar.text_input("AST/ALT:", value="45 / 52 (U/L)")
lab_creatinine = st.sidebar.text_input("Creatinine/eGFR:", value="1.2 mg/dL / 58")
lab_pt_inr = st.sidebar.text_input("PT/INR:", value="1.0 / 1.1")
lab_hba1c = st.sidebar.text_input("공복혈당/HbA1c:", value="126 mg/dL / 6.8%")
lab_bp = st.sidebar.text_input("혈압 (mmHg):", value="145 / 90")
lab_current_meds = st.sidebar.text_area("현재 복용약 상세:", value="아스피린 장용정 100mg\n로사르탄 50mg")
lab_allergy_hist = st.sidebar.text_input("알레르기 상세:", value="특이사항 없음")
lab_surgery_date = st.sidebar.text_input("수술/시술 예정일:", value="2026-08-15 (임플란트 시술)")

st.sidebar.divider()
selected_formula = st.sidebar.selectbox("분석할 한의학 처방 선택 (12종)", formulas_df["formula_name"])
analyze_btn = st.sidebar.button("처방 분석 및 리포트 생성", type="primary")

# ==========================================
# 메인 화면: 12단계 탭 구조
# ==========================================
if analyze_btn:
    f_info = formulas_df[formulas_df["formula_name"] == selected_formula].iloc[0]
    c_info = clinical_df[clinical_df["formula_name"] == selected_formula].iloc[0]
    is_level_3 = f_info["level"] == 3

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
        "10. 황제내경 병렬 해석",
        "11. 안전성 확인", 
        "12. 환자 설명문"
    ])
    
    # ------------------------------------------
    # 탭 1: 한의사용 1페이지 통합 요약 (가장 중요)
    # ------------------------------------------
    with tabs[0]:
        st.header(f"🧑‍⚕️ [{selected_formula}] 한의사용 임상 통합 요약")
        
        # 1. 처방 정합도 점검표 (동적 로직)
        st.subheader("✅ 환자 상태 ↔ 처방 정합도 점검")
        matches, cautions, trackers = [], [], ["소화 상태 및 대소변", "전반적인 피로도 변화"]
        
        # 증상 매칭
        if patient_symp:
            matches.append(f"입력 증상('{patient_symp}') ↔ 처방 방향({f_info['pattern_tags']}) 일치 여부 임상적 검토 완료 필요")
        
        # 맥/설 매칭 로직 (예시)
        if selected_formula in ["육미지황환", "산조인탕"]:
            if mac_force in ["허(虛)맥", "약(弱)맥"]: matches.append("맥상(허/약) ↔ 보음/보혈 방향 정합")
            if tongue_coat == "황니태(黃膩)": cautions.append("설태 황니(습열/식적) ↔ 자음제(숙지황 등) 위장 부담 우려 (재검토 요망)")
        elif selected_formula in ["보중익기탕", "사군자탕"]:
            if mac_force in ["허(虛)맥", "약(弱)맥"]: matches.append("맥상(허/약) ↔ 보기/승양 방향 정합")
            if cond_bp_high: cautions.append("고혈압/상열감 ↔ 승양(升陽) 방향 과잉 반응 우려 (주의)")
        elif selected_formula in ["평위산", "이진탕"]:
            if tongue_coat == "황니태(黃膩)": matches.append("설태 황니 ↔ 조습/화담 방향 정합")
            if tongue_color == "홍(紅)" and tongue_coat == "소태/무태": cautions.append("음허(홍설/무태) 환자에게 조습제 사용 시 진액 고갈 우려")
            
        # 안전성 매칭 로직
        if cond_dig: cautions.append("만성 소화불량 ↔ 보약 계열 처방 시 점액질 성분 위장 부담 주의")
        if med_anti_coag: cautions.append("항응고제 복용 ↔ 당귀, 목단피 등 활혈 약재 출혈 경향 모니터링")
        if med_diab: trackers.append("복용 전후 혈당 수치 변화")
        if med_bp or cond_bp_high: trackers.append("복용 전후 혈압 수치 변화")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.success("**🟢 정합 소견 (맞는 부분)**\n\n" + ("\n".join([f"- {m}" for m in matches]) if matches else "- 입력된 진맥/설진 정보가 부족합니다."))
        with col_m2:
            if cautions:
                st.error("**🔴 주의 및 재검토 (어긋날 수 있는 부분)**\n\n" + "\n".join([f"- {c}" for c in cautions]))
            else:
                st.info("**🟡 특이 주의 소견 없음**\n\n- 단, 임상적 판단에 따라 모니터링 요망")
        
        st.markdown("**🔍 복용 후 필수 추적 관찰:** " + ", ".join(trackers))
        st.divider()

        # 2. 처방 감별 비교표
        st.subheader("📊 처방 감별 비교 패널 (Differential Diagnosis)")
        st.caption("선택한 처방과 임상에서 자주 감별되는 유사 처방들의 방향성을 비교합니다.")
        
        def highlight_selected(row):
            return ['background-color: #d1e7dd' if row['처방'] == selected_formula else '' for _ in row]
            
        st.dataframe(diff_df.style.apply(highlight_selected, axis=1), use_container_width=True, hide_index=True)

    # ------------------------------------------
    # 탭 2: 전통 처방 Core
    # ------------------------------------------
    with tabs[1]:
        st.subheader("📌 전통 처방 Core 패널")
        st.info(f"**전통 변증 방향:** {f_info['indication_traditional']} ({f_info['pattern_tags']})")
        st.markdown(c_info['clinic_structure'])

    # ------------------------------------------
    # 탭 3: 동의보감 병렬 해석
    # ------------------------------------------
    with tabs[2]:
        st.subheader("📖 동의보감 병렬 해석 패널")
        if is_level_3:
            st.info("동의보감의 병증 이해, 양생, 장부·기혈·한열 관점을 원전 맥락에서 정리하는 주석층입니다.")
            st.markdown(f"**해석 방향:** {f_info['trad_interpret']}")
        else:
            st.warning("이 처방의 동의보감 원전 세부 매핑은 업데이트 진행 중입니다.")

    # ------------------------------------------
    # 탭 4: 진맥·설진 대조
    # ------------------------------------------
    with tabs[3]:
        st.subheader("🤚 진맥·설진 대조 패널")
        st.info("진맥·설진 정보는 자동 판정 값이 아니라, 한의사가 확인한 소견과 처방 방향을 대조하기 위한 도구입니다.")
        st.markdown(f"**선택 처방({selected_formula})의 기본 타겟 소견:**")
        if "허" in f_info['indication_traditional']:
            st.success("- **맥상:** 허맥, 약맥, 세맥 등 무력한 양상\n- **설진:** 담백설, 치흔, 소태 등 기혈음양 부족 양상")
        elif "습" in f_info['indication_traditional'] or "담" in f_info['indication_traditional']:
            st.error("- **맥상:** 활맥, 현맥 등 실증 양상\n- **설진:** 백니태, 황니태 등 습탁 정체 양상")
        else:
            st.markdown("- 해당 처방의 세부 진맥 가이드라인 업데이트 중")

    # ------------------------------------------
    # 탭 5: 침구 치료 방향
    # ------------------------------------------
    with tabs[4]:
        st.subheader("📍 침구 치료 방향 패널")
        st.warning("본 패널은 자동 침 처방이 아니라, 선택 처방의 변증에 맞춰 면허자가 검토할 치료 원칙(보사/승강출입)을 정리한 것입니다.")
        
        st.markdown("#### 침 치료 방향 원칙")
        st.markdown(c_info['clinic_direction'])
        
        st.markdown("#### 검토 가능한 경락/혈위군")
        st.markdown("- 변증 축에 따른 장부(Zang-fu) 원혈, 락혈, 배유혈 중심 검토\n- 기혈 소통 및 한열 완충 목적의 혈위 배합")

    # ------------------------------------------
    # 탭 6: 뜸 치료 방향
    # ------------------------------------------
    with tabs[5]:
        st.subheader("🔥 뜸 치료 방향 패널")
        st.error("**[주의]** 뜸은 화상, 알레르기, 감염 위험이 있으므로 당뇨성 말초신경병증(감각저하) 및 실열/허열 환자에게 극히 주의해야 합니다.")
        
        st.markdown("#### 뜸 치료 검토 지침")
        if "열" in f_info['indication_traditional'] or "음허" in f_info['indication_traditional']:
            st.error("❌ **뜸 주의 조건:** 오심번열, 도한, 실열 양상이 뚜렷할 경우 온열 자극 주의 (진액 고갈 우려)")
        else:
            st.success("🟢 **뜸 검토 가능:** 하복부 냉감, 비위 허한, 기허 피로가 뚜렷한 경우 완만한 온보 방향 검토")

    # ------------------------------------------
    # 탭 7: 처방 주변 변화 가능성 (구 H34)
    # ------------------------------------------
    with tabs[6]:
        st.subheader("🌐 처방 주변 변화 가능성 패널")
        st.caption("연구자용 구조명: H(3,4) Extension")
        if is_level_3:
            st.info("처방의 중심 변증 방향에서 벗어날 수 있는 주변 주의점(예: 승양 과잉, 보익 과잉)을 확인하는 확장 지도입니다.")
            st.markdown(f"**[{selected_formula} 주의점]**\n\n{c_info['clinic_caution']}")
        else:
            st.warning("이 처방의 주변 변화 가능성(H34) 심층 매핑은 데이터 수집 중입니다. (Level 1/2 우선 제공)")

    # ------------------------------------------
    # 탭 8: 보사·승강출입 균형 (구 다면체)
    # ------------------------------------------
    with tabs[7]:
        st.subheader("💎 보사·승강출입 균형 패널")
        st.caption("연구자용 구조명: 다면체 방향성 시각화 (Octahedron, RD 등)")
        if is_level_3:
            st.info("다면체 분석은 도형을 보라는 뜻이 아니라, 처방이 보충축과 배출축 중 어디에서 균형을 잡는지 정리한 것입니다.")
            st.markdown(c_info['clinic_direction'])
        else:
            st.warning("이 처방의 다면체 동적 평형 매핑은 데이터 수집 중입니다.")

    # ------------------------------------------
    # 탭 9, 10: 연구자용 주석 (Q6, 내경)
    # ------------------------------------------
    with tabs[8]:
        st.subheader("🧬 Q6 64큐브 Core 주석 패널 (연구자용)")
        if is_level_3:
            st.success(f"**Q6 변화 방향:** {f_info['q6_core_vector']}")
            st.markdown("약재별 코돈-아미노산 벡터 매핑 정보가 이 공간에 렌더링됩니다.")
        else:
            st.warning("이 처방은 현재 Level 1 상태로, Q6 코돈 벡터 매핑이 확정되지 않았습니다.")

    with tabs[9]:
        st.subheader("📚 황제내경 병렬 해석 패널 (연구자용)")
        if is_level_3:
            st.info("전통 생명론의 핵심 개념을 정보기하학 언어로 병렬 해석하는 층입니다.")
        else:
            st.warning("이 처방의 내경 장부/오행축 병렬 매핑은 연구 진행 중입니다.")

    # ------------------------------------------
    # 탭 11: 안전성 확인 패널
    # ------------------------------------------
    with tabs[10]:
        st.subheader("🚨 안전성 확인 패널")
        st.markdown("환자가 입력한 양약 복용력 및 기저질환과 처방 약재 간의 상호작용 위험도를 요약합니다. (상세 내용은 탭 1의 요약표 참고)")
        st.markdown(f"- **입력된 주요 복용약:** {med_anti_coag*'항응고제 '} {med_bp*'혈압약 '} {med_diab*'당뇨약 '}")
        st.markdown("- 처방에 특이 약재(마황, 부자 등) 포함 여부 및 환자 상태에 따른 금기/신중 투여 여부를 의료인이 최종 확인해야 합니다.")

    # ------------------------------------------
    # 탭 12: 환자 설명문
    # ------------------------------------------
    with tabs[11]:
        st.subheader("💬 환자 설명문 패널")
        patient_html = f"""
        <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
            <b>{selected_formula}</b>은 한 가지 증상만 억누르는 약이 아니라, 여러 약재가 조화롭게 작용하여 몸의 무너진 균형을 회복시키는 복합 처방입니다.<br><br>
            이 대시보드는 처방 복용 시 나타날 수 있는 우리 몸의 반응과 주의점을 한의사 선생님이 더 안전하게 살필 수 있도록 돕는 시스템입니다.<br><br>
            복용하시는 동안 소화 상태, 피로감, 수면 변화, (해당시) 혈당/혈압의 변화를 편안하게 관찰하시고 진료 시 말씀해 주시면 됩니다.
        </div>
        """
        st.markdown(patient_html, unsafe_allow_html=True)

else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 리포트 생성' 버튼을 눌러주세요.")
