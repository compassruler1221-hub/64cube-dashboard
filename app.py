# app.py
# 한의사 임상 구조화 × 6축 기하 분석 보조도구 v9.0
# 실행: streamlit run app.py
# 자체검사: python app.py --self-test
#
# 설계 원칙
# 1) 환자 자료 → 안전 게이트 → 소견 후보 → 한의사 확정 → 6축/Q6 분석 순서
# 2) 선택한 방제의 고정 정보와 환자 입력에서 계산된 구조를 분리
# 3) 방제·경혈은 추천이 아니라 구조 비교·문헌 확인 자료
# 4) 기하학 수치는 진단, 치료효과, 용량, 시술 강도를 뜻하지 않음

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

APP_VERSION = "9.0"
AXIS_NAMES = ["보충축", "소통·전환축", "수렴·안정축", "배출·이수축", "승양·상승축", "완충·조화축"]
AXIS_INDEX = {name: i for i, name in enumerate(AXIS_NAMES)}
AXIS_DESCRIPTIONS = {
    "보충축": "기·혈·음·양의 결손과 허약 소견을 정리하는 축",
    "소통·전환축": "기체·울체·표리·승강 전환과 연결성을 정리하는 축",
    "수렴·안정축": "불면·심계·불안·자한 등 안정·수렴 소견을 정리하는 축",
    "배출·이수축": "담·습·수분·대변·열·정체의 배출 방향을 정리하는 축",
    "승양·상승축": "하함·처짐·양허·상향 기능 소견을 정리하는 축",
    "완충·조화축": "한열·영위·중초·긴장 등 상반 소견의 조화를 정리하는 축",
}

FORMULAS = {'육미지황환': {'분류': '보음·자음 처방',
           '전통 변증': '간신음허, 허열도한, 정혈 부족, 하초 허약',
           '처방 방향': '자음, 보신, 허열 완충, 수렴·안정',
           '구성 약재': ['숙지황', '산수유', '산약', '복령', '택사', '목단피'],
           '잘 맞는 환자상': '요슬산연, 도한, 오심번열, 구건, 만성 피로, 음허성 열감',
           '주의 환자상': '설사, 식체, 더부룩함, 소화력 저하, 몸이 무겁고 습담이 뚜렷한 경우',
           '감별 처방': '십전대보탕, 팔미지황환, 보중익기탕, 소요산',
           '핵심 혈위': ['KI3', 'BL23', 'BL18', 'SP6', 'CV4', 'CV6', 'KI6'],
           '처방 방향축': ['보충축', '수렴·안정축', '완충·조화축']},
 '팔진탕': {'분류': '기혈쌍보 처방',
         '전통 변증': '기혈양허, 만성피로, 안색창백, 어지럼, 식욕저하',
         '처방 방향': '보기, 보혈, 기혈쌍보, 균형 보강',
         '구성 약재': ['인삼', '백출', '복령', '감초', '숙지황', '당귀', '천궁', '작약'],
         '잘 맞는 환자상': '피로, 안색창백, 어지럼, 식욕저하, 회복력 저하',
         '주의 환자상': '습담·식체가 강하거나 복부팽만이 심한 경우',
         '감별 처방': '십전대보탕, 보중익기탕, 귀비탕',
         '핵심 혈위': ['ST36', 'SP6', 'BL20', 'BL17', 'CV6', 'CV12'],
         '처방 방향축': ['보충축', '완충·조화축']},
 '십전대보탕': {'분류': '대보원기·기혈쌍보 처방',
           '전통 변증': '기혈양허, 허로, 허한, 수술·질병 후 회복 저하',
           '처방 방향': '대보원기, 기혈쌍보, 온보',
           '구성 약재': ['인삼', '백출', '복령', '감초', '숙지황', '당귀', '천궁', '작약', '황기', '육계'],
           '잘 맞는 환자상': '허약, 피로, 추위 탐, 회복 지연, 안색 저하',
           '주의 환자상': '상열감, 실열, 염증, 고혈압 조절 불량, 복부팽만이 강한 경우',
           '감별 처방': '팔진탕, 보중익기탕, 귀비탕',
           '핵심 혈위': ['ST36', 'CV6', 'BL20', 'BL23', 'GV4', 'SP6'],
           '처방 방향축': ['보충축', '승양·상승축']},
 '보중익기탕': {'분류': '보기·승양 처방',
           '전통 변증': '비위기허, 중기하함, 기허발열, 만성피로',
           '처방 방향': '보기, 승양, 중기 보강, 비위 회복',
           '구성 약재': ['황기', '인삼', '백출', '감초', '당귀', '진피', '승마', '시호'],
           '잘 맞는 환자상': '피로, 무력, 식욕저하, 처짐, 기단, 자한',
           '주의 환자상': '상열감, 불면, 심계, 실열, 혈압 조절 불량, 흉민이 뚜렷한 경우',
           '감별 처방': '팔진탕, 십전대보탕, 귀비탕',
           '핵심 혈위': ['ST36', 'CV6', 'GV20', 'BL20', 'SP3', 'CV12'],
           '처방 방향축': ['보충축', '승양·상승축', '소통·전환축']},
 '산조인탕': {'분류': '양혈안신 처방',
          '전통 변증': '허번불면, 혈허, 음허 내열, 심간 불안',
          '처방 방향': '수렴, 안신, 내부 안정, 허열 완충',
          '구성 약재': ['산조인', '복령', '지모', '천궁', '감초'],
          '잘 맞는 환자상': '잠을 깊이 못 잠, 심계, 불안, 건망, 피로, 허번',
          '주의 환자상': '과도한 졸림, 진정제·수면제 병용, 운전·기계 조작 예정',
          '감별 처방': '귀비탕, 천왕보심단, 가미소요산',
          '핵심 혈위': ['HT7', 'PC6', 'SP6', 'KI6', 'BL15', 'Anmian'],
          '처방 방향축': ['수렴·안정축', '완충·조화축']},
 '귀비탕': {'분류': '심비양허·기혈보강 처방',
         '전통 변증': '심비양허, 불면, 건망, 심계, 식욕저하, 피로',
         '처방 방향': '보기, 보혈, 안신, 심비 보강',
         '구성 약재': ['인삼', '황기', '백출', '복령', '용안육', '산조인', '목향', '감초', '당귀', '원지'],
         '잘 맞는 환자상': '불면, 건망, 심계, 피로, 식욕저하, 안색창백',
         '주의 환자상': '습담·식체가 강하거나 상열감이 뚜렷한 경우',
         '감별 처방': '산조인탕, 보중익기탕, 팔진탕',
         '핵심 혈위': ['HT7', 'SP6', 'ST36', 'BL20', 'BL15', 'PC6'],
         '처방 방향축': ['보충축', '수렴·안정축']},
 '사물탕': {'분류': '보혈조혈 처방',
         '전통 변증': '혈허, 어지럼, 안색창백, 월경량 감소, 건조',
         '처방 방향': '보혈, 조혈, 혈분 완충',
         '구성 약재': ['숙지황', '당귀', '천궁', '작약'],
         '잘 맞는 환자상': '혈허, 어지럼, 안색창백, 건조, 월경 관련 허증',
         '주의 환자상': '습담·식체, 설사, 복부팽만이 강한 경우',
         '감별 처방': '팔진탕, 귀비탕, 온경탕',
         '핵심 혈위': ['SP6', 'BL17', 'BL20', 'ST36', 'LR3'],
         '처방 방향축': ['보충축', '완충·조화축']},
 '소요산': {'분류': '소간해울·건비조혈 처방',
         '전통 변증': '간울, 혈허, 비허, 스트레스성 소화불량, 흉협불편',
         '처방 방향': '소간, 해울, 건비, 조화',
         '구성 약재': ['시호', '당귀', '작약', '백출', '복령', '감초', '생강', '박하'],
         '잘 맞는 환자상': '스트레스성 흉협불편, 답답함, 식욕저하, 월경 전후 불편',
         '주의 환자상': '심한 허한, 설사, 체력 저하가 뚜렷한 경우',
         '감별 처방': '가미소요산, 이진탕, 평위산',
         '핵심 혈위': ['LR3', 'PC6', 'SP6', 'ST36', 'GB34'],
         '처방 방향축': ['소통·전환축', '완충·조화축']},
 '이진탕': {'분류': '화담이기 처방',
         '전통 변증': '담음정체, 오심구토, 어지럼, 흉민, 습담',
         '처방 방향': '조습, 화담, 이기, 위기 하강',
         '구성 약재': ['반하', '진피', '복령', '감초', '생강', '오매'],
         '잘 맞는 환자상': '가래, 오심, 더부룩함, 어지럼, 흉민, 습담',
         '주의 환자상': '음허건조, 진액 부족, 강한 구건이 동반된 경우',
         '감별 처방': '평위산, 소요산, 반하백출천마탕',
         '핵심 혈위': ['ST40', 'PC6', 'CV12', 'ST36', 'SP9'],
         '처방 방향축': ['배출·이수축', '소통·전환축']},
 '평위산': {'분류': '조습화위 처방',
         '전통 변증': '비위습탁, 식체, 복부팽만, 더부룩함',
         '처방 방향': '조습, 행기, 소도, 비위 소통',
         '구성 약재': ['창출', '후박', '진피', '감초', '생강', '대조'],
         '잘 맞는 환자상': '복부팽만, 더부룩함, 식체, 습담, 식욕저하',
         '주의 환자상': '음허건조, 진액 부족, 강한 구건·건조감',
         '감별 처방': '이진탕, 보중익기탕, 소요산',
         '핵심 혈위': ['CV12', 'ST36', 'SP9', 'ST25', 'PC6'],
         '처방 방향축': ['소통·전환축', '배출·이수축']},
 '오령산': {'분류': '이수삼습 처방',
         '전통 변증': '수습정체, 소변불리, 부종, 갈증·구토, 수분대사 장애',
         '처방 방향': '이수, 삼습, 수분대사 조절, 기화 보조',
         '구성 약재': ['택사', '저령', '복령', '백출', '계지'],
         '잘 맞는 환자상': '소변불리, 부종, 몸이 무거움, 갈증, 구토, 수분 정체',
         '주의 환자상': '탈수, 전해질 이상, 신장 기능 저하, 이뇨제 병용',
         '감별 처방': '이진탕, 평위산, 진무탕',
         '핵심 혈위': ['SP9', 'CV9', 'BL22', 'KI7', 'ST36'],
         '처방 방향축': ['배출·이수축', '소통·전환축']},
 '반하사심탕': {'분류': '신개고강·한열조화 처방',
           '전통 변증': '심하비, 한열착잡, 비위불화, 위기상역, 구역',
           '처방 방향': '중초 조화, 신개고강, 한열 조절, 위기상역 완화, 비위 승강 회복',
           '구성 약재': ['반하', '황금', '황련', '건강', '인삼', '감초', '대조'],
           '잘 맞는 환자상': '명치 아래가 그득하지만 아프지 않음, 구역, 더부룩함, 복명, 설사 또는 묽은 변, 상부 열감과 중초 허한이 섞인 경우',
           '주의 환자상': '심하부가 단단하고 아픈 결흉 양상, 격심한 복통, 고열 지속, 탈수, 혈변, 급성 복증 의심',
           '감별 처방': '소시호탕, 소함흉탕, 대함흉탕, 이진탕, 평위산',
           '핵심 혈위': ['CV12', 'PC6', 'ST36', 'SP4', 'ST25', 'CV13'],
           '처방 방향축': ['소통·전환축', '완충·조화축']},
 '소시호탕': {'분류': '화해소양 처방',
          '전통 변증': '소양병, 왕래한열, 흉협고만, 구고, 인건, 목현, 심번희구',
          '처방 방향': '화해소양, 간담 소통, 흉협 조화, 위기상역 완화',
          '구성 약재': ['시호', '황금', '반하', '인삼', '감초', '생강', '대조'],
          '잘 맞는 환자상': '왕래한열, 흉협부 답답함, 입이 쓰고 목이 마름, 구역, 식욕저하, 맥현',
          '주의 환자상': '심하부가 그득하지만 아프지 않은 심하비, 심하부가 단단하고 아픈 결흉, 실열 고열, 강한 설사',
          '감별 처방': '반하사심탕, 대시호탕, 소함흉탕, 가미소요산',
          '핵심 혈위': ['GB34', 'TE5', 'PC6', 'LR3', 'CV12', 'BL18'],
          '처방 방향축': ['소통·전환축', '완충·조화축']},
 '대시호탕': {'분류': '소양양명 합병·공하겸화 처방',
          '전통 변증': '흉협고만, 심하급, 변비, 구역, 실열·실증 경향',
          '처방 방향': '소양 화해, 양명 실체 해소, 흉협·심하부 긴장 완화',
          '구성 약재': ['시호', '황금', '반하', '작약', '지실', '대황', '생강', '대조'],
          '잘 맞는 환자상': '흉협과 명치가 답답하고 단단함, 변비, 구역, 체격·실증 경향, 복부 긴장',
          '주의 환자상': '허약자, 설사, 탈수, 임신 가능성, 고령자, 항응고제 복용',
          '감별 처방': '소시호탕, 반하사심탕, 대함흉탕, 평위산',
          '핵심 혈위': ['GB34', 'LR3', 'PC6', 'ST25', 'ST36', 'CV12'],
          '처방 방향축': ['소통·전환축', '배출·이수축']},
 '소함흉탕': {'분류': '청열화담·개결 처방',
          '전통 변증': '소결흉, 담열결흉, 심하비만, 흉민, 명치 답답함',
          '처방 방향': '청열화담, 흉격 개결, 심하부 막힘 완화',
          '구성 약재': ['황련', '반하', '과루실'],
          '잘 맞는 환자상': '가슴·명치가 답답하고 담열·흉민이 있으며 심하부가 막힌 듯한 경우',
          '주의 환자상': '격심한 흉통·복통, 심혈관 응급 의심, 고열 지속, 허한성 설사',
          '감별 처방': '반하사심탕, 대함흉탕, 이진탕, 황련해독탕',
          '핵심 혈위': ['CV17', 'CV12', 'PC6', 'ST40', 'ST36'],
          '처방 방향축': ['소통·전환축', '완충·조화축']},
 '대함흉탕': {'분류': '준하축수·결흉 처방',
          '전통 변증': '결흉, 심하부 단단함과 통증, 수열결흉, 실증 급성 복증',
          '처방 방향': '결흉 해소, 수열 제거, 강한 사하·축수 방향',
          '구성 약재': ['대황', '망초', '감수'],
          '잘 맞는 환자상': '명치 아래가 단단하고 아프며 복부 긴장과 실증 양상이 분명한 경우',
          '주의 환자상': '허약자, 고령자, 임신 가능성, 탈수, 설사, 신장 기능 저하, 복통 원인 불명',
          '감별 처방': '반하사심탕, 소함흉탕, 대시호탕',
          '핵심 혈위': ['CV12', 'CV17', 'PC6', 'ST25', 'ST36'],
          '처방 방향축': ['배출·이수축', '소통·전환축']},
 '황련해독탕': {'분류': '청열해독 처방',
           '전통 변증': '삼초실열, 번조, 상열, 염증성 열감, 출혈 경향',
           '처방 방향': '청열, 해독, 실열 완화, 화열 진정',
           '구성 약재': ['황련', '황금', '황백', '치자'],
           '잘 맞는 환자상': '얼굴 붉음, 심번, 불면, 갈증, 열감, 염증성 소견, 실열 경향',
           '주의 환자상': '허한, 설사, 위장 허약, 냉감, 저혈압·허약자',
           '감별 처방': '백호탕, 소시호탕, 가미소요산, 천왕보심단',
           '핵심 혈위': ['LI11', 'LI4', 'ST44', 'GV14', 'PC6'],
           '처방 방향축': ['배출·이수축', '완충·조화축']},
 '백호가인삼탕': {'분류': '청기분열·익기생진 처방',
            '전통 변증': '양명기분열, 대열, 대한, 대갈, 맥홍대, 진액 손상',
            '처방 방향': '청열, 생진, 기분열 완화, 갈증 조절',
            '구성 약재': ['석고', '지모', '인삼', '감초', '갱미'],
            '잘 맞는 환자상': '고열성 열감, 갈증, 땀, 입마름, 피로, 진액 소모',
            '주의 환자상': '허한, 설사, 냉감, 위장 허약, 탈수와 전해질 문제',
            '감별 처방': '황련해독탕, 죽엽석고탕, 소시호탕',
            '핵심 혈위': ['LI11', 'ST44', 'ST36', 'SP6', 'CV12'],
            '처방 방향축': ['완충·조화축', '보충축']},
 '계지탕': {'분류': '해기조영위 처방',
         '전통 변증': '태양중풍, 표허, 자한, 오풍, 영위불화',
         '처방 방향': '해표, 조화영위, 표허 완충',
         '구성 약재': ['계지', '작약', '생강', '대조', '감초'],
         '잘 맞는 환자상': '땀이 나며 바람을 싫어함, 몸살, 가벼운 외감, 허약한 표증',
         '주의 환자상': '무한·실증·고열, 인후통 심함, 염증성 열감, 자한이 아닌 경우',
         '감별 처방': '마황탕, 갈근탕, 소시호탕',
         '핵심 혈위': ['LU7', 'LI4', 'BL13', 'ST36', 'CV17'],
         '처방 방향축': ['소통·전환축', '완충·조화축']},
 '마황탕': {'분류': '발한해표·선폐평천 처방',
         '전통 변증': '태양상한, 무한, 오한, 신통, 맥부긴, 해수·천식',
         '처방 방향': '발한, 해표, 선폐, 한사 발산',
         '구성 약재': ['마황', '계지', '행인', '감초'],
         '잘 맞는 환자상': '오한, 몸살, 땀 없음, 표실, 기침·천명, 맥긴',
         '주의 환자상': '고혈압, 심계, 불면, 허약자, 자한, 임신 가능성, 심혈관 위험',
         '감별 처방': '계지탕, 갈근탕, 소청룡탕',
         '핵심 혈위': ['LU7', 'LI4', 'BL13', 'GV14', 'LU9'],
         '처방 방향축': ['소통·전환축', '승양·상승축']},
 '갈근탕': {'분류': '해표해기·서근 처방',
         '전통 변증': '태양병, 항배강, 무한 또는 표증, 경항부 긴장',
         '처방 방향': '해표, 경항부 긴장 완화, 근육 이완, 표증 조절',
         '구성 약재': ['갈근', '마황', '계지', '작약', '생강', '대조', '감초'],
         '잘 맞는 환자상': '목·어깨가 뻣뻣함, 몸살, 오한, 두통, 표증',
         '주의 환자상': '고혈압·심계·불면, 강한 열감, 허약자, 자한',
         '감별 처방': '계지탕, 마황탕, 소시호탕',
         '핵심 혈위': ['GB20', 'BL10', 'LI4', 'LU7', 'ST36'],
         '처방 방향축': ['소통·전환축', '승양·상승축']},
 '팔미지황환': {'분류': '온보신양·보신 처방',
           '전통 변증': '신양허, 하초 냉감, 요슬냉통, 소변빈삭, 부종 경향',
           '처방 방향': '보신, 온양, 하초 냉감 완충, 기화 보조',
           '구성 약재': ['숙지황', '산수유', '산약', '복령', '택사', '목단피', '계지', '부자'],
           '잘 맞는 환자상': '허리·무릎 냉통, 하복부 냉감, 야뇨, 소변빈삭, 추위 탐, 기력 저하',
           '주의 환자상': '오심번열, 도한, 구건, 상열감, 고혈압 조절 불량, 염증성 열감',
           '감별 처방': '육미지황환, 진무탕, 십전대보탕',
           '핵심 혈위': ['KI3', 'BL23', 'GV4', 'CV4', 'CV6', 'KI7'],
           '처방 방향축': ['보충축', '승양·상승축']},
 '온경탕': {'분류': '온경산한·양혈조경 처방',
         '전통 변증': '충임허한, 혈허·어혈, 월경불순, 하복부 냉감, 손발 번열 혼재',
         '처방 방향': '온경, 양혈, 산한, 어혈 완충, 충임 조절',
         '구성 약재': ['오수유', '당귀', '천궁', '작약', '인삼', '계지', '아교', '목단피', '생강', '감초', '반하', '맥문동'],
         '잘 맞는 환자상': '하복부 냉감, 월경불순, 피로, 혈허, 건조, 손발 번열 혼재',
         '주의 환자상': '실열, 염증성 출혈, 임신 가능성, 과다출혈, 복통 심함',
         '감별 처방': '사물탕, 팔미지황환, 가미소요산',
         '핵심 혈위': ['SP6', 'CV4', 'CV6', 'ST36', 'BL17', 'LR3'],
         '처방 방향축': ['보충축', '완충·조화축']},
 '천왕보심단': {'분류': '자음양혈·안신 처방',
           '전통 변증': '심신불교, 음허혈소, 심계, 불면, 건망, 구건',
           '처방 방향': '자음, 양혈, 안신, 심신 교통, 허열 완충',
           '구성 약재': ['생지황', '인삼', '현삼', '단삼', '복령', '원지', '길경', '오미자', '당귀', '천문동', '맥문동', '백자인', '산조인'],
           '잘 맞는 환자상': '불면, 심계, 건망, 입마름, 허열, 불안, 집중 저하',
           '주의 환자상': '소화력 저하, 설사, 습담, 과도한 졸림, 진정제 병용',
           '감별 처방': '산조인탕, 귀비탕, 황련해독탕',
           '핵심 혈위': ['HT7', 'PC6', 'KI6', 'SP6', 'BL15', 'CV14'],
           '처방 방향축': ['수렴·안정축', '보충축', '완충·조화축']},
 '가미소요산': {'분류': '소간해울·청열조혈 처방',
           '전통 변증': '간울혈허, 울열, 월경 전 불편, 상열감, 짜증',
           '처방 방향': '소간, 해울, 청열, 건비, 혈분 조화',
           '구성 약재': ['시호', '당귀', '작약', '백출', '복령', '감초', '생강', '박하', '목단피', '치자'],
           '잘 맞는 환자상': '스트레스성 흉협불편, 짜증, 상열감, 월경 전 유방창통, 식욕저하',
           '주의 환자상': '허한·설사·냉감이 강한 경우, 위장 허약',
           '감별 처방': '소요산, 황련해독탕, 천왕보심단',
           '핵심 혈위': ['LR3', 'PC6', 'SP6', 'GB34', 'LI11', 'ST36'],
           '처방 방향축': ['소통·전환축', '완충·조화축']},
 '반하백출천마탕': {'분류': '화담식풍·건비 처방',
             '전통 변증': '풍담상요, 어지럼, 두중, 담음, 비위허약',
             '처방 방향': '화담, 식풍, 건비, 어지럼 완충',
             '구성 약재': ['반하', '백출', '천마', '진피', '복령', '감초', '생강', '대조'],
             '잘 맞는 환자상': '머리 무거움, 어지럼, 가래, 더부룩함, 메스꺼움, 비위허약',
             '주의 환자상': '음허건조, 강한 구건, 고혈압성 두통·신경학적 증상 의심',
             '감별 처방': '이진탕, 오령산, 갈근탕',
             '핵심 혈위': ['ST40', 'GB20', 'PC6', 'CV12', 'ST36', 'SP9'],
             '처방 방향축': ['배출·이수축', '소통·전환축']},
 '진무탕': {'분류': '온양이수 처방',
         '전통 변증': '양허수범, 부종, 어지럼, 복통, 설사, 소변불리',
         '처방 방향': '온양, 이수, 수습 조절, 하초·비신 보조',
         '구성 약재': ['부자', '복령', '작약', '백출', '생강'],
         '잘 맞는 환자상': '냉감, 무력, 설사, 부종, 소변불리, 어지럼, 하초 허한',
         '주의 환자상': '실열, 구건, 고혈압 조절 불량, 신장 기능 저하, 임신 가능성, 부자 사용 안전성',
         '감별 처방': '오령산, 팔미지황환, 십전대보탕',
         '핵심 혈위': ['KI7', 'CV4', 'CV6', 'SP9', 'BL23', 'ST36'],
         '처방 방향축': ['보충축', '배출·이수축']},
 '소건중탕': {'분류': '온중보허·완급지통 처방',
          '전통 변증': '중초허한, 복통, 허로, 피로, 식욕저하',
          '처방 방향': '온중, 보허, 완급, 비위 안정',
          '구성 약재': ['계지', '작약', '생강', '대조', '감초', '교이'],
          '잘 맞는 환자상': '복부가 허하고 은근히 아픔, 피로, 식욕저하, 냉감, 허약',
          '주의 환자상': '실열, 복부팽만·식체, 당뇨 조절 불량, 급성 복통',
          '감별 처방': '대건중탕, 보중익기탕, 평위산',
          '핵심 혈위': ['CV12', 'ST36', 'SP6', 'CV6', 'BL20'],
          '처방 방향축': ['보충축', '완충·조화축']},
 '대건중탕': {'분류': '온중산한·강역지통 처방',
          '전통 변증': '중초한성 복통, 복부 냉감, 장관운동 저하, 허한성 통증',
          '처방 방향': '온중, 산한, 강역, 복부 긴장 완화',
          '구성 약재': ['촉초', '건강', '인삼', '교이'],
          '잘 맞는 환자상': '배가 차고 통증, 복부 팽만, 허한성 장운동 저하, 냉감',
          '주의 환자상': '실열성 복통, 급성 복증, 장폐색 의심, 출혈, 고열',
          '감별 처방': '소건중탕, 진무탕, 평위산',
          '핵심 혈위': ['CV12', 'ST36', 'CV6', 'ST25', 'SP6'],
          '처방 방향축': ['보충축', '소통·전환축']},
 '향사평위산': {'분류': '행기화습·조중 처방',
           '전통 변증': '비위습탁, 기체, 식체, 복부팽만, 트림',
           '처방 방향': '행기, 화습, 조중, 비위 소통',
           '구성 약재': ['창출', '후박', '진피', '감초', '향부자', '사인', '생강', '대조'],
           '잘 맞는 환자상': '식후 더부룩함, 트림, 복부팽만, 기체, 습탁, 식욕저하',
           '주의 환자상': '음허건조, 강한 구건, 열감, 설사·탈수',
           '감별 처방': '평위산, 이진탕, 반하사심탕',
           '핵심 혈위': ['CV12', 'ST36', 'PC6', 'ST25', 'SP9'],
           '처방 방향축': ['소통·전환축', '배출·이수축']},
 '곽향정기산': {'분류': '화습해표·이기화중 처방',
           '전통 변증': '외감풍한과 내상습체, 오심구토, 설사, 복부불편',
           '처방 방향': '화습, 해표, 이기, 중초 조화',
           '구성 약재': ['곽향', '자소엽', '백지', '대복피', '복령', '백출', '진피', '반하', '후박', '길경', '감초', '생강', '대조'],
           '잘 맞는 환자상': '더부룩함, 오심, 설사, 몸무거움, 외감과 식체가 함께 있는 경우',
           '주의 환자상': '고열, 탈수, 혈변, 심한 복통, 임신 가능성, 감염성 설사 의심',
           '감별 처방': '평위산, 이진탕, 반하사심탕',
           '핵심 혈위': ['CV12', 'ST36', 'PC6', 'LI4', 'ST25'],
           '처방 방향축': ['소통·전환축', '배출·이수축']}}
MERIDIANS = {'LU': (11, '수태음폐경', '상지·흉부', '보충축, 소통·전환축', '폐기·호흡·표증 방향 참고', '흉부 깊은 자침 주의'),
 'LI': (20, '수양명대장경', '상지·면부', '소통·전환축', '표열·면구·장부 소통 방향 참고', '임신 중 강자극 주의'),
 'ST': (45, '족양명위경', '두면·흉복·하지', '보충축, 소통·전환축', '비위·소화·기혈 생성 방향 참고', '복부·흉부 자침 깊이 확인'),
 'SP': (21, '족태음비경', '하지·복부', '보충축, 수렴·안정축', '비·간·신 조절, 혈·음·수습 조절 방향 참고', '임신 가능성 확인'),
 'HT': (9, '수소음심경', '상지', '수렴·안정축', '심계·불면·안신 방향 참고', '과도한 자극 주의'),
 'SI': (19, '수태양소장경', '상지·견갑·두면', '소통·전환축', '경항·견갑·표증 방향 참고', '경부 자침 주의'),
 'BL': (67, '족태양방광경', '두항·배부·하지', '보충축, 소통·전환축', '배수혈·요배부·장부 반응점 방향 참고', '흉배부 깊은 자침 주의'),
 'KI': (27, '족소음신경', '하지·흉복', '보충축, 수렴·안정축', '신·음혈·하초·수면 방향 참고', '임신·허약자 자극 강도 확인'),
 'PC': (9, '수궐음심포경', '상지·흉부', '수렴·안정축, 소통·전환축', '심흉·오심·정서 긴장 방향 참고', '강자극 주의'),
 'TE': (23, '수소양삼초경', '상지·두면', '소통·전환축', '소양·수도·상중하초 소통 방향 참고', '두경부 자극 확인'),
 'GB': (44, '족소양담경', '두면·체측·하지', '소통·전환축', '간담·측부·긴장·통증 방향 참고', '임신 중 일부 혈위 주의'),
 'LR': (14, '족궐음간경', '하지·복부', '소통·전환축, 완충·조화축', '간울·혈분·정서 긴장 방향 참고', '강자극 주의'),
 'CV': (24, '임맥', '전중선·복부', '보충축, 수렴·안정축', '하초·중초·원기·음혈 방향 참고', '임신·복부 수술력 확인'),
 'GV': (28, '독맥', '후중선·두항', '승양·상승축', '양기·두항·승양 방향 참고', '두경부·척추부 자극 확인')}
ACU_OVERRIDES = {'KI3': {'혈명': '태계', 'standard_name': 'Taixi', '안전 메모': '허열·음허·임신 관련 상태 확인'},
 'BL23': {'혈명': '신수', 'standard_name': 'Shenshu', '안전 메모': '요부 심부 자침 위험, 신장 부위 해부학적 안전 확인'},
 'BL18': {'혈명': '간수', 'standard_name': 'Ganshu', '안전 메모': '흉배부 깊은 자침 주의'},
 'SP6': {'혈명': '삼음교', 'standard_name': 'Sanyinjiao', '안전 메모': '임신 가능성·임신 중 사용은 전문가 판단'},
 'CV4': {'혈명': '관원', 'standard_name': 'Guanyuan', '안전 메모': '복부 수술력, 임신, 심혈관 상태 확인'},
 'CV6': {'혈명': '기해', 'standard_name': 'Qihai', '안전 메모': '복부 열감, 임신, 염증 상태 확인'},
 'KI6': {'혈명': '조해', 'standard_name': 'Zhaohai', '안전 메모': '허열·음허 상태 확인. 강한 뜸은 신중'},
 'ST36': {'혈명': '족삼리', 'standard_name': 'Zusanli', '안전 메모': '과도한 강자극 주의'},
 'CV12': {'혈명': '중완', 'standard_name': 'Zhongwan', '안전 메모': '복부 수술력, 임신, 급성 복통 확인'},
 'GV20': {'혈명': '백회', 'standard_name': 'Baihui', '안전 메모': '혈압, 두통, 상열감 확인'},
 'HT7': {'혈명': '신문', 'standard_name': 'Shenmen', '안전 메모': '과도한 진정 반응 주의'},
 'PC6': {'혈명': '내관', 'standard_name': 'Neiguan', '안전 메모': '항응고제·출혈 경향 확인'},
 'LR3': {'혈명': '태충', 'standard_name': 'Taichong', '안전 메모': '강자극 주의'},
 'ST40': {'혈명': '풍륭', 'standard_name': 'Fenglong', '안전 메모': '국소 혈관·신경 주의'},
 'SP9': {'혈명': '음릉천', 'standard_name': 'Yinlingquan', '안전 메모': '부종·피부상태 확인'},
 'CV9': {'혈명': '수분', 'standard_name': 'Shuifen', '안전 메모': '복부 수술력·임신·급성 복통 확인'},
 'BL20': {'혈명': '비수', 'standard_name': 'Pishu', '안전 메모': '흉배부 깊은 자침 주의'},
 'BL17': {'혈명': '격수', 'standard_name': 'Geshu', '안전 메모': '흉배부 깊은 자침 주의'},
 'BL15': {'혈명': '심수', 'standard_name': 'Xinshu', '안전 메모': '흉배부 깊은 자침 주의'},
 'Anmian': {'혈명': '안면', 'standard_name': 'Anmian', '안전 메모': '경부 해부학적 안전 확인'},
 'SP3': {'혈명': '태백', 'standard_name': 'Taibai', '안전 메모': '국소 자극 확인'},
 'GB34': {'혈명': '양릉천', 'standard_name': 'Yanglingquan', '안전 메모': '국소 자극 확인'},
 'ST25': {'혈명': '천추', 'standard_name': 'Tianshu', '안전 메모': '복부 수술력·임신 확인'},
 'BL22': {'혈명': '삼초수', 'standard_name': 'Sanjiaoshu', '안전 메모': '흉요부 자침 주의'},
 'KI7': {'혈명': '복류', 'standard_name': 'Fuliu', '안전 메모': '허열·음허 확인'},
 'GV4': {'혈명': '명문', 'standard_name': 'Mingmen', '안전 메모': '강한 온보 자극 신중'},
 'SP4': {'혈명': '공손', 'standard_name': 'Gongsun', '안전 메모': '임신 가능성, 복부 급성 통증 확인'},
 'CV13': {'혈명': '상완', 'standard_name': 'Shangwan', '안전 메모': '복부 수술력·임신·급성 복통 확인'},
 'CV14': {'혈명': '거궐', 'standard_name': 'Juque', '안전 메모': '흉복부 깊은 자침 주의, 심혈관 증상 확인'},
 'CV17': {'혈명': '전중', 'standard_name': 'Shanzhong', '안전 메모': '흉부 깊은 자침 금지, 심혈관 응급 감별'},
 'LI11': {'혈명': '곡지', 'standard_name': 'Quchi', '안전 메모': '허약자 강자극 주의'},
 'LI4': {'혈명': '합곡', 'standard_name': 'Hegu', '안전 메모': '임신 가능성, 강자극 주의'},
 'ST44': {'혈명': '내정', 'standard_name': 'Neiting', '안전 메모': '허한·설사 경향 확인'},
 'LU7': {'혈명': '열결', 'standard_name': 'Lieque', '안전 메모': '국소 자극·임신 가능성 확인'},
 'BL13': {'혈명': '폐수', 'standard_name': 'Feishu', '안전 메모': '흉배부 깊은 자침 주의'},
 'LU9': {'혈명': '태연', 'standard_name': 'Taiyuan', '안전 메모': '국소 혈관·신경 확인'},
 'GB20': {'혈명': '풍지', 'standard_name': 'Fengchi', '안전 메모': '경부 해부학적 안전, 깊은 자침 주의'},
 'BL10': {'혈명': '천주', 'standard_name': 'Tianzhu', '안전 메모': '경부 깊은 자침 주의'},
 'GV14': {'혈명': '대추', 'standard_name': 'Dazhui', '안전 메모': '고열·허약자 강자극 주의'},
 'TE5': {'혈명': '외관', 'standard_name': 'Waiguan', '안전 메모': '강자극 주의'}}

# -----------------------------------------------------------------------------
# 임상 소견 태그 사전: 자동진단 규칙이 아니라 한의사가 확인·수정하는 구조화 초안
# axes 값은 0~3의 앱 내부 가중치다.
# -----------------------------------------------------------------------------
TAG_RULES: Dict[str, Dict[str, Any]] = {
    "기허": {"group":"기혈음양", "patterns":["기허", "피로", "무력", "기운이 없", "쉽게 지침", "기단", "자한"], "axes":{"보충축":3, "승양·상승축":1}, "questions":["식욕과 식후 피로는 어떤가?", "자한·기단·말소리 약화가 있는가?"]},
    "혈허": {"group":"기혈음양", "patterns":["혈허", "안색창백", "창백", "어지럼", "건조", "월경량 감소"], "axes":{"보충축":3, "수렴·안정축":1}, "questions":["안색·손발톱·피부 건조는 어떤가?", "월경량·어지럼·심계가 동반되는가?"]},
    "음허·허열": {"group":"기혈음양", "patterns":["음허", "허열", "도한", "오심번열", "구건", "입마름", "오후 열감"], "axes":{"보충축":2, "수렴·안정축":2, "완충·조화축":1}, "questions":["도한·오심번열·구건이 함께 있는가?", "설질 홍·태소와 관련되는가?"]},
    "양허·허한": {"group":"기혈음양", "patterns":["양허", "허한", "냉감", "추위", "손발이 차", "하복부 냉", "요슬냉통"], "axes":{"보충축":2, "승양·상승축":3}, "questions":["사지·하복부 냉감과 온열 선호가 있는가?", "야뇨·부종·설사가 동반되는가?"]},
    "간울·기체": {"group":"기기승강", "patterns":["간울", "기체", "스트레스", "답답", "울체", "한숨", "트림"], "axes":{"소통·전환축":3, "완충·조화축":1}, "questions":["정서 변화와 증상 변동이 연결되는가?", "흉협·복부 팽만이나 트림이 있는가?"]},
    "흉협고만·소양": {"group":"기기승강", "patterns":["흉협고만", "흉협", "왕래한열", "구고", "목현", "소양"], "axes":{"소통·전환축":3, "완충·조화축":2}, "questions":["왕래한열·구고·목현·구역이 함께 있는가?", "흉협부 저항·압통이 있는가?"]},
    "비위불화·심하비": {"group":"중초", "patterns":["심하비", "명치가 그득", "명치 그득", "더부룩", "복명", "비위불화"], "axes":{"소통·전환축":2, "완충·조화축":3}, "questions":["심하부는 그득하되 통증이 없는가?", "복명·구역·묽은 변과 한열 혼재가 있는가?"]},
    "위기상역·오심": {"group":"중초", "patterns":["오심", "구역", "구토", "메스꺼", "위기상역", "딸꾹질"], "axes":{"소통·전환축":2, "완충·조화축":2}, "questions":["식후·공복·냄새·동작과의 관련은?", "담음·열·허한 중 어느 소견이 동반되는가?"]},
    "식체·습체": {"group":"중초", "patterns":["식체", "식후 팽만", "복부팽만", "체기", "소화불량", "몸이 무거"], "axes":{"소통·전환축":2, "배출·이수축":2}, "questions":["식후 악화·트림·후중감이 있는가?", "설태 후니·맥활 소견이 있는가?"]},
    "담음·습담": {"group":"담습수", "patterns":["담음", "습담", "가래", "흉민", "머리 무거", "두중"], "axes":{"배출·이수축":3, "소통·전환축":1}, "questions":["가래의 양·색·점도와 흉민이 있는가?", "어지럼·오심·설태니가 동반되는가?"]},
    "수습·부종": {"group":"담습수", "patterns":["수습", "부종", "소변불리", "소변이 적", "몸이 붓", "수분 정체"], "axes":{"배출·이수축":3, "보충축":1}, "questions":["부종의 부위·시간대·압흔은?", "소변량·갈증·체중 변화는?"]},
    "설사·묽은변": {"group":"대소변", "patterns":["설사", "묽은 변", "무른 변", "복명설사"], "axes":{"완충·조화축":2, "보충축":1, "배출·이수축":1}, "questions":["횟수·양·냄새·복통·탈수 소견은?", "찬 음식·식후·새벽과의 관련은?"]},
    "변비·실체": {"group":"대소변", "patterns":["변비", "대변이 굳", "실체", "복부 긴장"], "axes":{"배출·이수축":3, "소통·전환축":1}, "questions":["배변 간격·변 형태·복부 긴장은?", "갈증·열감·허약 여부를 함께 확인했는가?"]},
    "실열·상열": {"group":"한열", "patterns":["실열", "상열", "고열", "얼굴 붉", "심번", "갈증", "염증성 열감"], "axes":{"배출·이수축":2, "완충·조화축":1}, "questions":["체온·갈증·대변·소변·설맥 소견은?", "허열과 실열을 구분할 근거가 충분한가?"]},
    "한열착잡": {"group":"한열", "patterns":["한열착잡", "상열하한", "한열 혼재", "열감과 냉감", "왕래한열"], "axes":{"완충·조화축":3, "소통·전환축":1}, "questions":["한·열 소견의 부위와 시간대가 다른가?", "중초 허한과 상부 열이 함께 있는가?"]},
    "불면·심계·불안": {"group":"신지", "patterns":["불면", "잠들기 어렵", "심계", "두근", "불안", "건망", "허번"], "axes":{"수렴·안정축":3, "완충·조화축":1}, "questions":["입면·중도각성·조기각성 중 무엇인가?", "심계·도한·구건·식욕 저하가 동반되는가?"]},
    "어지럼·두중": {"group":"두면", "patterns":["어지럼", "현훈", "두중", "머리 무거"], "axes":{"보충축":1, "배출·이수축":1, "소통·전환축":1}, "questions":["회전성·부유감·기립성 중 어떤 양상인가?", "담음·혈허·혈압·신경학적 소견을 확인했는가?"]},
    "표허·영위불화": {"group":"표리", "patterns":["자한", "오풍", "표허", "영위불화", "바람을 싫어"], "axes":{"완충·조화축":3, "보충축":1}, "questions":["땀이 나면서 오풍이 있는가?", "발열·오한·맥부완 등 표증 근거가 있는가?"]},
    "표실·한사": {"group":"표리", "patterns":["무한", "오한", "신통", "맥부긴", "표실", "몸살"], "axes":{"소통·전환축":2, "승양·상승축":1}, "questions":["땀의 유무와 오한·발열의 우세는?", "심계·혈압·허약 여부를 확인했는가?"]},
    "경항강·근긴장": {"group":"근골격", "patterns":["항배강", "경항강", "목이 뻣뻣", "어깨가 뻣뻣", "근육 긴장"], "axes":{"소통·전환축":2}, "questions":["외감·자세·외상과의 관련은?", "신경학적 결손·심한 두통이 없는가?"]},
    "하초허약·요슬": {"group":"하초", "patterns":["하초 허약", "요슬산연", "허리 무릎", "야뇨", "소변빈삭"], "axes":{"보충축":3, "수렴·안정축":1}, "questions":["냉감·도한·구건 중 어느 쪽이 우세한가?", "소변·부종·요통의 양상을 확인했는가?"]},
}

SAFETY_EMERGENCY_OPTIONS = [
    "숨이 매우 차서 문장으로 말하기 어렵다",
    "심하거나 지속되는 흉통·가슴 압박이 있다",
    "입술·얼굴이 파래지거나 회색빛이다",
    "실신·새로운 의식 혼미·반응 저하가 있다",
    "갑작스러운 한쪽 마비·언어장애·심한 신경학적 이상이 있다",
    "멈추지 않는 심한 출혈이 있다",
]
SAFETY_URGENT_OPTIONS = [
    "새로 발생했거나 악화되는 호흡곤란이 있다",
    "발열과 호흡곤란이 함께 있다",
    "지속되는 고열 또는 전신상태 악화가 있다",
    "심한 복통·복부 경직·반발통이 있다",
    "혈변·토혈·검은변 또는 심한 탈수 징후가 있다",
    "얼굴·혀·목 부종, 쌕쌕거림 등 심한 알레르기 반응이 의심된다",
]

@dataclass
class SafetyFinding:
    label: str
    suggested_level: str
    sentence: str
    reason: str


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    value = str(value).strip()
    return "" if value.lower() in {"none", "nan", "null", "미기록"} else value


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", clean_text(text))
    return [s.strip() for s in re.split(r"(?<=[.!?。])\s+|[\n;]+", text) if s.strip()]


def term_negated(sentence: str, term: str) -> bool:
    # 교육·연구 문맥은 환자 현재 소견으로 취급하지 않는다.
    if any(x in sentence for x in ["교육자료", "연구 메모", "테스트용", "템플릿", "설명하는 문장"]):
        return True
    if any(x in sentence for x in ["아버지", "어머니", "가족력"]):
        return True
    if "과거" in sentence and any(x in sentence for x in ["현재", "오늘"]) and any(x in sentence for x in ["없", "아니", "평소와 같다"]):
        return True
    if any(x in sentence for x in ["달리기 직후", "운동 직후"]) and any(x in sentence for x in ["완전히 회복", "곧 회복", "1분 쉬면"]):
        return True
    # 단순히 문장 안에 '없다'가 있다는 이유로 다른 증상까지 부정하지 않는다.
    # 해당 용어 자체가 부정되는 형태만 찾는다.
    escaped = re.escape(term)
    patterns = [
        rf"{escaped}(?:은|는|이|가|도|을|를)?\s*(?:없음|없다|없고|없으며|아니다|아니고)",
        rf"{escaped}[^.?!]{{0,8}}(?:하지 않|지 않|않다|않음)",
        rf"(?:현재|오늘)?[^.?!]{{0,8}}{escaped}[^.?!]{{0,8}}(?:없음|없다|없고|아니다|부인)",
        rf"{escaped}[^.?!]{{0,8}}부인",
    ]
    return any(re.search(p, sentence) for p in patterns)


def active_term(sentence: str, terms: Sequence[str]) -> bool:
    return any(term in sentence and not term_negated(sentence, term) for term in terms)


def detect_safety_findings(text: str) -> List[SafetyFinding]:
    out: List[SafetyFinding] = []
    for sentence in split_sentences(text):
        chest = active_term(sentence, ["흉통", "가슴 통증", "가슴 압박", "가슴이 조이", "짓눌리", "가슴 중앙"])
        chest_high = chest and active_term(sentence, ["식은땀", "왼팔", "오른팔", "턱", "등으로", "방사", "지속", "재발", "메스꺼움", "30분", "20분"])
        if chest_high:
            out.append(SafetyFinding("흉통 고위험 표현", "emergency", sentence, "압박성 흉부 증상과 방사·식은땀·지속/재발 표현의 조합"))
        elif chest:
            out.append(SafetyFinding("흉통 표현", "urgent", sentence, "현재 흉부 통증·압박 표현"))

        neuro = active_term(sentence, ["말이 어눌", "언어장애", "말을 이해하지 못", "얼굴이 처지", "한쪽 마비", "팔 힘이 빠", "다리가 마비"])
        if neuro:
            out.append(SafetyFinding("급성 신경학적 이상 표현", "emergency", sentence, "갑작스러운 편측 약화·언어 이상 표현"))

        severe_dyspnea = active_term(sentence, ["한 문장을 끝까지 말하지 못", "말을 하지 못", "숨이 매우 차", "호흡이 멎", "입술이 파랗", "얼굴이 파래", "질식"])
        dyspnea = active_term(sentence, ["호흡곤란", "숨가쁨", "숨참", "숨이 차", "숨쉬기 어렵", "숨쉬기가 힘들", "호흡이 가쁘", "숨이 막"])
        if severe_dyspnea:
            out.append(SafetyFinding("중증 호흡 이상 표현", "emergency", sentence, "말하기 곤란·청색증·질식 또는 매우 심한 호흡곤란 표현"))
        elif dyspnea:
            level = "urgent" if active_term(sentence, ["새로", "악화", "빠르게", "누우면", "발열", "39도", "40도"]) else "review"
            out.append(SafetyFinding("호흡곤란 표현", level, sentence, "현재 호흡 불편 표현"))

        if active_term(sentence, ["기절", "실신", "반응이 없", "의식저하", "의식이 흐려", "의식 혼미"]):
            out.append(SafetyFinding("의식 변화 표현", "emergency", sentence, "현재 실신·반응 저하·의식 변화 표현"))

        if active_term(sentence, ["대량 출혈", "지혈이 되지", "피를 많이 토", "검붉은 피를 많이", "토혈"]):
            level = "emergency" if active_term(sentence, ["많이", "실신", "식은땀", "계속", "지혈이 되지"]) else "urgent"
            out.append(SafetyFinding("중증 출혈 표현", level, sentence, "토혈·지속 출혈 또는 대량 출혈 표현"))
        elif active_term(sentence, ["혈변", "검은변", "새까만 변", "선홍색 혈액"]):
            out.append(SafetyFinding("위장관 출혈 표현", "urgent", sentence, "혈변·흑변 표현"))

        severe_abd = active_term(sentence, ["심한 복통", "격심한 복통", "반발통", "복부 경직", "배가 단단", "돌처럼 굳"])
        if severe_abd:
            out.append(SafetyFinding("급성 복증 표현", "urgent", sentence, "심한 복통·경직·반발통 표현"))

        allergy = active_term(sentence, ["혀와 목이 붓", "혀가 붓", "목이 붓", "얼굴이 붓", "쌕쌕"])
        if allergy:
            level = "emergency" if dyspnea or severe_dyspnea else "urgent"
            out.append(SafetyFinding("중증 알레르기 표현", level, sentence, "부종·쌕쌕거림 표현"))

        if active_term(sentence, ["경험하지 못한 극심한 두통", "갑작스러운 극심한 두통"]):
            out.append(SafetyFinding("돌발 극심한 두통 표현", "emergency", sentence, "갑작스럽고 매우 심한 두통 표현"))

        high_fever = active_term(sentence, ["39도", "39.4도", "40도", "고열", "열이 사흘째", "열이 지속"])
        if high_fever and not term_negated(sentence, "고열"):
            out.append(SafetyFinding("고열·전신악화 표현", "urgent", sentence, "고열·지속 발열 또는 전신악화 표현"))

        dehydration = active_term(sentence, ["심한 탈수", "소변이 거의 없", "소변이 나오지", "기력이 크게 떨어"])
        if dehydration:
            out.append(SafetyFinding("탈수·전신악화 표현", "urgent", sentence, "탈수 또는 전신상태 악화 표현"))

        pe_combo = dyspnea and active_term(sentence, ["종아리 통증", "맥박이 빠", "갑자기"])
        if pe_combo:
            out.append(SafetyFinding("급성 호흡·혈전 위험 조합", "emergency", sentence, "갑작스러운 호흡곤란과 하지 통증/빈맥의 조합"))

    # 중복 제거
    unique: Dict[Tuple[str, str], SafetyFinding] = {}
    for f in out:
        unique[(f.label, f.sentence)] = f
    return list(unique.values())


def triage_state(emergency: Sequence[str], urgent: Sequence[str], findings: Sequence[SafetyFinding], reviewed: bool) -> Dict[str, Any]:
    if emergency:
        return {"level":"emergency", "blocked":True, "title":"즉시 응급 대응 항목이 선택되었습니다.", "message":"한의학·기하학 비교를 중단하고 응급 의료체계 평가를 우선하십시오."}
    if urgent:
        return {"level":"urgent", "blocked":True, "title":"신속한 대면 의료평가 항목이 선택되었습니다.", "message":"한의학 구조 비교보다 신속한 대면 평가를 우선하십시오."}
    if findings and not reviewed:
        highest = "emergency" if any(f.suggested_level=="emergency" for f in findings) else "urgent" if any(f.suggested_level=="urgent" for f in findings) else "review"
        return {"level":"review", "suggested":highest, "blocked":True, "title":"안전 관련 표현의 문맥 확인이 필요합니다.", "message":"자동 감지는 확정 판정이 아닙니다. 구조화된 응급·긴급 항목을 직접 확인하고 문맥 검토를 완료하십시오."}
    return {"level":"clear", "blocked":False, "title":"구조화된 응급·긴급 항목이 선택되지 않았습니다.", "message":"진료 불필요 판정이 아닙니다. 임상 판단과 안전 확인은 한의사가 수행합니다."}


def record_text_fields(record: Mapping[str, Any]) -> Dict[str, str]:
    return {
        "주호소": clean_text(record.get("chief")),
        "발병·경과": " ".join(filter(None,[clean_text(record.get("onset")),clean_text(record.get("duration")),clean_text(record.get("course"))])),
        "부위·성상": " ".join(filter(None,[clean_text(record.get("location")),clean_text(record.get("quality"))])),
        "악화·완화": " ".join(filter(None,[clean_text(record.get("aggravating")),clean_text(record.get("relieving"))])),
        "동반소견": clean_text(record.get("associated")),
        "한열": clean_text(record.get("cold_heat")),
        "땀·갈증": " ".join(filter(None,[clean_text(record.get("sweat")),clean_text(record.get("thirst"))])),
        "식욕·소화": " ".join(filter(None,[clean_text(record.get("appetite")),clean_text(record.get("digestion"))])),
        "대변·소변": " ".join(filter(None,[clean_text(record.get("stool")),clean_text(record.get("urine"))])),
        "수면·정서": " ".join(filter(None,[clean_text(record.get("sleep")),clean_text(record.get("emotion"))])),
        "맥설복": " ".join(filter(None,[clean_text(record.get("pulse_tag")),clean_text(record.get("tongue")),clean_text(record.get("abdomen"))])),
        "병력·투약": " ".join(filter(None,[clean_text(record.get("history")),clean_text(record.get("allergy")),clean_text(record.get("meds"))])),
    }


def detect_clinical_tags(record: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows=[]
    for tag, rule in TAG_RULES.items():
        for field, text in record_text_fields(record).items():
            for term in rule["patterns"]:
                if term in text and not term_negated(text, term):
                    rows.append({"태그":tag, "분류":rule["group"], "근거 필드":field, "일치 표현":term, "원문":text[:180]})
                    break
            else:
                continue
            break
    return rows


def calculate_axis_scores(positive_tags: Sequence[str], adjustments: Mapping[str, float] | None = None) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    adjustments = adjustments or {}
    scores={axis:0.0 for axis in AXIS_NAMES}
    evidence=[]
    for tag in positive_tags:
        rule=TAG_RULES.get(tag)
        if not rule:
            continue
        for axis, value in rule["axes"].items():
            scores[axis]+=float(value)
            evidence.append({"확정 소견":tag, "축":axis, "기여":value, "근거":"소견 태그 사전"})
    for axis in AXIS_NAMES:
        adj=float(adjustments.get(axis,0.0))
        if adj:
            scores[axis]+=adj
            evidence.append({"확정 소견":"한의사 수동 보정", "축":axis, "기여":adj, "근거":"사용자 입력"})
        scores[axis]=max(0.0,min(10.0,scores[axis]))
    return scores,evidence


def axis_state(scores: Mapping[str,float], threshold: float=3.0) -> int:
    return sum((1<<AXIS_INDEX[a]) for a in AXIS_NAMES if float(scores.get(a,0))>=threshold)


def state_bits(state:int) -> str:
    return "".join(str((state>>i)&1) for i in range(6))


def q6_neighbors(state:int) -> List[Dict[str,Any]]:
    return [{"변경 축":axis,"이웃 상태":state^(1<<i),"이웃 6비트":state_bits(state^(1<<i))} for i,axis in enumerate(AXIS_NAMES)]


def hamming_distance(a:int,b:int) -> int:
    return int((a^b).bit_count())


def formula_axis_set(name:str) -> List[str]:
    return [a for a in FORMULAS[name].get("처방 방향축",[]) if a in AXIS_INDEX]


def extract_tags_from_text(text:str) -> List[str]:
    found=[]
    for tag,rule in TAG_RULES.items():
        if any(term in text for term in rule["patterns"]):
            found.append(tag)
    return found


def formula_profile(name:str, threshold:float=3.0) -> Dict[str,Any]:
    data=FORMULAS[name]
    axes=formula_axis_set(name)
    state=sum(1<<AXIS_INDEX[a] for a in axes)
    positive_text=" ".join([clean_text(data.get("전통 변증")),clean_text(data.get("처방 방향")),clean_text(data.get("잘 맞는 환자상"))])
    caution_text=clean_text(data.get("주의 환자상"))
    return {"name":name,"axes":axes,"state":state,"positive_tags":extract_tags_from_text(positive_text),"caution_tags":extract_tags_from_text(caution_text)}


def compare_formulas(positive_tags:Sequence[str], negative_tags:Sequence[str], scores:Mapping[str,float], threshold:float=3.0) -> pd.DataFrame:
    pset=set(positive_tags); nset=set(negative_tags); pstate=axis_state(scores,threshold); paxes={a for a in AXIS_NAMES if scores.get(a,0)>=threshold}
    rows=[]
    for name in FORMULAS:
        fp=formula_profile(name,threshold); faxes=set(fp["axes"]); fpos=set(fp["positive_tags"]); fcaution=set(fp["caution_tags"])
        rows.append({
            "방제":name,
            "문헌 분류":FORMULAS[name].get("분류",""),
            "축 거리(0=동일)":hamming_distance(pstate,fp["state"]),
            "일치 축":", ".join(sorted(paxes&faxes,key=AXIS_NAMES.index)) or "없음",
            "환자축 중 미포함":", ".join(sorted(paxes-faxes,key=AXIS_NAMES.index)) or "없음",
            "추가 방제축":", ".join(sorted(faxes-paxes,key=AXIS_NAMES.index)) or "없음",
            "일치 소견":", ".join(sorted(pset&fpos)) or "없음",
            "주의 충돌":", ".join(sorted(pset&fcaution)) or "없음",
            "명시적 부정과 충돌":", ".join(sorted(nset&fpos)) or "없음",
            "일치 소견 수":len(pset&fpos),
            "주의 충돌 수":len(pset&fcaution)+len(nset&fpos),
        })
    df=pd.DataFrame(rows)
    return df.sort_values(["주의 충돌 수","축 거리(0=동일)","일치 소견 수","방제"],ascending=[True,True,False,True]).reset_index(drop=True)


def build_acupoint_index() -> pd.DataFrame:
    rows=[]
    for prefix,meta in MERIDIANS.items():
        count,meridian,region,axis_text,meaning,warning=meta
        for n in range(1,count+1):
            code=f"{prefix}{n}"
            ov=ACU_OVERRIDES.get(code)
            rows.append({"code":code,"혈명":ov.get("혈명","") if ov else "","standard_name":ov.get("standard_name","") if ov else "","경락":meridian,"부위군":region,"기하 축":axis_text,"안전 메모":ov.get("안전 메모",warning) if ov else warning})
    return pd.DataFrame(rows)


def formula_point_rows(name:str, acu_df:pd.DataFrame) -> pd.DataFrame:
    codes=FORMULAS[name].get("핵심 혈위",[])
    rows=[]
    for code in codes:
        hit=acu_df[acu_df["code"]==code]
        if hit.empty:
            rows.append({"code":code,"혈명":"별도/경외혈","standard_name":"","경락":"","부위군":"","기하 축":"","안전 메모":"원자료와 표준 자료 대조 필요"})
        else:
            rows.append(hit.iloc[0].to_dict())
    return pd.DataFrame(rows)


def completeness(record:Mapping[str,Any]) -> Tuple[int,int,float]:
    keys=["age_group","sex","chief","onset","course","location","quality","associated","bp_sys","bp_dia","pulse_rate","temperature","cold_heat","sweat","thirst","appetite","digestion","stool","urine","sleep","pulse_tag","tongue","abdomen","history","allergy","meds"]
    filled=0
    for k in keys:
        v=record.get(k)
        if isinstance(v,(int,float)): ok=v not in (0,0.0)
        else: ok=bool(clean_text(v))
        filled+=int(ok)
    return filled,len(keys),100*filled/len(keys)


def next_questions(scores:Mapping[str,float], positive_tags:Sequence[str], threshold:float) -> List[Dict[str,str]]:
    rows=[]; seen=set()
    for axis in sorted(AXIS_NAMES,key=lambda a:scores.get(a,0)):
        if scores.get(axis,0)>=threshold+2: continue
        candidates=[(tag,rule) for tag,rule in TAG_RULES.items() if axis in rule["axes"] and tag not in positive_tags]
        for tag,rule in candidates[:2]:
            for q in rule["questions"][:1]:
                if q not in seen:
                    rows.append({"확인 축":axis,"감별 후보":tag,"다음 문진·관찰 질문":q}); seen.add(q)
        if len(rows)>=8: break
    return rows


def case_summary(record:Mapping[str,Any]) -> str:
    parts=[clean_text(record.get("chief")),clean_text(record.get("onset")),clean_text(record.get("duration")),clean_text(record.get("course")),clean_text(record.get("associated"))]
    return " / ".join(p for p in parts if p) or "주호소와 경과가 아직 입력되지 않았습니다."


def axis_radar(scores:Mapping[str,float], formula_name:str|None=None) -> go.Figure:
    theta=AXIS_NAMES+[AXIS_NAMES[0]]; patient=[scores.get(a,0) for a in AXIS_NAMES]; patient.append(patient[0])
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=patient,theta=theta,fill="toself",name="환자 확정 소견 구조"))
    if formula_name:
        faxes=set(formula_axis_set(formula_name)); vals=[8 if a in faxes else 0 for a in AXIS_NAMES]; vals.append(vals[0])
        fig.add_trace(go.Scatterpolar(r=vals,theta=theta,fill="toself",name=f"{formula_name} 자료 구조"))
    fig.update_layout(height=520,polar={"radialaxis":{"visible":True,"range":[0,10]}},margin={"l":30,"r":30,"t":45,"b":25},legend={"orientation":"h"})
    return fig


def axis_bar(scores:Mapping[str,float]) -> go.Figure:
    fig=go.Figure(go.Bar(x=AXIS_NAMES,y=[scores.get(a,0) for a in AXIS_NAMES],text=[f"{scores.get(a,0):.1f}" for a in AXIS_NAMES],textposition="outside"))
    fig.update_layout(height=390,yaxis={"range":[0,10],"title":"구조 점수"},xaxis_title="6축",margin={"l":30,"r":20,"t":20,"b":90})
    return fig


def chart_note(record:Mapping[str,Any],triage:Mapping[str,Any],positive:Sequence[str],negative:Sequence[str],scores:Mapping[str,float],threshold:float,selected_formula:str|None) -> str:
    state=axis_state(scores,threshold)
    lines=[
        "[비식별 한의 임상 구조화 기록]",
        f"사례코드: {clean_text(record.get('case_id')) or '미입력'}",
        f"기록일: {clean_text(record.get('encounter_date')) or '미입력'}",
        f"안전 게이트: {triage.get('level')}",
        f"주호소·경과: {case_summary(record)}",
        f"확정 소견: {', '.join(positive) or '없음'}",
        f"명시적 부정/배제: {', '.join(negative) or '없음'}",
        "6축 구조: "+"; ".join(f"{a}={scores.get(a,0):.1f}" for a in AXIS_NAMES),
        f"Q6 상태: {state} / 6비트(축순서)={state_bits(state)} / 임계값={threshold}",
    ]
    if selected_formula:
        lines.append(f"비교 방제 자료: {selected_formula} (구조 비교이며 처방 결정이 아님)")
    lines.append("주의: 이 기록은 한의사의 소견 구조화와 문헌 비교를 돕는 자료이며 자동 진단·처방·용량·침구 시술 지시가 아닙니다.")
    return "\n".join(lines)


def run_self_tests() -> Dict[str,Any]:
    acu=build_acupoint_index()
    tests=[]
    def check(name,cond,detail=""):
        tests.append({"test":name,"passed":bool(cond),"detail":detail})
    check("formula_count",len(FORMULAS)==31,str(len(FORMULAS)))
    check("acupoint_count",len(acu)==361,str(len(acu)))
    degrees=[len(q6_neighbors(n)) for n in range(64)]
    check("q6_degree",all(d==6 for d in degrees),str(set(degrees)))
    edges=sum(degrees)//2
    check("q6_edges",edges==192,str(edges))
    sample_scores={a:0 for a in AXIS_NAMES}; sample_scores["소통·전환축"]=4; sample_scores["완충·조화축"]=5
    check("state_roundtrip",axis_state(sample_scores,3)==34,str(axis_state(sample_scores,3)))
    safety_cases=[
        ("가슴이 짓눌리는 듯 아프고 식은땀과 메스꺼움이 있다.",True),
        ("갑자기 오른팔 힘이 빠지고 말이 어눌해졌다.",True),
        ("숨이 매우 차서 한 문장을 끝까지 말하지 못하고 입술이 파랗다.",True),
        ("호흡곤란 없음. 흉통도 없고 평소와 같다.",False),
        ("과거에 흉통이 있었으나 현재는 없음.",False),
        ("교육자료에서 호흡곤란이라는 표현을 읽었을 뿐 환자 증상은 아니다.",False),
    ]
    for i,(txt,expected) in enumerate(safety_cases,1):
        got=bool(detect_safety_findings(txt)); check(f"safety_{i}",got==expected,f"got={got}, expected={expected}")
    return {"version":APP_VERSION,"passed":all(t["passed"] for t in tests),"tests":tests}


if "--self-test" in sys.argv:
    print(json.dumps(run_self_tests(),ensure_ascii=False,indent=2))
    raise SystemExit(0)

# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------
import streamlit as st

st.set_page_config(page_title="한의사 임상 구조화 × 6축 기하 분석",page_icon="🧭",layout="wide")
st.markdown("""
<style>
.block-container{max-width:1480px;padding-top:1rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em}
[data-testid="stMetricValue"]{font-size:1.55rem}
.clinical-card{border:1px solid rgba(120,120,120,.28);border-radius:12px;padding:1rem 1.1rem;background:rgba(128,128,128,.045);margin:.4rem 0}
.small-note{font-size:.9rem;color:#6b7280}
</style>
""",unsafe_allow_html=True)


def show_df(df_or_rows:Any,height:int|None=None):
    df=df_or_rows.copy() if isinstance(df_or_rows,pd.DataFrame) else pd.DataFrame(df_or_rows)
    if df.empty:
        st.caption("표시할 항목이 없습니다."); return
    kwargs={"use_container_width":True,"hide_index":True}
    if height: kwargs["height"]=height
    st.dataframe(df,**kwargs)


def render_triage(t:Mapping[str,Any]):
    msg=f"**{t['title']}**\n\n{t['message']}"
    if t["level"]=="emergency": st.error(msg)
    elif t["level"] in {"urgent","review"}: st.warning(msg)
    else: st.info(msg)


def patient_record_from_state() -> Dict[str,Any]:
    g=st.session_state.get
    return {
        "case_id":g("pt_case_id","CASE-001"),"encounter_date":str(g("pt_date",date.today())),"age_group":g("pt_age","미기록"),"sex":g("pt_sex","미기록"),
        "chief":g("pt_chief",""),"onset":g("pt_onset",""),"duration":g("pt_duration",""),"course":g("pt_course","미기록"),"severity":g("pt_severity",0),
        "location":g("pt_location",""),"quality":g("pt_quality",""),"aggravating":g("pt_aggravating",""),"relieving":g("pt_relieving",""),"associated":g("pt_associated",""),
        "bp_sys":g("pt_bp_sys",0),"bp_dia":g("pt_bp_dia",0),"pulse_rate":g("pt_pulse_rate",0),"resp_rate":g("pt_resp_rate",0),"temperature":g("pt_temp",0.0),"spo2":g("pt_spo2",0),
        "cold_heat":g("pt_cold_heat","미기록"),"sweat":g("pt_sweat",""),"thirst":g("pt_thirst",""),"appetite":g("pt_appetite",""),"digestion":g("pt_digestion",""),
        "stool":g("pt_stool",""),"urine":g("pt_urine",""),"sleep":g("pt_sleep",""),"emotion":g("pt_emotion",""),"pulse_tag":g("pt_pulse_tag",""),"tongue":g("pt_tongue",""),"abdomen":g("pt_abdomen",""),
        "history":g("pt_history",""),"allergy":g("pt_allergy",""),"meds":g("pt_meds",""),"pregnancy":g("pt_pregnancy","해당 없음/미기록"),
        "emergency":g("pt_emergency",[]),"urgent":g("pt_urgent",[]),"keyword_reviewed":g("pt_keyword_reviewed",False),"note":g("pt_note","")
    }

with st.sidebar:
    st.header("환자·진료 기록")
    st.caption("성명·주민번호·전화번호·주소 대신 비식별 사례코드를 사용하십시오.")
    with st.expander("1. 기본·주호소",expanded=True):
        st.text_input("사례 코드",value="CASE-001",key="pt_case_id")
        st.date_input("기록일",value=date.today(),key="pt_date")
        c1,c2=st.columns(2)
        c1.selectbox("연령대",["미기록","소아","청소년","20대","30대","40대","50대","60대","70대","80대 이상"],key="pt_age")
        c2.selectbox("성별",["미기록","여성","남성","기타"],key="pt_sex")
        st.text_area("주호소",height=90,key="pt_chief")
        st.text_input("발병 시점",key="pt_onset")
        st.text_input("기간·빈도",key="pt_duration")
        st.selectbox("경과",["미기록","호전","악화","변동","유지","재발"],key="pt_course")
        st.slider("불편 정도 0~10",0,10,0,key="pt_severity")
        st.text_input("부위·분포",key="pt_location")
        st.text_input("성상·양상",key="pt_quality")
        st.text_area("악화 요인",height=60,key="pt_aggravating")
        st.text_area("완화 요인",height=60,key="pt_relieving")
        st.text_area("동반 소견",height=85,key="pt_associated")
    with st.expander("2. 활력징후",expanded=False):
        c1,c2=st.columns(2); c1.number_input("수축기",0,300,0,key="pt_bp_sys"); c2.number_input("이완기",0,200,0,key="pt_bp_dia")
        c1,c2=st.columns(2); c1.number_input("맥박",0,250,0,key="pt_pulse_rate"); c2.number_input("호흡수",0,100,0,key="pt_resp_rate")
        c1,c2=st.columns(2); c1.number_input("체온 ℃",0.0,45.0,0.0,.1,key="pt_temp"); c2.number_input("SpO₂ %",0,100,0,key="pt_spo2")
    with st.expander("3. 한의학 관찰",expanded=True):
        st.selectbox("한열",["미기록","한","열","한열왕래","상열하한","한열착잡","뚜렷하지 않음"],key="pt_cold_heat")
        st.text_input("땀",key="pt_sweat"); st.text_input("갈증·음수",key="pt_thirst")
        st.text_input("식욕",key="pt_appetite"); st.text_input("소화·오심·팽만",key="pt_digestion")
        st.text_input("대변",key="pt_stool"); st.text_input("소변",key="pt_urine")
        st.text_input("수면",key="pt_sleep"); st.text_input("정서·스트레스",key="pt_emotion")
        st.text_input("맥상",key="pt_pulse_tag"); st.text_area("설질·설태",height=60,key="pt_tongue"); st.text_area("복진",height=60,key="pt_abdomen")
    with st.expander("4. 병력·투약",expanded=False):
        st.text_area("과거력·현재 진단",height=70,key="pt_history")
        st.text_area("알레르기·이상반응",height=60,key="pt_allergy")
        st.text_area("복용약·한약·보충제",height=75,key="pt_meds")
        st.selectbox("임신·수유",["해당 없음/미기록","임신 가능성","임신 중","수유 중"],key="pt_pregnancy")
    with st.expander("5. 안전 게이트",expanded=True):
        st.multiselect("즉시 응급 확인",SAFETY_EMERGENCY_OPTIONS,key="pt_emergency")
        st.multiselect("신속 진료 확인",SAFETY_URGENT_OPTIONS,key="pt_urgent")
        st.checkbox("자동 감지 표현의 문맥 검토 완료",key="pt_keyword_reviewed")
    with st.expander("6. 기록 메모",expanded=False):
        st.text_area("결측·불확실성·추가 확인",height=90,key="pt_note")

record=patient_record_from_state()
combined_text="\n".join(record_text_fields(record).values())
safety_findings=detect_safety_findings(combined_text)
triage=triage_state(record["emergency"],record["urgent"],safety_findings,record["keyword_reviewed"])
detected_rows=detect_clinical_tags(record)
detected_tags=sorted({r["태그"] for r in detected_rows})
filled,total,complete=completeness(record)

with st.sidebar:
    st.divider()
    st.metric("핵심 기록 완성도",f"{complete:.0f}%",f"{filled}/{total}")
    st.caption(f"안전 게이트: {triage['level']}")
    st.caption(f"v{APP_VERSION} · 환자 입력과 방제 고정자료를 분리")

st.title("🧭 한의사 임상 구조화 × 6축 기하 분석")
st.caption("한의사가 확인한 소견을 6축·Q6 상태로 정리하고 방제 문헌 구조와 비교하는 보조도구")
st.info("자동 추출은 초안입니다. 최종 소견·축 보정·방제 비교의 해석은 한의사가 확인합니다. 기하학 거리는 처방 적합성이나 치료효과를 뜻하지 않습니다.")
render_triage(triage)

if safety_findings:
    with st.expander("자동 감지된 안전 표현",expanded=True):
        show_df([asdict(f) for f in safety_findings])

# confirmed states
st.session_state.setdefault("confirmed_tags",[])
st.session_state.setdefault("negative_tags",[])
st.session_state.setdefault("selected_formula_compare","선택 안 함")

positive=list(st.session_state.get("confirmed_tags",[])); negative=list(st.session_state.get("negative_tags",[]))
adjustments={axis:float(st.session_state.get(f"adj_{axis}",0.0)) for axis in AXIS_NAMES}
axis_scores,evidence_rows=calculate_axis_scores(positive,adjustments)
threshold=float(st.session_state.get("axis_threshold",3.0))
state=axis_state(axis_scores,threshold)

m1,m2,m3,m4,m5=st.columns(5)
m1.metric("기록 완성도",f"{complete:.0f}%")
m2.metric("확정 소견",len(positive))
m3.metric("활성 6축",sum(axis_scores[a]>=threshold for a in AXIS_NAMES))
m4.metric("Q6 상태",state)
m5.metric("6비트",state_bits(state))

tabs=st.tabs(["1. 진료 요약","2. 소견 확인","3. 6축 기하 분석","4. 방제 구조 비교","5. 경혈·경락 참고","6. 기록·내보내기","7. 수학·품질 감사"])

with tabs[0]:
    st.header("한눈에 보는 진료 구조")
    c1,c2=st.columns([1.25,1])
    with c1:
        st.subheader("사례 요약")
        st.markdown(f'<div class="clinical-card">{case_summary(record)}</div>',unsafe_allow_html=True)
        st.subheader("확정·배제 소견")
        show_df([
            {"구분":"확정 소견","내용":", ".join(positive) or "아직 확정하지 않음"},
            {"구분":"명시적 부정/배제","내용":", ".join(negative) or "미입력"},
            {"구분":"자동 추출 후보","내용":", ".join(detected_tags) or "없음"},
        ])
        st.subheader("다음 확인 질문")
        show_df(next_questions(axis_scores,positive,threshold),height=330)
    with c2:
        st.subheader("현재 6축 구조")
        st.plotly_chart(axis_bar(axis_scores),use_container_width=True)
        show_df([{"축":a,"점수":axis_scores[a],"활성":axis_scores[a]>=threshold,"의미":AXIS_DESCRIPTIONS[a]} for a in AXIS_NAMES])
    if triage["blocked"]:
        st.error("안전 게이트가 해제되기 전에는 방제 구조 비교를 표시하지 않습니다.")

with tabs[1]:
    st.header("자동 추출 후보를 한의사가 확인")
    st.warning("자동 추출 결과는 확정 소견이 아닙니다. 문맥·부정·과거력·검사 결과를 확인한 뒤 확정하십시오.")
    c1,c2=st.columns([1.2,1])
    with c1:
        st.subheader("감지 근거")
        show_df(detected_rows,height=430)
    with c2:
        if st.button("감지 후보를 확정 소견에 반영",use_container_width=True):
            st.session_state["confirmed_tags"]=sorted(set(st.session_state.get("confirmed_tags",[]))|set(detected_tags)); st.rerun()
        if st.button("확정·배제 소견 초기화",use_container_width=True):
            st.session_state["confirmed_tags"]=[]; st.session_state["negative_tags"]=[]; st.rerun()
        st.multiselect("확정 소견",list(TAG_RULES),key="confirmed_tags")
        remaining=[x for x in TAG_RULES if x not in st.session_state.get("confirmed_tags",[])]
        st.session_state["negative_tags"]=[x for x in st.session_state.get("negative_tags",[]) if x in remaining]
        st.multiselect("명시적 부정·배제 소견",remaining,key="negative_tags")
        st.caption("미입력은 음성이 아닙니다. 실제로 확인해 부정한 소견만 배제 목록에 넣으십시오.")
    st.subheader("소견 사전")
    show_df([{"태그":tag,"분류":r["group"],"연결 축":", ".join(f"{a}+{v}" for a,v in r["axes"].items()),"확인 질문":" / ".join(r["questions"])} for tag,r in TAG_RULES.items()],height=420)

with tabs[2]:
    st.header("한의사 확정 소견 → 6축 → Q6 상태")
    if triage["blocked"]:
        st.error("안전 게이트가 해제되지 않아 개인화 6축 분석을 중단했습니다.")
    else:
        st.slider("Q6 활성 임계값",1.0,8.0,3.0,.5,key="axis_threshold")
        st.subheader("축 수동 보정")
        cols=st.columns(3)
        for i,axis in enumerate(AXIS_NAMES):
            with cols[i%3]: st.slider(axis,-3.0,3.0,0.0,.5,key=f"adj_{axis}",help="자동 태그 기여를 한의사가 근거에 따라 보정")
        # recompute after widgets
        positive=list(st.session_state.get("confirmed_tags",[])); adjustments={a:float(st.session_state.get(f"adj_{a}",0)) for a in AXIS_NAMES}; threshold=float(st.session_state.get("axis_threshold",3.0))
        axis_scores,evidence_rows=calculate_axis_scores(positive,adjustments); state=axis_state(axis_scores,threshold)
        c1,c2=st.columns([1.15,1])
        with c1: st.plotly_chart(axis_radar(axis_scores),use_container_width=True)
        with c2:
            show_df([{"축":a,"점수":axis_scores[a],"비트":(state>>AXIS_INDEX[a])&1,"임계값":threshold,"설명":AXIS_DESCRIPTIONS[a]} for a in AXIS_NAMES])
            st.metric("Q6 정수 상태",state); st.code(state_bits(state))
        st.subheader("점수 근거")
        show_df(evidence_rows,height=350)
        st.subheader("한 비트만 바뀌는 Q6 이웃")
        show_df(q6_neighbors(state))

with tabs[3]:
    st.header("환자 확정 구조와 방제 문헌 구조 비교")
    st.caption("순서는 처방 우선순위가 아니라 주의 충돌·축 거리·소견 겹침을 정리한 비교 순서입니다.")
    if triage["blocked"]:
        st.error("안전 게이트가 해제되지 않아 방제 비교를 표시하지 않습니다.")
    elif not st.session_state.get("confirmed_tags"):
        st.warning("먼저 2번 탭에서 소견을 확정하십시오.")
    else:
        positive=list(st.session_state.get("confirmed_tags",[])); negative=list(st.session_state.get("negative_tags",[])); adjustments={a:float(st.session_state.get(f"adj_{a}",0)) for a in AXIS_NAMES}; threshold=float(st.session_state.get("axis_threshold",3.0)); axis_scores,_=calculate_axis_scores(positive,adjustments)
        comp=compare_formulas(positive,negative,axis_scores,threshold)
        show_df(comp.head(10),height=430)
        options=["선택 안 함"]+list(FORMULAS)
        selected=st.selectbox("상세 비교할 방제",options,key="selected_formula_compare")
        if selected!="선택 안 함":
            data=FORMULAS[selected]; fp=formula_profile(selected); row=comp[comp["방제"]==selected].iloc[0]
            c1,c2=st.columns([1.05,1])
            with c1:
                st.plotly_chart(axis_radar(axis_scores,selected),use_container_width=True)
            with c2:
                show_df([
                    {"항목":"문헌 분류","내용":data.get("분류","")},
                    {"항목":"전통 변증","내용":data.get("전통 변증","")},
                    {"항목":"처방 방향","내용":data.get("처방 방향","")},
                    {"항목":"구성 약재","내용":", ".join(data.get("구성 약재",[]))},
                    {"항목":"문헌상 관련 소견","내용":data.get("잘 맞는 환자상","")},
                    {"항목":"주의·감별 소견","내용":data.get("주의 환자상","")},
                    {"항목":"감별 자료","내용":data.get("감별 처방","")},
                ],height=420)
            st.subheader("이 사례와의 구조 비교")
            show_df([
                {"비교":"축 거리","결과":row["축 거리(0=동일)"],"해석":"0은 6개 활성/비활성 축이 같다는 뜻일 뿐 임상 적합성 확정이 아님"},
                {"비교":"일치 축","결과":row["일치 축"],"해석":"환자 확정축과 방제 자료축의 교집합"},
                {"비교":"환자축 중 미포함","결과":row["환자축 중 미포함"],"해석":"현재 사례에서 확인됐지만 방제 고정축에 없는 항목"},
                {"비교":"일치 소견","결과":row["일치 소견"],"해석":"같은 태그 사전으로 추출된 문헌상 겹침"},
                {"비교":"주의 충돌","결과":row["주의 충돌"],"해석":"현재 확정 소견이 원자료 주의 문구와 겹치는 항목"},
                {"비교":"명시적 부정과 충돌","결과":row["명시적 부정과 충돌"],"해석":"환자에게 없다고 확인한 소견을 방제 자료가 요구하는 경우"},
            ])

with tabs[4]:
    st.header("경혈·경락 문헌 연결 참고")
    st.warning("환자 소견에서 혈위를 자동 선정하지 않습니다. 선택한 방제 자료에 저장된 경혈 코드와 안전 메모만 표시합니다.")
    acu=build_acupoint_index()
    selected=st.selectbox("방제 자료",list(FORMULAS),index=list(FORMULAS).index("반하사심탕") if "반하사심탕" in FORMULAS else 0,key="acu_formula")
    st.subheader("선택 방제의 문헌 연결 혈위")
    show_df(formula_point_rows(selected,acu))
    st.subheader("361경혈 인덱스 검색")
    q=st.text_input("코드·혈명·경락 검색",key="acu_q")
    filtered=acu
    if q.strip():
        mask=acu.astype(str).apply(lambda c:c.str.contains(q.strip(),case=False,na=False)).any(axis=1); filtered=acu[mask]
    show_df(filtered,height=470)

with tabs[5]:
    st.header("진료 기록 초안과 데이터 내보내기")
    selected=st.session_state.get("selected_formula_compare","선택 안 함")
    selected=None if selected=="선택 안 함" else selected
    positive=list(st.session_state.get("confirmed_tags",[])); negative=list(st.session_state.get("negative_tags",[])); adjustments={a:float(st.session_state.get(f"adj_{a}",0)) for a in AXIS_NAMES}; threshold=float(st.session_state.get("axis_threshold",3.0)); axis_scores,evidence_rows=calculate_axis_scores(positive,adjustments)
    note=chart_note(record,triage,positive,negative,axis_scores,threshold,selected)
    st.text_area("구조화 기록 초안",note,height=300)
    payload={"app_version":APP_VERSION,"generated_at":datetime.now().isoformat(timespec="seconds"),"patient_record":record,"safety":{"state":triage,"findings":[asdict(f) for f in safety_findings]},"confirmed_positive_tags":positive,"confirmed_negative_tags":negative,"axis_scores":axis_scores,"axis_threshold":threshold,"q6_state":axis_state(axis_scores,threshold),"q6_bits":state_bits(axis_state(axis_scores,threshold)),"selected_formula_for_comparison":selected,"scope":"clinician_support_not_autonomous_decision"}
    c1,c2=st.columns(2)
    c1.download_button("JSON 다운로드",json.dumps(payload,ensure_ascii=False,indent=2).encode("utf-8"),file_name=f"{clean_text(record.get('case_id')) or 'case'}_tcm_geometry.json",mime="application/json",use_container_width=True)
    c2.download_button("기록 TXT 다운로드",note.encode("utf-8"),file_name=f"{clean_text(record.get('case_id')) or 'case'}_note.txt",mime="text/plain",use_container_width=True)
    axis_df=pd.DataFrame([{"axis":a,"score":axis_scores[a],"active":axis_scores[a]>=threshold} for a in AXIS_NAMES])
    st.download_button("6축 CSV 다운로드",axis_df.to_csv(index=False).encode("utf-8-sig"),file_name="axis_scores.csv",mime="text/csv")

with tabs[6]:
    st.header("수학·품질 감사")
    results=run_self_tests()
    show_df(results["tests"])
    if results["passed"]: st.success("내장 단위검사가 모두 통과했습니다.")
    else: st.error("일부 내장 단위검사가 실패했습니다.")
    st.subheader("Q6 정의")
    st.latex(r"Q_6=\{0,1\}^6,\qquad d_H(x,y)=1\;\Longleftrightarrow\;x,y\text{ are adjacent}")
    show_df([
        {"항목":"꼭짓점","값":64,"검증":"2^6"},
        {"항목":"각 꼭짓점 차수","값":6,"검증":"한 번에 한 축만 전환"},
        {"항목":"모서리","값":192,"검증":"64×6÷2"},
        {"항목":"방제 비교 거리","값":"Hamming 0~6","검증":"활성축의 대칭차 개수"},
    ])
    st.subheader("출력 경계")
    show_df([
        {"가능":"한의사가 확정한 소견의 구조화, 누락 질문, 6축 시각화, 방제 문헌 비교"},
        {"가능":"경혈·경락 인덱스 및 선택 방제의 문헌 연결 코드 확인"},
        {"금지":"자동 진단, 자동 처방 선택, 약재 가감·용량, 자침·뜸 강도 결정"},
        {"금지":"Q6 거리·벡터·중심성을 치료효과나 생리학적 인과로 해석"},
    ])

st.divider()
st.caption("한의사 판단 보조용 구조화·문헌 비교 도구입니다. 응급·긴급 상황에서는 표준 의료평가를 우선하고, 원자료의 방제·경혈 정보는 원전·공정서·제품설명서와 대조하십시오.")
