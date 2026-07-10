import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# 0. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="한의 임상 의사결정 지원 대시보드",
    page_icon="☯️",
    layout="wide",
)

st.title("☯️ 한의 임상 의사결정 지원 대시보드")
st.caption("전통 처방 · 동의보감 · 황제내경 · 진맥·설진 · 침구·뜸 · 안전성 · 소견서 통합")

st.warning(
    "**[주의] 본 대시보드는 자동 진단 또는 자동 처방 도구가 아닙니다.**\n\n"
    "- 이 시스템은 한의사가 입력한 종합소견, 변증, 진맥·설진, 복용약, 검사값을 바탕으로 "
    "한약·침구·뜸·추적관찰·소견서 초안을 정리하는 보조 도구입니다.\n"
    "- 침구와 뜸 방향은 자동 시술 지시가 아니라, 면허자가 검토할 수 있는 치료 원칙과 주의점을 정리한 것입니다.\n"
    "- 실제 처방, 용량, 혈위, 자침 깊이, 유침 시간, 뜸 부위와 강도는 반드시 면허가 있는 한의사가 최종 결정해야 합니다."
)

st.markdown(
    "### 한의 임상 해석 구조 = 종합소견 + 전통 변증 + 동의보감 + 황제내경 + 진맥·설진 + 침뜸 방향 + 안전성 확인"
)

show_research = st.sidebar.checkbox("🔬 연구자용 부록 보기", value=False)

if show_research:
    with st.expander("🔬 연구자용 구조 설명"):
        st.markdown(
            """
            한의사용 기본 화면에서는 연구자용 용어를 직접 노출하지 않습니다.

            | 연구자용 표현 | 한의사용 번역 |
            |---|---|
            | 64큐브 / Q6 | 처방 방향 6축 |
            | H(3,4) | 처방 주변 변화 가능성 |
            | 다면체 방향성 | 보사·승강출입 균형 |
            | 코돈 / 아미노산 | 연구자용 배경 주석 |

            이 구조는 약재가 유전암호를 조절한다는 뜻이 아니라, 전통 처방 방향을 구조적으로 정리하는 보조 해석층입니다.
            """
        )


# ============================================================
# 1. 처방 데이터
# ============================================================

def make_formula(
    name,
    category,
    indication,
    direction,
    herbs,
    dongui_chapter,
    dongui_pattern,
    dongui_interpret,
    neijing_concepts,
    pulse_tongue,
    best_fit,
    poor_fit,
    differential,
    modification,
    acupuncture,
    moxa,
    followup,
    caution,
    red_flags,
):
    return {
        "처방명": name,
        "분류": category,
        "전통 변증": indication,
        "처방 방향": direction,
        "구성 약재": herbs,
        "동의보감 편제": dongui_chapter,
        "동의보감 병증": dongui_pattern,
        "동의보감 해석": dongui_interpret,
        "황제내경 개념": neijing_concepts,
        "진맥·설진 목표": pulse_tongue,
        "잘 맞는 환자상": best_fit,
        "주의 환자상": poor_fit,
        "감별 처방": differential,
        "가감·조정 방향": modification,
        "침구 방향": acupuncture,
        "뜸 방향": moxa,
        "추적 관찰": followup,
        "안전성 주의": caution,
        "위험 신호": red_flags,
    }


FORMULAS = [
    make_formula(
        "육미지황환",
        "보음·보신·허열 완충",
        "간신음허, 허열도한, 정혈 부족",
        "자음, 보신, 수렴, 허열 완충, 수습 조절",
        "숙지황, 산수유, 산약, 복령, 택사, 목단피",
        "신형(身形), 신(腎), 소아(小兒)",
        "신수 부족, 진음 고갈, 허열, 도한",
        "신수와 진음이 부족하여 생기는 허열·도한·소모성 피로를 보음·보신 방향에서 해석합니다.",
        "음양, 신장, 기혈진액, 승강출입, 표본중기",
        "맥: 침세, 세삭, 약 / 설: 홍 또는 담홍, 소태·무태, 건조",
        "요슬산연, 도한, 오심번열, 구건, 피로, 만성 소모성 허증",
        "설태 후니, 식체·습담, 설사 잦음, 실열·습열이 강한 경우",
        "보중익기탕: 기허·중기하함 / 귀비탕: 심비양허·불면 / 오령산: 수습정체",
        "소화불량이 강하면 숙지황 부담 확인, 수습이 강하면 이수·건비 방향 검토",
        "간·신 축 보강, 정혈·진액 보존, 허열 완충, 수습 조절 방향. 보법 또는 평보평사 중심.",
        "냉감·허한이 동반될 때만 검토. 오심번열, 도한, 구건, 실열 소견이 강하면 강한 온열 자극 주의.",
        "3~7일: 소화불량·설사·부종 / 2~4주: 피로감·도한·열감·수면·소변 상태",
        "소화불량, 설사, 항응고제, 당뇨약, 이뇨제, 간·신장 기능 저하 확인",
        "항응고제 복용, 만성 설사, 심한 식체, 간·신장 기능 저하, 수술 예정",
    ),
    make_formula(
        "보중익기탕",
        "보기·승양·중기 보강",
        "비위기허, 중기하함, 기허 피로",
        "보기, 승양, 중기 보강, 비위 회복",
        "황기, 인삼, 백출, 감초, 당귀, 진피, 승마, 시호",
        "내상(內傷), 비위(脾胃), 기(氣)",
        "노권상, 음식상, 기허발열, 중기하함",
        "무너진 중기를 세우고 맑은 양기를 위로 끌어올리는 보기·승양 방향에서 해석합니다.",
        "음양, 비위, 기, 승강출입, 표본중기",
        "맥: 허, 약, 무력 / 설: 담백, 치흔, 백태",
        "피로, 식욕저하, 자한, 무력감, 내장하수감, 말하기 힘든 기허",
        "상열감, 고혈압, 심계, 불면, 실열, 습열, 식적이 뚜렷한 경우",
        "사군자탕: 순수 비위기허 / 십전대보탕: 기혈양허·허한 / 소요산: 간울비허",
        "상열감이 있으면 승양 과잉 주의, 식체가 있으면 소도·화위 방향 먼저 검토",
        "비·위 축 보강, 중기 보강, 승양 방향. 고혈압·심계가 있으면 강한 상승 자극 주의.",
        "비위허한, 복부 냉감, 기허 피로가 뚜렷하면 검토. 상열감·불면·혈압 상승 경향이면 주의.",
        "3~7일: 식욕·피로·소화 / 1~2주: 혈압·두근거림·불면·상열감",
        "고혈압, 불면, 심계, 당뇨약, 혈압약, 이뇨제 병용 확인",
        "혈압 상승, 심계, 불면 악화, 상열감, 흉민, 심한 식체",
    ),
    make_formula(
        "산조인탕",
        "안신·수렴·허번불면",
        "심비양허, 허번불면, 안신 필요",
        "수렴, 안신, 내부 안정, 허열 완충",
        "산조인, 지모, 복령, 천궁, 감초",
        "몽(夢), 신형(身形), 심(心)",
        "허번불면, 심담허겁, 심신불안",
        "허번과 불면, 심신불안을 안정시키는 안신·수렴 방향에서 해석합니다.",
        "심, 음양, 신지, 기혈진액, 개합추",
        "맥: 세, 현세, 약 / 설: 담홍 또는 홍, 소태, 건조",
        "잠은 오나 깊이 못 자는 불면, 심계, 불안, 피로, 허번",
        "실열성 불면, 담열, 과도한 졸림, 진정제 병용으로 반응 저하가 있는 경우",
        "귀비탕: 불면+건망+식욕저하 / 온담탕: 담열·흉민 / 천왕보심단: 음허화왕",
        "담음이 강하면 화담 방향 검토, 주간 졸림이 있으면 진정 과잉 주의",
        "심·간·담 축, 안신, 수렴, 내부 안정 방향. 과도한 자극보다 완만한 조절 중심.",
        "허한성 불면·냉감이 동반될 때만 검토. 번조·열감·구건이 뚜렷하면 강한 뜸 자극 주의.",
        "3~7일: 입면시간·수면 깊이·주간 졸림 / 2주: 불안·심계·피로",
        "수면제, 진정제, 항우울제 병용, 주간 졸림, 간·신장 기능 저하 확인",
        "주간 졸림 심화, 반응 저하, 실열성 불면 악화, 약물 병용 이상반응",
    ),
    make_formula(
        "평위산",
        "조습·화위·비위습탁",
        "비위습탁, 식체, 복부팽만",
        "조습, 행기, 소도, 비위 소통",
        "창출, 후박, 진피, 감초, 생강, 대조",
        "비위(脾胃), 내상(內傷), 담음(痰飮)",
        "식적, 습탁, 담음, 비위 운화 저하",
        "비위에 습탁과 식체가 정체된 상태를 조습·행기·화위 방향에서 해석합니다.",
        "비위, 기기, 습, 승강출입, 개합추",
        "맥: 활, 완 / 설: 백니태, 후태",
        "복부팽만, 더부룩함, 트림, 식체, 백니태, 몸이 무거운 습체",
        "음허, 구건, 마른 체형, 무태, 진액 부족, 위음허성 속쓰림",
        "이진탕: 담음·오심 / 반하사심탕: 심하비·한열착잡 / 향사평위산: 기체·복통",
        "식체가 강하면 소도 방향, 담음이 강하면 화담 방향, 진액 부족이면 조습 과잉 주의",
        "비위 소통, 중초 기기 조절, 습탁 배출 방향. 복부 반응과 대변 상태 확인.",
        "복부 냉감과 습체가 뚜렷하면 검토. 구건·음허·열감이 있으면 강한 온조 자극 주의.",
        "3~5일: 복부팽만·트림·대변·입마름 / 1~2주: 식욕·소화력",
        "임신, 심한 탈수, 음허, 구건, 변비 악화 확인",
        "입마름 심화, 변비 악화, 속쓰림, 탈수, 심한 음허",
    ),
    make_formula(
        "귀비탕",
        "심비양허·보기보혈·안신",
        "심비양허, 불면, 건망, 사려과다",
        "보기, 보혈, 안신, 심비 보강",
        "인삼, 황기, 백출, 복령, 당귀, 용안육, 산조인, 원지, 감초, 목향",
        "건망(健忘), 몽(夢), 혈(血), 비위(脾胃)",
        "사려과다, 심비양허, 건망, 불면",
        "생각이 많아 심과 비가 손상되어 불면, 건망, 식욕저하가 나타나는 방향에서 해석합니다.",
        "심, 비, 혈, 신지, 기혈진액",
        "맥: 세약 / 설: 담백",
        "불면, 건망, 심계, 피로, 식욕저하, 생각이 많고 쉽게 지치는 상태",
        "습담·식체가 뚜렷함, 열감·번조 강함, 과도한 졸림",
        "산조인탕: 허번불면 / 보중익기탕: 중기하함 / 팔진탕: 기혈양허",
        "소화력이 약하면 보익·안신 약재 부담 확인, 담열성 불면이면 온담탕 계열 감별",
        "심비 보강, 안신, 기혈 보충 방향. 소화 상태와 수면 상태를 함께 봅니다.",
        "수족냉증·복부 냉감이 있으면 검토. 열감·번조가 강하면 주의.",
        "1주: 수면·식욕·심계 / 2~4주: 건망·피로·소화력",
        "진정제 병용, 소화불량, 졸림, 혈압약·당뇨약 병용 확인",
        "주간 졸림, 소화불량 심화, 심계 악화, 약물 병용 이상반응",
    ),
    make_formula(
        "팔진탕",
        "기혈쌍보",
        "기혈양허, 만성피로, 안색창백",
        "보기, 보혈, 기혈쌍보, 균형 보강",
        "사군자탕 + 사물탕",
        "허로(虛勞), 기혈(氣血), 혈(血), 비위(脾胃)",
        "기혈양허, 식소무력, 안색창백, 어지럼",
        "기와 혈이 함께 부족한 상태를 보기·보혈로 균형 있게 보강하는 방향에서 해석합니다.",
        "기혈진액, 비위, 음양, 표본중기",
        "맥: 허, 완 / 설: 담백",
        "피로, 안색창백, 어지럼, 식욕저하, 회복력 저하",
        "식체, 습담, 실열, 상열감, 보약 복용 후 체하는 환자",
        "십전대보탕: 허한·온보 강함 / 귀비탕: 불면·건망 / 사물탕: 혈허 중심",
        "소화력이 약하면 건비 방향 선행, 열감이 있으면 온보 처방과 감별",
        "기혈 보강과 전신 순환 조절 방향. 무리한 강자극보다 평보평사 중심.",
        "냉감과 허한이 있으면 검토. 열감·상열감이 있으면 주의.",
        "1주: 소화·피로·대변 / 2~4주: 안색·어지럼·체력",
        "소화불량, 설사, 항응고제, 상열감 확인",
        "체기, 설사, 열감, 흉민, 혈압 변화",
    ),
    make_formula(
        "십전대보탕",
        "기혈쌍보·온보·허로",
        "기혈양허, 허로, 허한",
        "대보원기, 기혈쌍보, 온보",
        "사군자탕 + 사물탕 + 황기 + 육계",
        "허로(虛勞), 기혈(氣血), 한(寒)",
        "기혈양허, 극심한 허로, 자한도한, 허한",
        "기혈이 크게 허하고 냉감이 동반된 상태를 강하게 보충하고 데우는 방향에서 해석합니다.",
        "음양, 기혈진액, 한열, 비신, 승강출입",
        "맥: 침지, 무력 / 설: 담백, 치흔, 백태",
        "기혈양허, 허로, 수술 후 회복기, 면색창백, 수족냉증, 체력저하",
        "실열, 고혈압, 상열감, 안면홍조, 염증성 열감, 식체",
        "팔진탕: 온보보다 기혈쌍보 / 보중익기탕: 승양 중심 / 사물탕: 혈허 중심",
        "열감이 있으면 온보 과잉 주의, 소화가 약하면 보익 부담 확인",
        "기혈 쌍보, 전신 회복, 허한 보강 방향. 열감 환자에서는 온보 자극 주의.",
        "허한·냉감·체력저하가 뚜렷하면 검토. 고혈압·상열감·불면·실열은 주의.",
        "1주: 소화·열감·혈압 / 2~4주: 피로·냉감·체력 변화",
        "고혈압, 상열감, 불면, 염증성 질환, 항응고제, 수술 예정 확인",
        "열감 악화, 혈압 상승, 불면 심화, 염증성 열감 악화",
    ),
]

# 기본 확장 처방: 전통 Core 중심 분석
EXTRA_FORMULAS = [
    ("사물탕", "보혈·화혈", "혈허, 영혈부족, 어지럼", "보혈, 화혈, 순환 보조", "숙지황, 당귀, 천궁, 작약", "혈(血), 부인(婦人)", "영혈 부족", "혈허와 혈의 순환 문제를 보혈·화혈 방향에서 해석합니다.", "혈, 기혈진액, 충임, 음양"),
    ("사군자탕", "보기·건비", "비위기허, 식욕저하, 무력", "익기, 건비, 소화력 회복", "인삼, 백출, 복령, 감초", "기(氣), 비위(脾胃)", "비위기허", "비위의 기운을 북돋아 소화흡수력과 전신 기력을 회복하는 방향입니다.", "비위, 기, 승강출입"),
    ("소요산", "소간해울·건비", "간울비허, 흉협고만, 스트레스성 소화불량", "소간, 해울, 건비, 조화", "시호, 당귀, 작약, 백출, 복령, 감초, 박하, 생강", "화(火), 부인(婦人), 간(肝)", "간기울결, 비허, 혈허", "간기 울결과 비위허약이 함께 있는 상태를 풀고 조화시키는 방향입니다.", "간, 비위, 기기, 오행 생극, 개합추"),
    ("이진탕", "조습화담·강역", "담음정체, 오심구토, 어지럼", "조습, 화담, 강역, 위기 하강", "반하, 진피, 복령, 감초, 생강, 오매", "담음(痰飮), 구토(嘔吐), 비위(脾胃)", "담음정체, 위기불화", "담음을 말리고 위기를 내려 오심·구토·어지럼을 조절하는 방향입니다.", "비위, 담음, 승강출입, 기기"),
    ("오령산", "이수삼습·방광기화", "수습정체, 소변불리, 부종", "이수, 삼습, 수분 대사, 기화 조절", "택사, 저령, 복령, 백출, 계지", "소변(小便), 부종(浮腫), 수(水)", "방광기화불리, 수음정체", "수음 정체와 소변불리를 수분 대사와 기화 작용 방향에서 해석합니다.", "수, 방광, 기화, 승강출입"),
    ("육군자탕", "비위기허+담음", "비위기허와 담음", "보기, 화담, 건비", "인삼, 백출, 복령, 감초, 반하, 진피", "비위(脾胃), 담음(痰飮)", "비위기허와 담음", "기허와 담음이 함께 있는 상태를 보기·화담 방향에서 해석합니다.", "비위, 담음, 기, 승강출입"),
    ("반하사심탕", "한열착잡·심하비", "심하비, 한열착잡, 위기불화", "화위, 조중, 한열 조절", "반하, 황금, 황련, 건강, 인삼, 감초, 대조", "비위(脾胃), 구토(嘔吐), 비만(痞滿)", "한열착잡, 심하비", "상하·한열이 맞지 않아 심하비와 구역이 생기는 방향에서 해석합니다.", "음양, 한열, 비위, 개합추"),
    ("온담탕", "화담·안신", "담열, 불안, 불면", "화담, 청담열, 안신", "반하, 죽여, 지실, 진피, 복령, 감초", "담음(痰飮), 몽(夢), 심(心)", "담열, 심담불안", "담열과 심담불안으로 인한 불면·불안을 화담·안신 방향에서 해석합니다.", "심, 담, 신지, 개합추"),
    ("갈근탕", "해표·경항부 이완", "풍한표증, 항배강", "해표, 승진, 경항부 이완", "갈근, 마황, 계지, 작약, 감초, 생강, 대조", "한(寒), 두통(頭痛), 풍(風)", "풍한표증", "초기 외감과 목·어깨 긴장을 해표·승진 방향에서 해석합니다.", "태양, 표리, 풍한, 개합"),
    ("소청룡탕", "온폐화음", "한담, 수양성 비염, 기침", "온폐, 화음, 해표", "마황, 작약, 세신, 건강, 감초, 계지, 반하, 오미자", "해수(咳嗽), 담음(痰飮), 폐(肺)", "한음범폐", "찬 수음과 기침·비염을 온폐·화음 방향에서 해석합니다.", "폐, 한음, 표리, 승강출입"),
    ("맥문동탕", "자음윤폐", "폐위음허, 마른기침", "자음, 윤폐, 강역", "맥문동, 반하, 인삼, 감초, 갱미, 대조", "해수(咳嗽), 폐(肺), 위(胃)", "폐위음허, 마른기침", "진액 부족과 마른기침을 자음·윤폐 방향에서 해석합니다.", "폐위, 진액, 음양, 승강출입"),
    ("계지복령환", "활혈·어혈 조절", "어혈, 하복부 정체", "활혈, 어혈 조절", "계지, 복령, 목단피, 도인, 작약", "혈(血), 부인(婦人), 징가(癥瘕)", "어혈정체", "어혈과 하복부 정체를 활혈·어혈 조절 방향에서 해석합니다.", "혈, 충임, 기기, 개합추"),
    ("황련해독탕", "청열사화", "삼초실열, 번조, 염증성 열감", "청열, 사화, 해독", "황련, 황금, 황백, 치자", "화(火), 열(熱), 번조", "삼초실열", "실열과 화열을 사하는 방향에서 해석합니다.", "화, 삼초, 음양, 표본중기"),
    ("방풍통성산", "해표·청열·공하", "표리실열, 비만, 변비", "해표, 청열, 공하, 배출", "방풍, 형개, 마황, 대황, 망초, 석고 등", "풍(風), 열(熱), 대변, 비만", "표리실열", "발산·청열·배출이 강한 방향에서 해석합니다.", "표리, 열, 배출, 개합"),
    ("천왕보심단", "자음안신", "음허화왕, 불면, 심계", "자음, 안신, 심신 안정", "생지황, 천문동, 맥문동, 산조인, 원지 등", "몽(夢), 심(心), 혈(血)", "음허화왕, 심번불면", "음혈 부족과 심번불면을 자음·안신 방향에서 해석합니다.", "심, 신지, 음양, 기혈진액"),
]

for item in EXTRA_FORMULAS:
    name, category, indication, direction, herbs, chapter, pattern, interpret, neijing = item
    FORMULAS.append(
        make_formula(
            name=name,
            category=category,
            indication=indication,
            direction=direction,
            herbs=herbs,
            dongui_chapter=chapter,
            dongui_pattern=pattern,
            dongui_interpret=interpret,
            neijing_concepts=neijing,
            pulse_tongue="맥·설 소견은 변증에 따라 한의사가 직접 확인하여 대조합니다.",
            best_fit=f"{indication}이 중심이고, {direction} 방향이 필요한 환자",
            poor_fit="한열허실, 허실, 담음, 어혈, 식체 방향이 맞지 않으면 재검토가 필요합니다.",
            differential="유사 처방과 변증 차이를 비교하여 한의사가 검토합니다.",
            modification="증상 강도, 소화력, 한열허실, 복용약, 검사값에 따라 가감 방향을 검토합니다.",
            acupuncture=f"{direction} 방향에 맞춰 보법·사법·평보평사와 승강출입 방향을 검토합니다.",
            moxa="허한·냉감이 뚜렷할 때만 검토합니다. 실열, 상열감, 피부 감각 저하, 감염, 화상 위험은 주의합니다.",
            followup="3~7일: 증상·소화·대소변 변화 / 2~4주: 전반 반응과 안전성 확인",
            caution="복용약, 임신·수유, 간·신장 기능, 소화상태, 알레르기, 수술 예정 여부를 확인합니다.",
            red_flags="중증 기저질환, 다약제 복용, 임신·수유, 수술 예정, 알레르기, 검사값 이상",
        )
    )

FORMULA_DF = pd.DataFrame(FORMULAS)


# ============================================================
# 2. 한의사용 6축 해석
# ============================================================

AXES = [
    {
        "축": "보충축",
        "뜻": "기·혈·음·양·정혈을 보태는 방향",
        "대표 확인 소견": "피로, 무력, 안색창백, 식욕저하, 요슬산연",
        "임상 질문": "허증, 피로, 소모, 기혈부족, 음양부족이 뚜렷한가?",
        "keywords": ["보기", "보혈", "자음", "보신", "기혈쌍보", "대보원기", "온보", "익기", "보폐", "보간신"],
    },
    {
        "축": "수렴·안정축",
        "뜻": "흩어진 기운을 안으로 모으고 안정시키는 방향",
        "대표 확인 소견": "불면, 심계, 도한, 허번, 불안, 진액 소모",
        "임상 질문": "불면, 심계, 도한, 허번, 불안, 진액 소모가 있는가?",
        "keywords": ["수렴", "안신", "내부 안정", "허열", "불면", "도한", "심신 안정", "완급"],
    },
    {
        "축": "승양·상승축",
        "뜻": "아래로 처진 기운을 위로 끌어올리는 방향",
        "대표 확인 소견": "처짐, 중기하함, 무력감, 기단, 자한",
        "임상 질문": "중기하함, 무력감, 처짐, 식욕저하, 기단이 있는가?",
        "keywords": ["승양", "중기", "보기", "기허", "비위기허", "승진"],
    },
    {
        "축": "배출·이수축",
        "뜻": "정체된 수분·습담·노폐를 밖으로 빼는 방향",
        "대표 확인 소견": "부종, 소변불리, 몸무거움, 담음, 백니태",
        "임상 질문": "부종, 소변불리, 몸이 무거움, 습담, 담음이 있는가?",
        "keywords": ["이수", "삼습", "수습", "담음", "화담", "조습", "부종", "공하", "배출"],
    },
    {
        "축": "소통·전환축",
        "뜻": "막힌 기혈과 비위의 흐름을 돌리는 방향",
        "대표 확인 소견": "흉협고만, 복부팽만, 식체, 기체, 어혈, 통증",
        "임상 질문": "복부팽만, 흉협고만, 식체, 기체, 어혈, 통증이 있는가?",
        "keywords": ["행기", "소간", "해울", "활혈", "화위", "소도", "통락", "거풍습", "전환", "어혈", "산한"],
    },
    {
        "축": "완충·조화축",
        "뜻": "치우친 보·사·한·열을 조절하는 방향",
        "대표 확인 소견": "보하면 체하고, 사하면 허해지는 중간형 반응",
        "임상 질문": "보사·한열·허실이 한쪽으로 치우쳐 있지는 않은가?",
        "keywords": ["완충", "조화", "균형", "평보평사", "조중", "한열 조절", "화위"],
    },
]


def axis_profile(formula):
    text = f"{formula['처방 방향']} {formula['전통 변증']} {formula['분류']} {formula['동의보감 해석']}"
    rows = []

    for axis in AXES:
        hit = sum(1 for k in axis["keywords"] if k in text)
        if hit >= 2:
            level = "강함"
        elif hit == 1:
            level = "중간"
        else:
            level = "낮음 또는 보조"

        rows.append(
            {
                "처방 방향축": axis["축"],
                "쉽게 말하면": axis["뜻"],
                "대표 확인 소견": axis["대표 확인 소견"],
                "한의사가 확인할 질문": axis["임상 질문"],
                "현재 처방 관련성": level,
            }
        )

    return pd.DataFrame(rows)


def axis_summary_sentence(formula):
    df = axis_profile(formula)
    strong_axes = df[df["현재 처방 관련성"] == "강함"]["처방 방향축"].tolist()
    mid_axes = df[df["현재 처방 관련성"] == "중간"]["처방 방향축"].tolist()

    if strong_axes:
        return f"{formula['처방명']}은 한의사용 6축 해석상 **{', '.join(strong_axes)}**이 중심입니다."
    if mid_axes:
        return f"{formula['처방명']}은 한의사용 6축 해석상 **{', '.join(mid_axes)}**을 보조적으로 확인합니다."
    return f"{formula['처방명']}은 보충·수렴·승양·배출·소통·완충 축을 종합 확인합니다."


# ============================================================
# 3. 황제내경·동의보감 매핑
# ============================================================

NEIJING_RULES = [
    {
        "개념": "음양",
        "keywords": ["자음", "온보", "청열", "허열", "실열", "한열", "음허", "양허", "냉감", "상열"],
        "해석": "부족과 과잉, 차가움과 열감, 안과 밖의 균형을 확인합니다.",
        "진료실 질문": "이 환자는 부족해서 생긴 열인가, 실제 열이 강한가? 차가움과 열감이 섞여 있는가?",
    },
    {
        "개념": "오행 생극제화",
        "keywords": ["간", "심", "비", "폐", "신", "소간", "보신", "비위", "심비", "폐위"],
        "해석": "장부 간의 밀고 당김, 상생·상극·조절 관계를 확인합니다.",
        "진료실 질문": "간이 비위를 누르는가? 신음 부족이 허열로 올라오는가? 심비가 함께 약한가?",
    },
    {
        "개념": "장부·기혈진액",
        "keywords": ["기", "혈", "진액", "담음", "수습", "어혈", "정혈", "보혈", "보기", "자음"],
        "해석": "기, 혈, 체액, 담음, 어혈의 부족·정체·소모를 확인합니다.",
        "진료실 질문": "부족한 것은 기인가, 혈인가, 진액인가? 정체된 것은 담음인가, 어혈인가?",
    },
    {
        "개념": "승강출입",
        "keywords": ["승양", "강역", "수렴", "해표", "배출", "이수", "공하", "기화", "소통"],
        "해석": "기운이 오르는지, 내려가는지, 안으로 모이는지, 밖으로 풀리는지 확인합니다.",
        "진료실 질문": "올려야 하는가, 내려야 하는가, 안으로 모아야 하는가, 밖으로 풀어야 하는가?",
    },
    {
        "개념": "개합추",
        "keywords": ["해표", "수렴", "안신", "화위", "조중", "소간", "해울", "한열착잡"],
        "해석": "열고, 닫고, 가운데에서 돌리는 조절 구조를 확인합니다.",
        "진료실 질문": "막힌 것을 열어야 하는가, 흩어진 것을 닫아야 하는가, 가운데에서 조화시켜야 하는가?",
    },
    {
        "개념": "표본중기",
        "keywords": ["표", "본", "허", "실", "담음", "식체", "허열", "실열", "기허", "습담"],
        "해석": "겉으로 보이는 증상과 뿌리 병기를 구분합니다.",
        "진료실 질문": "지금 보이는 증상이 본질인가, 겉으로 나타난 반응인가?",
    },
    {
        "개념": "삼음삼양 병기",
        "keywords": ["태양", "양명", "소양", "태음", "소음", "궐음", "외감", "비위", "간", "신", "심"],
        "해석": "병이 겉에서 속으로, 양에서 음으로, 얕은 층에서 깊은 층으로 움직이는 흐름을 확인합니다.",
        "진료실 질문": "병이 표에 있는가, 리에 있는가? 비위·신·간·심 어느 층으로 깊어졌는가?",
    },
    {
        "개념": "육기",
        "keywords": ["풍", "한", "서", "습", "조", "화", "담음", "열", "냉감", "건조", "습탁"],
        "해석": "풍·한·습·조·화 등 환경적·병리적 기운의 영향을 확인합니다.",
        "진료실 질문": "풍한인가, 습담인가, 건조인가, 열인가? 계절·환경 요인이 영향을 주는가?",
    },
]


def infer_neijing_context(formula, inputs):
    text = (
        f"{formula['처방명']} {formula['분류']} {formula['전통 변증']} "
        f"{formula['처방 방향']} {formula['황제내경 개념']} "
        f"{inputs.get('patient_symp', '')} {inputs.get('doctor_assessment', '')}"
    )

    rows = []
    for rule in NEIJING_RULES:
        if any(k in text for k in rule["keywords"]):
            rows.append(
                {
                    "황제내경 해당 개념": rule["개념"],
                    "이 소견과 연결되는 이유": rule["해석"],
                    "한의사가 확인할 질문": rule["진료실 질문"],
                }
            )

    if not rows:
        rows.append(
            {
                "황제내경 해당 개념": "종합 변증",
                "이 소견과 연결되는 이유": "입력 정보가 부족하여 특정 개념보다 음양·장부·기혈진액을 종합 확인합니다.",
                "한의사가 확인할 질문": "허실한열, 표리, 장부, 기혈진액 중 어느 축이 중심인가?",
            }
        )

    return pd.DataFrame(rows).drop_duplicates()


DONGUI_KEYWORD_RULES = [
    ("불면|수면|꿈|심계|불안|건망", "몽(夢)·건망(健忘)·심(心)", "수면, 꿈, 심계, 건망, 정서 불안과 관련된 병증 해석"),
    ("피로|허약|허로|회복|수술|안색창백", "허로(虛勞)·기혈(氣血)", "오래 지치고 회복력이 떨어지는 허로·기혈 부족 해석"),
    ("소화|식욕|더부룩|트림|복부팽만|설사|식체", "비위(脾胃)·내상(內傷)", "소화력 저하, 식체, 비위 운화 장애 해석"),
    ("부종|소변|수분|갈증|몸무거움", "소변(小便)·부종(浮腫)·수(水)", "수분 대사, 소변불리, 부종과 관련된 해석"),
    ("기침|가래|비염|폐|숨", "해수(咳嗽)·폐(肺)·담음(痰飮)", "기침, 가래, 폐계 증상과 담음 해석"),
    ("통증|관절|허리|무릎|근육|경련", "비증(痺證)·통증·근골", "근골격 통증, 비증, 경락 소통 장애 해석"),
    ("월경|갱년기|하복부|어혈|출혈", "부인(婦人)·혈(血)·충임", "월경, 하복부, 충임, 혈허·어혈 관련 해석"),
    ("스트레스|흉협|답답|울|간울|화", "간(肝)·화(火)·울증", "간기울결, 화, 흉협불편, 정서성 소견 해석"),
]


def infer_donguibogam_context(formula, inputs):
    import re

    text = f"{inputs.get('patient_symp', '')} {inputs.get('doctor_assessment', '')} {formula['전통 변증']} {formula['처방 방향']}"
    rows = [
        {
            "동의보감 해당 편제": formula["동의보감 편제"],
            "해당 병증": formula["동의보감 병증"],
            "이 소견과 연결되는 이유": formula["동의보감 해석"],
        }
    ]

    for pattern, chapter, meaning in DONGUI_KEYWORD_RULES:
        if re.search(pattern, text):
            rows.append(
                {
                    "동의보감 해당 편제": chapter,
                    "해당 병증": "입력 소견 기반 추가 연결",
                    "이 소견과 연결되는 이유": meaning,
                }
            )

    return pd.DataFrame(rows).drop_duplicates()


# ============================================================
# 4. 정합도·안전성·혈위군·뜸 부위군 로직
# ============================================================

def build_match_logic(formula, inputs):
    matches = []
    cautions = []
    trackers = ["소화 상태", "대소변 변화", "피로감 변화"]

    text = f"{formula['처방 방향']} {formula['전통 변증']} {inputs.get('doctor_assessment', '')}"

    if inputs["patient_symp"]:
        matches.append(f"입력 증상 '{inputs['patient_symp']}'과 처방 방향 '{formula['처방 방향']}'의 정합 여부 검토")

    if any(k in text for k in ["보기", "보혈", "자음", "보신", "기혈쌍보", "온보", "대보원기"]):
        if inputs["mac_force"] in ["허맥", "약맥", "무력"] or inputs["tongue_color"] == "담" or inputs["tongue_fluid"] == "치흔":
            matches.append("맥 허·약 또는 설 담백·치흔 → 보충 방향과 정합 가능")
        if inputs["cond_bp_high"] or inputs["mac_force"] == "실맥" or inputs["tongue_color"] == "홍":
            cautions.append("고혈압·상열감·실맥·홍설 → 보충·승양·온보 과잉 반응 확인 필요")

    if any(k in text for k in ["자음", "수렴", "안신", "허열"]):
        if inputs["tongue_fluid"] == "건조" or inputs["tongue_coat"] == "소태/무태" or inputs["tongue_color"] == "홍":
            matches.append("설진 건조·홍설·소태 경향 → 자음·허열 완충 방향과 정합 가능")
        if inputs["med_sedative"]:
            cautions.append("수면제·진정제·항우울제 병용 → 주간 졸림과 반응 저하 확인")
            trackers.append("주간 졸림")

    if any(k in text for k in ["조습", "화담", "이수", "삼습", "소도", "공하", "배출"]):
        if inputs["tongue_coat"] in ["백태", "후태", "황니태"] or inputs["mac_shape"] == "활" or inputs["abd_exam"] == "더부룩함/가스":
            matches.append("백태·후태·활맥·복부 더부룩함 → 습담·수습 조절 방향과 정합 가능")
        if inputs["tongue_fluid"] == "건조" or inputs["tongue_coat"] == "소태/무태":
            cautions.append("건조·무태 → 조습·이수 방향이 진액 부족을 심화할 수 있어 확인 필요")

    if any(k in text for k in ["소간", "해울", "활혈", "통락", "어혈", "행기"]):
        if inputs["mac_shape"] == "현" or inputs["abd_exam"] in ["압통/저항", "복직근 긴장"]:
            matches.append("현맥·복부 긴장·압통 → 소통·전환 방향과 정합 가능")
        if inputs["med_anti_coag"] or inputs["cond_surgery"]:
            cautions.append("항응고제 또는 수술 예정 → 활혈·혈류 관련 약재 병용 확인")

    if inputs["cond_dig"]:
        cautions.append("만성 소화불량/설사 → 보익·자음 처방의 위장 부담 또는 조습 처방의 건조 반응 확인")
    if inputs["med_anti_coag"]:
        cautions.append("항응고제/항혈소판제/NSAIDs → 멍, 코피, 잇몸출혈, 수술 예정 여부 확인")
    if inputs["med_diab"]:
        cautions.append("당뇨약/인슐린 → 혈당 변화 및 저혈당 증상 확인")
        trackers.append("혈당")
    if inputs["med_bp"] or inputs["cond_bp_high"]:
        cautions.append("혈압약 또는 고혈압/상열감 → 혈압·두근거림·상열 반응 확인")
        trackers.append("혈압")
    if inputs["cond_liver"]:
        cautions.append("간·신장 질환 병력 → 장기 복용 전 검사값 확인")
    if inputs["cond_preg"]:
        cautions.append("임신/수유 → 처방·침구·뜸 모두 전문가 확인 필요")
    if inputs["cond_surgery"]:
        cautions.append("수술/시술 예정 → 출혈 관련 약재 및 복용 중단 여부 전문가 판단 필요")
    if inputs["cond_neuro"]:
        cautions.append("피부 감각저하/당뇨성 말초신경병증 → 뜸 화상 위험 주의")

    if "불면" in formula["전통 변증"] or "안신" in formula["처방 방향"]:
        trackers.append("수면 질")

    return matches, cautions, list(dict.fromkeys(trackers))


def fit_level(matches, cautions):
    score = len(matches) - len(cautions)
    if len(cautions) >= 5:
        return "주의 높음", "처방 방향보다 안전성·불일치 확인이 우선입니다."
    if score >= 2:
        return "정합 가능", "입력 정보상 처방 방향과 맞는 요소가 있습니다."
    if score <= -1:
        return "재검토 필요", "입력 정보상 주의하거나 어긋날 수 있는 요소가 있습니다."
    return "정보 부족", "진맥·설진·증상 입력을 더 보강해야 합니다."


def safety_table(inputs):
    rows = []

    def add(item, level, note):
        rows.append({"확인 항목": item, "우선순위": level, "확인 내용": note})

    if inputs["med_anti_coag"]:
        add("항응고제/항혈소판제/NSAIDs", "높음", "활혈·혈류 관련 약재 병용 시 출혈 경향, 멍, 코피, 수술 예정 여부 확인")
    if inputs["med_bp"]:
        add("혈압약", "중간~높음", "승양·온보 처방에서 혈압 상승, 어지럼, 두근거림 확인")
    if inputs["med_diab"]:
        add("당뇨약/인슐린", "중간", "혈당 변화 및 저혈당 증상 확인")
    if inputs["med_diuretic"]:
        add("이뇨제", "중간", "이수·삼습 처방과 병용 시 탈수, 전해질, 갈증 확인")
    if inputs["med_sedative"]:
        add("수면제/진정제/항우울제", "중간~높음", "안신 처방과 병용 시 주간 졸림, 반응 저하 확인")
    if inputs["cond_preg"]:
        add("임신/수유", "높음", "처방·침구·뜸 모두 전문가 확인 필요")
    if inputs["cond_liver"]:
        add("간·신장 질환", "높음", "AST/ALT, Creatinine/eGFR 등 검사값 확인")
    if inputs["cond_dig"]:
        add("만성 소화불량/설사", "중간", "보익·자음 처방의 위장 부담 또는 조습 처방의 건조 반응 확인")
    if inputs["cond_surgery"]:
        add("수술/시술 예정", "높음", "출혈 관련 약재 및 복용 중단 여부 전문가 판단 필요")
    if inputs["cond_neuro"]:
        add("피부 감각저하/당뇨성 말초신경병증", "높음", "뜸 시 화상 위험 주의")

    if not rows:
        add("특이 입력 없음", "일반주의", "복용약, 병력, 알레르기, 검사값은 실제 진료에서 재확인 필요")

    return pd.DataFrame(rows)


def build_acupuncture_groups(formula):
    text = f"{formula['처방 방향']} {formula['전통 변증']} {formula['분류']}"
    groups = []

    if any(k in text for k in ["보기", "비위", "기허", "건비", "승양", "중기"]):
        groups.append("비위·중기 보강군: 족삼리, 중완, 기해, 비수, 위수 등 검토")
    if any(k in text for k in ["보혈", "기혈", "혈허", "쌍보"]):
        groups.append("기혈 보강군: 삼음교, 혈해, 격수, 간수 등 검토")
    if any(k in text for k in ["자음", "보신", "간신", "허열", "정혈"]):
        groups.append("간신·자음 보강군: 태계, 신수, 간수, 삼음교, 관원 등 검토")
    if any(k in text for k in ["안신", "불면", "심계", "불안"]):
        groups.append("안신 조절군: 신문, 내관, 백회, 안면, 삼음교 등 검토")
    if any(k in text for k in ["이수", "삼습", "수습", "부종", "담음", "화담", "조습"]):
        groups.append("수습·담음 조절군: 음릉천, 풍륭, 수분, 중완, 방광수 등 검토")
    if any(k in text for k in ["소간", "해울", "기체", "흉협", "스트레스"]):
        groups.append("소간해울·기기소통군: 태충, 합곡, 양릉천, 내관 등 검토")
    if any(k in text for k in ["활혈", "어혈", "통증", "통락"]):
        groups.append("활혈통락군: 혈해, 격수, 삼음교, 아시혈 등 검토")

    if not groups:
        groups.append("기본 변증 확인 후 혈위군 선택: 실제 혈위는 한의사가 최종 결정")

    return groups


def build_moxa_area_groups(formula, inputs):
    text = f"{formula['처방 방향']} {formula['전통 변증']} {formula['분류']}"
    possible = []
    caution = []

    if any(k in text for k in ["보기", "건비", "비위", "기허", "허한", "온보", "대보원기"]):
        possible.append("비위허한·복부 냉감 확인 시: 중완·기해·관원·족삼리 주변 검토")
    if any(k in text for k in ["보신", "간신", "양허", "하복부", "수족냉증"]):
        possible.append("하복부 냉감·허한 확인 시: 관원·기해·신수 주변 검토")
    if any(k in text for k in ["부종", "수습", "이수", "삼습"]):
        possible.append("양허성 부종 확인 시: 수분·기해·관원 주변 검토")

    if inputs.get("cond_bp_high"):
        caution.append("고혈압·상열감·심계가 있어 강한 온열 자극 주의")
    if inputs.get("cond_neuro"):
        caution.append("피부 감각저하 또는 당뇨성 말초신경병증이 있어 화상 위험 주의")
    if inputs.get("cond_preg"):
        caution.append("임신·수유 관련 상태가 있어 뜸 시술 여부 전문가 확인 필요")
    if any(k in text for k in ["허열", "상열", "실열", "청열"]):
        caution.append("열감·번조·구건·실열 소견이 있으면 강한 뜸 자극 주의")

    if not possible:
        possible.append("뜸은 허한·냉감·양허 소견 확인 후 제한적으로 검토")
    if not caution:
        caution.append("피부 상태, 감각저하, 화상 위험, 실열 여부를 시술 전 확인")

    return possible, caution


def build_integrated_clinical_note(formula, inputs, matches, cautions, trackers):
    acupuncture_groups = build_acupuncture_groups(formula)
    moxa_possible, moxa_caution = build_moxa_area_groups(formula, inputs)
    neijing_df = infer_neijing_context(formula, inputs)
    dongui_df = infer_donguibogam_context(formula, inputs)

    neijing_lines = "\n".join(
        [
            f"- {row['황제내경 해당 개념']}: {row['한의사가 확인할 질문']}"
            for _, row in neijing_df.iterrows()
        ]
    )

    dongui_lines = "\n".join(
        [
            f"- {row['동의보감 해당 편제']} / {row['해당 병증']}: {row['이 소견과 연결되는 이유']}"
            for _, row in dongui_df.iterrows()
        ]
    )

    patient_symp = inputs.get("patient_symp") or "미입력"
    doctor_assessment = inputs.get("doctor_assessment") or "한의사 종합소견 미입력"
    treatment_goal = inputs.get("treatment_goal") or "미입력"
    treatment_memo = inputs.get("treatment_memo") or "미입력"

    note = f"""
[한의사 종합소견 기반 치료계획 초안]

작성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}

1. 한의사 입력 소견
- 주증상/진단명: {patient_symp}
- 종합검진 소견: {doctor_assessment}
- 치료 목표: {treatment_goal}
- 추가 메모: {treatment_memo}

2. 황제내경 해당 개념
{neijing_lines}

3. 동의보감 해당 편제 및 병증
{dongui_lines}

4. 변증 및 치법 방향 초안
- 선택 처방: {formula['처방명']}
- 전통 변증: {formula['전통 변증']}
- 처방 방향: {formula['처방 방향']}
- 치법 요약: {formula['분류']}

5. 한약 처방 검토안
- {formula['처방명']} 계열 검토
- 잘 맞을 수 있는 환자상: {formula['잘 맞는 환자상']}
- 주의하거나 재검토할 환자상: {formula['주의 환자상']}
- 가감·조정 방향: {formula['가감·조정 방향']}
- 감별 처방: {formula['감별 처방']}

6. 침구 치료 방향 초안
- 기본 방향: {formula['침구 방향']}
- 검토 가능한 혈위군:
{chr(10).join(['  - ' + g for g in acupuncture_groups])}
- 주의: 실제 혈위 선택, 자침 깊이, 유침 시간, 자극 강도는 한의사가 최종 결정한다.

7. 뜸 치료 방향 초안
- 기본 방향: {formula['뜸 방향']}
- 뜸 검토 가능 부위군:
{chr(10).join(['  - ' + m for m in moxa_possible])}
- 뜸 주의 조건:
{chr(10).join(['  - ' + c for c in moxa_caution])}
- 주의: 뜸은 화상, 감염, 피부 자극 위험이 있으므로 감각저하·당뇨성 신경병증·실열·상열 여부를 확인한다.

8. 정합 소견
{chr(10).join(['- ' + m for m in matches]) if matches else '- 입력 정보 부족'}

9. 주의 및 재검토 소견
{chr(10).join(['- ' + c for c in cautions]) if cautions else '- 현재 입력상 큰 주의 신호 없음'}

10. 안전성 확인
- 처방 자체 주의: {formula['안전성 주의']}
- 위험 신호: {formula['위험 신호']}

11. 추적 관찰 계획
- 처방별 추적: {formula['추적 관찰']}
- 입력 기반 추적 항목: {', '.join(trackers)}

12. 차트용 요약문
상기 환자는 '{patient_symp}'을 주호소로 내원하였고, 한의사 종합소견상 '{doctor_assessment}'로 기록됨.
황제내경 관점에서는 {', '.join(neijing_df['황제내경 해당 개념'].tolist())} 개념과 연결하여 확인할 수 있으며,
동의보감 관점에서는 {', '.join(dongui_df['동의보감 해당 편제'].tolist())} 편제와 병증 해석을 참고할 수 있음.
현재 {formula['처방명']}은/는 '{formula['전통 변증']}' 및 '{formula['처방 방향']}' 방향에서 검토 가능하나,
'{formula['주의 환자상']}'에 해당하는 소견이 있는 경우 재검토가 필요함.
침구는 '{formula['침구 방향']}' 방향으로 검토하며, 뜸은 '{formula['뜸 방향']}' 원칙하에 허한·냉감·피부상태·감각저하 여부를 확인 후 제한적으로 검토함.
복용 및 시술 후에는 {', '.join(trackers)} 등을 추적 관찰하기로 함.

※ 본 문서는 자동 확정 처방이 아니라 한의사의 최종 판단을 돕는 임상 초안이다.
"""
    return note.strip()


# ============================================================
# 5. 환자 설명 쉬운 말
# ============================================================

EASY_TERMS = {
    "기혈양허": "기운과 혈이 모두 부족한 상태",
    "비위기허": "소화기 기운이 약한 상태",
    "간신음허": "몸의 진액과 정혈이 부족한 상태",
    "허열": "몸이 부족해서 생기는 열감",
    "담음": "몸 안에 정체된 불필요한 수분과 노폐",
    "어혈": "혈액 순환이 막히거나 정체된 상태",
    "중기하함": "몸의 중심 기운이 아래로 처진 상태",
    "습담": "습기와 노폐가 몸 안에 정체된 상태",
    "식체": "음식이 소화되지 않고 막힌 상태",
    "허로": "오래 지쳐 회복력이 떨어진 상태",
}


def patient_friendly_text(formula, trackers):
    easy_indication = formula["전통 변증"]
    explanations = []

    for term, meaning in EASY_TERMS.items():
        if term in formula["전통 변증"] or term in formula["처방 방향"] or term in formula["동의보감 병증"]:
            explanations.append(f"- {term}: {meaning}")

    if not explanations:
        explanations.append("- 현재 처방 방향은 담당 한의사가 환자 상태에 맞춰 설명합니다.")

    text = f"""
{formula['처방명']}은 전통 한의학에서 '{formula['전통 변증']}' 방향에서 검토되는 처방입니다.

쉽게 말하면, 환자의 몸 상태에서 부족한 부분, 막힌 부분, 열감이나 냉감, 소화 상태, 수면 상태 등을 함께 살펴 처방 방향을 정리하는 것입니다.

이 처방과 관련해 쉬운 말로 풀면 다음과 같습니다.

{chr(10).join(explanations)}

이 대시보드는 처방을 자동으로 정하거나 특정 효과를 보장하는 도구가 아닙니다.
담당 한의사가 환자의 증상, 맥과 설진, 복용약, 검사값, 안전성 확인 항목을 함께 보면서 처방 방향과 주의점을 정리하는 데 도움을 주기 위한 설명 도구입니다.

복용 전후에는 다음 항목을 관찰해 주세요.

- {', '.join(trackers)}
- 소화 상태
- 대소변 변화
- 열감이나 두근거림
- 수면 변화
- 기존 복용약과 관련된 변화

현재 처방에서 특히 확인할 점은 다음과 같습니다.

{formula['안전성 주의']}

불편감이 생기거나 기존 증상이 악화되면 임의로 계속 복용하지 말고 담당 한의사에게 알려야 합니다.
"""
    return text.strip()


# ============================================================
# 6. 사이드바 입력
# ============================================================

st.sidebar.header("📝 환자 임상 정보 입력")

patient_symp = st.sidebar.text_input("주증상 및 진단명", placeholder="예: 피로, 소화불량, 불면, 부종, 통증")

st.sidebar.subheader("🧑‍⚕️ 한의사 종합소견")
doctor_assessment = st.sidebar.text_area(
    "한의사 종합검진 소견",
    placeholder=(
        "예: 만성피로, 식욕저하, 안색창백. "
        "맥 허약, 설 담백, 치흔. 소화력 약함. "
        "혈압약 복용 중. 기혈양허 및 비위기허 경향."
    ),
    height=150,
)

treatment_goal = st.sidebar.text_input(
    "치료 목표",
    placeholder="예: 피로 회복, 소화 안정, 수면 개선, 부종 완화",
)

treatment_memo = st.sidebar.text_area(
    "추가 치료 메모",
    placeholder="예: 뜸은 복부 냉감 확인 후 검토. 강자극 침은 피함.",
    height=90,
)

st.sidebar.subheader("🤚 진맥·설진·복진")
col_a, col_b = st.sidebar.columns(2)

with col_a:
    mac_depth = st.selectbox("맥위", ["선택안함", "부맥", "중맥", "침맥"])
    mac_speed = st.selectbox("맥속", ["선택안함", "지맥", "평맥", "삭맥"])
    mac_force = st.selectbox("맥력", ["선택안함", "허맥", "실맥", "약맥", "무력"])

with col_b:
    mac_shape = st.selectbox("맥형", ["선택안함", "현", "활", "세", "긴", "완", "대"])
    tongue_color = st.selectbox("설질", ["선택안함", "담", "홍", "암", "자", "반점"])
    tongue_coat = st.selectbox("설태", ["선택안함", "박태", "후태", "백태", "황니태", "소태/무태"])

col_c, col_d = st.sidebar.columns(2)

with col_c:
    tongue_fluid = st.selectbox("진액/형태", ["선택안함", "건조", "윤택", "치흔", "부종감"])

with col_d:
    abd_exam = st.selectbox("복진", ["선택안함", "복부 냉감", "압통/저항", "더부룩함/가스", "복직근 긴장"])

st.sidebar.subheader("🚨 복용약")
med_anti_coag = st.sidebar.checkbox("항응고제/항혈소판제/NSAIDs")
med_bp = st.sidebar.checkbox("혈압약")
med_diab = st.sidebar.checkbox("당뇨약/인슐린")
med_diuretic = st.sidebar.checkbox("이뇨제")
med_sedative = st.sidebar.checkbox("수면제/진정제/항우울제")
med_immuno = st.sidebar.checkbox("스테로이드/면역억제제")
med_cancer = st.sidebar.checkbox("항암제/표적치료제")
med_suppl = st.sidebar.checkbox("다른 한약/건기식 병용")

st.sidebar.subheader("🚨 환자 상태")
cond_preg = st.sidebar.checkbox("임신/수유")
cond_frail = st.sidebar.checkbox("소아/고령자/허약자")
cond_liver = st.sidebar.checkbox("간질환 또는 신장질환 병력")
cond_bp_high = st.sidebar.checkbox("고혈압/상열감/심계")
cond_dig = st.sidebar.checkbox("만성 소화불량/설사")
cond_allergy = st.sidebar.checkbox("알레르기/약물 과민반응")
cond_surgery = st.sidebar.checkbox("수술/시술 예정")
cond_neuro = st.sidebar.checkbox("피부 감각저하/당뇨성 말초신경병증")

st.sidebar.subheader("🧪 검사값 및 메모")
lab_ast_alt = st.sidebar.text_input("AST/ALT")
lab_creatinine = st.sidebar.text_input("Creatinine/eGFR")
lab_bp_val = st.sidebar.text_input("혈압")
lab_current_meds = st.sidebar.text_area("현재 복용약 상세")

selected_formula = st.sidebar.selectbox("분석할 한의학 처방 선택", FORMULA_DF["처방명"].tolist())

analyze_btn = st.sidebar.button("처방 분석 및 소견서 생성", type="primary")

inputs = {
    "patient_symp": patient_symp,
    "doctor_assessment": doctor_assessment,
    "treatment_goal": treatment_goal,
    "treatment_memo": treatment_memo,
    "mac_depth": mac_depth,
    "mac_speed": mac_speed,
    "mac_force": mac_force,
    "mac_shape": mac_shape,
    "tongue_color": tongue_color,
    "tongue_coat": tongue_coat,
    "tongue_fluid": tongue_fluid,
    "abd_exam": abd_exam,
    "med_anti_coag": med_anti_coag,
    "med_bp": med_bp,
    "med_diab": med_diab,
    "med_diuretic": med_diuretic,
    "med_sedative": med_sedative,
    "med_immuno": med_immuno,
    "med_cancer": med_cancer,
    "med_suppl": med_suppl,
    "cond_preg": cond_preg,
    "cond_frail": cond_frail,
    "cond_liver": cond_liver,
    "cond_bp_high": cond_bp_high,
    "cond_dig": cond_dig,
    "cond_allergy": cond_allergy,
    "cond_surgery": cond_surgery,
    "cond_neuro": cond_neuro,
}


# ============================================================
# 7. 메인 렌더링
# ============================================================

if not analyze_btn:
    st.info("👈 좌측에서 환자 정보, 한의사 종합소견, 처방을 입력한 뒤 '처방 분석 및 소견서 생성'을 눌러주세요.")
    st.stop()

formula = FORMULA_DF[FORMULA_DF["처방명"] == selected_formula].iloc[0].to_dict()

matches, cautions, trackers = build_match_logic(formula, inputs)
level, level_comment = fit_level(matches, cautions)

neijing_df = infer_neijing_context(formula, inputs)
dongui_df = infer_donguibogam_context(formula, inputs)

tab_names = [
    "1. 한의사용 통합 요약",
    "2. 소견서·치료계획",
    "3. 황제내경·동의보감 해당",
    "4. 전통 처방 Core",
    "5. 진맥·설진 대조",
    "6. 침구 치료 방향",
    "7. 뜸 치료 방향",
    "8. 처방 방향 6축",
    "9. 처방 감별·가감",
    "10. 안전성 확인",
    "11. 환자 설명문",
]

if show_research:
    tab_names.append("12. 연구자용 부록")

tabs = st.tabs(tab_names)
tab = dict(zip(tab_names, tabs))


# ============================================================
# 탭 1. 통합 요약
# ============================================================

with tab["1. 한의사용 통합 요약"]:
    st.header(f"🧑‍⚕️ [{selected_formula}] 한의사용 통합 요약")

    c1, c2, c3 = st.columns(3)
    c1.metric("정합도 판정", level)
    c2.metric("정합 소견 수", len(matches))
    c3.metric("주의 소견 수", len(cautions))
    st.info(level_comment)

    st.subheader("한의사 종합소견")
    st.info(doctor_assessment or "한의사 종합소견이 입력되지 않았습니다.")

    st.subheader("처방 핵심 방향")
    st.success(axis_summary_sentence(formula))
    st.markdown(f"**전통 변증:** {formula['전통 변증']}")
    st.markdown(f"**처방 방향:** {formula['처방 방향']}")

    st.subheader("황제내경·동의보감 연결 요약")
    c4, c5 = st.columns(2)
    with c4:
        st.markdown("**황제내경 해당 개념**")
        st.dataframe(neijing_df, use_container_width=True, hide_index=True)
    with c5:
        st.markdown("**동의보감 해당 편제**")
        st.dataframe(dongui_df, use_container_width=True, hide_index=True)

    st.subheader("정합 소견 / 주의 소견")
    c6, c7 = st.columns(2)
    with c6:
        st.success("\n".join([f"- {m}" for m in matches]) if matches else "정합 소견을 보려면 입력 정보를 보강하세요.")
    with c7:
        st.error("\n".join([f"- {c}" for c in cautions]) if cautions else "현재 입력상 큰 주의 소견은 표시되지 않았습니다.")

    st.subheader("추적 관찰")
    st.info(f"{formula['추적 관찰']}\n\n입력 기반 추적 항목: {', '.join(trackers)}")


# ============================================================
# 탭 2. 소견서·치료계획
# ============================================================

with tab["2. 소견서·치료계획"]:
    st.header("📝 소견서·치료계획 초안 패널")
    st.warning(
        "이 패널은 한의사가 입력한 종합소견을 바탕으로 한약·침구·뜸·추적관찰을 하나의 치법 방향으로 정리한 초안입니다. "
        "자동 확정 처방이 아닙니다."
    )

    integrated_note = build_integrated_clinical_note(
        formula=formula,
        inputs=inputs,
        matches=matches,
        cautions=cautions,
        trackers=trackers,
    )

    st.text_area("차트용 소견서·치료계획 초안", integrated_note, height=760)

    st.download_button(
        "소견서·치료계획 초안 다운로드",
        data=integrated_note,
        file_name=f"{selected_formula}_clinical_plan_draft.txt",
        mime="text/plain",
    )

    st.subheader("검토 가능한 혈위군")
    for group in build_acupuncture_groups(formula):
        st.markdown(f"- {group}")

    st.subheader("뜸 검토 가능 부위군 및 주의 조건")
    moxa_possible, moxa_caution = build_moxa_area_groups(formula, inputs)

    st.markdown("**뜸 검토 가능 부위군**")
    for item in moxa_possible:
        st.markdown(f"- {item}")

    st.markdown("**뜸 주의 조건**")
    for item in moxa_caution:
        st.markdown(f"- {item}")


# ============================================================
# 탭 3. 황제내경·동의보감 해당
# ============================================================

with tab["3. 황제내경·동의보감 해당"]:
    st.header("📚 황제내경·동의보감 해당 해석 패널")
    st.warning(
        "이 패널은 황제내경·동의보감이 현대 생물학적 기전을 증명한다는 뜻이 아닙니다. "
        "한의사가 입력한 소견을 전통 의학의 개념과 편제에 맞춰 정리하는 원전 주석층입니다."
    )

    st.subheader("1. 황제내경 해당 개념")
    st.dataframe(neijing_df, use_container_width=True, hide_index=True)

    st.subheader("2. 동의보감 해당 편제 및 병증")
    st.dataframe(dongui_df, use_container_width=True, hide_index=True)

    st.subheader("3. 한의사용 해석")
    st.info(
        "소견서에 입력된 증상과 변증을 황제내경의 음양·오행·장부·기혈진액·승강출입·표본중기 개념으로 다시 정리하고, "
        "동의보감의 병증 편제와 연결하여 처방·침구·뜸 방향이 같은 치법을 향하는지 확인합니다."
    )


# ============================================================
# 탭 4. 전통 처방 Core
# ============================================================

with tab["4. 전통 처방 Core"]:
    st.header("📌 전통 처방 Core 패널")
    st.info(f"**전통 변증 방향:** {formula['전통 변증']}")
    st.markdown(f"**처방 분류:** {formula['분류']}")
    st.markdown(f"**구성 약재:** {formula['구성 약재']}")
    st.markdown(f"**핵심 방향:** {formula['처방 방향']}")

    st.subheader("처방 구조 해석")
    st.markdown(
        f"""
- 이 처방은 `{formula['처방 방향']}` 방향에서 검토합니다.
- 한 가지 증상만 억누르는 접근이 아니라, 여러 약재가 함께 변증 방향을 조절하는 복합 처방입니다.
- 실제 적용은 증상, 맥상, 설진, 복진, 병력, 복용약, 검사값을 종합하여 판단해야 합니다.
"""
    )


# ============================================================
# 탭 5. 진맥·설진
# ============================================================

with tab["5. 진맥·설진 대조"]:
    st.header("🤚 진맥·설진 대조 패널")
    st.info(
        "진맥·설진 정보는 대시보드가 자동 판정하는 값이 아니라, "
        "한의사가 직접 확인한 소견과 처방 방향을 대조하기 위한 참고 정보입니다."
    )

    st.success(f"**선택 처방의 목표 소견:** {formula['진맥·설진 목표']}")

    input_findings = pd.DataFrame([
        {"항목": "맥위", "입력": mac_depth},
        {"항목": "맥속", "입력": mac_speed},
        {"항목": "맥력", "입력": mac_force},
        {"항목": "맥형", "입력": mac_shape},
        {"항목": "설질", "입력": tongue_color},
        {"항목": "설태", "입력": tongue_coat},
        {"항목": "진액/형태", "입력": tongue_fluid},
        {"항목": "복진", "입력": abd_exam},
    ])
    st.dataframe(input_findings, use_container_width=True, hide_index=True)

    st.subheader("정합/불일치 해석")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**정합 소견**")
        st.markdown("\n".join([f"- {m}" for m in matches]) if matches else "- 입력 정보 부족")
    with c2:
        st.markdown("**주의 소견**")
        st.markdown("\n".join([f"- {c}" for c in cautions]) if cautions else "- 현재 입력상 큰 주의 소견 없음")


# ============================================================
# 탭 6. 침구
# ============================================================

with tab["6. 침구 치료 방향"]:
    st.header("📍 침구 치료 방향 패널")
    st.warning(
        "본 패널은 자동 침 처방이 아니라, 선택 처방의 변증 방향에 따라 "
        "한의사가 검토할 수 있는 침구 치료 원칙과 주의점을 정리한 것입니다."
    )

    st.info(formula["침구 방향"])

    st.subheader("검토 가능한 혈위군")
    for group in build_acupuncture_groups(formula):
        st.markdown(f"- {group}")

    st.subheader("침구 시 확인할 임상 포인트")
    st.markdown(
        """
- 처방 방향과 침 자극 방향이 서로 충돌하지 않는지 확인
- 허증 환자에게 과도한 사법·강자극을 쓰지 않도록 주의
- 실열·상열감 환자에게 승양·온보 자극이 과하지 않은지 확인
- 복부 냉감, 더부룩함, 압통 등 복진과 함께 판단
- 실제 혈위 선택, 자침 깊이, 유침 시간, 자극 강도는 한의사의 판단으로 결정
"""
    )


# ============================================================
# 탭 7. 뜸
# ============================================================

with tab["7. 뜸 치료 방향"]:
    st.header("🔥 뜸 치료 방향 패널")
    st.error(
        "뜸은 화상, 알레르기, 감염 위험이 있으므로 피부 감각저하, 당뇨성 말초신경병증, "
        "실열·상열 환자에게 주의가 필요합니다."
    )

    st.warning(formula["뜸 방향"])

    moxa_possible, moxa_caution = build_moxa_area_groups(formula, inputs)

    st.subheader("뜸 검토 가능 부위군")
    for item in moxa_possible:
        st.markdown(f"- {item}")

    st.subheader("뜸 주의 조건")
    for item in moxa_caution:
        st.markdown(f"- {item}")

    st.subheader("뜸 치료 전 확인 사항")
    st.markdown(
        """
- 피부 감각 저하 여부
- 당뇨성 말초신경병증 여부
- 피부질환, 상처, 감염 여부
- 실열, 허열, 상열감 여부
- 임신 여부
- 고령자·허약자의 화상 위험
- 시술 후 발적, 물집, 통증, 감염 징후
"""
    )


# ============================================================
# 탭 8. 처방 방향 6축
# ============================================================

with tab["8. 처방 방향 6축"]:
    st.header("🧭 처방 방향 6축 해석 패널")
    st.info(
        "이 패널은 연구자용 구조를 한의사가 이해할 수 있는 임상 언어로 번역한 화면입니다. "
        "처방을 보충·수렴·승양·배출·소통·완충의 6개 방향축으로 나누어 봅니다."
    )

    st.success(axis_summary_sentence(formula))
    st.dataframe(axis_profile(formula), use_container_width=True, hide_index=True)


# ============================================================
# 탭 9. 감별·가감
# ============================================================

with tab["9. 처방 감별·가감"]:
    st.header("🔁 처방 감별·가감 패널")

    st.subheader("감별 처방")
    st.info(formula["감별 처방"])

    st.subheader("가감·조정 검토 방향")
    st.markdown(formula["가감·조정 방향"])

    st.subheader("주요 처방 비교표")
    priority = [
        "육미지황환", "보중익기탕", "산조인탕", "귀비탕", "팔진탕",
        "십전대보탕", "사물탕", "사군자탕", "평위산", "소요산", "이진탕", "오령산",
        selected_formula,
    ]

    diff_rows = []
    for _, row in FORMULA_DF.iterrows():
        if row["처방명"] in priority:
            diff_rows.append(
                {
                    "처방": row["처방명"],
                    "전통 변증": row["전통 변증"],
                    "강한 방향": row["처방 방향"],
                    "대표 확인 소견": row["잘 맞는 환자상"],
                    "주의 환자상": row["주의 환자상"],
                }
            )

    diff_df = pd.DataFrame(diff_rows).drop_duplicates()

    def highlight_selected(row):
        return ["background-color: #d1e7dd" if row["처방"] == selected_formula else "" for _ in row]

    st.dataframe(diff_df.style.apply(highlight_selected, axis=1), use_container_width=True, hide_index=True)


# ============================================================
# 탭 10. 안전성
# ============================================================

with tab["10. 안전성 확인"]:
    st.header("🚨 안전성 확인 패널")
    st.warning("이 경고는 처방 금지 판정이 아니라, 실제 복용 전 추가 확인이 필요한 항목을 표시한 것입니다.")

    st.subheader("입력 정보 기반 안전성 체크")
    st.dataframe(safety_table(inputs), use_container_width=True, hide_index=True)

    st.subheader("처방 자체 주의")
    st.markdown(f"- {formula['안전성 주의']}")
    st.markdown(f"- **위험 신호:** {formula['위험 신호']}")

    st.subheader("검사값 및 복용약 메모")
    lab_df = pd.DataFrame([
        {"항목": "AST/ALT", "입력값": lab_ast_alt or "미입력"},
        {"항목": "Creatinine/eGFR", "입력값": lab_creatinine or "미입력"},
        {"항목": "혈압", "입력값": lab_bp_val or "미입력"},
        {"항목": "현재 복용약", "입력값": lab_current_meds or "미입력"},
    ])
    st.dataframe(lab_df, use_container_width=True, hide_index=True)


# ============================================================
# 탭 11. 환자 설명문
# ============================================================

with tab["11. 환자 설명문"]:
    st.header("💬 환자 설명문 패널")

    patient_text = patient_friendly_text(formula, trackers)

    st.text_area("환자 설명문", patient_text, height=430)

    st.download_button(
        "환자 설명문 다운로드",
        data=patient_text,
        file_name=f"{selected_formula}_patient_explanation.txt",
        mime="text/plain",
    )


# ============================================================
# 연구자용 부록
# ============================================================

if show_research:
    with tab["12. 연구자용 부록"]:
        st.header("🔬 연구자용 부록")
        st.warning("이 탭은 연구자용입니다. 한의사용 기본 화면에서는 직접 볼 필요가 없습니다.")

        st.markdown(
            """
            | 연구자용 표현 | 한의사용 번역 |
            |---|---|
            | 64큐브 / Q6 Core | 처방 방향 6축 |
            | H(3,4) Extension | 처방 주변 변화 가능성 |
            | Polyhedron Layer | 보사·승강출입 균형 |
            | Codon / Amino Acid | 연구자용 배경 주석 |
            | Bit transition | 변증 방향 전환 가능성 |
            | Zone transition | 처방 방향이 다른 축으로 넘어가는 지점 |
            """
        )

        st.info(
            "연구자용 구조는 처방 효과를 증명하거나 약재가 유전자를 조절한다는 뜻이 아닙니다. "
            "전통 처방 방향을 정보기하학적으로 주석화하는 보조 구조입니다."
        )

        st.subheader("처방 방향 6축 원자료")
        st.dataframe(axis_profile(formula), use_container_width=True, hide_index=True)

        st.subheader("황제내경·동의보감 매핑 원자료")
        st.dataframe(neijing_df, use_container_width=True, hide_index=True)
        st.dataframe(dongui_df, use_container_width=True, hide_index=True)
