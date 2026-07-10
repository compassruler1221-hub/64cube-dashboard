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
st.set_page_config(page_title="64큐브-다면체 처방 대시보드", layout="wide")

st.warning(
    "**[주의] 본 대시보드에서 한의학 처방 분석은 전통 처방의 생리적 효과를 자동으로 증명하거나 예측하는 시스템이 아닙니다.**\n\n"
    "- 이 시스템의 약재-코돈 매핑은 약재가 실제 유전암호를 조절한다는 뜻이 아닙니다.\n"
    "- 전통 처방 Core가 중심이며, Q6 64큐브는 해석(Core)층, H(3,4)는 생물정보 확장(Extension)층입니다.\n"
    "- 실제 처방은 면허가 있는 한의사의 변증, 환자 병력, 검사 결과, 안전성 평가를 바탕으로 결정되어야 합니다."
)

st.title("☯️ 64큐브-다면체 기반 코돈·아미노산 벡터 처방 해석 대시보드")
st.markdown(
    "**Formula_Vector = Traditional_Core + Donguibogam_Layer + Q6_Core_Annotation + Polyhedron_Visualization + H(3,4)_Biochemical_Extension + Safety_Filter**\n\n"
    "전통 처방 구조와 한국 한의학의 동의보감 병증 해석을 최상위 Core Layer로 두고, 이를 64큐브 상태공간과 H(3,4) 생물정보망, 다면체 동적평형 구조로 주석화(Annotation)하는 융합 해석 모델입니다."
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
        "db_pattern": ["허번불면(虛煩不眠), 심담허겁(心膽虛怯)", "식적(食積), 담음(痰飮), 비위 불화", "노권상(勞倦傷), 음식상(飮食傷), 기허발열(氣虛發熱)", "신수(腎水) 부족, 진음(眞陰) 고갈"],
        "db_interpret": [
            "과도한 사려(思慮)로 심비(心脾)가 상하여 발생하는 수면 장애와 정서 불안을 다스리는 양생적 조절 방향성을 제시합니다.",
            "비위의 운화 기능이 떨어져 습(濕)이 정체된 병증에 대해 덥히고 말려 기기를 소통시키는 병리적 주석을 제공합니다.",
            "과도한 피로와 섭생 불량으로 중기가 무너져 열이 위로 뜨는 허열(虛熱)을 내리고 맑은 양기를 위로 끌어올리는 승양(升陽)의 지혜를 담고 있습니다.",
            "선천적 바탕이 부족하거나 극심한 소모로 정(精)이 고갈된 상태를 채워 체액의 고갈을 막는 근본적인 보음(補陰)의 원리를 설명합니다."
        ]
    })
    
    clinical = pd.DataFrame({
        "formula_name": ["산조인탕", "평위산", "보중익기탕", "육미지황환"],
        "clinic_pattern": [
            "심비양허, 허번불면, 영혈 소모 동반 가능성",
            "비위습탁, 기체, 소화불량 및 복부 팽만 동반 가능성",
            "비위기허, 중기하함, 만성 피로 및 기력 저하 동반 가능성",
            "간신음허, 정혈 부족, 허열, 수분 정체 동반 가능성"
        ],
        "clinic_structure": [
            "- 수렴·안신: 산조인\n- 자음·청열: 지모\n- 활혈·행기: 천궁\n- 조화: 감초\n- 해석: 소모된 진액을 보충하고 허열을 진정시키는 수렴형 처방 구조",
            "- 조습·건비: 창출\n- 행기·제만: 후박\n- 이기·화담: 진피\n- 조화: 감초\n- 해석: 정체된 습탁을 제거하고 기운을 강하게 돌리는 배출/전환형 처방 구조",
            "- 승양·보기: 황기, 승마, 시호\n- 건비·익기: 인삼, 백출, 감초\n- 해석: 아래로 처진 기운을 강하게 위로 끌어올리는 발산/상승형 처방 구조",
            "- 삼보(三補): 숙지황·산수유·산약\n- 삼사(三瀉): 복령·택사·목단피\n- 해석: 보충축과 배출·완충축이 함께 배치된 균형형 처방 구조"
        ],
        "clinic_direction": [
            "- 보사: 영혈 보충과 허열 제어가 중심\n- 승강: 수렴 및 하행 안정 방향이 우세\n- 출입: 외부 발산보다는 내부 저장과 안신 방향\n- 한열: 허열을 식히는 청열 완충 방향",
            "- 보사: 사(瀉)법 위주 (제습, 행기)\n- 승강: 탁한 것을 내리고 기운을 소통시킴\n- 출입: 내부 정체 해소 및 배출 방향\n- 한열: 조습(燥濕)을 통한 냉습(冷濕) 제어",
            "- 보사: 기혈 보충 중심\n- 승강: 강력한 상승(승양) 방향 우세\n- 출입: 위기를 보충하여 체표로 에너지를 발산하는 방향\n- 한열: 기허로 인한 허열을 조절하고 따뜻하게 보함",
            "- 보사: 보충이 중심이나 사(瀉)법이 함께 배치됨\n- 승강: 저장·수렴·하행 안정 방향이 우세\n- 출입: 내부 보존과 수습 조절 방향\n- 한열: 허열 완충 방향"
        ],
        "clinic_caution": [
            "- 주간 졸음 및 무기력 동반 환자 주의\n- 진정제/수면제 병용 시 과도한 진정 작용 확인\n- 소화장애 동반 시 위장 부담 여부 확인",
            "- 임산부 및 심한 기허 환자 신중 투여\n- 장기 복용 시 진액 소모 우려\n- 건조한 체질(음허) 환자 주의 요망",
            "- 고혈압, 상열감, 급성 염증 환자 주의\n- 과도한 발한 및 음허화왕 환자 주의\n- 혈당 변동성 모니터링",
            "- 소화불량·설사 경향 환자는 숙지황 등으로 인한 위장 부담 확인\n- 항응고제 복용 환자는 목단피 등 혈류 관련 약재 확인\n- 당뇨약 복용 환자는 혈당 변화 확인\n- 간·신장 기능 저하 환자는 장기 복용 전 검사값 확인\n- 수술·시술 예정자는 복용 여부를 전문가와 상의"
        ],
        "clinic_followup": [
            "- 수면의 질 및 수면 시간\n- 주간 피로도 및 인지 기능\n- 두근거림 및 가슴 답답함\n- 소화 상태",
            "- 복부 팽만감 및 가스 발생 여부\n- 대변 상태\n- 식욕 및 소화력\n- 입마름 및 갈증 상태",
            "- 만성 피로도 회복 여부\n- 소화력 및 식욕 상태\n- 상열감 또는 두통 발생 여부\n- 혈압 및 혈당 수치 변동",
            "- 소화 상태\n- 설사 여부\n- 부종 변화\n- 피로감\n- 열감·도한\n- 혈당 변화\n- 간·신장 검사값"
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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "전통 처방 Core 패널", 
        "동의보감 병렬 해석 패널",
        "한의사용 임상 요약 패널",
        "Q6 64큐브 Core 주석 패널", 
        "처방 주변 변화 가능성 패널", 
        "보사·승강출입 균형 패널", # [NEW] 다면체 -> 보사·승강출입
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
        st.subheader("📖 2. 동의보감 병렬 해석 패널 (Donguibogam Layer)")
        st.error("**[해석 주의] 동의보감 해석 패널은 처방의 전통적 병증 이해, 양생, 장부·기혈·담음·허실·한열 관점을 한국 한의학 원전 맥락에서 정리하는 층입니다. 이는 동의보감이 현대 유전암호나 코돈 구조를 직접 설명했다는 뜻이 아니라, 전통 한의학의 병증·처방 해석 언어를 본 대시보드의 전통 처방 Core layer에 보강하는 원전 주석층입니다.**")
        
        st.markdown(f"#### 1. {selected_formula_name} 문헌적 병증 해석")
        st.markdown(f"- 📜 **동의보감 편제:** `{db_info['db_chapter']}`")
        st.markdown(f"- 🤒 **핵심 적응증 및 병리:** `{db_info['db_pattern']}`")
        
        st.markdown("#### 2. 양생(養生) 및 병리 조절 방향성")
        st.info(db_info['db_interpret'])

    # ------------------------------------------
    with tab3:
        st.subheader("🧑‍⚕️ 3. 한의사용 임상 요약 패널")
        st.warning(
            "본 패널은 Q6, H(3,4), 다면체 분석 결과를 한의사가 익숙한 "
            "**변증·보사·승강출입·한열허실 언어**로 다시 번역한 설명층입니다. "
            "자동 진단 또는 자동 처방 도구가 아닙니다."
        )

        st.subheader("1. 변증 요약")
        st.info(clinical_info['clinic_pattern'])

        st.subheader("2. 처방 구조 요약")
        st.markdown(clinical_info['clinic_structure'])

        st.subheader("3. 보사·승강출입 해석")
        st.markdown(clinical_info['clinic_direction'])

        st.subheader("4. Q6/H(3,4)/다면체 결과의 한의학 번역")
        translate_df = pd.DataFrame([
            {"연구자용 표현": "Q6 Core", "한의사용 해석": "처방의 기본 방향성을 6가지 변화축으로 정리한 것"},
            {"연구자용 표현": "H(3,4) Extension", "한의사용 해석": "처방 좌표 주변의 변화 가능성을 넓게 참고하는 생물정보 보조층"},
            {"연구자용 표현": "다면체 방향성", "한의사용 해석": "보사·승강출입·수렴발산의 균형 구조"},
            {"연구자용 표현": "RD 3:3 안정화", "한의사용 해석": "삼보와 삼사가 균형을 이루는 보충-배출 조절 구조"},
            {"연구자용 표현": "Octahedron 6방향", "한의사용 해석": "보존·보충·수렴·완충·발산·배출의 기본 방향성"},
            {"연구자용 표현": "VE 12축", "한의사용 해석": "약재 방향성을 더 세밀하게 나누는 보조 분류"},
            {"연구자용 표현": "H(3,4) diagonal edge", "한의사용 해석": "기본 방향에서 벗어나는 주변 변화 가능성 참고축"}
        ])
        st.dataframe(translate_df, use_container_width=True, hide_index=True)

        st.subheader("5. 임상 주의 포인트")
        st.markdown(clinical_info['clinic_caution'])

        st.subheader("6. 추적 관찰 항목")
        st.markdown(clinical_info['clinic_followup'])

    # ------------------------------------------
    with tab4:
        st.subheader("🧬 4. Q6 64큐브 Core 주석 패널")
        st.info("Q6 layer는 64괘·64코돈·384효사·384 directed bit-flip mutation을 병렬 배치하는 정보기하학적 해석층으로, 처방의 전통적 방향성을 6비트 상태공간의 언어로 주석화(Annotation)합니다.")
        st.success(f"**💡 Q6 64큐브 핵심 변화 방향:** `{formula_info['q6_core_vector']}`")
        
        for idx, row in merged_herbs_vectors.iterrows():
            st.markdown(f"### **[약재: {row['herb_name']}]**")
            st.markdown(f"- 🏛️ **전통 역할:** {row['role']} / {row['trad_role_desc']}")
            
            if str(row['q6_coord']) == "미고정":
                st.markdown(f"- 🧬 **Q6 Core 주석:** `좌표 미고정 / 추후 고정 필요` | **해석축:** {row['q6_axis']}")
            else:
                st.markdown(f"- 🧬 **Q6 Core 주석:** `{row['codon']} ➔ {row['amino_acid']}` | **64큐브 좌표:** n={row['q6_coord']} | **해석축:** {row['q6_axis']}")
                
            st.markdown(f"- ⚠️ **[해석 주의]:** 이 매핑은 {row['herb_name']}이(가) 실제 유전암호를 조절한다는 뜻이 아니라, 전통적 작용 방향을 코돈-아미노산 물성 벡터 언어로 주석화한 것입니다.")
            st.divider()

    # ------------------------------------------
    with tab5:
        st.subheader("🌐 5. 처방 주변 변화 가능성 패널")
        st.caption("연구자용 구조명: H(3,4) 생물정보 확장층")

        st.warning(
            "본 패널은 처방의 중심 방향에서 벗어날 수 있는 주변 변화 가능성을 "
            "한의학적 변증·보사·승강출입·안전성 언어로 번역한 보조 설명층입니다. "
            "약재가 실제 유전암호를 조절한다는 뜻이 아닙니다."
        )

        st.markdown("""
        ### 🔑 한의사용 해석

        H(3,4) Extension은 한의사에게는 복잡한 그래프가 아니라  
        **처방의 중심 변증 방향 주변에서 어떤 주의점이 생길 수 있는지 보는 확장 지도**로 이해하면 됩니다.

        - **Q6 Core**: 처방의 중심 변증 방향
        - **H(3,4) Extension**: 중심 방향 주변의 변증 전환 가능성
        - **Diagonal edge**: 기본 방향에서 벗어나는 주변 주의축
        - **Zone transition**: 보사·승강출입 균형이 다른 방향으로 넘어가는 지점
        """)

        if selected_formula_name == "보중익기탕":
            st.subheader("🎯 보중익기탕 주변 변화 가능성")
            st.info("중심 방향: 비위기허, 중기하함, 보기, 승양")

            st.markdown("""
            #### 1. 승양 과잉 방향
            - 상열감, 두근거림, 불면, 안면홍조, 혈압 상승 경향 확인
            - 고혈압 또는 심계가 있는 환자는 반응 관찰 필요

            #### 2. 보익 과잉 방향
            - 식체, 더부룩함, 복부 팽만, 소화불량 확인
            - 습담·식적이 뚜렷한 환자는 먼저 소화 상태 확인

            #### 3. 혈당·혈압 변동 방향
            - 인삼, 감초 등과 관련하여 당뇨약·혈압약 복용 환자 확인
            - 복용 전후 혈당, 혈압 변화 관찰

            #### 4. 약물 병용 주의 방향
            - 감초: 이뇨제·혈압약 병용 확인
            - 당귀: 항응고제/항혈소판제 병용 확인
            - 시호: 간 기능 저하 또는 간효소 상승 병력 확인
            """)

        elif selected_formula_name == "육미지황환":
            st.subheader("🎯 육미지황환 주변 변화 가능성")
            st.info("중심 방향: 간신음허, 정혈 부족, 허열, 자음, 보신")

            st.markdown("""
            #### 1. 보음·보신 부담 방향
            - 소화불량, 더부룩함, 설사 경향 확인
            - 숙지황 등으로 인한 위장 부담 가능성 확인

            #### 2. 수습 조절 방향
            - 부종, 소변 상태, 몸이 무거운 느낌 확인
            - 택사·복령 관련 수분 대사 방향 확인

            #### 3. 허열 완충 방향
            - 도한, 오심번열, 열감, 수면 변화 확인
            - 실열이 뚜렷한 경우 처방 방향 재검토

            #### 4. 약물 병용 주의 방향
            - 항응고제/항혈소판제 복용 시 목단피 확인
            - 당뇨약 복용 시 혈당 변화 확인
            - 간·신장 기능 저하 시 장기 복용 전 검사값 확인
            """)

        elif selected_formula_name == "산조인탕":
            st.subheader("🎯 산조인탕 주변 변화 가능성")
            st.info("중심 방향: 허번불면, 안신, 수렴, 내부 안정")

            st.markdown("""
            #### 1. 진정 과잉 방향
            - 졸림, 무기력, 반응 저하 확인
            - 수면제·진정제·항우울제 병용 확인

            #### 2. 허열·번조 방향
            - 야간 열감, 가슴 답답함, 불안, 입마름 확인
            - 실열성 불면인지 허번불면인지 구분 필요

            #### 3. 혈류 관련 주의 방향
            - 천궁 등 혈류 관련 약재와 항응고제 병용 확인

            #### 4. 소화 상태
            - 복부 불편감, 설사, 식욕 저하 여부 확인
            """)
        else: # 평위산 등 기본 처리
            st.subheader(f"🎯 {selected_formula_name} 주변 변화 가능성")
            st.info(f"중심 방향: {formula_info['pattern_tags']}")
            st.markdown("""
            - 기본 방향에서 벗어나는 주요 변증 전환 가능성 점검
            - 사용 약재에 따른 소화기계, 혈류, 대사 관련 주변 주의점 확인
            """)

    # ------------------------------------------
    # [NEW] 6. 보사·승강출입 균형 패널 (구 다면체 시각화 패널)
    # ------------------------------------------
    with tab6:
        st.subheader("⚖️ 6. 보사·승강출입 균형 패널")
        st.caption("연구자용 구조명: 다면체 방향성 시각화")

        st.info(
            "본 패널은 처방 효과를 증명하는 도구가 아니라, "
            "처방의 보사·승강출입·수렴발산·한열허실 방향을 구조적으로 정리한 보조 설명층입니다."
        )

        st.markdown("""
        ### 🔑 한의사용 해석

        다면체 분석은 도형 자체를 보라는 뜻이 아니라,  
        **처방이 어느 방향으로 치우치고, 어느 축에서 균형을 잡는지**를 보는 설명 방식입니다.

        - **정팔면체 Octahedron** → 보존·보충·수렴·완충·발산·배출의 6대 방향
        - **벡터평형체 VE** → 약재 방향을 더 세밀하게 나눈 보조 분류
        - **마름모십이면체 RD** → 보법과 사법, 보충축과 배출축의 균형 구조
        - **깎은 정팔면체 TO** → 처방 방향이 전신 네트워크로 확산되는 양상
        """)

        if selected_formula_name == "육미지황환":
            st.subheader("🎯 육미지황환의 보사·승강출입 균형")
            st.success("핵심 해석: 삼보와 삼사가 함께 배치된 보충-배출 균형형 처방")

            st.markdown("""
            #### 1. 보사 균형
            - **보충축:** 숙지황·산수유·산약
            - **배출·완충축:** 복령·택사·목단피
            - 해석: 보음·보신만 강조되는 처방이 아니라, 수습 조절과 허열 완충이 함께 배치됨

            #### 2. 승강출입
            - 저장·수렴·보존 방향이 강함
            - 급격한 발산이나 공하 방향은 낮음
            - 내부 진액과 정혈을 보존하는 방향으로 해석

            #### 3. 한열허실
            - 허증 중심
            - 허열 완충 방향
            - 수습 정체가 동반되는지 확인 필요

            #### 4. 임상 확인
            - 소화불량, 설사 경향
            - 부종, 소변 상태
            - 도한, 열감, 수면 변화
            - 항응고제, 당뇨약, 이뇨제 병용 여부
            - 간·신장 기능
            """)

        elif selected_formula_name == "보중익기탕":
            st.subheader("🎯 보중익기탕의 보사·승강출입 균형")
            st.success("핵심 해석: 보기·승양 방향이 강한 상승형 처방")

            st.markdown("""
            #### 1. 보사 균형
            - 보법 중심
            - 비위기허와 중기하함을 보완하는 방향
            - 사법이나 배출축은 상대적으로 약함

            #### 2. 승강출입
            - 상승·발산 방향이 강함
            - 중기를 들어 올리는 방향으로 해석
            - 기허하함 환자에게 적합한 방향에서 검토

            #### 3. 한열허실
            - 허증 중심
            - 실열·습열이 뚜렷한 경우 재검토 필요
            - 상열감이 있는 환자는 반응 확인 필요

            #### 4. 임상 확인
            - 혈압 상승 경향
            - 두근거림, 불면, 안면홍조
            - 식체, 복부 더부룩함
            - 당뇨약, 혈압약, 이뇨제 병용 여부
            """)

        elif selected_formula_name == "산조인탕":
            st.subheader("🎯 산조인탕의 보사·승강출입 균형")
            st.success("핵심 해석: 수렴·안신·내부 안정 방향이 강한 처방")

            st.markdown("""
            #### 1. 보사 균형
            - 보혈·자음과 안정 방향
            - 과도한 발산을 줄이고 내부 안정 방향으로 해석

            #### 2. 승강출입
            - 내부 수렴 방향이 강함
            - 정신적 번조를 가라앉히는 방향
            - 수면과 정서 안정 축을 중심으로 검토

            #### 3. 한열허실
            - 허번불면 방향에서 검토
            - 실열성 불면과 구분 필요

            #### 4. 임상 확인
            - 졸림, 무기력, 반응 저하
            - 수면제·진정제·항우울제 병용 여부
            - 간·신장 기능
            - 낮 시간 졸림 여부
            """)
        else: # 평위산 등 기본 처리
            st.subheader(f"🎯 {selected_formula_name}의 보사·승강출입 균형")
            st.success(f"핵심 해석: {formula_info['pattern_tags']}")
            st.markdown(poly_info['rd_plane'])

    # ------------------------------------------
    with tab7:
        st.subheader("📚 7. 황제내경 병렬 해석 패널")
        st.error("**[해석 주의] 본 패널은 황제내경 원문을 직접적인 생물학적 증명 자료로 사용하는 것이 아니라, 전통 생명론의 핵심 개념을 정보기하학 언어로 병렬 해석하는 교육·연구 보조 층입니다.**")
        
        st.markdown("#### 1. 황제내경 해석축 (Neijing Axis)")
        st.markdown(f"- 🏛️ **장부축 매핑:** `{nj_info['zang_fu']}`")
        st.markdown(f"- 🩸 **기혈진액 변증축:** `{nj_info['qi_blood']}`")
        st.markdown(f"- ☯️ **오행 작용 벡터:** `{nj_info['wuxing']}`")
        
        st.markdown("#### 2. 64큐브 - 황제내경 병렬 매핑 결론")
        st.info(nj_info['interpretation'])

    # ------------------------------------------
    with tab8:
        st.subheader("🚨 8. 안전성 확인 패널 (Safety Filter)")
        st.info("**이 경고는 처방 금지 판정이 아니라, 실제 복용 전 의료인의 추가 확인이 필요한 항목을 표시한 것입니다.**")
        
        fatal_alerts, high_alerts, med_alerts, notice_alerts, info_alerts = [], [], [], [], []

        if cond_preg and any(formula_safety["pregnancy_flag"].str.contains("금기|신중", na=False)): fatal_alerts.append("❌ **[특수조건: 금기 추정]** 임산부 금기/신중투여 약재 포함 (투여 타당성 절대 확인 요망)")
        if cond_surgery and any(formula_safety["drug_interaction_flag"].str.contains("항응고제|항혈소판제", na=False)): fatal_alerts.append("❌ **[수술 전후: 금기 추정]** 수술/시술 예정 환자의 지혈 지연 우려 (중단 검토 요망)")
        
        if med_anti_coag and any(formula_safety["drug_interaction_flag"].str.contains("항응고제|항혈소판제|아스피린", na=False)): high_alerts.append("🔴 **[약물병용: 높음]** 항응고제/항혈소판제 병용 시 출혈 위험 증가")
        if (med_cancer or med_immuno) and any(formula_safety["drug_interaction_flag"].str.contains("면역", na=False)): high_alerts.append("🔴 **[약물병용: 높음]** 항암제/면역억제제 병용 시 면역계 자극/상호작용 우려")
        if cond_liver or cond_kidney or cond_lab:
            if any(formula_safety["liver_kidney_flag"].str.contains("간|신장", na=False)): high_alerts.append("🔴 **[임상기저치: 높음]** 간/신장 기능 저하 환자의 장기 사용 시 배설 부담 및 효소 추이 검토 요망")
        
        if med_bp and any(formula_safety["drug_interaction_flag"].str.contains("혈압약", na=False)): med_alerts.append("🟡 **[약물병용: 중간]** 혈압약 병용 시 혈압 변동성 검토 요망")
        if med_diab and any(formula_safety["drug_interaction_flag"].str.contains("혈당", na=False)): med_alerts.append("🟡 **[약물병용: 중간]** 당뇨약 병용 시 혈당 변동성(시너지 효과 등) 검토 요망")
        if med_diuretic and any(formula_safety["drug_interaction_flag"].str.contains("이뇨제", na=False)): med_alerts.append("🟡 **[약물병용: 중간]** 이뇨제 병용 시 전해질 불균형 검토 요망")
        if (med_sedative or med_psych) and any(formula_safety["drug_interaction_flag"].str.contains("수면제|진정제", na=False)): med_alerts.append("🟡 **[약물병용: 중간]** 수면제/진정제 병용 시 과도한 진정 작용 유발 가능성 검토")
        
        if cond_dig and any(formula_safety["liver_kidney_flag"].str.contains("소화", na=False)): notice_alerts.append("🟢 **[소화기계: 주의]** 만성 소화불량 환자 복용 시 위장 장애(점액질 등) 부담 검토")
        if cond_frail: notice_alerts.append("🟢 **[특수조건: 주의]** 소아/고령자/허약자의 경우 초기 용량 감량 및 반응 모니터링 요망")
        if cond_allergy: notice_alerts.append("🟢 **[알레르기: 주의]** 약물 과민반응 병력이 있으므로 한약재 교차 알레르기 발생 여부 관찰 요망")
        notice_alerts.append("🟢 **[일반주의]** 복용 전후 전신 반응 주기적 확인 요망")

        if med_suppl: info_alerts.append("⚪ **[정보부족]** 타 한약/건기식 병용 시 문헌적 근거 부족으로 임상적 판단 및 주의 관찰 요망")

        if fatal_alerts:
            st.markdown("### **[우선순위: 금기 추정 (Contraindicated)]**")
            for alert in fatal_alerts: st.error(alert)
        if high_alerts:
            st.markdown("### **[우선순위: 높음 (High)]**")
            for alert in high_alerts: st.error(alert)
        if med_alerts:
            st.markdown("### **[우선순위: 중간 (Medium)]**")
            for alert in med_alerts: st.warning(alert)
        if notice_alerts:
            st.markdown("### **[우선순위: 주의 (Notice)]**")
            for alert in notice_alerts: st.info(alert)
        if info_alerts:
            st.markdown("### **[우선순위: 정보부족 (Info Needed)]**")
            for alert in info_alerts: st.markdown(alert)
            
        st.markdown("---")
        st.markdown("**약재별 상세 안전성 데이터**")
        st.dataframe(formula_safety[["herb_name", "drug_interaction_flag", "pregnancy_flag", "liver_kidney_flag", "evidence_note"]], use_container_width=True, hide_index=True)

        if lab_ast_alt or lab_creatinine or lab_hba1c or lab_bp:
            st.markdown("---")
            st.markdown("#### 🧪 임상 검사값 리마인더")
            st.markdown(f"- **AST/ALT**: {lab_ast_alt if lab_ast_alt else '입력안됨'} | **Creatinine/eGFR**: {lab_creatinine if lab_creatinine else '입력안됨'}")
            st.markdown(f"- **PT/INR**: {lab_pt_inr if lab_pt_inr else '입력안됨'} | **혈당/HbA1c**: {lab_hba1c if lab_hba1c else '입력안됨'}")
            st.markdown(f"- **혈압**: {lab_bp if lab_bp else '입력안됨'} | **수술예정**: {lab_surgery_date if lab_surgery_date else '없음'}")

    # ------------------------------------------
    with tab9:
        st.subheader("💬 9. 환자 설명문 패널")
        
        if selected_formula_name == "육미지황환":
            symptom_warnings = [w for w, cond in zip(["혈당 변동 가능성", "소화 상태 및 설사 여부", "피로감 및 부종 여부"], [med_diab, cond_dig, cond_liver]) if cond]
            warning_text = f"다만, 현재 입력된 질환 정보나 검사 수치가 체크되어 있으므로, 진료 과정에서 <b>{', '.join(symptom_warnings)}</b>를 세밀하게 확인해야 합니다." if symptom_warnings else "복용 전후의 반응을 진료 과정에서 세밀하게 확인하면서 조절해야 합니다."

            patient_html = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                <b>육미지황환</b>은 숙지황·산수유·산약의 삼보(三補)와 복령·택사·목단피의 삼사(三瀉)로 구성된 처방입니다. 전통적으로 자음·보신·허열 완충 방향에서 해석되며, 동의보감에서는 정(精)을 보존하는 양생의 핵심으로 설명합니다.<br><br>
                본 대시보드에서는 이 삼보삼사 구조를 Q6 64큐브 Core 층에서 보존형 변화와 수렴형 완충 방향으로 주석화하고, 다면체 층에서는 보충축과 배출축의 균형을 시각화합니다.<br><br>
                H(3,4) 생물학 Extension 층은 약재가 실제 유전암호를 조절한다는 뜻이 아니라, 선택된 코돈-아미노산 좌표 주변의 전체 단일염기 치환망과 물성 변화 가능성을 별도 분석하는 보조 정보층입니다.<br><br>
                {warning_text}
            </div>
            """
            st.markdown(patient_html, unsafe_allow_html=True)
            
        else:
            patient_html_generic = f"""
            <div style="background-color:#eaf3ff; padding:20px; border-radius:10px; line-height:1.8; color:#1e293b;">
                <b>{selected_formula_name}</b>은 한 가지 성분이 한 가지 증상만 조절하는 방식이 아니라, 여러 약재가 함께 작용하여 몸의 균형 방향을 조절하는 복합 처방입니다.<br><br>
                본 대시보드는 <b>{formula_info['indication_traditional']}</b>이라는 전통적 작용 방향을 Q6 64큐브 Core 층의 기하학적 언어로 주석화하고 동의보감의 병증 해석과 함께 시각화하여 처방의 이해를 돕습니다.<br><br>
                약재가 실제 유전암호를 조절한다는 뜻이 아니며, 복용 전후의 반응을 한의사의 진료 과정에서 세밀하게 확인하고 조절해야 합니다.
            </div>
            """
            st.markdown(patient_html_generic, unsafe_allow_html=True)
else:
    st.info("👈 좌측 패널에서 환자 정보를 입력하고 '처방 분석 및 리포트 생성' 버튼을 눌러주세요.")
