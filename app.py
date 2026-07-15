# app.py
# 한의사용 처방·침구·뜸 보조 대시보드 v96-safe + 텐세그리티 역학 엔진
# 실행: streamlit run app.py
# 목적: 교육·연구·임상 설명 보조. 자동 진단/처방/침구 시술 지시가 아닙니다.

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="한의사용 처방·침구·뜸 보조 대시보드", page_icon="🟣", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1400px;padding-top:1.2rem;padding-bottom:2rem}
h1,h2,h3{letter-spacing:-0.04em}
div[data-testid="stMetricValue"]{font-size:1.8rem}
</style>
""", unsafe_allow_html=True)

# ---------------- 공통 안전 함수 ----------------
def clean_cell(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    s = str(v)
    return "" if s.strip().lower() in {"none", "nan", "null"} else s

def clean_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [{k: clean_cell(v) for k, v in r.items()} for r in rows]

def df_from(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(clean_rows(rows))

def show_df(rows_or_df: Any, height: Optional[int] = None) -> None:
    if isinstance(rows_or_df, pd.DataFrame):
        df = rows_or_df.copy()
        for c in df.columns:
            df[c] = df[c].map(clean_cell)
    else:
        df = df_from(rows_or_df)
    if df.empty:
        st.caption("표시할 항목이 없습니다.")
        return
    kwargs = {"use_container_width": True, "hide_index": True}
    if isinstance(height, int) and height > 0:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)

def show_small(rows: List[Dict[str, Any]]) -> None:
    df = df_from(rows)
    if df.empty:
        st.caption("표시할 항목이 없습니다.")
    else:
        st.table(df)

def box(kind: str, text: str) -> None:
    {"info": st.info, "warn": st.warning, "error": st.error, "success": st.success}.get(kind, st.info)(text)

def has_any(text: str, words: List[str]) -> bool:
    text = clean_cell(text)
    return any(w in text for w in words)

# ---------------- 연구자용 Q6/H(3,4) ----------------
BASE_TO_BITS = {"G": "00", "A": "10", "U": "01", "C": "11"}
BITS_TO_BASE = {v: k for k, v in BASE_TO_BITS.items()}
GENETIC_CODE = {
"UUU":"Phe","UUC":"Phe","UUA":"Leu","UUG":"Leu","UCU":"Ser","UCC":"Ser","UCA":"Ser","UCG":"Ser",
"UAU":"Tyr","UAC":"Tyr","UAA":"Stop","UAG":"Stop","UGU":"Cys","UGC":"Cys","UGA":"Stop","UGG":"Trp",
"CUU":"Leu","CUC":"Leu","CUA":"Leu","CUG":"Leu","CCU":"Pro","CCC":"Pro","CCA":"Pro","CCG":"Pro",
"CAU":"His","CAC":"His","CAA":"Gln","CAG":"Gln","CGU":"Arg","CGC":"Arg","CGA":"Arg","CGG":"Arg",
"AUU":"Ile","AUC":"Ile","AUA":"Ile","AUG":"Met","ACU":"Thr","ACC":"Thr","ACA":"Thr","ACG":"Thr",
"AAU":"Asn","AAC":"Asn","AAA":"Lys","AAG":"Lys","AGU":"Ser","AGC":"Ser","AGA":"Arg","AGG":"Arg",
"GUU":"Val","GUC":"Val","GUA":"Val","GUG":"Val","GCU":"Ala","GCC":"Ala","GCA":"Ala","GCG":"Ala",
"GAU":"Asp","GAC":"Asp","GAA":"Glu","GAG":"Glu","GGU":"Gly","GGC":"Gly","GGA":"Gly","GGG":"Gly"}

def n_to_hyo_bits(n: int) -> str:
    return "".join(str((n >> i) & 1) for i in range(6))

def n_to_codon(n: int) -> str:
    bits = n_to_hyo_bits(n)
    return "".join(BITS_TO_BASE[bits[i:i+2]] for i in range(0, 6, 2))

def codon_to_n(codon: str) -> int:
    bits = "".join(BASE_TO_BITS[b] for b in codon.upper())
    return sum(int(bits[i]) << i for i in range(6))

def q6_neighbors(n: int) -> List[int]:
    return [n ^ (1 << i) for i in range(6)]

# ---------------- 처방 DB ----------------
FORMULAS: Dict[str, Dict[str, Any]] = {
"육미지황환": {
"분류":"보음·자음 처방","전통 변증":"간신음허, 허열도한, 정혈 부족, 하초 허약",
"처방 방향":"자음, 보신, 허열 완충, 수렴·안정","구성 약재":["숙지황","산수유","산약","복령","택사","목단피"],
"잘 맞는 환자상":"요슬산연, 도한, 오심번열, 구건, 만성 피로, 음허성 열감",
"주의 환자상":"설사, 식체, 더부룩함, 소화력 저하, 몸이 무겁고 습담이 뚜렷한 경우",
"감별 처방":"십전대보탕, 팔미지황환, 보중익기탕, 소요산",
"가감 방향":"허열이 뚜렷하면 청허열 방향, 소화력이 약하면 보비·화습 방향 보조 검토",
"핵심 혈위":["KI3","BL23","BL18","SP6","CV4","CV6","KI6"],"처방 방향축":["보충축","수렴·안정축","완충·조화축"],
"뜸 가능 조건":"하복부 냉감, 하초 허한, 요슬 냉통이 분명하고 열감·도한이 약할 때 제한 검토",
"뜸 주의 조건":"도한, 오심번열, 구건, 오후 열감, 붉은 혀, 열성 피부질환이 있으면 강한 뜸 주의",
"권장 강도":"약~중. 허열이 동반되면 보류 또는 매우 약하게 검토",
"환자용 핵심":"몸 아래쪽의 허약감, 마른 열감, 도한, 입마름 같은 상태를 보완하는 방향에서 검토됩니다."},
"팔진탕": {
"분류":"기혈쌍보 처방","전통 변증":"기혈양허, 만성피로, 안색창백, 어지럼, 식욕저하",
"처방 방향":"보기, 보혈, 기혈쌍보, 균형 보강","구성 약재":["인삼","백출","복령","감초","숙지황","당귀","천궁","작약"],
"잘 맞는 환자상":"피로, 안색창백, 어지럼, 식욕저하, 회복력 저하","주의 환자상":"습담·식체가 강하거나 복부팽만이 심한 경우",
"감별 처방":"십전대보탕, 보중익기탕, 귀비탕","가감 방향":"식체가 있으면 소화 보조 방향, 허열이 있으면 보혈·자음 강도 조절",
"핵심 혈위":["ST36","SP6","BL20","BL17","CV6","CV12"],"처방 방향축":["보충축","완충·조화축"],
"뜸 가능 조건":"기허·양허·냉감이 분명하고 염증성 열감이 없을 때 제한 검토","뜸 주의 조건":"열감, 염증, 상열감, 흉민이 뚜렷하면 강한 뜸 주의","권장 강도":"약~중",
"환자용 핵심":"기운과 혈의 부족으로 피로와 어지럼, 식욕저하가 동반될 때 검토됩니다."},
"십전대보탕": {
"분류":"대보원기·기혈쌍보 처방","전통 변증":"기혈양허, 허로, 허한, 수술·질병 후 회복 저하",
"처방 방향":"대보원기, 기혈쌍보, 온보","구성 약재":["인삼","백출","복령","감초","숙지황","당귀","천궁","작약","황기","육계"],
"잘 맞는 환자상":"허약, 피로, 추위 탐, 회복 지연, 안색 저하","주의 환자상":"상열감, 실열, 염증, 고혈압 조절 불량, 복부팽만이 강한 경우",
"감별 처방":"팔진탕, 보중익기탕, 귀비탕","가감 방향":"상열감이 있으면 온보 강도를 낮추고 식체가 있으면 소화 보조",
"핵심 혈위":["ST36","CV6","BL20","BL23","GV4","SP6"],"처방 방향축":["보충축","승양·상승축"],
"뜸 가능 조건":"허한·냉감·기력저하가 분명할 때 제한 검토","뜸 주의 조건":"고혈압 조절 불량, 상열감, 얼굴 홍조, 염증성 열감이 있으면 주의","권장 강도":"약~중",
"환자용 핵심":"기운과 혈을 함께 보강하고 몸을 따뜻하게 하는 방향의 처방입니다."},
"보중익기탕": {
"분류":"보기·승양 처방","전통 변증":"비위기허, 중기하함, 기허발열, 만성피로",
"처방 방향":"보기, 승양, 중기 보강, 비위 회복","구성 약재":["황기","인삼","백출","감초","당귀","진피","승마","시호"],
"잘 맞는 환자상":"피로, 무력, 식욕저하, 처짐, 기단, 자한","주의 환자상":"상열감, 불면, 심계, 실열, 혈압 조절 불량, 흉민이 뚜렷한 경우",
"감별 처방":"팔진탕, 십전대보탕, 귀비탕","가감 방향":"상열감이 강하면 승양·온보 강도를 낮추고 소화불량이 강하면 보비·화습 보조",
"핵심 혈위":["ST36","CV6","GV20","BL20","SP3","CV12"],"처방 방향축":["보충축","승양·상승축","소통·전환축"],
"뜸 가능 조건":"기허·냉감·하함이 뚜렷하고 상열감이 약할 때 제한 검토","뜸 주의 조건":"상열감, 불면, 심계, 고혈압 조절 불량, 구건이 뚜렷하면 강한 뜸 주의","권장 강도":"약. 상열감이 있으면 보류 검토",
"환자용 핵심":"떨어진 기운을 올리고 비위 기능을 보강하는 방향에서 검토됩니다."},
"산조인탕": {
"분류":"양혈안신 처방","전통 변증":"허번불면, 혈허, 음허 내열, 심간 불안",
"처방 방향":"수렴, 안신, 내부 안정, 허열 완충","구성 약재":["산조인","복령","지모","천궁","감초"],
"잘 맞는 환자상":"잠을 깊이 못 잠, 심계, 불안, 건망, 피로, 허번","주의 환자상":"과도한 졸림, 진정제·수면제 병용, 운전·기계 조작 예정",
"감별 처방":"귀비탕, 천왕보심단, 가미소요산","가감 방향":"실열성 불면이면 청열 방향, 담음이 강하면 화담 방향 보조 검토",
"핵심 혈위":["HT7","PC6","SP6","KI6","BL15","Anmian"],"처방 방향축":["수렴·안정축","완충·조화축"],
"뜸 가능 조건":"허한·냉감이 분명하고 불면이 허한성일 때 제한 검토","뜸 주의 조건":"도한, 오심번열, 심번, 열감이 뚜렷하면 뜸보다 안신·청허열 방향 확인","권장 강도":"보류~약",
"환자용 핵심":"긴장과 불안을 가라앉히고 수면을 안정시키는 방향에서 검토됩니다."},
"귀비탕": {
"분류":"심비양허·기혈보강 처방","전통 변증":"심비양허, 불면, 건망, 심계, 식욕저하, 피로",
"처방 방향":"보기, 보혈, 안신, 심비 보강","구성 약재":["인삼","황기","백출","복령","용안육","산조인","목향","감초","당귀","원지"],
"잘 맞는 환자상":"불면, 건망, 심계, 피로, 식욕저하, 안색창백","주의 환자상":"습담·식체가 강하거나 상열감이 뚜렷한 경우",
"감별 처방":"산조인탕, 보중익기탕, 팔진탕","가감 방향":"불면 중심이면 안신 방향, 식체가 있으면 소화 보조",
"핵심 혈위":["HT7","SP6","ST36","BL20","BL15","PC6"],"처방 방향축":["보충축","수렴·안정축"],
"뜸 가능 조건":"심비양허와 냉감·기허가 분명할 때 제한 검토","뜸 주의 조건":"상열감, 심번, 구건, 불면 악화가 있으면 강한 뜸 주의","권장 강도":"약",
"환자용 핵심":"피로와 불면, 심계가 함께 있을 때 심비를 보강하고 안정시키는 방향입니다."},
"사물탕": {
"분류":"보혈조혈 처방","전통 변증":"혈허, 어지럼, 안색창백, 월경량 감소, 건조",
"처방 방향":"보혈, 조혈, 혈분 완충","구성 약재":["숙지황","당귀","천궁","작약"],
"잘 맞는 환자상":"혈허, 어지럼, 안색창백, 건조, 월경 관련 허증","주의 환자상":"습담·식체, 설사, 복부팽만이 강한 경우",
"감별 처방":"팔진탕, 귀비탕, 온경탕","가감 방향":"기허가 동반되면 보기 방향, 어혈이 있으면 활혈 방향 보조",
"핵심 혈위":["SP6","BL17","BL20","ST36","LR3"],"처방 방향축":["보충축","완충·조화축"],
"뜸 가능 조건":"혈허와 냉감이 함께 있을 때 제한 검토","뜸 주의 조건":"열감·도한·상열감이 강하면 보류 검토","권장 강도":"보류~약",
"환자용 핵심":"혈의 부족과 관련된 어지럼, 건조, 안색 저하를 보완하는 방향입니다."},
"소요산": {
"분류":"소간해울·건비조혈 처방","전통 변증":"간울, 혈허, 비허, 스트레스성 소화불량, 흉협불편",
"처방 방향":"소간, 해울, 건비, 조화","구성 약재":["시호","당귀","작약","백출","복령","감초","생강","박하"],
"잘 맞는 환자상":"스트레스성 흉협불편, 답답함, 식욕저하, 월경 전후 불편","주의 환자상":"심한 허한, 설사, 체력 저하가 뚜렷한 경우",
"감별 처방":"가미소요산, 이진탕, 평위산","가감 방향":"허열이 있으면 청열 방향, 소화력이 약하면 보비 방향 보조",
"핵심 혈위":["LR3","PC6","SP6","ST36","GB34"],"처방 방향축":["소통·전환축","완충·조화축"],
"뜸 가능 조건":"복부 냉감·비허가 동반될 때 제한 검토","뜸 주의 조건":"상열감, 흉민, 두통, 염증성 열감이 강하면 강한 뜸 주의","권장 강도":"보류~약",
"환자용 핵심":"스트레스와 소화, 긴장성 불편이 함께 있을 때 기혈 흐름을 조화시키는 방향입니다."},
"이진탕": {
"분류":"화담이기 처방","전통 변증":"담음정체, 오심구토, 어지럼, 흉민, 습담",
"처방 방향":"조습, 화담, 이기, 위기 하강","구성 약재":["반하","진피","복령","감초","생강","오매"],
"잘 맞는 환자상":"가래, 오심, 더부룩함, 어지럼, 흉민, 습담","주의 환자상":"음허건조, 진액 부족, 강한 구건이 동반된 경우",
"감별 처방":"평위산, 소요산, 반하백출천마탕","가감 방향":"열담이면 청열화담, 허증이 강하면 보비 방향 보조",
"핵심 혈위":["ST40","PC6","CV12","ST36","SP9"],"처방 방향축":["배출·이수축","소통·전환축"],
"뜸 가능 조건":"냉담·비위허한이 뚜렷할 때 제한 검토","뜸 주의 조건":"열담, 구건, 인후건조, 음허가 뚜렷하면 강한 뜸 주의","권장 강도":"보류~약",
"환자용 핵심":"가래, 메스꺼움, 더부룩함처럼 습담이 막힌 상태를 풀어주는 방향입니다."},
"평위산": {
"분류":"조습화위 처방","전통 변증":"비위습탁, 식체, 복부팽만, 더부룩함",
"처방 방향":"조습, 행기, 소도, 비위 소통","구성 약재":["창출","후박","진피","감초","생강","대조"],
"잘 맞는 환자상":"복부팽만, 더부룩함, 식체, 습담, 식욕저하","주의 환자상":"음허건조, 진액 부족, 강한 구건·건조감",
"감별 처방":"이진탕, 보중익기탕, 소요산","가감 방향":"허증이 강하면 보비 방향, 열이 있으면 청열 방향 보조",
"핵심 혈위":["CV12","ST36","SP9","ST25","PC6"],"처방 방향축":["소통·전환축","배출·이수축"],
"뜸 가능 조건":"비위허한·복부 냉감이 동반될 때 제한 검토","뜸 주의 조건":"열감, 구건, 음허 건조가 분명하면 강한 뜸 주의","권장 강도":"약",
"환자용 핵심":"비위에 습이 쌓이고 더부룩한 상태를 풀어주는 방향입니다."},
"오령산": {
"분류":"이수삼습 처방","전통 변증":"수습정체, 소변불리, 부종, 갈증·구토, 수분대사 장애",
"처방 방향":"이수, 삼습, 수분대사 조절, 기화 보조","구성 약재":["택사","저령","복령","백출","계지"],
"잘 맞는 환자상":"소변불리, 부종, 몸이 무거움, 갈증, 구토, 수분 정체","주의 환자상":"탈수, 전해질 이상, 신장 기능 저하, 이뇨제 병용",
"감별 처방":"이진탕, 평위산, 진무탕","가감 방향":"허한이 뚜렷하면 온양화기 방향, 열이 있으면 청열이수 방향 검토",
"핵심 혈위":["SP9","CV9","BL22","KI7","ST36"],"처방 방향축":["배출·이수축","소통·전환축"],
"뜸 가능 조건":"수습정체와 냉감·양허가 동반될 때 제한 검토","뜸 주의 조건":"탈수, 열감, 신장 기능 저하, 임신 가능성, 피부질환이 있으면 주의","권장 강도":"보류~약",
"환자용 핵심":"몸의 수분 정체와 소변 문제를 조절하는 방향입니다."}
}

COMPARE_ROWS = [{"처방": k, "분류": v["분류"], "전통 변증": v["전통 변증"], "핵심 방향": v["처방 방향"], "잘 맞는 환자상": v["잘 맞는 환자상"], "주의 환자상": v["주의 환자상"]} for k, v in FORMULAS.items()]

# ---------------- 361 경혈 생성 ----------------
MERIDIANS = {
"LU":(11,"수태음폐경","상지·흉부","보충축, 소통·전환축","폐기·호흡·표증 방향 참고","흉부 깊은 자침 주의"),
"LI":(20,"수양명대장경","상지·면부","소통·전환축","표열·면구·장부 소통 방향 참고","임신 중 강자극 주의"),
"ST":(45,"족양명위경","두면·흉복·하지","보충축, 소통·전환축","비위·소화·기혈 생성 방향 참고","복부·흉부 자침 깊이 확인"),
"SP":(21,"족태음비경","하지·복부","보충축, 수렴·안정축","비·간·신 조절, 혈·음·수습 조절 방향 참고","임신 가능성 확인"),
"HT":(9,"수소음심경","상지","수렴·안정축","심계·불면·안신 방향 참고","과도한 자극 주의"),
"SI":(19,"수태양소장경","상지·견갑·두면","소통·전환축","경항·견갑·표증 방향 참고","경부 자침 주의"),
"BL":(67,"족태양방광경","두항·배부·하지","보충축, 소통·전환축","배수혈·요배부·장부 반응점 방향 참고","흉배부 깊은 자침 주의"),
"KI":(27,"족소음신경","하지·흉복","보충축, 수렴·안정축","신·음혈·하초·수면 방향 참고","임신·허약자 자극 강도 확인"),
"PC":(9,"수궐음심포경","상지·흉부","수렴·안정축, 소통·전환축","심흉·오심·정서 긴장 방향 참고","강자극 주의"),
"TE":(23,"수소양삼초경","상지·두면","소통·전환축","소양·수도·상중하초 소통 방향 참고","두경부 자극 확인"),
"GB":(44,"족소양담경","두면·체측·하지","소통·전환축","간담·측부·긴장·통증 방향 참고","임신 중 일부 혈위 주의"),
"LR":(14,"족궐음간경","하지·복부","소통·전환축, 완충·조화축","간울·혈분·정서 긴장 방향 참고","강자극 주의"),
"CV":(24,"임맥","전중선·복부","보충축, 수렴·안정축","하초·중초·원기·음혈 방향 참고","임신·복부 수술력 확인"),
"GV":(28,"독맥","후중선·두항","승양·상승축","양기·두항·승양 방향 참고","두경부·척추부 자극 확인")}
ACU_OVERRIDES = {
"KI3":("태계","Taixi","신음·신기 보강, 허열 완충, 요슬산연·하초 허약 방향 보조","자음·보신 처방에서 핵심 후보. 하초 허약과 허열 완충 방향에 맞음","허열·음허·임신 관련 상태 확인","조건부 가능","허열·음허·도한·구건이 뚜렷하면 강한 뜸 주의","약"),
"BL23":("신수","Shenshu","신허·하초 허약 보조, 요슬산연, 만성 허약 방향","신허와 하초 허약을 배수혈에서 보조하기 위한 핵심 후보","요부 심부 자침 위험, 신장 부위 해부학적 안전 확인","조건부 가능","하복부 냉감·허한이 분명할 때 제한 검토","약~중"),
"BL18":("간수","Ganshu","간혈·간음 조절, 정서 긴장과 혈분 조절 보조","간신음허·혈허·협륵 긴장과 연결될 때 보조 후보","흉배부 깊은 자침 주의","제한적","허열·음허·구건·도한이 뚜렷하면 강한 뜸 주의","약"),
"SP6":("삼음교","Sanyinjiao","비·간·신 조절, 혈·음·수습 조절, 하초·부인과 방향 보조","음혈·수습·하초 방향을 동시에 다루는 핵심 교회혈 후보","임신 가능성·임신 중 사용은 전문가 판단","조건부 가능","허열·음허·구건·도한이 뚜렷하면 강한 뜸 주의","약"),
"CV4":("관원","Guanyuan","하초 보강, 정혈·원기 보강, 허약·냉감 방향","하초 허약과 정혈 부족 방향에서 보조 후보","복부 수술력, 임신, 심혈관 상태 확인","조건부 가능","하복부 냉감·허한이 분명할 때 제한 검토","약~중"),
"CV6":("기해","Qihai","원기 보강, 기허 조절, 하복부 허약 보조","기허·피로·하복부 무력감이 동반될 때 보조 후보","복부 열감, 임신, 염증 상태 확인","조건부 가능","하복부 냉감·허한이 분명할 때 제한 검토","약~중"),
"KI6":("조해","Zhaohai","음교맥, 수면·허열·음혈 부족 방향 보조","음허·허열·수면 불안정이 동반될 때 보조 후보","허열·음허 상태 확인. 강한 뜸은 신중","제한적","허열·음허·구건·불면이 뚜렷하면 강한 뜸 주의","약"),
"ST36":("족삼리","Zusanli","비위 보강, 기혈 생성, 피로·소화 방향 보조","기허·피로·소화력 저하가 중심일 때 핵심 후보","과도한 강자극 주의","조건부 가능","열감·염증·상열감이 있으면 강도 조절","약~중"),
"CV12":("중완","Zhongwan","비위 조절, 식체·복부팽만·소화불량 방향","소화 상태를 처방 방향과 함께 조정하기 위한 후보","복부 수술력, 임신, 급성 복통 확인","조건부 가능","복부 열감·염증성 소견 주의","약"),
"GV20":("백회","Baihui","승양, 두부·정신 안정, 처짐 보조","중기하함·처짐·무력감에서 승양 방향 보조 후보","혈압, 두통, 상열감 확인","제한적","상열감·고혈압·두통이 있으면 강한 뜸 금물","보류~약"),
"HT7":("신문","Shenmen","안신, 심계·불면·불안 방향","불면·심계·불안이 중심일 때 핵심 후보","과도한 진정 반응 주의","보류","강한 온열 자극보다는 안신 방향 중심","보류"),
"PC6":("내관","Neiguan","심흉부 안정, 오심, 긴장 완화 방향","심계·불안·오심·흉민이 동반될 때 후보","항응고제·출혈 경향 확인","보류~약","국소 피부 상태와 열감 확인","보류~약"),
"LR3":("태충","Taichong","간울 소통, 긴장·흉협불편 조절 방향","간울·스트레스성 긴장과 연결될 때 후보","강자극 주의","보류","상열감·두통·흥분이 있으면 강한 자극 주의","보류"),
"ST40":("풍륭","Fenglong","담음·습담 조절 방향","담음정체, 가래, 어지럼, 흉민이 있을 때 후보","국소 혈관·신경 주의","조건부 가능","열담·구건·음허가 뚜렷하면 강한 뜸 주의","약"),
"SP9":("음릉천","Yinlingquan","수습·부종·소변 문제 방향","수습정체와 부종·소변불리 방향 보조 후보","부종·피부상태 확인","조건부 가능","열감·염증·피부질환 확인","약"),
"CV9":("수분","Shuifen","수분 정체, 복부 수습 조절 방향","부종·소변불리·수분 정체 보조 후보","복부 수술력·임신·급성 복통 확인","조건부 가능","복부 열감·염증·임신 주의","약"),
"BL20":("비수","Pishu","비위 운화, 기혈 생성, 습담 조절","소화력 저하, 피로, 습담 경향이 있을 때 후보","흉배부 깊은 자침 주의","조건부 가능","열감·염증성 상태 주의","약~중"),
"BL17":("격수","Geshu","혈분 조절, 혈허·어혈 방향 참고","혈허·어혈·긴장성 혈분 문제 확인 시 후보","흉배부 깊은 자침 주의","제한적","열감·출혈경향 확인","보류~약"),
"BL15":("심수","Xinshu","심계·불면·정서 긴장 보조","심계·불면·안신 방향에서 보조 후보","흉배부 깊은 자침 주의","제한적","상열감·염증성 상태 확인","보류~약"),
"Anmian":("안면","Anmian","수면 안정, 불면 방향 참고","불면이 주 증상일 때 보조 후보","경부 해부학적 안전 확인","보류","경부 강한 온열 자극은 신중","보류"),
"SP3":("태백","Taibai","비위 보강, 운화 보조","비위기허와 식욕저하가 중심일 때 후보","국소 자극 확인","조건부 가능","열감·염증 확인","약"),
"GB34":("양릉천","Yanglingquan","간담 소통, 측부 긴장 완화","간울·흉협불편·긴장성 소견 때 후보","국소 자극 확인","보류","강한 자극 주의","보류"),
"ST25":("천추","Tianshu","장부 소통, 복부팽만·대변 조절","복부팽만·식체·대변 문제가 있을 때 후보","복부 수술력·임신 확인","조건부 가능","복부 열감·염증 확인","약"),
"BL22":("삼초수","Sanjiaoshu","수도·기화 조절","수분정체·소변불리 방향 후보","흉요부 자침 주의","조건부 가능","열감·신장기능 확인","약"),
"KI7":("복류","Fuliu","수분대사·신기 조절","부종·소변·땀 조절 문제 때 후보","허열·음허 확인","조건부 가능","허열·구건 확인","약"),
"GV4":("명문","Mingmen","원양 보조, 허한 방향","허한·냉감·기력저하가 분명할 때 후보","강한 온보 자극 신중","조건부 가능","상열감·혈압 확인","약~중")
}

def build_acu() -> List[Dict[str, str]]:
    rows = []
    for pre, (cnt, mer, area, axis, meaning, caution) in MERIDIANS.items():
        for i in range(1, cnt+1):
            code = f"{pre}{i}"
            r = {"code":code,"혈명":code,"standard_name":code,"경락":mer,"부위군":area,"처방 방향축":axis,"임상 의미":meaning,
                 "왜 후보인가":"현재 입력 증상·처방 방향과 맞을 때 참고 후보","주의점":caution,"뜸 가능 여부":"조건부 가능",
                 "뜸 주의 조건":"열감·염증·피부 상태·임신 가능성 확인","권장 강도":"보류~약"}
            if code in ACU_OVERRIDES:
                name, std, meaning2, why, safe, moxa, moxa_warn, strength = ACU_OVERRIDES[code]
                r.update({"혈명":name,"standard_name":std,"임상 의미":meaning2,"왜 후보인가":why,"주의점":safe,"뜸 가능 여부":moxa,"뜸 주의 조건":moxa_warn,"권장 강도":strength})
            rows.append(r)
    assert len(rows) == 361
    return clean_rows(rows)
ACUPOINT_361 = build_acu()
ACU_INDEX = {r["code"]: r for r in ACUPOINT_361}
if "Anmian" not in ACU_INDEX:
    name, std, meaning2, why, safe, moxa, moxa_warn, strength = ACU_OVERRIDES["Anmian"]
    ACU_INDEX["Anmian"] = {"code":"Anmian","혈명":name,"standard_name":std,"경락":"경외기혈","부위군":"두경부","처방 방향축":"수렴·안정축","임상 의미":meaning2,"왜 후보인가":why,"주의점":safe,"뜸 가능 여부":moxa,"뜸 주의 조건":moxa_warn,"권장 강도":strength}

def acu(code: str) -> Dict[str, str]:
    return ACU_INDEX.get(code, {"code":code,"혈명":code,"standard_name":code,"경락":"참고","부위군":"","처방 방향축":"","임상 의미":"전문가 검토","왜 후보인가":"전문가 판단","주의점":"안전 확인","뜸 가능 여부":"보류","뜸 주의 조건":"전문가 판단","권장 강도":"보류"})

# ---------------- 입력 상태 ----------------
EXAMPLES = {
"육미지황환 테스트": {"formula_name":"육미지황환","chief":"허리와 무릎이 약하고 오후에 열감이 있으며, 입마름과 도한이 있음. 피로가 오래가고 소변이 잦음.","global_note":"만성피로와 회복력 저하를 주소로 내원함. 안색은 창백하고 쉽게 피로하며, 식욕저하와 가벼운 어지럼을 동반함. 맥은 허약하고 설질은 담백하고 치흔이 관찰됨.","goal":"피로 회복, 허열 완충, 하초 허약 보조, 소화 부담 최소화","pulse":"허맥, 세맥","tongue":"건조, 소태","abdomen":"하복부 무력","bp":"118/76","labs":"","meds":"","checked_safety":["만성 소화불량/설사"]},
"보중익기탕 테스트": {"formula_name":"보중익기탕","chief":"오래 피곤하고 기운이 처지며 식욕이 떨어짐. 말할 때 힘이 없고 오후에 무력감이 심함.","global_note":"중기하함과 기허가 의심됨. 단, 불면과 상열감이 동반되는지 확인 필요.","goal":"피로 회복, 기허 보강, 비위 기능 회복","pulse":"허맥","tongue":"담백, 치흔","abdomen":"상복부 무력","bp":"126/78","labs":"","meds":"","checked_safety":[]},
"산조인탕 테스트": {"formula_name":"산조인탕","chief":"잠을 깊이 못 자고 쉽게 깨며 심계와 불안이 있음. 낮에는 피로하고 집중이 어려움.","global_note":"허번불면과 혈허 경향 확인. 수면제 병용 여부와 낮 졸림을 반드시 확인.","goal":"수면 안정, 심계 완화, 불안 완충","pulse":"세맥","tongue":"건조","abdomen":"긴장","bp":"112/70","labs":"","meds":"수면제 복용 여부 확인 필요","checked_safety":["수면제/항우울제/진정제"]}
}
DEFAULT = dict(EXAMPLES["육미지황환 테스트"])
DEFAULT["show_research"] = False
for k, v in DEFAULT.items():
    st.session_state.setdefault(k, v)

SAFETY_OPTIONS = ["항응고제/항혈소판제/NSAIDs","혈압약","당뇨약","수면제/항우울제/진정제","임신/수유","소아/고령자/허약자","만성 소화불량/설사","피부 감각저하/당뇨성 말초신경병증","실열/염증성 열감","피부질환/상처/감염","수술/시술 예정","간·신장 기능 저하","다른 한약·건기식·보충제 병용"]

with st.sidebar:
    st.header("입력")
    ex_name = st.selectbox("테스트 예시 불러오기", list(EXAMPLES.keys()), key="example_name")
    if st.button("예시 적용", width="stretch"):
        for k, v in EXAMPLES[ex_name].items():
            st.session_state[k] = v
        st.rerun()
    st.selectbox("처방 선택", list(FORMULAS.keys()), key="formula_name")
    st.text_area("주증상 / 메모", key="chief", height=110)
    st.text_area("한의사 종합소견", key="global_note", height=150)
    st.text_area("치료 목표", key="goal", height=90)
    st.subheader("진맥·설진·복진")
    st.text_input("맥상", key="pulse")
    st.text_input("설질·설태", key="tongue")
    st.text_input("복진/형태", key="abdomen")
    st.subheader("안전성")
    st.text_input("혈압", key="bp", placeholder="예: 118/76")
    st.text_area("AST/ALT, creatinine/eGFR 등 검사값", key="labs", height=80)
    st.text_area("현재 복용약 상세", key="meds", height=80)
    st.multiselect("해당 항목 선택", SAFETY_OPTIONS, key="checked_safety")
    st.checkbox("🔬 연구자용 Q6/H(3,4) 탭 보기", key="show_research")

formula_name = st.session_state.get("formula_name","육미지황환")
formula = FORMULAS.get(formula_name, FORMULAS["육미지황환"])
chief = st.session_state.get("chief","")
global_note = st.session_state.get("global_note", st.session_state.get("global",""))
goal = st.session_state.get("goal","")
pulse = st.session_state.get("pulse","")
tongue = st.session_state.get("tongue","")
abdomen = st.session_state.get("abdomen","")
bp = st.session_state.get("bp","")
labs = st.session_state.get("labs","")
meds = st.session_state.get("meds","")
checked_safety = st.session_state.get("checked_safety",[])

# ---------------- 분석 함수 ----------------
def parse_bp(text: str) -> Optional[tuple[int,int]]:
    m = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", clean_cell(text))
    return (int(m.group(1)), int(m.group(2))) if m else None

def bp_message(text: str) -> str:
    p = parse_bp(text)
    if not p:
        return "혈압 미입력. 고혈압·저혈압 병력과 현재 복용약 확인."
    s, d = p
    if s >= 160 or d >= 100:
        return f"입력 혈압 {s}/{d}: 고혈압 범위 가능성. 강한 온열·승양 자극 전 재확인."
    if s >= 140 or d >= 90:
        return f"입력 혈압 {s}/{d}: 혈압 추적 및 혈압약 복용 여부 확인."
    if s < 90 or d < 60:
        return f"입력 혈압 {s}/{d}: 저혈압 경향 가능성. 어지럼·허약감 확인."
    return f"입력 혈압 {s}/{d}: 입력 기준으로는 고혈압 경고가 자동 발생하지 않습니다."

def safety_rows() -> List[Dict[str,str]]:
    rows=[]; text=" ".join([chief, global_note, labs, meds])
    if "만성 소화불량/설사" in checked_safety or has_any(text,["설사","식체","더부룩","복부팽만","소화력 저하"]):
        rows.append({"확인 항목":"만성 소화불량/설사","우선순위":"높음","확인 내용":"보음·보혈·보약 처방의 위장 부담, 설사·복부팽만·식체 확인."})
    if not clean_cell(labs):
        rows.append({"확인 항목":"검사값 미입력","우선순위":"중간","확인 내용":"장기 복용 전 AST/ALT, creatinine/eGFR 확인 권장."})
    if "항응고제/항혈소판제/NSAIDs" in checked_safety or has_any(meds,["아스피린","와파린","클로피도그렐","항응고","항혈소판"]):
        rows.append({"확인 항목":"항응고제/항혈소판제/NSAIDs","우선순위":"높음","확인 내용":"출혈 경향, 자침 후 멍·출혈, 약재 상호작용 가능성 확인."})
    if "수면제/항우울제/진정제" in checked_safety or has_any(meds,["수면제","졸피뎀","벤조","항우울","진정제"]):
        rows.append({"확인 항목":"수면제/항우울제/진정제","우선순위":"중간","확인 내용":"졸림, 반응저하, 낮 시간 기능저하, 병용 약물 확인."})
    if "임신/수유" in checked_safety:
        rows.append({"확인 항목":"임신/수유","우선순위":"높음","확인 내용":"약재·혈위·뜸 사용은 반드시 전문가 판단. 강자극 혈위 주의."})
    if "피부 감각저하/당뇨성 말초신경병증" in checked_safety:
        rows.append({"확인 항목":"피부 감각저하/말초신경병증","우선순위":"높음","확인 내용":"뜸 화상 위험 증가. 온열 자극 전 피부 감각 확인."})
    if "실열/염증성 열감" in checked_safety or has_any(text,["열감","염증","붉은","상열","오후열감"]):
        rows.append({"확인 항목":"열감/염증성 소견","우선순위":"중간","확인 내용":"강한 뜸·온보·승양 자극 전 허열/실열 구분."})
    if "수술/시술 예정" in checked_safety:
        rows.append({"확인 항목":"수술/시술 예정","우선순위":"중간","확인 내용":"시술 전후 출혈·감염·복용약 조정 여부 확인."})
    if "간·신장 기능 저하" in checked_safety:
        rows.append({"확인 항목":"간·신장 기능 저하","우선순위":"높음","확인 내용":"장기 복용 전후 검사값 확인 및 용량·기간 신중 검토."})
    return rows or [{"확인 항목":"특이 안전 신호 없음","우선순위":"낮음","확인 내용":"입력된 정보 기준. 실제 문진·맥진·검사값 확인 필요."}]

def safety_summary(rows: List[Dict[str,str]]) -> str:
    s = "; ".join(f"{r['확인 항목']}({r['우선순위']})" for r in rows if r["확인 항목"]!="특이 안전 신호 없음")
    return s or "현재 입력 기준 특이 안전 신호 없음"

def candidate_rows() -> List[Dict[str,str]]:
    out=[]
    for c in formula["핵심 혈위"]:
        a=acu(c)
        out.append({"code":c,"혈명":a["혈명"],"standard_name":a["standard_name"],"경락":a["경락"],"처방 방향축":a["처방 방향축"],"임상 의미":a["임상 의미"],"왜 후보인가":a["왜 후보인가"],"주의점":a["주의점"]})
    return out

def moxa_rows() -> List[Dict[str,str]]:
    out=[]
    for c in formula["핵심 혈위"]:
        a=acu(c)
        out.append({"code":c,"혈명":a["혈명"],"가능/보류":a["뜸 가능 여부"],"주의 조건":a["뜸 주의 조건"],"권장 강도":a["권장 강도"],"시술 전 확인":a["주의점"]})
    return out

def chart_note() -> str:
    safe = safety_rows()
    ac_names = ", ".join([f"{c} {acu(c)['혈명']}" for c in formula["핵심 혈위"]])
    checked = ", ".join(checked_safety) if checked_safety else "특이 선택 없음"
    safe_lines = "\n".join([f"- {r['확인 항목']}({r['우선순위']}): {r['확인 내용']}" for r in safe if r["확인 항목"]!="특이 안전 신호 없음"]) or "- 현재 입력 기준 특이 안전 신호는 뚜렷하지 않음. 단, 실제 문진과 검사값 확인 필요."
    return f"""[변증 초안]
{formula['전통 변증']} 경향. 주증상과 전체 소견을 종합할 때 '{formula_name}' 방향 검토.
입력 주증상: {chief or '미입력'}
종합 소견: {global_note or '미입력'}

[처방 방향]
{formula['처방 방향']}
치료 목표: {goal or '미입력'}
주의 환자상: {formula['주의 환자상']}

[진맥·설진·복진 대조]
맥상: {pulse or '미입력'}
설질·설태: {tongue or '미입력'}
복진/형태: {abdomen or '미입력'}
해석: 입력 소견이 처방 방향과 다르면 처방 자체보다 감별·가감·침구 방향을 먼저 조정.

[침구 방향]
핵심 후보: {ac_names}
후보 근거: 해당 혈위는 자동 시술 지시가 아니라 처방 변증과 자주 연결되는 참고 후보입니다.
임상 확인: 처방 방향과 침구 자극 방향이 서로 충돌하지 않는지 확인.

[뜸]
가능 조건: {formula['뜸 가능 조건']}
주의 조건: {formula['뜸 주의 조건']}
권장 강도: {formula['권장 강도']}
판단: 뜸은 화상·감염·피부 자극 위험이 있으므로 감각저하, 당뇨성 말초신경병증, 실열·상열, 임신, 피부질환을 확인한 뒤 결정.

[안전성 및 추적]
{safe_lines}
혈압: {bp_message(bp)}
검사/복용약 메모: {labs or '검사값 미입력'} / {meds or '복용약 미입력'}
체크된 안전 항목: {checked}

[최종 확인]
이 문서는 EMR에 복사하기 위한 초안입니다. 자동 확정 처방이 아니며, 실제 처방 여부·용량·복용 기간·침구 혈위·자침 깊이·뜸 부위와 강도는 면허가 있는 한의사가 문진, 맥진, 설진, 복진, 검사값, 복용약, 환자 상태를 종합하여 최종 결정합니다."""

def patient_text() -> str:
    checked = ", ".join(checked_safety) if checked_safety else "현재 입력 기준 특별히 체크된 항목 없음"
    return f"""입력된 증상/메모: {chief or '미입력'}

{formula_name}은/는 전통 한의학에서 '{formula['전통 변증']}' 방향에서 검토되는 처방입니다.

쉽게 말하면, {formula['환자용 핵심']} 다만 환자 상태에 따라 맞지 않을 수 있으므로 맥, 설진, 복진, 복용약, 검사값을 함께 확인해야 합니다.

현재 이 처방은 '{formula['처방 방향']}' 방향에서 검토됩니다.

복용 전후에는 다음 항목을 관찰해 주세요.
- 소화상태, 대변 변화, 피로감 변화, 수면 변화, 소변 변화, 열감·도한, 혈압/혈당 변화

현재 안전 체크 항목:
- {checked}

불편감이 생기거나 기존 증상이 악화되면 임의로 계속 복용하지 말고 담당 한의사에게 알려야 합니다.

이 설명은 처방을 자동으로 정하거나 효과를 보장하는 내용이 아닙니다. 실제 복용 여부와 용량은 담당 한의사가 결정합니다."""

def core_rows():
    return [{"항목":k, "내용":v} for k,v in [
        ("처방명",formula_name),("분류",formula["분류"]),("전통 변증",formula["전통 변증"]),("처방 방향",formula["처방 방향"]),
        ("구성 약재",", ".join(formula["구성 약재"])),("잘 맞는 환자상",formula["잘 맞는 환자상"]),("주의 환자상",formula["주의 환자상"]),
        ("감별 처방",formula["감별 처방"]),("가감 방향",formula["가감 방향"])]]

def axes_rows():
    axes=set(formula["처방 방향축"])
    base=[("보충축","기·혈·음·양·정혈을 보태는 방향","피로, 무력, 안색창백, 식욕저하, 요슬산연"),
          ("수렴·안정축","흩어진 기운을 안으로 모으고 안정시키는 방향","불면, 심계, 도한, 불안, 진액 소모"),
          ("승양·상승축","아래로 처진 기운을 위로 끌어올리는 방향","처짐, 중기하함, 무력감, 기단, 하수감"),
          ("배출·이수축","정체된 수분·습담·노폐를 밖으로 빼는 방향","부종, 소변불리, 몸무거움, 습담"),
          ("소통·전환축","막힌 기혈과 비위 흐름을 돌리는 방향","흉협고만, 복부팽만, 식체, 기체, 어혈"),
          ("완충·조화축","치우친 보·사·한·열을 조절하는 중간 조화 방향","보하면 체하고, 사하면 허해지는 중간형")]
    return [{"축":a,"뜻":b,"대표 소견":c,"현재 처방 관련성":"중심" if a in axes else "보조 확인"} for a,b,c in base]

def herb_rows():
    roles=["군약","신약","신약","좌사약","사약","사약","보조","보조","보조","보조"]
    return [{"역할":roles[i] if i<len(roles) else "구성","약재":h,"전통 역할":"처방 방향을 구성하는 약재. 실제 용량·배합은 한의사 판단","확인":"귀경·사기·오미·용량 확인"} for i,h in enumerate(formula["구성 약재"])]

def dongui_rows():
    return [
        {"동의보감 편제":"신(腎)·허로(虛勞)·정(精)","연결 이유":"간신 부족, 허로, 정혈 부족 편제와 연결 가능"},
        {"동의보감 편제":"허로·기혈","연결 이유":"오래 지치고 회복력이 떨어지는 허로·기혈 부족 해석"},
        {"동의보감 편제":"내상","연결 이유":"소화력이 약한 경우 비위 내상 관점과 함께 재검토"}]

def get_tensegrity_html(acu_list: List[str]) -> str:
    acu_buttons_html = ""
    for acu_code in acu_list[:4]: # 최대 4개까지만 버튼 생성
        acu_name = acu(acu_code)["혈명"]
        acu_buttons_html += f"""<button onclick="applyTreatment('{acu_code}')" class="btn-heal py-2 px-1 rounded shadow text-sm">{acu_code} {acu_name}</button>\n"""

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>한의 CDSS 텐세그리티 역학 모델</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Pretendard', sans-serif; overflow: hidden; margin:0; padding:0; }}
            canvas {{ background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); box-shadow: 0 0 20px rgba(0,0,0,0.5); border-radius: 1rem; width: 100%; height: 100%; object-fit: contain; }}
            .panel-bg {{ background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(10px); border: 1px solid #334155; }}
            .btn-disease {{ background: #7f1d1d; color: white; transition: all 0.2s; }}
            .btn-disease:hover {{ background: #991b1b; }}
            .btn-heal {{ background: #14532d; color: white; transition: all 0.2s; }}
            .btn-heal:hover {{ background: #166534; }}
        </style>
    </head>
    <body class="flex h-screen w-screen p-4 gap-4 box-border">

        <!-- Left Panel: CDSS Controls -->
        <div class="w-1/3 p-5 flex flex-col gap-5 z-10 panel-bg shadow-xl rounded-xl h-full overflow-y-auto">
            <div>
                <h1 class="text-xl font-bold text-cyan-400 mb-1">☯️ 한의 CDSS 역학 엔진</h1>
                <p class="text-xs text-slate-400">4D 하이퍼큐브 텐세그리티 (수승화강 모델)</p>
            </div>

            <!-- Dashboard -->
            <div class="bg-slate-800 p-3 rounded-lg border border-slate-700">
                <h2 class="text-md font-semibold mb-2 text-slate-200">📊 실시간 정적 평형 상태</h2>
                <div class="flex justify-between items-center mb-1">
                    <span class="text-slate-400 text-sm">벡터 합력 (Vector Sum)</span>
                    <span id="vectorSum" class="font-mono text-cyan-300 font-bold text-sm">{{ 0.00, 0.00 }}</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-slate-400 text-sm">생체 시스템 상태</span>
                    <span id="healthStatus" class="px-2 py-1 rounded text-xs font-bold bg-green-900 text-green-300">무극 (평형)</span>
                </div>
            </div>

            <!-- Disease Input -->
            <div>
                <h2 class="text-md font-semibold mb-2 border-b border-slate-700 pb-1 text-red-400">🔥 병리 입력 (사기 침범)</h2>
                <div class="grid grid-cols-2 gap-2">
                    <button onclick="applyPathology('heart')" class="btn-disease py-2 rounded shadow text-sm">심화항염 (불면/번조)</button>
                    <button onclick="applyPathology('liver')" class="btn-disease py-2 rounded shadow text-sm">간기울결 (스트레스)</button>
                    <button onclick="applyPathology('spleen')" class="btn-disease py-2 rounded shadow text-sm">비위허약 (식체)</button>
                    <button onclick="applyPathology('kidney')" class="btn-disease py-2 rounded shadow text-sm">신양허 (요통/냉증)</button>
                </div>
            </div>

            <!-- Treatment Input -->
            <div>
                <h2 class="text-md font-semibold mb-2 border-b border-slate-700 pb-1 text-green-400">🌿 침구 처방 (현재 처방 맞춤)</h2>
                <div class="grid grid-cols-2 gap-2">
                    {acu_buttons_html}
                </div>
            </div>
            
            <button onclick="resetSystem()" class="mt-auto bg-slate-700 hover:bg-slate-600 py-2 rounded font-bold text-slate-200 transition text-sm">↻ 시스템 초기화 (평형)</button>
        </div>

        <!-- Right Panel: Canvas Visualization -->
        <div class="w-2/3 h-full relative flex justify-center items-center">
            <canvas id="tensegrityCanvas"></canvas>
        </div>

    <script>
        const canvas = document.getElementById('tensegrityCanvas');
        const ctx = canvas.getContext('2d');
        
        // Setup internal resolution for sharp rendering
        const size = 800;
        canvas.width = size;
        canvas.height = size;
        const cx = size / 2;
        const cy = size / 2;
        const scale = 180;

        const u = Math.SQRT2 - 1;
        const r2 = Math.SQRT2;

        const baseNodes = [
            {{ x: 0, y: 0, label: "단전(비위)", id: "spleen" }},
            {{ x: 0, y: -r2, label: "심(心)", id: "heart" }},
            {{ x: 0, y: r2, label: "신(腎)", id: "kidney" }},
            {{ x: r2, y: 0, label: "폐(肺)", id: "lung" }},
            {{ x: -r2, y: 0, label: "간(肝)", id: "liver" }},
            {{ x: u, y: -u, label: "", id: "ne" }},
            {{ x: -u, y: -u, label: "", id: "nw" }},
            {{ x: u, y: u, label: "", id: "se" }},
            {{ x: -u, y: u, label: "", id: "sw" }}
        ];

        let nodes = baseNodes.map(n => ({{ ...n, cx: n.x, cy: n.y, tx: n.x, ty: n.y }}));

        const edges = [
            [0,1], [0,2], [0,3], [0,4],
            [0,5], [0,6], [0,7], [0,8],
            [1,5], [5,3], [3,7], [7,2], [2,8], [8,4], [4,6], [6,1],
            [1,3], [3,2], [2,4], [4,1]
        ];

        function updatePhysics() {{
            let totalForceX = 0;
            let totalForceY = 0;

            nodes.forEach(n => {{
                n.cx += (n.tx - n.cx) * 0.05;
                n.cy += (n.ty - n.cy) * 0.05;
                totalForceX += (n.cx - n.x);
                totalForceY += (n.cy - n.y);
            }});

            const forceMag = Math.sqrt(totalForceX**2 + totalForceY**2);
            document.getElementById('vectorSum').innerText = `{{ ${{totalForceX.toFixed(2)}}, ${{totalForceY.toFixed(2)}} }}`;
            
            const statusEl = document.getElementById('healthStatus');
            if (forceMag < 0.05) {{
                statusEl.innerText = "무극 (정적평형)";
                statusEl.className = "px-2 py-1 rounded text-xs font-bold bg-green-900 text-green-300";
            }} else {{
                statusEl.innerText = "병리 (불균형)";
                statusEl.className = "px-2 py-1 rounded text-xs font-bold bg-red-900 text-red-300";
            }}
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            edges.forEach(([i, j]) => {{
                const n1 = nodes[i];
                const n2 = nodes[j];
                
                const baseX = baseNodes[i].x - baseNodes[j].x;
                const baseY = baseNodes[i].y - baseNodes[j].y;
                const baseLen = Math.sqrt(baseX**2 + baseY**2);
                
                const curX = n1.cx - n2.cx;
                const curY = n1.cy - n2.cy;
                const curLen = Math.sqrt(curX**2 + curY**2);
                
                const tension = Math.abs(curLen - baseLen);

                ctx.beginPath();
                ctx.moveTo(cx + n1.cx * scale, cy + n1.cy * scale);
                ctx.lineTo(cx + n2.cx * scale, cy + n2.cy * scale);
                
                if (tension > 0.1) {{
                    ctx.strokeStyle = `rgba(239, 68, 68, ${{0.4 + tension}})`;
                    ctx.lineWidth = 2 + tension * 5;
                }} else {{
                    ctx.strokeStyle = 'rgba(6, 182, 212, 0.3)';
                    ctx.lineWidth = 2;
                }}
                ctx.stroke();
            }});

            nodes.forEach(n => {{
                const px = cx + n.cx * scale;
                const py = cy + n.cy * scale;
                const dist = Math.sqrt((n.cx - n.x)**2 + (n.cy - n.y)**2);
                
                ctx.beginPath();
                ctx.arc(px, py, dist > 0.1 ? 12 : 8, 0, Math.PI * 2);
                ctx.fillStyle = dist > 0.1 ? '#ef4444' : '#06b6d4';
                ctx.fill();
                ctx.strokeStyle = '#1e293b';
                ctx.lineWidth = 2;
                ctx.stroke();

                if (n.label) {{
                    ctx.fillStyle = '#cbd5e1';
                    ctx.font = '16px Pretendard, sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(n.label, px, py - 18);
                }}
            }});
        }}

        function loop() {{
            updatePhysics();
            draw();
            requestAnimationFrame(loop);
        }}
        requestAnimationFrame(loop);

        function applyPathology(organ) {{
            const intensity = 0.6;
            if (organ === 'heart') {{ nodes[1].ty -= intensity; nodes[1].tx += intensity * 0.2; }}
            if (organ === 'liver') {{ nodes[4].tx -= intensity; nodes[4].ty -= intensity * 0.2; }}
            if (organ === 'kidney') {{ nodes[2].ty += intensity; nodes[2].tx -= intensity * 0.2; }}
            if (organ === 'spleen') {{ nodes[0].tx += intensity * 0.5; nodes[0].ty += intensity * 0.5; }}
        }}

        function applyTreatment(acu_code) {{
            // 혈위별로 가장 연관성 높은 장부 노드를 평형으로 복원
            const mapping = {{
                'HT7': 1, 'PC6': 1, 'BL15': 1, // Heart
                'LR3': 4, 'GB34': 4, 'BL18': 4, // Liver
                'KI3': 2, 'KI6': 2, 'BL23': 2, 'CV4': 2, // Kidney
                'LU1': 3, 'LU9': 3, // Lung
                'ST36': 0, 'CV12': 0, 'BL20': 0, 'SP3': 0, 'CV6': 0 // Spleen/Center
            }};
            
            let targetIdx = mapping[acu_code];
            // SP6 (삼음교) 같은 교회혈은 간, 비, 신을 모두 약간씩 회복
            if (acu_code === 'SP6') {{
                nodes[0].tx = baseNodes[0].x; nodes[0].ty = baseNodes[0].y;
                nodes[2].tx = baseNodes[2].x; nodes[2].ty = baseNodes[2].y;
                nodes[4].tx = baseNodes[4].x; nodes[4].ty = baseNodes[4].y;
                return;
            }}

            if (targetIdx !== undefined) {{
                nodes[targetIdx].tx = baseNodes[targetIdx].x;
                nodes[targetIdx].ty = baseNodes[targetIdx].y;
            }} else {{
                // 기본 매핑이 없는 혈위는 중심(비위)을 회복시킴
                nodes[0].tx = baseNodes[0].x;
                nodes[0].ty = baseNodes[0].y;
            }}
        }}

        function resetSystem() {{
            nodes.forEach((n, i) => {{
                n.tx = baseNodes[i].x;
                n.ty = baseNodes[i].y;
            }});
        }}
    </script>
    </body>
    </html>
    """

# ---------------- 화면 ----------------
safety = safety_rows()
st.title("🟣 한의사용 처방·침구·뜸 보조 대시보드")
st.caption("교육·연구·임상 설명 보조용입니다. 자동 진단, 자동 처방, 자동 침구 시술 지시가 아닙니다.")
st.success(f"현재 처방 방향: {formula['처방 방향']}")

tabs = st.tabs([
    "1. 통합 요약", "2. 차트 소견서", "3. 361 경혈 DB", "4. 침구·혈위 후보", 
    "5. 뜸 주의", "6. 진맥·설진·복진 대조", "7. 처방 방향 6축·감별", 
    "8. 황제내경·동의보감", "9. 전통 처방 Core", "10. 안전성 확인", 
    "11. 환자 설명문", "12. 연구자용 Q6/H(3,4)", "13. 텐세그리티 역학 엔진"
])

with tabs[0]:
    st.header("1. 통합 요약")
    box("info","한의사가 바쁜 진료 환경에서 가장 먼저 확인해야 할 핵심 정보입니다. 자동 확정이 아니라 검토 순서를 정리합니다.")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("선택 처방", formula_name); c2.metric("핵심 후보 혈위", f"{len(formula['핵심 혈위'])}개"); c3.metric("안전 확인", f"{len([r for r in safety if r['우선순위'] in {'높음','중간'}])}건"); c4.metric("361 DB","361개")
    a,b=st.columns(2)
    with a:
        st.subheader("✅ 처방이 잘 맞는 환자상"); st.write(formula["잘 맞는 환자상"])
        st.subheader("🔁 감별 및 가감 방향"); st.write(f"유사 처방 감별: {formula['감별 처방']}"); st.write(f"가감 조정: {formula['가감 방향']}")
    with b:
        st.subheader("⚠️ 주의하거나 재검토할 환자상"); st.write(formula["주의 환자상"])
        st.markdown("**현재 입력에서 잡힌 안전 신호**"); show_df(safety)
    st.subheader("핵심 혈위 요약"); show_df(pd.DataFrame(candidate_rows())[["code","혈명","경락","처방 방향축","임상 의미","왜 후보인가"]])

with tabs[1]:
    st.header("2. 차트용 압축 소견서")
    box("warn","EMR 차트에 복사해 넣기 좋은 압축 초안입니다. 자동 확정 처방이 아니므로 한의사가 직접 검토·수정하십시오.")
    note=chart_note()
    st.text_area("소견서 텍스트", note, height=430)
    st.download_button("차트 소견서 다운로드", data=note, file_name=f"{formula_name}_chart_note.txt", mime="text/plain")
    st.subheader("차트형 핵심 체크")
    show_small([{"항목":"변증 방향","내용":formula["전통 변증"]},{"항목":"처방 방향","내용":formula["처방 방향"]},{"항목":"핵심 혈위","내용":", ".join([f"{c} {acu(c)['혈명']}" for c in formula["핵심 혈위"]])},{"항목":"뜸 기준","내용":f"{formula['뜸 가능 조건']} / {formula['뜸 주의 조건']}"},{"항목":"안전 신호","내용":safety_summary(safety)}])

with tabs[2]:
    st.header("3. 361 표준 경혈 DB")
    box("info","전체 DB는 기본적으로 접어 두고, 현재 처방과 관련 높은 핵심 후보 혈위를 먼저 보여줍니다.")
    st.subheader("현재 처방 핵심 후보 먼저 보기")
    show_df(pd.DataFrame(candidate_rows())[["code","혈명","standard_name","경락","처방 방향축","임상 의미","왜 후보인가","주의점"]])
    with st.expander("전체 361 경혈 DB 열기 / 검색", expanded=False):
        acu_df=pd.DataFrame(ACUPOINT_361)
        c1,c2,c3=st.columns(3)
        mf=c1.multiselect("경락 필터", sorted(acu_df["경락"].unique()))
        af=c2.multiselect("처방 방향축 필터", ["보충축","수렴·안정축","승양·상승축","배출·이수축","소통·전환축","완충·조화축"])
        sr=c3.text_input("경혈 검색", placeholder="예: KI3, 태계, Taixi")
        f=acu_df.copy()
        if mf: f=f[f["경락"].isin(mf)]
        if af:
            mask=pd.Series(False,index=f.index)
            for x in af: mask = mask | f["처방 방향축"].str.contains(x, na=False)
            f=f[mask]
        if sr:
            mask=pd.Series(False,index=f.index)
            for col in f.columns: mask = mask | f[col].astype(str).str.lower().str.contains(sr.lower(), na=False)
            f=f[mask]
        st.caption(f"표시: {len(f)} / 전체 361개")
        show_df(f, height=420)
        st.download_button("361 경혈 DB CSV 다운로드", data=f.to_csv(index=False).encode("utf-8-sig"), file_name="acupoint_361_db.csv", mime="text/csv")

with tabs[3]:
    st.header("4. 침구·혈위 후보")
    box("warn","아래 혈위는 자동 시술 지시가 아니라, 해당 처방의 변증 방향과 임상적으로 자주 연결되는 후보군을 근거와 함께 제시한 것입니다.")
    show_df(candidate_rows())
    for c in formula["핵심 혈위"]:
        a=acu(c)
        with st.expander(f"{c} {a['혈명']} — 왜 이 혈위인가", expanded=(c==formula["핵심 혈위"][0])):
            st.markdown(f"**경락:** {a['경락']} / **표준명:** {a['standard_name']}")
            st.markdown(f"**임상 의미:** {a['임상 의미']}")
            st.markdown(f"**후보 근거:** {a['왜 후보인가']}")
            st.markdown(f"**자침·안전:** {a['주의점']}")
    st.subheader("침구 시 확인할 임상 포인트")
    st.markdown("- 처방 방향과 침구 자극 방향이 서로 충돌하지 않는지 확인\n- 허증 환자에게 과도한 사법·강자극을 쓰지 않도록 주의\n- 실열·상열감 환자에게 승양·온보 자극이 과하지 않은지 확인\n- 복부 냉감, 더부룩함, 압통, 흉협고만은 복진과 함께 판단")

with tabs[4]:
    st.header("5. 뜸 치료 가능 여부 및 주의 조건")
    box("error","뜸은 화상, 감염, 피부 자극 위험이 있으므로 감각저하, 당뇨성 말초신경병증, 실열·상열, 임신, 피부질환을 반드시 확인해야 합니다.")
    st.subheader("처방별 뜸 조건: 가능/주의/강도")
    show_small([{"항목":"가능 조건","내용":formula["뜸 가능 조건"]},{"항목":"주의 조건","내용":formula["뜸 주의 조건"]},{"항목":"권장 강도","내용":formula["권장 강도"]}])
    st.subheader("핵심 혈위별 뜸 검토"); show_df(moxa_rows())
    st.subheader("강도 기준")
    show_small([{"강도":"보류","의미":"열감·염증·감각저하·임신 등 위험 신호가 있거나 처방 방향상 뜸 필요성이 낮음"},{"강도":"약","의미":"짧고 약한 온열 자극만 검토. 환자 반응을 즉시 확인"},{"강도":"약~중","의미":"허한·냉감이 명확할 때 제한적으로 검토"},{"강도":"중","의미":"허한·원기 저하가 분명하고 금기 신호가 없을 때만 전문가 판단으로 검토"}])

with tabs[5]:
    st.header("6. 진맥·설진·복진 대조")
    box("info","자동 판정이 아니라 선택 처방의 목표 소견과 실제 입력 소견을 대조하는 참고표입니다.")
    show_small([{"항목":"맥상","입력":pulse or "미입력","처방 적합성 대조":"허맥·세맥은 보충축·수렴축과 잘 맞을 수 있음. 현맥은 소통축 검토."},{"항목":"설질·설태","입력":tongue or "미입력","처방 적합성 대조":"건조·소태는 음허 방향 참고, 후태·황태는 습담·실열 재검토."},{"항목":"복진/형태","입력":abdomen or "미입력","처방 적합성 대조":"하복부 무력은 하초 허약 방향 확인, 복부 긴장·팽만은 비위·담음·기체 확인."}])
    st.subheader("해석 참고")
    st.markdown("- 맥상·설진·복진이 처방 방향과 다르면 처방 자체보다 감별·가감·침구 방향을 먼저 조정합니다.\n- 예: 보음 처방을 보면서 후태·복부팽만·설사가 뚜렷하면 보음약의 위장 부담을 확인합니다.")

with tabs[6]:
    st.header("7. 처방 방향 6축·감별")
    show_df(axes_rows())
    st.subheader("주요 처방 비교표"); show_df(pd.DataFrame(COMPARE_ROWS), height=360)
    st.subheader("감별·가감"); st.markdown(f"**감별 처방:** {formula['감별 처방']}"); st.markdown(f"**가감 방향:** {formula['가감 방향']}")

with tabs[7]:
    st.header("8. 황제내경·동의보감 원전 대응 해석")
    box("warn","원전을 현대 생물학적으로 증명한다는 뜻이 아니라, 입력 소견을 전통 개념과 편제에 맞춰 정리하는 주석층입니다.")
    st.subheader("황제내경 해당 개념")
    show_small([{"개념":"음양","해석":"부족한 음분과 과한 허열의 균형 확인","한의사 질문":"실제 열인가, 부족에서 생긴 열감인가?"},{"개념":"장부·기혈진액","해석":"간·신·정혈·진액의 부족과 소모 확인","한의사 질문":"허리·무릎, 도한, 구건, 소변 상태는 어떤가?"},{"개념":"개합추","해석":"수렴과 저장 기능이 약해진 상태 확인","한의사 질문":"땀·수면·정서·소변의 새는 양상이 있는가?"}])
    st.subheader("동의보감 해당 편제"); show_small(dongui_rows())
    st.subheader("한의사용 해석")
    box("info","소견서에 입력된 증상과 변증을 음양, 장부·기혈진액, 승강출입, 표본중기, 삼음삼양 병기 등의 언어로 재정리하고, 동의보감의 병증 편제와 연결해 처방·침구·뜸 방향이 같은 치료 방향을 향하는지 확인합니다.")

with tabs[8]:
    st.header("9. 전통 처방 Core")
    show_small(core_rows())
    st.subheader("군신좌사·약재 방향"); show_df(herb_rows())
    st.subheader("동의보감 해당 편제"); show_small(dongui_rows())

with tabs[9]:
    st.header("10. 안전성 확인")
    box("warn","아래 항목은 금지 판정이 아니라 추가 확인이 필요한 위험 신호입니다.")
    show_df(safety)
    st.subheader("혈압 해석")
    msg=bp_message(bp)
    box("warn" if "고혈압" in msg or "저혈압" in msg or "미입력" in msg else "success", msg)
    st.subheader("검사값·복용약 메모")
    show_small([{"항목":"AST/ALT 등 간기능","입력값":labs or "미입력"},{"항목":"creatinine/eGFR 등 신장기능","입력값":labs or "미입력"},{"항목":"혈압","입력값":bp or "미입력"},{"항목":"복용약","입력값":meds or "미입력"},{"항목":"체크된 안전 항목","입력값":", ".join(checked_safety) if checked_safety else "없음"}])

with tabs[10]:
    st.header("11. 환자 설명문 패널")
    box("info","환자에게 복용을 안내할 때 사용할 수 있는 쉬운 표현입니다. 실제 안내 전에는 환자 상황에 맞게 한의사가 검토해야 합니다.")
    exp=patient_text()
    st.text_area("환자 설명문", exp, height=430)
    st.download_button("환자 설명문 다운로드", data=exp, file_name=f"{formula_name}_patient_explanation.txt", mime="text/plain")

with tabs[11]:
    st.header("12. 연구자용 Q6 / H(3,4) 보조 구조")
    if not st.session_state.get("show_research", False):
        box("info","이 탭은 연구자용입니다. 한의사용 판단 화면에서는 6축·처방·혈위 해설만 보면 됩니다.")
    show_df([{"구조":"Q6 64큐브 Core","vertices":64,"undirected_edges":192,"directed_edges":384,"한의사용 번역":"처방 변화를 6개 방향축으로 정리하는 Core 구조"},{"구조":"H(3,4) Extension","vertices":64,"undirected_edges":288,"directed_edges":576,"한의사용 번역":"처방 주변 변화 가능성과 감별 지점을 넓게 보는 확장 구조"}])
    codon_rows=[]
    for n in [0,9,18,63]:
        codon=n_to_codon(n)
        codon_rows.append({"n":n,"효 순서 비트":n_to_hyo_bits(n),"codon":codon,"amino_acid":GENETIC_CODE[codon],"Q6 이웃":", ".join(map(str,q6_neighbors(n))),"H(3,4) 이웃 수":9})
    show_df(codon_rows)
    box("warn","약재-코돈-아미노산 매핑은 약재가 실제 유전자나 아미노산을 조절한다는 뜻이 아닙니다. 전통적 작용 방향을 생명정보학적 벡터 언어로 주석화한 연구자용 해석층입니다.")

with tabs[12]:
    st.header("13. 텐세그리티 역학 시각화 엔진 (Hypercube 2D Projection)")
    box("info", "4차원 하이퍼큐브의 정적 평형 원리를 응용한 침구 생체 역학 모델입니다. 좌측 사이드바에서 선택한 처방의 핵심 혈위가 '침구 처방' 버튼에 자동으로 연동됩니다.")
    
    # Generate and embed the interactive HTML engine
    html_content = get_tensegrity_html(formula["핵심 혈위"])
    components.html(html_content, height=750, scrolling=False)

st.divider()
st.caption("교육·연구·임상 설명 보조용입니다. 자동 진단, 자동 처방, 자동 침구 시술 지시가 아닙니다. 실제 처방 여부와 용량, 혈위, 자침 깊이, 유침 시간, 보사법, 뜸 부위와 강도는 면허가 있는 한의사가 환자 상태를 종합하여 최종 결정해야 합니다.")
