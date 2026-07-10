import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# 한의 임상 의사결정 지원 대시보드 (V_MAX 완전판)
# - 12개 핵심 처방 완벽 데이터 내장 (Placeholder 제로)
# - 진맥/설진 동적 정합도 평가
# - 침/뜸 치료 방향 및 안전성 통합
# ============================================================

st.set_page_config(
    page_title="한의 임상 의사결정 지원 대시보드",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

def topic_josa(word: str) -> str:
    if not word: return "은/는"
    last = word[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        return "은" if (code - 0xAC00) % 28 else "는"
    return "은/는"

def safe_join(items, sep=", "):
    return sep.join([str(x) for x in items if str(x).strip()])

def parse_bp(bp_text: str):
    import re
    nums = re.findall(r"\d+", str(bp_text or ""))
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    return None, None

def is_bp_warning(bp_text, bp_med_checked=False, bp_state_checked=False):
    sbp, dbp = parse_bp(bp_text)
    value_high = False
    if sbp is not None and dbp is not None:
        value_high = sbp >= 140 or dbp >= 90
    return bool(bp_med_checked or bp_state_checked or value_high)

FORMULAS = {
    "육미지황환": {
        "category": "보음·자음 처방",
        "pattern": "간신음허, 허열도한, 정혈 부족",
        "direction": "자음, 보신, 수렴, 허열 완충, 수습 조절",
        "core_axes": ["보충축", "수렴·안정축", "완충·조화축"],
        "herbs": "숙지황, 산수유, 산약, 복령, 택사, 목단피",
        "best_for": "요슬산연, 도한, 오심번열, 구건, 만성 피로, 음허성 열감",
        "poor_fit": "설태 후니, 식체·습담이 뚜렷함, 설사가 잦음, 실열·습열이 강함",
        "differential": "보중익기탕: 기허·중기하함 중심 / 귀비탕: 심비양허·불면·건망 중심 / 오령산: 수습정체·소변불리 중심",
        "modification": "소화불량이 강하면 숙지황 부담 확인, 수습이 강하면 이수·건비 방향 검토, 허열이 강하면 청허열 방향 검토",
        "acu_detail": "간·신 축 보강, 정혈·진액 보존, 허열 완충, 수습 조절 방향. 강자극보다 보법 또는 평보평사 중심.",
        "moxa_detail": "냉감·허한이 동반될 때만 검토. 오심번열, 도한, 구건, 실열 소견이 강하면 강한 온열 자극 주의.",
        "followup": "3~7일: 소화불량·설사·부종 확인 / 2~4주: 피로감·도한·열감·수면·소변 상태 확인",
        "pulse_target": "침세, 세삭, 허맥",
        "tongue_target": "홍, 담홍, 소태, 건조",
        "core_points": ["KI3", "BL23", "BL18", "SP6", "CV4", "CV6", "KI6"],
        "q6_annotation": "보존형 변화 및 수렴형 완충 방향 주도",
        "polyhedron": "삼보삼사 대칭 구조, 수렴/하행 안정 중심",
        "h34_extension": "- 보음 과잉으로 인한 소화불량 방향\n- 수습 조절 미흡 시 부종 잔존 방향\n- 허열 완충 한계 시 상열감 발현 방향",
        "neijing_map": "- 음양: 부족한 음분과 과한 허열의 균형 확인\n- 장부: 간·신·정혈의 소모 확인\n- 승강출입: 수렴과 저장 기능 약화 확인",
        "dongui_map": "- 신(腎), 허로(虛勞): 간신 부족, 정혈 고갈 병증\n- 내상: 소화력 약화 시 주의"
    },
    "보중익기탕": {
        "category": "보기·승양 처방",
        "pattern": "비위기허, 중기하함, 기허 피로",
        "direction": "보기, 승양, 중기 보강, 비위 회복",
        "core_axes": ["보충축", "승양·상승축", "완충·조화축"],
        "herbs": "황기, 인삼, 백출, 감초, 당귀, 진피, 승마, 시호",
        "best_for": "피로, 기단, 식욕저하, 자한, 내장하수감, 말하기 힘듦",
        "poor_fit": "상열감, 고혈압, 심계, 불면, 실열, 습열, 식적이 뚜렷한 경우",
        "differential": "사군자탕: 순수 비위기허 / 십전대보탕: 기혈양허·허한 강함 / 소요산: 간울·스트레스성 소화불량",
        "modification": "상열감이 있으면 승양 방향 과잉 주의, 식체가 있으면 소도·화위 방향 먼저 검토",
        "acu_detail": "비·위 축 보강, 중기 보강, 승양 방향. 고혈압·심계가 있으면 강한 상승 자극 주의.",
        "moxa_detail": "비위허한, 복부 냉감, 기허 피로가 뚜렷하면 검토. 상열감·불면·혈압 상승 경향이 있으면 주의.",
        "followup": "3~7일: 식욕·피로·소화상태 확인 / 1~2주: 혈압·두근거림·불면·상열감 확인",
        "pulse_target": "허맥, 약맥, 완맥, 무력맥",
        "tongue_target": "담백, 치흔, 백태",
        "core_points": ["ST36", "CV12", "CV6", "BL20", "BL21", "GV20"],
        "q6_annotation": "발산/상승 및 전환형 변화 주도",
        "polyhedron": "강력한 상승(승양) 방향 우세, 보법 중심 구조",
        "h34_extension": "- 승양 과잉 방향 (상열감, 두근거림, 혈압상승)\n- 보익 과잉 방향 (식체, 복부팽만)\n- 약물 상호작용 (혈당/혈압 변동)",
        "neijing_map": "- 승강출입: 처진 기운을 올리는 상승 방향\n- 장부: 비폐 기허 확인\n- 표본중기: 피로의 근본 원인(본) 파악",
        "dongui_map": "- 내상(內傷), 비위(脾胃): 음식노상, 기허발열\n- 기문(氣門): 기단, 무력감"
    },
    "산조인탕": {
        "category": "안신·양혈 처방",
        "pattern": "허번불면, 심신불안, 음혈 부족",
        "direction": "수렴, 안신, 내부 안정, 허열 완충",
        "core_axes": ["수렴·안정축", "완충·조화축", "보충축"],
        "herbs": "산조인, 지모, 복령, 천궁, 감초",
        "best_for": "잠은 오나 깊이 못 자는 불면, 심계, 불안, 피로, 허번",
        "poor_fit": "실열성 불면, 담열, 과도한 졸림, 진정제 병용으로 반응 저하가 있는 경우",
        "differential": "귀비탕: 불면+건망+식욕저하 / 온담탕: 담열·흉민·불안 / 천왕보심단: 음허화왕·구건·심번",
        "modification": "담음이 강하면 화담 방향 검토, 주간 졸림이 있으면 진정 과잉 주의",
        "acu_detail": "심·간·담 축, 안신, 수렴, 내부 안정 방향. 과도한 자극보다 완만한 조절 중심.",
        "moxa_detail": "허한성 불면·냉감이 동반될 때만 검토. 번조·열감·구건이 뚜렷하면 강한 뜸 자극 주의.",
        "followup": "3~7일: 수면의 깊이·입면시간·주간 졸림 확인 / 2주: 불안·심계·피로도 확인",
        "pulse_target": "세맥, 약맥, 현세맥",
        "tongue_target": "담홍, 홍, 소태",
        "core_points": ["HT7", "PC6", "SP6", "KI3", "GV20", "BL15"],
        "q6_annotation": "수렴·안정 방향 중심, 내부 안정 및 완충 축",
        "polyhedron": "내부 수렴 방향 강함, 발산 억제 구조",
        "h34_extension": "- 진정 과잉 방향 (주간 졸림, 무기력)\n- 허열·번조 악화 방향 (실열성 불면 감별 요망)\n- 위장관 부담 방향 (소화불량)",
        "neijing_map": "- 신지·정신: 심계, 불안, 다몽 확인\n- 음양: 양이 음으로 수렴되지 못하는 불교(不交) 상태",
        "dongui_map": "- 몽(夢), 몽매: 불면, 다몽, 심신불안\n- 혈문: 혈허성 불면과 어지럼"
    },
    "귀비탕": {
        "category": "심비양허·보혈안신 처방",
        "pattern": "심비양허, 불면, 건망, 사려과다",
        "direction": "보기, 보혈, 안신, 심비 보강",
        "core_axes": ["보충축", "수렴·안정축", "완충·조화축"],
        "herbs": "인삼, 황기, 백출, 복령, 당귀, 용안육, 산조인, 원지, 감초, 목향",
        "best_for": "불면, 건망, 심계, 피로, 식욕저하, 생각이 많고 쉽게 지치는 상태",
        "poor_fit": "습담·식체가 뚜렷함, 열감·번조가 강함, 과도한 졸림",
        "differential": "산조인탕: 허번불면 중심 / 보중익기탕: 중기하함 중심 / 팔진탕: 기혈양허 중심",
        "modification": "소화력이 약하면 보익·안신 약재 부담 확인, 담열성 불면이면 온담탕 감별",
        "acu_detail": "심비 보강, 안신, 기혈 보충 방향. 소화 상태와 수면 상태를 함께 봄. 평보평사 중심.",
        "moxa_detail": "수족냉증·복부 냉감이 있으면 검토. 열감·번조가 강하면 주의.",
        "followup": "1주: 수면·식욕·심계 확인 / 2~4주: 건망·피로·소화력 확인",
        "pulse_target": "세약맥, 허맥",
        "tongue_target": "담백, 치흔, 백태",
        "core_points": ["ST36", "SP6", "HT7", "PC6", "BL20", "BL17", "GV20"],
        "q6_annotation": "보충·수렴 방향, 심비 안정과 기혈 보강 주도",
        "polyhedron": "보혈·자음과 수렴 안정 방향 구조",
        "h34_extension": "- 보익 과잉 방향 (식체, 복부팽만)\n- 진정 과잉 방향 (졸림, 무기력)\n- 습담 정체 발생 방향",
        "neijing_map": "- 신지·정신: 사려 과다로 인한 소모\n- 장부: 심비의 기혈 생성과 저장 둔화",
        "dongui_map": "- 건망(健忘), 몽(夢): 수면불량, 심신허약\n- 허로: 정신적 피로 누적"
    },
    "소요산": {
        "category": "소간해울·조화 처방",
        "pattern": "간울비허, 흉협고만, 스트레스성 소화불량",
        "direction": "소간, 해울, 건비, 조화",
        "core_axes": ["소통·전환축", "완충·조화축", "보충축"],
        "herbs": "시호, 당귀, 작약, 백출, 복령, 감초, 박하, 생강",
        "best_for": "흉협고만, 스트레스성 소화불량, 월경 전 불편, 피로, 감정기복",
        "poor_fit": "극심한 기허, 음허화왕, 상열감이 심한 경우",
        "differential": "가미소요산: 열감 뚜렷 / 귀비탕: 불면·사려과다 / 평위산: 순수 식체",
        "modification": "열감이 강하면 청열(가미소요산) 방향, 식체가 강하면 화위 방향 보강",
        "acu_detail": "소간해울, 기기 소통, 비위 조화 방향. 태충·양릉천 등 소양/궐음경 중심 검토.",
        "moxa_detail": "허한·냉감이 동반될 때 제한 검토. 울열·상열감·안면홍조가 뚜렷하면 뜸 주의.",
        "followup": "3~7일: 흉협답답함·소화상태 확인 / 월경주기: 감정기복·생리통 변화 확인",
        "pulse_target": "현맥, 현세맥",
        "tongue_target": "담홍, 박태, 변동성",
        "core_points": ["LR3", "GB34", "PC6", "SP6", "ST36"],
        "q6_annotation": "소통·전환과 조화 축 중심, 간비 불화 조절",
        "polyhedron": "울체된 기운을 부드럽게 흩어주는 소통형 구조",
        "h34_extension": "- 화열(火熱) 변동 방향 (상열감 심화)\n- 기허 심화 방향 (소간 과잉으로 인한 피로)\n- 혈허 변동 방향",
        "neijing_map": "- 오행 생극: 목극토(木剋土), 간기 울결이 비위를 손상\n- 승강출입: 기기 소통 막힘",
        "dongui_map": "- 울증(鬱證), 화(火), 부인(婦人): 정서적 억눌림, 생리 전후 증후군"
    },
    "십전대보탕": {
        "category": "기혈쌍보·온보 처방",
        "pattern": "기혈양허, 허로, 허한",
        "direction": "대보원기, 기혈쌍보, 온보",
        "core_axes": ["보충축", "승양·상승축", "수렴·안정축"],
        "herbs": "인삼, 백출, 복령, 감초, 숙지황, 당귀, 작약, 천궁, 황기, 육계",
        "best_for": "기혈양허, 허로, 수술 후 회복기, 면색창백, 수족냉증, 체력저하",
        "poor_fit": "실열, 고혈압, 상열감, 안면홍조, 염증성 열감, 식체",
        "differential": "팔진탕: 온보(육계/황기) 제외 기혈쌍보 / 보중익기탕: 승양 중심 / 사물탕: 혈허 중심",
        "modification": "열감이 있으면 온보 과잉 주의(팔진탕 감별), 소화가 약하면 보익 부담 확인",
        "acu_detail": "기혈 쌍보, 전신 회복, 허한 보강 방향. 강한 사법 배제, 보법 위주.",
        "moxa_detail": "허한·냉감·체력저하가 뚜렷하면 적극 검토. 고혈압·상열감·불면·실열은 뜸 금지.",
        "followup": "1주: 소화장애·상열감·혈압 상승 유무 확인 / 2~4주: 피로·냉감·체력 변화 관찰",
        "pulse_target": "허대, 약맥, 세무력",
        "tongue_target": "담백, 치흔, 습윤",
        "core_points": ["ST36", "CV6", "CV4", "SP6", "BL20", "BL23"],
        "q6_annotation": "강력한 보충·수렴 및 승양 축 통합 주도",
        "polyhedron": "기혈 쌍보 및 온보 중심, 사법(瀉法) 완전 배제 구조",
        "h34_extension": "- 온보 과잉 방향 (상열, 혈압 상승, 염증 악화)\n- 소화 부담 방향 (더부룩함, 식체)",
        "neijing_map": "- 음양: 허한(虛寒)과 기혈 부족 극심 상태\n- 표본중기: 리(裏)의 근본 원기 고갈",
        "dongui_map": "- 허로(虛勞), 기혈(氣血): 대병 후 쇠약, 산후/수술후 회복"
    },
    "팔진탕": {
        "category": "기혈쌍보 처방",
        "pattern": "기혈양허, 만성피로, 안색창백",
        "direction": "보기, 보혈, 기혈쌍보, 균형 보강",
        "core_axes": ["보충축", "완충·조화축"],
        "herbs": "인삼, 백출, 복령, 감초, 숙지황, 당귀, 백작약, 천궁",
        "best_for": "피로, 안색창백, 어지럼, 식욕저하, 회복력 저하",
        "poor_fit": "식체, 습담, 실열, 상열감, 보약 복용 후 체하는 환자",
        "differential": "십전대보탕: 온보력 더 강함 / 사물탕: 혈허 중심 / 사군자탕: 기허 중심",
        "modification": "소화력이 약하면 건비 방향 선행, 열감이 있으면 온보 처방과 감별",
        "acu_detail": "기혈 보강, 비위 보강, 전신 순환 조절 방향. 평보평사 중심.",
        "moxa_detail": "허한·냉감·무력감이 있으면 검토 가능. 실열·상열·피부 과민이 있으면 주의.",
        "followup": "1주: 소화상태·식후 팽만감 확인 / 2주: 피로 회복, 안색, 어지럼 완화 확인",
        "pulse_target": "허맥, 세약맥",
        "tongue_target": "담백, 치흔, 백태",
        "core_points": ["ST36", "CV12", "CV6", "SP6", "BL20", "BL17"],
        "q6_annotation": "보충·완충 방향 중심, 기혈 동시 조화",
        "polyhedron": "기혈 쌍보, 한열 치우침 없는 평보평사 구조",
        "h34_extension": "- 소화 부담 방향 (숙지황 등 위장 장애)\n- 기체·습담 발생 방향 (운화력 저하 시)",
        "neijing_map": "- 기혈진액: 기와 혈의 동시 부족\n- 음양: 기(양)와 혈(음)의 균형",
        "dongui_map": "- 허로, 기혈: 일반적인 만성 피로와 영양 부족"
    },
    "사물탕": {
        "category": "보혈 기본 처방",
        "pattern": "혈허, 영혈 부족, 어지럼, 월경 허증",
        "direction": "보혈, 화혈, 혈맥 조화",
        "core_axes": ["보충축", "소통·전환축", "완충·조화축"],
        "herbs": "숙지황, 당귀, 천궁, 백작약",
        "best_for": "안색창백, 어지럼, 혈허성 피로, 월경 후 허약, 손발 저림",
        "poor_fit": "설사, 식체, 습담, 복부팽만, 어혈·실증이 강한 경우",
        "differential": "팔진탕: 기혈양허 / 당귀작약산: 혈허+수독 / 십전대보탕: 극심 허한",
        "modification": "소화력이 약하면 숙지황 부담 확인, 어혈 뚜렷하면 활혈(도홍사물탕) 방향 검토",
        "acu_detail": "보혈과 혈맥 조화, 간비 조절. 삼음교·혈해·격수 계열 중심.",
        "moxa_detail": "혈허성 하복부 냉감이 있으면 제한 검토. 출혈 경향·열감은 뜸 주의.",
        "followup": "월경주기: 생리량 및 통증 관찰 / 1주: 어지럼·소화력·대변 무름 확인",
        "pulse_target": "세맥, 삽맥",
        "tongue_target": "담백, 건조, 혈색 부족",
        "core_points": ["SP6", "BL17", "BL18", "ST36", "LR8"],
        "q6_annotation": "보혈·순환 조화 축 중심",
        "polyhedron": "음혈 보충 및 혈맥 소통 지향 구조",
        "h34_extension": "- 소화 장애 방향 (숙지황 설사, 묽은 변)\n- 어혈 심화 방향 (소통 부족 시)\n- 출혈 경향 변동 (천궁/당귀 과잉 시)",
        "neijing_map": "- 장부·기혈진액: 혈의 절대적 부족과 흐름 둔화",
        "dongui_map": "- 혈문, 부인문: 조경(調經) 및 산후/월경 후 영양 보충"
    },
    "사군자탕": {
        "category": "보기·건비 기본 처방",
        "pattern": "비위기허, 식소무력, 기단무력",
        "direction": "보기, 건비, 비위 보강, 소화 흡수 회복",
        "core_axes": ["보충축", "완충·조화축"],
        "herbs": "인삼, 백출, 복령, 감초",
        "best_for": "식욕저하, 쉽게 피로함, 말하기 힘듦, 대변이 묽음, 안색 누렇고 무력함",
        "poor_fit": "식체·습담이 뚜렷하거나 실열·상열감이 강한 경우",
        "differential": "보중익기탕: 하함(처짐) 동반 / 육군자탕: 담음 동반 / 평위산: 습탁 동반",
        "modification": "담음이 있으면 반하·진피 계열(육군자탕) 검토, 기하함이면 보중익기탕 감별",
        "acu_detail": "비위 보강, 중초 조화, 기허 회복 방향. 족삼리·중완 중심의 평보평사.",
        "moxa_detail": "복부 냉감, 설사, 비위허한이 있으면 검토. 실열·상열감은 뜸 주의.",
        "followup": "3~7일: 식욕 증가 여부, 복부 가스 찬 느낌 확인 / 2주: 체력 및 대변 굳기 확인",
        "pulse_target": "허맥, 약맥, 완맥",
        "tongue_target": "담백, 치흔",
        "core_points": ["ST36", "CV12", "CV6", "BL20", "BL21"],
        "q6_annotation": "보충·안정 방향 중심, 비위 기운 생성",
        "polyhedron": "순수 비위 보강, 기허 회복의 단일 지향 구조",
        "h34_extension": "- 기체(氣滯) 방향 (소화불량, 팽만감)\n- 상열 변동 방향 (인삼 과민 시)",
        "neijing_map": "- 장부: 후천의 본(비위) 허약\n- 기혈진액: 기(氣) 생성력 저하",
        "dongui_map": "- 비위, 기(氣): 음식 맛이 없고 기운이 없는 병증"
    },
    "평위산": {
        "category": "조습·화위 처방",
        "pattern": "비위습탁, 식체, 복부팽만",
        "direction": "조습, 행기, 소도, 비위 소통",
        "core_axes": ["배출·이수축", "소통·전환축", "완충·조화축"],
        "herbs": "창출, 후박, 진피, 감초, 생강, 대조",
        "best_for": "복부팽만, 더부룩함, 트림, 식체, 백니태, 몸이 무거운 습체",
        "poor_fit": "음허, 구건, 마른 체형, 진액 부족, 위음허성 속쓰림",
        "differential": "이진탕: 담음·오심 중심 / 반하사심탕: 한열착잡·심하비 / 향사평위산: 기체·복통",
        "modification": "식체가 강하면 소도 방향, 진액 부족이 있으면 조습 과잉 주의",
        "acu_detail": "비위 소통, 중초 기기 조절, 습탁 배출. 풍륭·천추 등 소통 위주 사법 검토.",
        "moxa_detail": "복부 냉감과 습체가 뚜렷하면 검토. 구건·음허·열감이 있으면 강한 온조 자극 주의.",
        "followup": "3~5일: 복부팽만·트림·대변·입마름 확인 / 1~2주: 소화력 본질적 회복 확인",
        "pulse_target": "활맥, 완맥, 유맥",
        "tongue_target": "백니태, 후태",
        "core_points": ["CV12", "ST25", "ST36", "ST40", "SP9"],
        "q6_annotation": "소통·전환 방향, 습탁 배출과 조화 주도",
        "polyhedron": "조습·강역 방향, 사법(瀉法) 위주 구조",
        "h34_extension": "- 조열(燥熱) 발생 방향 (입마름, 속쓰림)\n- 진액 소모 방향 (변비 유발 가능성)",
        "neijing_map": "- 승강출입: 위기 하강 역조(트림, 오심)\n- 육기: 내습(內濕) 정체",
        "dongui_map": "- 비위, 담음: 식적, 더부룩함, 체기"
    },
    "이진탕": {
        "category": "화담·이기 처방",
        "pattern": "담음정체, 오심구토, 어지럼, 흉민",
        "direction": "조습, 화담, 강역, 위기 하강",
        "core_axes": ["배출·이수축", "소통·전환축", "완충·조화축"],
        "herbs": "반하, 진피, 복령, 감초, 생강, 오매",
        "best_for": "담음, 오심, 흉민, 어지럼, 가래, 식후 더부룩함",
        "poor_fit": "음허, 마른기침, 구건, 진액 부족, 임신 관련 구역(주의)",
        "differential": "평위산: 식적·복부 중심 / 온담탕: 담열·불안 중심 / 오령산: 수분·소변 중심",
        "modification": "담열이면 청담열, 수습이면 이수, 기체면 행기 방향 병행 검토",
        "acu_detail": "화담강역, 비위 조절, 중초 기기 회복. 족양명·족태음경 중심 사법 검토.",
        "moxa_detail": "냉담·한담·비위허한이 뚜렷하면 검토. 열담·구건·음허는 뜸 자극 주의.",
        "followup": "3~7일: 오심·가래·어지럼 완화 여부, 구건·위염 악화 여부 확인",
        "pulse_target": "활맥",
        "tongue_target": "백니태, 후태, 활윤",
        "core_points": ["ST40", "CV12", "PC6", "SP9", "ST36"],
        "q6_annotation": "배출·전환 방향 중심, 담음 제거",
        "polyhedron": "위기 하강 및 수습 배출 지향 구조",
        "h34_extension": "- 진액 소모 방향 (마른 기침, 구건)\n- 조열 발생 방향 (반하/진피 온조 성질)",
        "neijing_map": "- 담음: 비정상적 체액 축적\n- 승강출입: 맑은 것은 오르고 탁한 것은 내리는 기능 상실",
        "dongui_map": "- 담음, 구토: 미식거림, 현훈, 흉민"
    },
    "오령산": {
        "category": "이수·수습 조절 처방",
        "pattern": "방광기화불리, 수습정체, 소변불리",
        "direction": "이수, 삼습, 기화 조절, 수분 대사 조절",
        "core_axes": ["배출·이수축", "소통·전환축", "완충·조화축"],
        "herbs": "택사, 저령, 복령, 백출, 계지",
        "best_for": "부종, 소변불리, 몸이 무거움, 갈증과 수분 정체가 함께 보임, 차멀미",
        "poor_fit": "탈수, 음허갈증, 진액 부족, 신장질환(진단된), 이뇨제 병용자",
        "differential": "저령탕: 열증 동반 / 방기황기탕: 표허 부종 / 진무탕: 양허 냉증 부종",
        "modification": "한습이면 온양 기화, 열이 있으면 청열 이수 방향 검토",
        "acu_detail": "수분 대사, 방광기화, 비신 조절. 음릉천, 수분 혈 등 이수 방향 사법 검토.",
        "moxa_detail": "양허성 부종·냉감이 뚜렷하면 적극 검토. 음허갈증·탈수 상태는 뜸 금지.",
        "followup": "1~3일: 소변량 증가, 부종 감소, 체중 변화 관찰 / 이상 반응: 어지럼, 탈수",
        "pulse_target": "부맥, 활맥, 수습 무력맥",
        "tongue_target": "습윤, 백태, 치흔, 반대",
        "core_points": ["SP9", "CV9", "BL22", "BL28", "ST36"],
        "q6_annotation": "배출·이수와 수분 조절 축 중심",
        "polyhedron": "기화(氣化) 및 이수(利水) 하행 구조",
        "h34_extension": "- 음허·탈수 방향 (과도한 이뇨로 인한 진액 고갈)\n- 한습·양허 심화 방향 (온양 부족 시)",
        "neijing_map": "- 수습, 방광: 방광의 기화(배출) 기능 장애\n- 개합추: 하초의 배출구(추) 닫힘",
        "dongui_map": "- 소변, 수종, 담음: 붓고 소변이 시원치 않으며 물을 마시면 토하는 증"
    }
}

FORMULA_DF = pd.DataFrame([{"처방명": k, **v} for k, v in FORMULAS.items()])

POINT_NAMES = {
    "LU": ["Zhongfu", "Yunmen", "Tianfu", "Xiabai", "Chize", "Kongzui", "Lieque", "Jingqu", "Taiyuan", "Yuji", "Shaoshang"],
    "LI": ["Shangyang", "Erjian", "Sanjian", "Hegu", "Yangxi", "Pianli", "Wenliu", "Xialian", "Shanglian", "Shousanli", "Quchi", "Zhouliao", "Shouwuli", "Binao", "Jianyu", "Jugu", "Tianding", "Futu", "Kouheliao", "Yingxiang"],
    "ST": ["Chengqi", "Sibai", "Juliao", "Dicang", "Daying", "Jiache", "Xiaguan", "Touwei", "Renying", "Shuitu", "Qishe", "Quepen", "Qihu", "Kufang", "Wuyi", "Yingchuang", "Ruzhong", "Rugen", "Burong", "Chengman", "Liangmen", "Guanmen", "Taiyi", "Huaroumen", "Tianshu", "Wailing", "Daju", "Shuidao", "Guilai", "Qichong", "Biguan", "Futu", "Yinshi", "Liangqiu", "Dubi", "Zusanli", "Shangjuxu", "Tiaokou", "Xiajuxu", "Fenglong", "Jiexi", "Chongyang", "Xiangu", "Neiting", "Lidui"],
    "SP": ["Yinbai", "Dadu", "Taibai", "Gongsun", "Shangqiu", "Sanyinjiao", "Lougu", "Diji", "Yinlingquan", "Xuehai", "Jimen", "Chongmen", "Fushe", "Fujie", "Daheng", "Fuai", "Shidou", "Tianxi", "Xiongxiang", "Zhourong", "Dabao"],
    "HT": ["Jiquan", "Qingling", "Shaohai", "Lingdao", "Tongli", "Yinxi", "Shenmen", "Shaofu", "Shaochong"],
    "SI": ["Shaoze", "Qiangu", "Houxi", "Wangu", "Yanggu", "Yanglao", "Zhizheng", "Xiaohai", "Jianzhen", "Naoshu", "Tianzong", "Bingfeng", "Quyuan", "Jianwaishu", "Jianzhongshu", "Tianchuang", "Tianrong", "Quanliao", "Tinggong"],
    "BL": ["Jingming", "Zanzhu", "Meichong", "Qucha", "Wuchu", "Chengguang", "Tongtian", "Luoque", "Yuzhen", "Tianzhu", "Dazhu", "Fengmen", "Feishu", "Jueyinshu", "Xinshu", "Dushu", "Geshu", "Ganshu", "Danshu", "Pishu", "Weishu", "Sanjiaoshu", "Shenshu", "Qihaishu", "Dachangshu", "Guanyuanshu", "Xiaochangshu", "Pangguangshu", "Zhonglushu", "Baihuanshu", "Shangliao", "Ciliao", "Zhongliao", "Xialiao", "Huiyang", "Chengfu", "Yinmen", "Fuxi", "Weiyang", "Weizhong", "Fufen", "Pohu", "Gaohuang", "Shentang", "Yixi", "Geguan", "Hunmen", "Yanggang", "Yishe", "Weicang", "Huangmen", "Zhishi", "Baohuang", "Zhibian", "Heyang", "Chengjin", "Chengshan", "Feiyang", "Fuyang", "Kunlun", "Pucan", "Shenmai", "Jinmen", "Jinggu", "Shugu", "Zutonggu", "Zhiyin"],
    "KI": ["Yongquan", "Rangu", "Taixi", "Dazhong", "Shuiquan", "Zhaohai", "Fuliu", "Jiaoxin", "Zhubin", "Yingu", "Henggu", "Dahe", "Qixue", "Siman", "Zhongzhu", "Huangshu", "Shangqu", "Shiguan", "Yindu", "Futonggu", "Youmen", "Bulang", "Shenfeng", "Lingxu", "Shencang", "Yuzhong", "Shufu"],
    "PC": ["Tianchi", "Tianquan", "Quze", "Ximen", "Jianshi", "Neiguan", "Daling", "Laogong", "Zhongchong"],
    "TE": ["Guanchong", "Yemen", "Zhongzhu", "Yangchi", "Waiguan", "Zhigou", "Huizong", "Sanyangluo", "Sidu", "Tianjing", "Qinglengyuan", "Xiaoluo", "Naohui", "Jianliao", "Tianliao", "Tianyou", "Yifeng", "Chimai", "Luxi", "Jiaosun", "Ermen", "Heliao", "Sizhukong"],
    "GB": ["Tongziliao", "Tinghui", "Shangguan", "Hanyan", "Xuanlu", "Xuanli", "Qubin", "Shuaigu", "Tianchong", "Fubai", "Touqiaoyin", "Wangu", "Benshen", "Yangbai", "Toulinqi", "Muchuang", "Zhengying", "Chengling", "Naokong", "Fengchi", "Jianjing", "Yuanye", "Zhejin", "Riyue", "Jingmen", "Daimai", "Wushu", "Weidao", "Juliao", "Huantiao", "Fengshi", "Zhongdu", "Xiyangguan", "Yanglingquan", "Yangjiao", "Waiqiu", "Guangming", "Yangfu", "Xuanzhong", "Qiuxu", "Zulinqi", "Diwuhui", "Xiaxi", "Zuqiaoyin"],
    "LR": ["Dadun", "Xingjian", "Taichong", "Zhongfeng", "Ligou", "Zhongdu", "Xiguan", "Ququan", "Yinbao", "Zuwuli", "Yinlian", "Jimai", "Zhangmen", "Qimen"],
    "CV": ["Huiyin", "Qugu", "Zhongji", "Guanyuan", "Shimen", "Qihai", "Yinjiao", "Shenque", "Shuifen", "Xiawan", "Jianli", "Zhongwan", "Shangwan", "Juque", "Jiuwei", "Zhongting", "Shanzhong", "Yutang", "Zigong", "Huagai", "Xuanji", "Tiantu", "Lianquan", "Chengjiang"],
    "GV": ["Changqiang", "Yaoshu", "Yaoyangguan", "Mingmen", "Xuanshu", "Jizhong", "Zhongshu", "Jinsuo", "Zhiyang", "Lingtai", "Shendao", "Shenzhu", "Taodao", "Dazhui", "Yamen", "Fengfu", "Naohu", "Qiangjian", "Houding", "Baihui", "Qianding", "Xinhui", "Shangxing", "Shenting", "Suliao", "Shuigou", "Duiduan", "Yinjiao"],
}

COMMON_KO = {
    "LU1": "중부", "LU7": "열결", "LU9": "태연", "LU10": "어제", "LU11": "소상",
    "LI4": "합곡", "LI10": "수삼리", "LI11": "곡지", "LI15": "견우", "LI20": "영향",
    "ST25": "천추", "ST36": "족삼리", "ST40": "풍륭", "ST44": "내정",
    "SP3": "태백", "SP4": "공손", "SP6": "삼음교", "SP9": "음릉천", "SP10": "혈해",
    "HT7": "신문", "HT8": "소부", "SI3": "후계", "SI19": "청궁",
    "BL13": "폐수", "BL15": "심수", "BL17": "격수", "BL18": "간수", "BL20": "비수", "BL21": "위수", "BL23": "신수", "BL25": "대장수", "BL28": "방광수", "BL40": "위중", "BL60": "곤륜",
    "KI1": "용천", "KI3": "태계", "KI6": "조해", "KI7": "복류",
    "PC6": "내관", "PC7": "대릉", "PC8": "노궁", "TE5": "외관", "TE6": "지구",
    "GB20": "풍지", "GB21": "견정", "GB34": "양릉천", "GB39": "현종", "GB41": "족임읍",
    "LR3": "태충", "LR8": "곡천", "LR13": "장문", "LR14": "기문",
    "CV4": "관원", "CV6": "기해", "CV9": "수분", "CV12": "중완", "CV17": "전중",
    "GV4": "명문", "GV14": "대추", "GV20": "백회",
}

MERIDIAN_META = {
    "LU": {"경락": "수태음폐경", "기본축": ["보충축", "소통·전환축"], "부위": "상지·흉부", "x": 28, "y1": 35, "y2": 78, "주의": "흉부 혈위 깊은 자침 주의"},
    "LI": {"경락": "수양명대장경", "기본축": ["소통·전환축", "배출·이수축"], "부위": "상지·두면", "x": 72, "y1": 78, "y2": 28, "주의": "LI4 등 임신 중 주의"},
    "ST": {"경락": "족양명위경", "기본축": ["보충축", "소통·전환축", "완충·조화축"], "부위": "두면·흉복·하지", "x": 62, "y1": 22, "y2": 92, "주의": "복부 혈위 임신 확인"},
    "SP": {"경락": "족태음비경", "기본축": ["보충축", "배출·이수축", "완충·조화축"], "부위": "하지·복흉", "x": 38, "y1": 92, "y2": 42, "주의": "SP6 임신 중 금기"},
    "HT": {"경락": "수소음심경", "기본축": ["수렴·안정축", "보충축"], "부위": "상지·흉부", "x": 24, "y1": 42, "y2": 82, "주의": "심계·불안 환자 강자극 주의"},
    "SI": {"경락": "수태양소장경", "기본축": ["소통·전환축", "수렴·안정축"], "부위": "상지·견갑·두면", "x": 75, "y1": 82, "y2": 25, "주의": "경항부 깊은 자침 주의"},
    "BL": {"경락": "족태양방광경", "기본축": ["소통·전환축", "배출·이수축", "보충축"], "부위": "두항·배부·하지", "x": 56, "y1": 18, "y2": 92, "주의": "흉배부 기흉 주의"},
    "KI": {"경락": "족소음신경", "기본축": ["보충축", "수렴·안정축"], "부위": "하지·복흉", "x": 45, "y1": 92, "y2": 38, "주의": "허열·음허 상태 확인"},
    "PC": {"경락": "수궐음심포경", "기본축": ["수렴·안정축", "소통·전환축"], "부위": "흉부·상지", "x": 31, "y1": 38, "y2": 82, "주의": "흉통은 의학적 감별 필요"},
    "TE": {"경락": "수소양삼초경", "기본축": ["소통·전환축", "배출·이수축"], "부위": "상지·두면", "x": 69, "y1": 82, "y2": 22, "주의": "두면부 자극 주의"},
    "GB": {"경락": "족소양담경", "기본축": ["소통·전환축", "승양·상승축"], "부위": "두측·몸측·하지", "x": 72, "y1": 20, "y2": 92, "주의": "GB21 임신 중 주의"},
    "LR": {"경락": "족궐음간경", "기본축": ["소통·전환축", "수렴·안정축", "보충축"], "부위": "하지·복흉", "x": 34, "y1": 92, "y2": 40, "주의": "어혈·임신 확인"},
    "CV": {"경락": "임맥", "기본축": ["보충축", "수렴·안정축", "완충·조화축"], "부위": "전중선", "x": 50, "y1": 88, "y2": 18, "주의": "하복부 혈위 임신 주의"},
    "GV": {"경락": "독맥", "기본축": ["승양·상승축", "소통·전환축"], "부위": "후중선·두부", "x": 50, "y1": 88, "y2": 14, "주의": "경항부·두면부 자극 주의"},
}

POINT_OVERRIDES = {
    "ST36": {"방향": "비위 보강, 기혈 보강, 전신 회복", "뜸": "허한·냉감 시 검토 가능"},
    "CV12": {"방향": "중초 화위, 복부팽만, 식체 조절", "뜸": "복부 냉감 시 검토 가능"},
    "CV6": {"방향": "원기 보강, 기허 조절", "뜸": "허한·냉감 시 검토 가능"},
    "CV4": {"방향": "하초 보강, 정혈·원기 보강", "뜸": "허한 확인 시 검토, 임신 시 주의"},
    "SP6": {"방향": "간·비·신 조절, 혈·수분·안신 보조", "뜸": "허한 시 검토, 임신 중 주의"},
    "KI3": {"방향": "간신·자음 보강, 허열 완충", "뜸": "허한 시 검토"},
    "LR3": {"방향": "소간해울, 기기 소통", "뜸": "일반적으로 침구 조절 중심"},
    "PC6": {"방향": "안신, 흉민, 오심, 위기 조절", "뜸": "대개 침구 조절 중심"},
    "HT7": {"방향": "안신, 심계, 불면 조절", "뜸": "자극 강도 조절"},
    "GV20": {"방향": "청양 상승, 안신, 두면부 조절", "뜸": "화상·상열감 주의"},
    "BL20": {"방향": "비위 보강, 운화 조절", "뜸": "허한·냉감 시 검토"},
    "BL23": {"방향": "신기·하초 보강", "뜸": "허한·냉감 시 검토"},
    "SP9": {"방향": "수습·부종·습담 조절", "뜸": "냉습 시 검토"},
    "ST40": {"방향": "화담, 담음 조절", "뜸": "담음+냉감 시 검토"},
    "ST25": {"방향": "장부 기능, 대변·복부팽만 조절", "뜸": "복부 냉감 시 검토"},
}

PREGNANCY_CAUTION = {"LI4", "SP6", "BL60", "BL67", "GB21", "CV3", "CV4", "CV5", "CV6", "CV7"}

def point_coords(prefix, idx, count):
    meta = MERIDIAN_META[prefix]
    t = 0 if count <= 1 else (idx - 1) / (count - 1)
    x = meta["x"]
    y = meta["y1"] + (meta["y2"] - meta["y1"]) * t
    if prefix in ["BL", "GB", "ST"]: x += (idx % 3 - 1) * 2
    if prefix in ["LU", "LI", "HT", "SI", "PC", "TE"]: x += (idx % 2) * 2
    return round(x, 2), round(y, 2)

def build_acupoint_db():
    rows = []
    for prefix, names in POINT_NAMES.items():
        meta = MERIDIAN_META[prefix]
        for i, name in enumerate(names, start=1):
            code = f"{prefix}{i}"
            axes = list(meta["기본축"])
            direction = POINT_OVERRIDES.get(code, {}).get("방향", f"{meta['경락']}의 기본 방향: {', '.join(axes)}")
            moxa = POINT_OVERRIDES.get(code, {}).get("뜸", "허한·냉감 소견 시 한의사가 검토")
            caution = meta["주의"]
            if code in PREGNANCY_CAUTION: caution += " / 임신 중 주의요망"
            x, y = point_coords(prefix, i, len(names))
            rows.append({
                "code": code,
                "경혈명": COMMON_KO.get(code, name),
                "standard_name": name,
                "경락코드": prefix,
                "경락": meta["경락"],
                "부위군": meta["부위"],
                "처방 방향축": ", ".join(axes),
                "임상 방향": direction,
                "금기·주의": caution,
                "뜸 가능 여부": moxa,
                "임신 주의": "주의" if code in PREGNANCY_CAUTION else "일반 확인",
                "x": x, "y": y
            })
    return pd.DataFrame(rows)

ACUPOINT_DF = build_acupoint_db()

st.sidebar.header("📝 환자 임상 정보 입력")

# 드롭다운에서 12개 처방이 모두 나오게 연결
selected_formula = st.sidebar.selectbox("분석할 한의학 처방 (12종)", FORMULA_DF["처방명"].tolist())
formula = FORMULA_DF[FORMULA_DF["처방명"] == selected_formula].iloc[0].to_dict()

symptom = st.sidebar.text_input("주증상 및 진단명", placeholder="예: 만성피로, 안색창백, 어지럼, 식욕저하")
assessment = st.sidebar.text_area("한의사 종합검진 소견", height=100, placeholder="예: 맥 허약, 설 담백, 치흔. 기혈양허와 비위기허 경향.")

st.sidebar.subheader("🩺 진맥·설진·복진")
c_p1, c_p2 = st.sidebar.columns(2)
pulse_power = c_p1.selectbox("맥력", ["미입력", "허맥", "약맥", "무력", "실맥", "유력", "부맥", "침맥"])
pulse_shape = c_p2.selectbox("맥상", ["미입력", "세맥", "현맥", "활맥", "삭맥", "지맥", "긴맥", "삽맥"])
c_t1, c_t2 = st.sidebar.columns(2)
tongue_color = c_t1.selectbox("설질", ["미입력", "담백", "담홍", "홍", "자암", "어반"])
tongue_coat = c_t2.selectbox("설태", ["미입력", "박백태", "백태", "후태", "황태", "황니태", "소태/무태"])
tongue_fluid = st.sidebar.selectbox("진액/형태", ["미입력", "정상", "건조", "윤택", "치흔", "열문", "종대"])
abdomen = st.sidebar.selectbox("복진", ["미입력", "더부룩함/가스", "복부 냉감", "심하비", "압통", "복직근 긴장", "하복부 무력"])

st.sidebar.subheader("🧪 임상 검사값 및 특이사항 입력")
ast_alt = st.sidebar.text_input("AST/ALT:", placeholder="예: 45 / 52 (U/L)")
creatinine = st.sidebar.text_input("Creatinine/eGFR:", placeholder="예: 1.2 mg/dL / 58")
bp = st.sidebar.text_input("혈압 (mmHg):", placeholder="예: 145 / 90")
meds = st.sidebar.text_area("현재 복용약 상세:", placeholder="예: 아스피린 장용정 100mg\n로사르탄 50mg", height=80)

st.sidebar.subheader("💊 약물 병용 안전성 체크")
anti_coag = st.sidebar.checkbox("항응고제/항혈소판제/NSAIDs")
bp_med = st.sidebar.checkbox("혈압약")
diabetes_med = st.sidebar.checkbox("당뇨약/인슐린")
diuretic = st.sidebar.checkbox("이뇨제")
sedative = st.sidebar.checkbox("수면제/항우울제/진정제")
steroid = st.sidebar.checkbox("스테로이드/면역억제제")
cancer_med = st.sidebar.checkbox("항암제/호르몬제")

st.sidebar.subheader("🚨 환자 기저상태 체크")
pregnant = st.sidebar.checkbox("임신/수유 중")
child_elder = st.sidebar.checkbox("소아/고령자/허약자")
liver_kidney = st.sidebar.checkbox("간 기능 저하 또는 간질환 병력")
kidney_disease = st.sidebar.checkbox("신장 기능 저하 또는 신장질환 병력")
bp_state = st.sidebar.checkbox("고혈압 또는 저혈압 변동")
digestion_problem = st.sidebar.checkbox("만성 소화불량/설사/위장장애")
surgery = st.sidebar.checkbox("수술/시술/치과치료 예정")
neuro = st.sidebar.checkbox("피부 감각저하/당뇨성 말초신경병증")
heat_inflammation = st.sidebar.checkbox("실열/염증성 열감")
edema_urination = st.sidebar.checkbox("부종/소변불리")

show_research = st.sidebar.checkbox("🔬 연구자용 공식 보기 (Click to Expand)", value=False)

inputs = {
    "symptom": symptom, "assessment": assessment, "bp": bp, "meds": meds,
    "ast_alt": ast_alt, "creatinine": creatinine,
    "pulse_power": pulse_power, "pulse_shape": pulse_shape,
    "tongue_color": tongue_color, "tongue_coat": tongue_coat,
    "tongue_fluid": tongue_fluid, "abdomen": abdomen,
    "anti_coag": anti_coag, "bp_med": bp_med, "diabetes_med": diabetes_med,
    "diuretic": diuretic, "sedative": sedative, "steroid": steroid, "cancer_med": cancer_med,
    "pregnant": pregnant, "child_elder": child_elder, "liver_kidney": liver_kidney or kidney_disease,
    "bp_state": bp_state, "digestion_problem": digestion_problem, "surgery": surgery,
    "neuro": neuro, "heat_inflammation": heat_inflammation, "edema_urination": edema_urination,
}

def clinical_observation_text(inp):
    parts = []
    for k, lbl in [("pulse_power", "맥력"), ("pulse_shape", "맥상"), ("tongue_color", "설질"), ("tongue_coat", "설태"), ("tongue_fluid", "진액"), ("abdomen", "복진")]:
        if inp.get(k) and inp[k] != "미입력": parts.append(f"{lbl}: {inp[k]}")
    return ", ".join(parts) if parts else "미입력"

match_list, caution_list, review_list = [], [], []

if pulse_power in ["허맥", "약맥", "무력"]:
    if "보충축" in formula["core_axes"]: match_list.append("맥력 허약/무력 → 보충축 방향 처방과 정합성 높음")
    else: caution_list.append("맥력 무력 → 사법/소통 위주 처방 시 환자 체력 부담 확인")
if pulse_power in ["실맥", "유력"]:
    if "보충축" in formula["core_axes"]: caution_list.append("맥력 유력/실맥 → 보익 처방 시 체기/상열감 주의")
    else: match_list.append("맥력 실맥 → 사법/소통축 처방과 정합성 높음")
if tongue_color == "홍" or tongue_fluid == "건조" or tongue_coat == "소태/무태":
    if "허열" in formula["pattern"] or "자음" in formula["direction"]: match_list.append("홍설·건조·소태 → 자음·허열 완충 방향과 정합성 높음")
    elif "온보" in formula["direction"] or "승양" in formula["direction"]: caution_list.append("홍설·건조·열감 소견 → 승양·온보 자극 과잉 여부 확인")
if tongue_coat in ["후태", "황니태"] or abdomen in ["더부룩함/가스", "심하비"] or digestion_problem:
    if "보충축" in formula["core_axes"]: caution_list.append("후태·더부룩함·만성 소화불량 → 보익·보음 처방의 위장 부담 확인 (숙지황, 당귀 등)")
    if any(k in formula["direction"] for k in ["조습", "화담", "소도"]): match_list.append("후태·더부룩함 → 조습·화담 방향과 정합성 높음")
if edema_urination:
    if "배출·이수축" in formula["core_axes"]: match_list.append("부종·소변불리 → 배출·이수축 방향 처방과 정합성 높음")
    else: caution_list.append("부종·소변불리 뚜렷 시 → 이수·수습 조절 처방과 감별 필요")
if heat_inflammation:
    if "온보" in formula["direction"]: review_list.append("실열/염증 뚜렷 시 온보 처방(육계, 황기 등) 재검토 필요")
    if "청열" not in formula["direction"]: caution_list.append("실열 뚜렷 시 염증 컨트롤 방향 추가 검토")

safety_rows = []
def add_safety(label, prio, note): safety_rows.append({"확인 항목": label, "우선순위": prio, "확인 내용": note})

if anti_coag: add_safety("항응고제/항혈소판제", "높음", "활혈 약재(당귀, 목단피, 천궁 등), 출혈 경향, 수술 예정 확인")
if is_bp_warning(bp, bp_med, bp_state): add_safety("고혈압/혈압약", "높음", "승양·온보 자극 과잉 여부, 혈압 상승, 상열감, 심계 확인")
if diabetes_med: add_safety("당뇨약/인슐린", "중간", "혈당 변동, 저혈당 증상, 감각저하(뜸 화상 위험) 여부 확인")
if sedative: add_safety("수면제/진정제", "중간", "안신 처방·침구 병용 시 과도한 주간 졸림 및 반응저하 확인")
if pregnant: add_safety("임신/수유", "높음", "처방·침구·뜸 모두 임산부 금기/주의(합곡, 삼음교, 하복부) 확인")
if digestion_problem: add_safety("만성 소화불량", "높음", "숙지황, 당귀 등 윤제(보음/보혈) 복용 시 설사, 소화장애 유발 확인")
if surgery: add_safety("수술/시술 예정", "높음", "출혈 지연 관련 약재/혈위 중단 및 감염 위험 확인")
if neuro: add_safety("당뇨병성 신경병증/감각저하", "높음", "뜸 화상 위험 극도로 높음, 피부 상처 및 감염 주의")
if not safety_rows: add_safety("특이사항 없음", "일반", "기본적인 복용 전후 반응 관찰")

target_axes = set(formula["core_axes"])
cand_df = ACUPOINT_DF.copy()
def score_point(row):
    axes = set([a.strip() for a in row["처방 방향축"].split(",")])
    s = len(target_axes & axes) * 3
    if row["code"] in formula["core_points"]: s += 5
    if "비위" in formula["pattern"] and "비위" in row["임상 방향"]: s += 2
    if "허열" in formula["pattern"] and "허열" in row["임상 방향"]: s += 2
    if "담음" in formula["pattern"] and "담음" in row["임상 방향"]: s += 2
    return s
cand_df["관련도"] = cand_df.apply(score_point, axis=1)
cand_df = cand_df[cand_df["관련도"] > 0].sort_values(["관련도", "경락코드", "순번"], ascending=[False, True, True])

if show_research:
    st.markdown("### ☯️ 한의 임상 의사결정 지원 대시보드 (CDSS)")
    st.markdown("##### 처방 해석 구조 = 전통 처방 구조 + 동의보감 병증 해석 + 진맥·설진 대조 + 침구 방향 + 뜸 주의 + 주변 변화 가능성 + 안전성 확인")
    with st.expander("🔬 연구자용 공식 보기 (Click to Expand)"):
        st.code("Formula_Vector = Traditional_Core + Donguibogam_Layer + Q6_Core + H(3,4)_Extension + Polyhedron_Layer + Safety_Filter")
    st.info("전통 처방 구조와 동의보감 병증 해석을 **중심 설명층**으로 두고, Q6·H(3,4)·다면체 구조는 이를 보조적으로 주석화하는 해석층으로 사용합니다.")
else:
    st.markdown("### ☯️ 한의 임상 의사결정 지원 대시보드 (CDSS)")
    st.markdown("##### 처방 해석 구조 = 전통 처방 구조 + 동의보감 병증 해석 + 진맥·설진 대조 + 침구 방향 + 뜸 주의 + 주변 변화 가능성 + 안전성 확인")
    st.info("좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 리포트 생성' 버튼을 눌러주세요.")

tabs = st.tabs([
    "1. 한의사용 통합 요약", "2. 전통 처방 Core", "3. 동의보감 병렬 해석",
    "4. 진맥·설진 대조", "5. 침구 치료 방향", "6. 뜸 치료 방향",
    "7. 처방 주변 변화 가능성", "8. 보사·승강출입 균형",
    "9. Q6 64큐브 주석", "10. 황제내경 병렬 해석", "11. 안전성 확인", "12. 환자 설명문"
])

with tabs[0]:
    st.markdown("### 📋 한의사용 1페이지 통합 요약")
    st.success(f"**선택 처방:** {formula['처방명']} ({formula['category']})\n\n**핵심 치료 방향:** {formula['direction']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ 진맥·설진 동적 정합도 평가")
        st.markdown(f"**입력된 소견:** {clinical_observation_text(inputs)}")
        if match_list:
            st.markdown("**[정합 소견]**")
            for m in match_list: st.markdown(f"- 🟢 {m}")
        else:
            st.markdown("**[정합 소견]**\n- ⚪ 입력된 정보 중 처방 방향과 명확히 일치하는 데이터가 부족합니다.")
        
        if caution_list or review_list:
            st.markdown("**[주의 및 재검토 소견]**")
            for c in caution_list: st.markdown(f"- 🟡 {c}")
            for r in review_list: st.markdown(f"- 🔴 {r}")
        else:
            st.markdown("**[주의 소견]**\n- ⚪ 현재 입력상 처방 방향과 크게 어긋나는 주의 소견은 발견되지 않았습니다.")

    with col2:
        st.markdown("#### 🧭 처방 깊이 해석")
        st.markdown(f"**👍 잘 맞는 환자상:**\n{formula['best_for']}")
        st.markdown(f"**👎 안 맞는 환자상 (주의):**\n{formula['poor_fit']}")
        st.markdown(f"**🔀 감별 처방 비교:**\n{formula['differential']}")
        st.markdown(f"**🛠️ 가감·조정 검토 방향:**\n{formula['modification']}")
        st.markdown(f"**📆 복용 후 추적 관찰 항목:**\n{formula['followup']}")

with tabs[1]:
    st.markdown("### 📌 전통 처방 Core 패널")
    st.markdown(f"**전통 변증:** {formula['pattern']}\n\n**구성 약재:** {formula['herbs']}")
    st.markdown(f"**처방 방향 6축:** {', '.join(formula['core_axes'])}")

with tabs[2]:
    st.markdown("### 📖 동의보감 병렬 해석 패널")
    st.info("전통 처방 구조와 동의보감 병증 해석을 중심 설명층으로 둡니다.")
    st.markdown(formula['dongui_map'])

with tabs[3]:
    st.markdown("### ✋ 진맥·설진 대조 패널")
    st.info("진맥·설진 정보는 자동 판정 값이 아니라, 한의사가 확인한 소견과 처방 방향을 대조하기 위한 도구입니다.")
    st.success(f"**선택 처방({formula['처방명']})의 기본 타겟 소견:**\n\n- **목표 소견:** 맥: {formula['pulse_target']} / 설: {formula['tongue_target']}")
    
    obs_df = pd.DataFrame([
        {"항목": "맥력", "입력값": pulse_power, "임상 대조 가이드": "허·약은 보충축, 실·유력은 사법/소통축 재검토"},
        {"항목": "맥상", "입력값": pulse_shape, "임상 대조 가이드": "세맥은 혈·음 부족, 현맥은 간울, 활맥은 담습, 삭맥은 열 확인"},
        {"항목": "설질", "입력값": tongue_color, "임상 대조 가이드": "담백은 기혈·양허, 홍은 열·음허, 자암/어반은 어혈"},
        {"항목": "설태", "입력값": tongue_coat, "임상 대조 가이드": "후태·황니태는 식체·습담·습열, 소태/무태는 진액 부족"},
        {"항목": "진액/형태", "입력값": tongue_fluid, "임상 대조 가이드": "건조는 음허·진액 부족, 치흔·종대는 비허·습담 경향"},
        {"항목": "복진", "입력값": abdomen, "임상 대조 가이드": "더부룩함·심하비는 중초 불화, 냉감은 허한, 긴장은 간울·통증"},
    ])
    st.table(obs_df)

with tabs[4]:
    st.markdown("### 📍 침구 치료 방향 패널")
    st.warning("본 패널은 자동 침 처방이 아니라, 선택 처방의 변증에 맞춰 면허자가 검토할 치료 원칙(보사/승강출입)을 정리한 것입니다.")
    st.markdown(f"**침구 치료 검토 지침:**\n- {formula['acu_detail']}")
    st.markdown("**처방 변증 연계 핵심 혈위 후보 (참고용)**")
    st.dataframe(cand_df[["code", "경혈명", "경락", "처방 방향축", "임상 방향", "금기·주의"]].head(10), hide_index=True)

with tabs[5]:
    st.markdown("### 🔥 뜸 치료 방향 패널")
    st.error("[주의] 뜸은 화상, 알레르기, 감염 위험이 있으므로 당뇨성 말초신경병증(감각저하) 및 실열/허열 환자에게 극히 주의해야 합니다.")
    st.markdown(f"**뜸 치료 검토 지침:**\n- {formula['moxa_detail']}")
    if neuro or heat_inflammation or pregnant:
        st.error("🚨 **[위험 경고]** 현재 환자 정보에 피부 감각저하, 실열/염증, 또는 임신 상태가 체크되어 있습니다. 뜸 시술을 엄격하게 제한하거나 금지해야 합니다.")

with tabs[6]:
    st.markdown("### 🌐 처방 주변 변화 가능성 패널")
    st.caption("연구자용 구조명: H(3,4) Extension")
    st.info("이 패널은 처방의 중심 방향에서 벗어날 수 있는 주변 변화 가능성을 한의학적으로 정리한 보조 지도입니다.")
    st.markdown(f"**[{formula['처방명']} 주의점]**\n{formula['h34_extension']}")

with tabs[7]:
    st.markdown("### 💎 보사·승강출입 균형 패널")
    st.caption("연구자용 구조명: 다면체 방향성 시각화")
    st.info(f"**[{formula['처방명']} 균형 방향]**\n- {formula['polyhedron']}")

with tabs[8]:
    st.markdown("### 🧬 Q6 64큐브 Core 주석 패널 (연구자용)")
    st.success(f"**Q6 변화 방향:** {formula['q6_annotation']}")

with tabs[9]:
    st.markdown("### 📚 황제내경 병렬 해석 패널 (연구자용)")
    st.info("전통 생명론의 핵심 개념을 정보기하학 언어로 병렬 해석하는 층입니다.")
    st.markdown(formula['neijing_map'])

with tabs[10]:
    st.markdown("### 🚨 안전성 확인 패널")
    st.caption("환자가 입력한 양약 복용력 및 기저질환과 처방 약재 간의 상호작용 위험도를 요약합니다. (상세 내용은 탭 1의 요약표 참고)")
    meds_summary = safe_join([m for m, c in zip(["항응고제", "혈압약", "당뇨약", "수면제", "스테로이드", "항암제"], [anti_coag, bp_med, diabetes_med, sedative, steroid, cancer_med]) if c])
    state_summary = safe_join([s for s, c in zip(["임신/수유", "간신질환", "수술예정", "감각저하", "염증/발열"], [pregnant, liver_kidney, surgery, neuro, heat_inflammation]) if c])
    
    st.markdown(f"- **입력된 주요 복용약/상태:** {meds_summary or '특이사항 없음'} / {state_summary or '특이사항 없음'}")
    st.markdown("- 처방에 특이 약재 포함 여부 및 환자 상태에 따른 금기/신중 투여 여부를 의료인이 최종 확인해야 합니다.")
    st.table(pd.DataFrame(safety_rows))

with tabs[11]:
    st.markdown("### 💬 환자 설명문 패널")
    patient_html = f"""
    <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
        <b>{formula['처방명']}</b>은 한 가지 증상만 억누르는 약이 아니라, 여러 약재가 조화롭게 작용하여 몸의 무너진 균형을 회복시키는 복합 처방입니다.<br><br>
        이 대시보드는 처방 복용 시 나타날 수 있는 우리 몸의 반응과 주의점을 한의사 선생님이 더 안전하게 살필 수 있도록 돕는 시스템입니다.<br><br>
        복용하시는 동안 <b>소화 상태, 피로감, 수면 변화, (해당시) 혈당/혈압의 변화</b>를 편안하게 관찰하시고 진료 시 말씀해 주시면 됩니다.
    </div>
    """
    st.markdown(patient_html, unsafe_allow_html=True)
    st.download_button("설명문 복사/저장", data=patient_html.replace("<br>", "\n").replace("<b>", "").replace("</b>", ""), file_name=f"{formula['처방명']}_환자설명문.txt")

st.divider()
st.caption("본 앱은 교육 및 연구 검토용 시뮬레이터이며, 의료인의 진단을 대체하지 않습니다. 모든 처방과 시술은 담당 한의사의 면허 범위 내에서 이루어져야 합니다.")
