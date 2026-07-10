import streamlit as st
import pandas as pd
from datetime import datetime
from html import escape

# ============================================================
# 0. 기본 설정
# ============================================================
st.set_page_config(
    page_title="한의 임상 의사결정 지원 대시보드 + 361 경혈",
    page_icon="☯️",
    layout="wide",
)

st.title("☯️ 한의 임상 의사결정 지원 대시보드")
st.caption("전통 처방 · 황제내경 · 동의보감 · 침구 · 뜸 · 361 표준 경혈 DB · 안전성 · 소견서 통합")

st.warning(
    "**[주의] 본 앱은 자동 진단·자동 처방·자동 침구 시술 지시 도구가 아닙니다.**\n\n"
    "한의사가 입력한 종합소견을 바탕으로 처방 방향, 침구 방향, 뜸 주의, 안전성, 소견서 초안을 정리하는 보조 도구입니다. "
    "실제 처방, 용량, 혈위, 자침 깊이, 유침 시간, 보사법, 뜸 부위와 강도는 반드시 면허가 있는 한의사가 최종 결정해야 합니다."
)

# ============================================================
# 1. 전통 처방 DB
# ============================================================
FORMULAS = [
    {
        "처방명": "육미지황환",
        "전통 변증": "간신음허, 허열도한, 정혈 부족",
        "처방 방향": "자음, 보신, 수렴, 허열 완충, 수습 조절",
        "처방 방향축": ["보충축", "수렴·안정축", "완충·조화축"],
        "구성 약재": "숙지황, 산수유, 산약, 복령, 택사, 목단피",
        "잘 맞는 환자상": "요슬산연, 도한, 오심번열, 구건, 만성 피로, 음허성 열감",
        "주의 환자상": "설태 후니, 식체·습담, 설사 잦음, 실열·습열이 강한 경우",
        "감별 처방": "보중익기탕, 귀비탕, 오령산, 지백지황환",
        "가감": "소화불량이 강하면 숙지황 부담 확인, 수습이 강하면 이수·건비 방향 검토",
        "침구 방향": "간신·자음 보강, 허열 완충, 수렴 안정 방향. 강한 온보 자극은 주의.",
        "뜸 방향": "냉감·허한이 동반될 때 제한적으로 검토. 오심번열·도한·구건이 뚜렷하면 강한 뜸 주의.",
        "동의보감": "신(腎), 신형(身形), 허로(虛勞), 소아(小兒) 편제와 연결 가능",
        "황제내경": "음양, 장부·기혈진액, 신장, 승강출입, 표본중기",
    },
    {
        "처방명": "보중익기탕",
        "전통 변증": "비위기허, 중기하함, 기허 피로",
        "처방 방향": "보기, 승양, 중기 보강, 비위 회복",
        "처방 방향축": ["보충축", "승양·상승축", "완충·조화축"],
        "구성 약재": "황기, 인삼, 백출, 감초, 당귀, 진피, 승마, 시호",
        "잘 맞는 환자상": "피로, 식욕저하, 자한, 무력감, 처짐, 말하기 힘든 기허",
        "주의 환자상": "상열감, 고혈압, 심계, 불면, 실열, 습열, 식적이 뚜렷한 경우",
        "감별 처방": "사군자탕, 팔진탕, 십전대보탕, 소요산",
        "가감": "상열감이 있으면 승양 과잉 주의, 식체가 있으면 소도·화위 방향 먼저 검토",
        "침구 방향": "비위·중기 보강, 승양 방향. 고혈압·심계가 있으면 상승 자극 과잉 주의.",
        "뜸 방향": "비위허한, 복부 냉감, 기허 피로가 뚜렷하면 검토. 상열감·불면·혈압 상승 경향이면 주의.",
        "동의보감": "내상(內傷), 비위(脾胃), 기(氣), 허로(虛勞) 편제와 연결 가능",
        "황제내경": "비위, 기, 승강출입, 음양, 표본중기",
    },
    {
        "처방명": "산조인탕",
        "전통 변증": "허번불면, 심신불안, 음혈 부족",
        "처방 방향": "수렴, 안신, 내부 안정, 허열 완충",
        "처방 방향축": ["수렴·안정축", "완충·조화축", "보충축"],
        "구성 약재": "산조인, 지모, 복령, 천궁, 감초",
        "잘 맞는 환자상": "잠은 오나 깊이 못 자는 불면, 심계, 불안, 피로, 허번",
        "주의 환자상": "실열성 불면, 담열, 과도한 졸림, 진정제 병용으로 반응 저하가 있는 경우",
        "감별 처방": "귀비탕, 온담탕, 천왕보심단",
        "가감": "담음이 강하면 화담 방향 검토, 주간 졸림이 있으면 진정 과잉 주의",
        "침구 방향": "안신, 수렴, 심신 안정 방향. 강자극보다 완만한 조절 중심.",
        "뜸 방향": "허한성 불면·냉감이 동반될 때 제한적으로 검토. 번조·열감·구건이면 강한 뜸 주의.",
        "동의보감": "몽(夢), 건망(健忘), 심(心), 혈(血) 편제와 연결 가능",
        "황제내경": "심, 신지, 음양, 개합추, 기혈진액",
    },
    {
        "처방명": "팔진탕",
        "전통 변증": "기혈양허, 만성피로, 안색창백",
        "처방 방향": "보기, 보혈, 기혈쌍보, 균형 보강",
        "처방 방향축": ["보충축", "완충·조화축"],
        "구성 약재": "사군자탕 + 사물탕",
        "잘 맞는 환자상": "피로, 안색창백, 어지럼, 식욕저하, 회복력 저하",
        "주의 환자상": "식체, 습담, 실열, 상열감, 보약 복용 후 체하는 환자",
        "감별 처방": "십전대보탕, 귀비탕, 사물탕, 사군자탕",
        "가감": "소화력이 약하면 건비 방향 선행, 열감이 있으면 온보 처방과 감별",
        "침구 방향": "기혈 보강, 비위 보강, 전신 순환 조절 방향. 평보평사 중심.",
        "뜸 방향": "냉감과 허한이 있으면 검토. 열감·상열감이 있으면 주의.",
        "동의보감": "허로(虛勞), 기혈(氣血), 혈(血), 비위(脾胃) 편제와 연결 가능",
        "황제내경": "기혈진액, 비위, 음양, 표본중기",
    },
    {
        "처방명": "평위산",
        "전통 변증": "비위습탁, 식체, 복부팽만",
        "처방 방향": "조습, 행기, 소도, 비위 소통",
        "처방 방향축": ["배출·이수축", "소통·전환축", "완충·조화축"],
        "구성 약재": "창출, 후박, 진피, 감초, 생강, 대조",
        "잘 맞는 환자상": "복부팽만, 더부룩함, 트림, 식체, 백니태, 몸이 무거운 습체",
        "주의 환자상": "음허, 구건, 마른 체형, 무태, 진액 부족, 위음허성 속쓰림",
        "감별 처방": "이진탕, 반하사심탕, 향사평위산",
        "가감": "식체가 강하면 소도 방향, 담음이 강하면 화담 방향, 진액 부족이면 조습 과잉 주의",
        "침구 방향": "비위 소통, 중초 기기 조절, 습탁 배출 방향. 복부 반응과 대변 상태 확인.",
        "뜸 방향": "복부 냉감과 습체가 뚜렷하면 검토. 구건·음허·열감이 있으면 강한 온조 자극 주의.",
        "동의보감": "비위(脾胃), 내상(內傷), 담음(痰飮) 편제와 연결 가능",
        "황제내경": "비위, 기기, 습, 승강출입, 개합추",
    },
    {
        "처방명": "귀비탕",
        "전통 변증": "심비양허, 불면, 건망, 사려과다",
        "처방 방향": "보기, 보혈, 안신, 심비 보강",
        "처방 방향축": ["보충축", "수렴·안정축", "완충·조화축"],
        "구성 약재": "인삼, 황기, 백출, 복령, 당귀, 용안육, 산조인, 원지, 감초, 목향",
        "잘 맞는 환자상": "불면, 건망, 심계, 피로, 식욕저하, 생각이 많고 쉽게 지치는 상태",
        "주의 환자상": "습담·식체가 뚜렷함, 열감·번조 강함, 과도한 졸림",
        "감별 처방": "산조인탕, 보중익기탕, 팔진탕, 온담탕",
        "가감": "소화력이 약하면 보익·안신 약재 부담 확인, 담열성 불면이면 온담탕 감별",
        "침구 방향": "심비 보강, 안신, 기혈 보충 방향. 소화 상태와 수면 상태를 함께 봄.",
        "뜸 방향": "수족냉증·복부 냉감이 있으면 검토. 열감·번조가 강하면 주의.",
        "동의보감": "건망(健忘), 몽(夢), 혈(血), 비위(脾胃) 편제와 연결 가능",
        "황제내경": "심, 비, 혈, 신지, 기혈진액",
    },
    {
        "처방명": "십전대보탕",
        "전통 변증": "기혈양허, 허로, 허한",
        "처방 방향": "대보원기, 기혈쌍보, 온보",
        "처방 방향축": ["보충축", "승양·상승축"],
        "구성 약재": "사군자탕 + 사물탕 + 황기 + 육계",
        "잘 맞는 환자상": "기혈양허, 허로, 수술 후 회복기, 면색창백, 수족냉증, 체력저하",
        "주의 환자상": "실열, 고혈압, 상열감, 안면홍조, 염증성 열감, 식체",
        "감별 처방": "팔진탕, 보중익기탕, 사물탕",
        "가감": "열감이 있으면 온보 과잉 주의, 소화가 약하면 보익 부담 확인",
        "침구 방향": "기혈 쌍보, 전신 회복, 허한 보강 방향. 열감 환자에서는 온보 자극 주의.",
        "뜸 방향": "허한·냉감·체력저하가 뚜렷하면 검토. 고혈압·상열감·불면·실열은 주의.",
        "동의보감": "허로(虛勞), 기혈(氣血), 한(寒) 편제와 연결 가능",
        "황제내경": "음양, 기혈진액, 한열, 비신, 승강출입",
    },
    {
        "처방명": "이진탕",
        "전통 변증": "담음정체, 오심구토, 어지럼",
        "처방 방향": "조습, 화담, 강역, 위기 하강",
        "처방 방향축": ["배출·이수축", "소통·전환축", "완충·조화축"],
        "구성 약재": "반하, 진피, 복령, 감초, 생강, 오매",
        "잘 맞는 환자상": "오심, 가래, 어지럼, 흉민, 백니태, 담음정체",
        "주의 환자상": "음허, 마른기침, 구건, 진액 부족, 임신 관련 상태",
        "감별 처방": "평위산, 온담탕, 반하사심탕",
        "가감": "담열이면 온담탕, 식체가 강하면 평위산·소도 방향 감별",
        "침구 방향": "화담강역, 비위 조절, 중초 기기 회복 방향.",
        "뜸 방향": "담음+냉감이 뚜렷하면 검토. 구건·열감이면 강한 온조 자극 주의.",
        "동의보감": "담음(痰飮), 구토(嘔吐), 비위(脾胃) 편제와 연결 가능",
        "황제내경": "비위, 담음, 승강출입, 기기",
    },
    {
        "처방명": "소요산",
        "전통 변증": "간울비허, 흉협고만, 스트레스성 소화불량",
        "처방 방향": "소간, 해울, 건비, 조화",
        "처방 방향축": ["소통·전환축", "완충·조화축", "보충축"],
        "구성 약재": "시호, 당귀, 작약, 백출, 복령, 감초, 박하, 생강",
        "잘 맞는 환자상": "흉협고만, 스트레스성 소화불량, 월경 관련 불편, 피로",
        "주의 환자상": "극심한 기허, 음허화왕, 상열감이 심한 경우",
        "감별 처방": "가미소요산, 귀비탕, 평위산, 반하사심탕",
        "가감": "열감이 강하면 청열 방향, 식체가 강하면 화위 방향 보강",
        "침구 방향": "소간해울, 기기 소통, 비위 조화 방향.",
        "뜸 방향": "허한·냉감이 동반될 때 제한 검토. 울열·상열감이면 강한 뜸 주의.",
        "동의보감": "간(肝), 화(火), 울증, 부인(婦人) 편제와 연결 가능",
        "황제내경": "간, 비위, 오행 생극제화, 기기, 개합추",
    },
]

FORMULA_DF = pd.DataFrame(FORMULAS)

# ============================================================
# 2. 361 표준 경혈 DB 생성
#    - WHO 표준 361 경혈 체계의 코드/경락/순번 기반 DB
#    - 정확 취혈 위치 원문 전체가 아니라 앱용 구조화/분류 DB
# ============================================================
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
    "LU1": "중부", "LU5": "척택", "LU7": "열결", "LU9": "태연", "LU10": "어제", "LU11": "소상",
    "LI4": "합곡", "LI10": "수삼리", "LI11": "곡지", "LI14": "비노", "LI15": "견우", "LI20": "영향",
    "ST25": "천추", "ST36": "족삼리", "ST37": "상거허", "ST40": "풍륭", "ST41": "해계", "ST44": "내정",
    "SP3": "태백", "SP4": "공손", "SP6": "삼음교", "SP9": "음릉천", "SP10": "혈해", "SP21": "대포",
    "HT3": "소해", "HT5": "통리", "HT6": "음극", "HT7": "신문", "HT8": "소부", "HT9": "소충",
    "SI3": "후계", "SI6": "양로", "SI11": "천종", "SI19": "청궁",
    "BL10": "천주", "BL11": "대저", "BL13": "폐수", "BL15": "심수", "BL17": "격수", "BL18": "간수", "BL19": "담수", "BL20": "비수", "BL21": "위수", "BL22": "삼초수", "BL23": "신수", "BL25": "대장수", "BL28": "방광수", "BL32": "차료", "BL40": "위중", "BL57": "승산", "BL60": "곤륜", "BL62": "신맥", "BL67": "지음",
    "KI1": "용천", "KI3": "태계", "KI6": "조해", "KI7": "복류", "KI10": "음곡", "KI27": "수부",
    "PC3": "곡택", "PC4": "극문", "PC5": "간사", "PC6": "내관", "PC7": "대릉", "PC8": "노궁", "PC9": "중충",
    "TE3": "중저", "TE5": "외관", "TE6": "지구", "TE14": "견료", "TE17": "예풍", "TE23": "사죽공",
    "GB20": "풍지", "GB21": "견정", "GB24": "일월", "GB25": "경문", "GB26": "대맥", "GB30": "환도", "GB31": "풍시", "GB34": "양릉천", "GB39": "현종", "GB40": "구허", "GB41": "족임읍", "GB44": "족규음",
    "LR2": "행간", "LR3": "태충", "LR5": "여구", "LR8": "곡천", "LR13": "장문", "LR14": "기문",
    "CV3": "중극", "CV4": "관원", "CV5": "석문", "CV6": "기해", "CV8": "신궐", "CV9": "수분", "CV12": "중완", "CV14": "거궐", "CV17": "전중", "CV22": "천돌", "CV24": "승장",
    "GV3": "요양관", "GV4": "명문", "GV14": "대추", "GV16": "풍부", "GV20": "백회", "GV24": "신정", "GV26": "수구", "GV28": "은교",
}

MERIDIAN_META = {
    "LU": {"경락": "수태음폐경", "기본축": ["보충축", "소통·전환축"], "부위": "상지·흉부", "view": "front", "x": 28, "y1": 35, "y2": 78, "주의": "흉부 혈위는 깊은 자침 주의"},
    "LI": {"경락": "수양명대장경", "기본축": ["소통·전환축", "배출·이수축"], "부위": "상지·두면", "view": "front", "x": 72, "y1": 78, "y2": 28, "주의": "LI4 등 일부 혈위는 임신 중 주의"},
    "ST": {"경락": "족양명위경", "기본축": ["보충축", "소통·전환축", "완충·조화축"], "부위": "두면·흉복·하지", "view": "front", "x": 62, "y1": 22, "y2": 92, "주의": "복부 혈위는 임신·복부 질환 확인"},
    "SP": {"경락": "족태음비경", "기본축": ["보충축", "배출·이수축", "완충·조화축"], "부위": "하지·복흉", "view": "front", "x": 38, "y1": 92, "y2": 42, "주의": "SP6 등 일부 혈위는 임신 중 주의"},
    "HT": {"경락": "수소음심경", "기본축": ["수렴·안정축", "보충축"], "부위": "상지·흉부", "view": "front", "x": 24, "y1": 42, "y2": 82, "주의": "심계·불안 환자 자극 강도 조절"},
    "SI": {"경락": "수태양소장경", "기본축": ["소통·전환축", "수렴·안정축"], "부위": "상지·견갑·두면", "view": "back", "x": 75, "y1": 82, "y2": 25, "주의": "경항부·견갑부 자침 깊이 주의"},
    "BL": {"경락": "족태양방광경", "기본축": ["소통·전환축", "배출·이수축", "보충축"], "부위": "두항·배부·하지", "view": "back", "x": 56, "y1": 18, "y2": 92, "주의": "흉배부 혈위는 기흉 등 깊은 자침 위험 주의"},
    "KI": {"경락": "족소음신경", "기본축": ["보충축", "수렴·안정축"], "부위": "하지·복흉", "view": "front", "x": 45, "y1": 92, "y2": 38, "주의": "허열·음허·임신 관련 상태 확인"},
    "PC": {"경락": "수궐음심포경", "기본축": ["수렴·안정축", "소통·전환축"], "부위": "흉부·상지", "view": "front", "x": 31, "y1": 38, "y2": 82, "주의": "흉부 혈위는 깊은 자침 주의"},
    "TE": {"경락": "수소양삼초경", "기본축": ["소통·전환축", "배출·이수축"], "부위": "상지·두면", "view": "back", "x": 69, "y1": 82, "y2": 22, "주의": "두면·이개 주변 자극 주의"},
    "GB": {"경락": "족소양담경", "기본축": ["소통·전환축", "승양·상승축"], "부위": "두측·몸측·하지", "view": "side", "x": 72, "y1": 20, "y2": 92, "주의": "GB21 등 일부 혈위는 임신 중 주의"},
    "LR": {"경락": "족궐음간경", "기본축": ["소통·전환축", "수렴·안정축", "보충축"], "부위": "하지·복흉", "view": "front", "x": 34, "y1": 92, "y2": 40, "주의": "간울·어혈·월경 관련 상태 확인"},
    "CV": {"경락": "임맥", "기본축": ["보충축", "수렴·안정축", "완충·조화축"], "부위": "전중선", "view": "front", "x": 50, "y1": 88, "y2": 18, "주의": "복부·임신·심혈관 상태 확인"},
    "GV": {"경락": "독맥", "기본축": ["승양·상승축", "소통·전환축"], "부위": "후중선·두부", "view": "back", "x": 50, "y1": 88, "y2": 14, "주의": "경항부·척추 주변 자극 주의"},
}

# 주요 혈위별 임상 방향 보강
POINT_OVERRIDES = {
    "ST36": {"축": ["보충축", "승양·상승축", "완충·조화축"], "방향": "비위 보강, 기혈 보강, 전신 회복", "뜸": "허한·냉감 시 검토 가능"},
    "CV12": {"축": ["소통·전환축", "완충·조화축"], "방향": "중초 화위, 복부팽만, 식체 조절", "뜸": "복부 냉감 시 검토 가능"},
    "CV6": {"축": ["보충축", "수렴·안정축"], "방향": "원기 보강, 기허 조절", "뜸": "허한·냉감 시 검토 가능"},
    "CV4": {"축": ["보충축", "수렴·안정축"], "방향": "하초 보강, 정혈·원기 보강", "뜸": "허한 확인 시 검토, 임신 시 주의"},
    "SP6": {"축": ["보충축", "수렴·안정축", "배출·이수축"], "방향": "간·비·신 조절, 혈·수분·안신 보조", "뜸": "허한 시 검토, 임신 중 주의"},
    "KI3": {"축": ["보충축", "수렴·안정축"], "방향": "간신·자음 보강, 허열 완충", "뜸": "허한 시 검토"},
    "LR3": {"축": ["소통·전환축", "수렴·안정축"], "방향": "소간해울, 기기 소통", "뜸": "일반적으로 침구 조절 중심"},
    "LI4": {"축": ["소통·전환축", "배출·이수축"], "방향": "기기 소통, 표증·두면부 조절", "뜸": "필요시 제한 검토, 임신 중 주의"},
    "PC6": {"축": ["수렴·안정축", "소통·전환축"], "방향": "안신, 흉민, 오심, 위기 조절", "뜸": "대개 침구 조절 중심"},
    "HT7": {"축": ["수렴·안정축"], "방향": "안신, 심계, 불면 조절", "뜸": "자극 강도 조절"},
    "GV20": {"축": ["승양·상승축", "수렴·안정축"], "방향": "청양 상승, 안신, 두면부 조절", "뜸": "화상·상열감 주의"},
    "GV14": {"축": ["승양·상승축", "소통·전환축"], "방향": "양기 조절, 표증·열감 확인", "뜸": "허한 시 검토, 실열 시 주의"},
    "BL20": {"축": ["보충축", "완충·조화축"], "방향": "비위 보강, 운화 조절", "뜸": "허한·냉감 시 검토"},
    "BL21": {"축": ["보충축", "소통·전환축"], "방향": "위기 조절, 소화 기능 보조", "뜸": "허한·냉감 시 검토"},
    "BL23": {"축": ["보충축", "수렴·안정축"], "방향": "신기·하초 보강", "뜸": "허한·냉감 시 검토"},
    "BL17": {"축": ["보충축", "소통·전환축"], "방향": "혈 조절, 활혈 보조", "뜸": "허한 시 검토, 출혈 경향 확인"},
    "BL18": {"축": ["소통·전환축", "보충축"], "방향": "간기·혈 조절", "뜸": "허한 시 검토"},
    "SP9": {"축": ["배출·이수축"], "방향": "수습·부종·습담 조절", "뜸": "냉습 시 검토"},
    "ST40": {"축": ["배출·이수축", "소통·전환축"], "방향": "화담, 담음 조절", "뜸": "담음+냉감 시 검토"},
    "GB34": {"축": ["소통·전환축"], "방향": "소양·근회, 기기 소통", "뜸": "상태에 따라 제한 검토"},
    "CV17": {"축": ["수렴·안정축", "소통·전환축"], "방향": "흉부 기기, 심계·흉민 보조", "뜸": "흉부 열감·피부상태 주의"},
    "ST25": {"축": ["소통·전환축", "배출·이수축"], "방향": "장부 기능, 대변·복부팽만 조절", "뜸": "복부 냉감 시 검토"},
    "CV9": {"축": ["배출·이수축"], "방향": "수분 대사, 부종 조절", "뜸": "허한성 수습 시 검토"},
    "BL40": {"축": ["소통·전환축", "배출·이수축"], "방향": "요배부·하지 순환, 열·습 조절", "뜸": "상태에 따라 제한 검토"},
    "BL60": {"축": ["소통·전환축"], "방향": "경락 소통, 요배부·하지 조절", "뜸": "임신 중 주의"},
    "BL67": {"축": ["승양·상승축", "소통·전환축"], "방향": "방광경 말단, 승양·전환 보조", "뜸": "임신 관련 상태 전문가 확인"},
    "GB21": {"축": ["소통·전환축", "승양·상승축"], "방향": "견부 긴장, 기기 소통", "뜸": "임신 중 주의"},
}

PREGNANCY_CAUTION = {"LI4", "SP6", "BL60", "BL67", "GB21", "CV3", "CV4", "CV5", "CV6", "CV7"}
FACE_HEAD_CAUTION_PREFIXES = {"ST1", "BL1", "GB1"}


def point_coords(prefix, idx, count):
    meta = MERIDIAN_META[prefix]
    t = 0 if count <= 1 else (idx - 1) / (count - 1)
    x = meta["x"]
    y = meta["y1"] + (meta["y2"] - meta["y1"]) * t

    # 긴 경락은 겹침 방지를 위해 약간 흔들림을 줌
    if prefix in ["BL", "GB", "ST"]:
        x = x + (idx % 3 - 1) * 2
    if prefix in ["LU", "LI", "HT", "SI", "PC", "TE"]:
        x = x + (idx % 2) * 2
    return round(x, 2), round(y, 2)


def build_acupoint_db():
    rows = []
    for prefix, names in POINT_NAMES.items():
        meta = MERIDIAN_META[prefix]
        count = len(names)
        for i, name in enumerate(names, start=1):
            code = f"{prefix}{i}"
            axes = list(meta["기본축"])
            direction = f"{meta['경락']}의 기본 방향: {', '.join(axes)}"
            moxa = "허한·냉감 소견이 명확할 때 한의사가 제한적으로 검토"
            caution = meta["주의"]
            if code in POINT_OVERRIDES:
                axes = POINT_OVERRIDES[code].get("축", axes)
                direction = POINT_OVERRIDES[code].get("방향", direction)
                moxa = POINT_OVERRIDES[code].get("뜸", moxa)
            if code in PREGNANCY_CAUTION:
                caution += " / 임신 중 사용 주의 또는 전문가 확인 필요"
            if code in FACE_HEAD_CAUTION_PREFIXES or meta["부위"].startswith("두"):
                caution += " / 두면부·안와 주변 자극 주의"
            x, y = point_coords(prefix, i, count)
            rows.append(
                {
                    "code": code,
                    "경혈명": COMMON_KO.get(code, name),
                    "standard_name": name,
                    "경락코드": prefix,
                    "경락": meta["경락"],
                    "순번": i,
                    "부위군": meta["부위"],
                    "처방 방향축": ", ".join(axes),
                    "임상 방향": direction,
                    "금기·주의": caution,
                    "뜸 가능 여부": moxa,
                    "임신 주의": "주의" if code in PREGNANCY_CAUTION else "일반 확인",
                    "표시화면": meta["view"],
                    "x": x,
                    "y": y,
                }
            )
    df = pd.DataFrame(rows)
    return df

ACUPOINT_DF = build_acupoint_db()
assert len(ACUPOINT_DF) == 361, f"경혈 DB 수가 361개가 아닙니다: {len(ACUPOINT_DF)}"

# ============================================================
# 3. 황제내경·동의보감 매핑
# ============================================================
NEIJING_RULES = [
    ("음양", ["자음", "온보", "청열", "허열", "실열", "한열", "음허", "양허", "냉감", "상열"], "부족과 과잉, 차가움과 열감, 안과 밖의 균형을 확인합니다."),
    ("오행 생극제화", ["간", "심", "비", "폐", "신", "소간", "보신", "비위", "심비", "폐위"], "장부 간의 밀고 당김, 상생·상극·조절 관계를 확인합니다."),
    ("장부·기혈진액", ["기", "혈", "진액", "담음", "수습", "어혈", "정혈", "보혈", "보기", "자음"], "기, 혈, 체액, 담음, 어혈의 부족·정체·소모를 확인합니다."),
    ("승강출입", ["승양", "강역", "수렴", "해표", "배출", "이수", "공하", "기화", "소통"], "기운이 오르는지, 내려가는지, 안으로 모이는지, 밖으로 풀리는지 확인합니다."),
    ("개합추", ["해표", "수렴", "안신", "화위", "조중", "소간", "해울", "한열착잡"], "열고, 닫고, 가운데에서 돌리는 조절 구조를 확인합니다."),
    ("표본중기", ["표", "본", "허", "실", "담음", "식체", "허열", "실열", "기허", "습담"], "겉으로 보이는 증상과 뿌리 병기를 구분합니다."),
    ("삼음삼양 병기", ["태양", "양명", "소양", "태음", "소음", "궐음", "외감", "비위", "간", "신", "심"], "병이 표에서 리로, 양에서 음으로, 얕은 층에서 깊은 층으로 움직이는 흐름을 확인합니다."),
    ("육기", ["풍", "한", "서", "습", "조", "화", "담음", "열", "냉감", "건조", "습탁"], "풍·한·습·조·화 등 환경적·병리적 기운의 영향을 확인합니다."),
]

DONGUI_RULES = [
    ("불면|수면|꿈|심계|불안|건망", "몽(夢)·건망(健忘)·심(心)", "수면, 꿈, 심계, 건망, 정서 불안과 관련된 병증 해석"),
    ("피로|허약|허로|회복|수술|안색창백", "허로(虛勞)·기혈(氣血)", "오래 지치고 회복력이 떨어지는 허로·기혈 부족 해석"),
    ("소화|식욕|더부룩|트림|복부팽만|설사|식체", "비위(脾胃)·내상(內傷)", "소화력 저하, 식체, 비위 운화 장애 해석"),
    ("부종|소변|수분|갈증|몸무거움", "소변(小便)·부종(浮腫)·수(水)", "수분 대사, 소변불리, 부종과 관련된 해석"),
    ("기침|가래|비염|폐|숨", "해수(咳嗽)·폐(肺)·담음(痰飮)", "기침, 가래, 폐계 증상과 담음 해석"),
    ("통증|관절|허리|무릎|근육|경련", "비증(痺證)·통증·근골", "근골격 통증, 비증, 경락 소통 장애 해석"),
    ("월경|갱년기|하복부|어혈|출혈", "부인(婦人)·혈(血)·충임", "월경, 하복부, 충임, 혈허·어혈 관련 해석"),
    ("스트레스|흉협|답답|울|간울|화", "간(肝)·화(火)·울증", "간기울결, 화, 흉협불편, 정서성 소견 해석"),
]


def infer_neijing(formula, symptom_text, assessment_text):
    text = f"{formula['전통 변증']} {formula['처방 방향']} {formula['황제내경']} {symptom_text} {assessment_text}"
    rows = []
    for concept, keywords, reason in NEIJING_RULES:
        if any(k in text for k in keywords):
            rows.append({"황제내경 해당 개념": concept, "연결 이유": reason, "한의사 확인 질문": clinical_question(concept)})
    if not rows:
        rows.append({"황제내경 해당 개념": "종합 변증", "연결 이유": "입력 정보 부족으로 음양·장부·기혈진액을 종합 확인합니다.", "한의사 확인 질문": "허실한열, 표리, 장부, 기혈진액 중 어느 축이 중심인가?"})
    return pd.DataFrame(rows).drop_duplicates()


def clinical_question(concept):
    return {
        "음양": "부족해서 생긴 열인가, 실제 열이 강한가? 차가움과 열감이 섞였는가?",
        "오행 생극제화": "간이 비위를 누르는가? 신음 부족이 허열로 올라오는가? 심비가 함께 약한가?",
        "장부·기혈진액": "부족한 것은 기·혈·진액 중 무엇인가? 정체된 것은 담음인가 어혈인가?",
        "승강출입": "올려야 하는가, 내려야 하는가, 안으로 모아야 하는가, 밖으로 풀어야 하는가?",
        "개합추": "막힌 것을 열어야 하는가, 흩어진 것을 닫아야 하는가, 가운데에서 조화시켜야 하는가?",
        "표본중기": "지금 보이는 증상이 본질인가, 겉으로 나타난 반응인가?",
        "삼음삼양 병기": "병이 표에 있는가 리에 있는가? 어느 층으로 깊어졌는가?",
        "육기": "풍한인가, 습담인가, 건조인가, 열인가? 계절·환경 요인이 영향을 주는가?",
    }.get(concept, "허실한열과 장부·기혈진액을 종합 확인합니다.")


def infer_dongui(formula, symptom_text, assessment_text):
    import re
    text = f"{formula['전통 변증']} {formula['처방 방향']} {formula['동의보감']} {symptom_text} {assessment_text}"
    rows = [{"동의보감 해당 편제": formula["동의보감"], "연결 이유": "선택 처방의 전통 변증과 직접 연결"}]
    for pattern, chapter, reason in DONGUI_RULES:
        if re.search(pattern, text):
            rows.append({"동의보감 해당 편제": chapter, "연결 이유": reason})
    return pd.DataFrame(rows).drop_duplicates()

# ============================================================
# 4. 경혈 추천 후보군 로직
# ============================================================
def acupoint_candidates(formula, symptom_text, assessment_text, include_all_axis=False):
    target_axes = set(formula["처방 방향축"])
    text = f"{formula['전통 변증']} {formula['처방 방향']} {symptom_text} {assessment_text}"
    df = ACUPOINT_DF.copy()

    def score(row):
        axes = set([a.strip() for a in row["처방 방향축"].split(",")])
        s = len(target_axes & axes) * 3
        # 주요 임상 혈위 가중치
        if row["code"] in POINT_OVERRIDES:
            s += 2
        for keyword in ["비위", "기혈", "자음", "안신", "담음", "수습", "소간", "어혈", "허열", "온보", "불면", "복부", "피로"]:
            if keyword in text and keyword in row["임상 방향"]:
                s += 2
        return s

    df["관련도"] = df.apply(score, axis=1)
    if include_all_axis:
        return df.sort_values(["관련도", "경락코드", "순번"], ascending=[False, True, True])
    return df[df["관련도"] > 0].sort_values(["관련도", "경락코드", "순번"], ascending=[False, True, True])


def build_matches_and_cautions(formula, inputs):
    matches, cautions = [], []
    text = f"{formula['전통 변증']} {formula['처방 방향']} {inputs['symptom']} {inputs['assessment']}"
    if inputs["symptom"]:
        matches.append(f"입력 증상 '{inputs['symptom']}'과 처방 방향 '{formula['처방 방향']}'의 정합 여부 검토")
    if any(k in text for k in ["보기", "보혈", "자음", "보신", "기혈"]):
        matches.append("보충·수렴·완충 방향 소견 확인: 피로, 안색, 맥력, 설질, 소화상태 확인")
    if any(k in text for k in ["습담", "담음", "식체", "후태", "더부룩"]):
        cautions.append("습담·식체·후태 소견 → 보익·자음 처방의 위장 부담 또는 조습 처방 필요성 확인")
    if inputs["bp"] or inputs["meds"]:
        cautions.append("혈압·복용약 입력 → 혈압약, 항응고제, 당뇨약, 수면제 병용 여부 세부 확인")
    return matches, cautions

# ============================================================
# 5. 인체 SVG 시각화
# ============================================================
def make_body_svg(points_df, title="경혈 표시", show_labels=True):
    # points_df columns: x, y, code, 경혈명, 처방 방향축, 관련도
    circles = []
    for _, r in points_df.iterrows():
        x, y = float(r["x"]), float(r["y"])
        rel = float(r.get("관련도", 1))
        radius = 2.5 + min(rel, 10) * 0.15
        color = "#ff4b4b" if rel >= 6 else "#1f77b4" if rel >= 3 else "#7f7f7f"
        label = f"{r['code']} {r['경혈명']}"
        circles.append(f'<circle cx="{x}" cy="{y}" r="{radius:.1f}" fill="{color}" opacity="0.85"><title>{escape(label)}</title></circle>')
        if show_labels:
            circles.append(f'<text x="{x+2.8}" y="{y+1.5}" font-size="3.2" fill="#111">{escape(str(r["code"]))}</text>')
    svg = f'''
    <svg viewBox="0 0 100 105" width="100%" height="620" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="100" height="105" fill="#ffffff"/>
      <text x="50" y="5" text-anchor="middle" font-size="5" font-weight="bold">{escape(title)}</text>
      <!-- human silhouette -->
      <circle cx="50" cy="15" r="8" fill="#f2f2f2" stroke="#333" stroke-width="0.5"/>
      <path d="M42 25 C39 38,39 54,42 68 L46 68 C45 77,44 89,43 98 L49 98 C49 82,50 74,50 68 C50 74,51 82,51 98 L57 98 C56 89,55 77,54 68 L58 68 C61 54,61 38,58 25 Z" fill="#f2f2f2" stroke="#333" stroke-width="0.5"/>
      <path d="M42 28 C30 35,23 48,20 62" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round"/>
      <path d="M58 28 C70 35,77 48,80 62" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round"/>
      <path d="M46 68 C43 78,38 89,35 99" fill="none" stroke="#333" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M54 68 C57 78,62 89,65 99" fill="none" stroke="#333" stroke-width="2.2" stroke-linecap="round"/>
      <text x="6" y="102" font-size="3.2" fill="#555">※ 교육·검토용 도식입니다. 실제 취혈은 체표 표지와 촌법에 따라 한의사가 결정합니다.</text>
      {''.join(circles)}
    </svg>
    '''
    return svg

# ============================================================
# 6. 소견서 생성
# ============================================================
def build_clinical_note(formula, inputs, cand_df, neijing_df, dongui_df, matches, cautions):
    top_points = cand_df.head(12)
    point_lines = "\n".join([f"- {r['code']} {r['경혈명']} ({r['경락']}): {r['임상 방향']} / 주의: {r['금기·주의']}" for _, r in top_points.iterrows()])
    neijing_lines = "\n".join([f"- {r['황제내경 해당 개념']}: {r['한의사 확인 질문']}" for _, r in neijing_df.iterrows()])
    dongui_lines = "\n".join([f"- {r['동의보감 해당 편제']}: {r['연결 이유']}" for _, r in dongui_df.iterrows()])
    note = f"""
[한의사 종합소견 기반 치료계획 초안]
작성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}

1. 입력 소견
- 주증상/진단명: {inputs['symptom'] or '미입력'}
- 한의사 종합소견: {inputs['assessment'] or '미입력'}
- 치료 목표: {inputs['goal'] or '미입력'}
- 복용약/검사값 메모: {inputs['meds'] or '미입력'} / 혈압: {inputs['bp'] or '미입력'}

2. 황제내경 해당 개념
{neijing_lines}

3. 동의보감 해당 편제
{dongui_lines}

4. 변증 및 처방 방향
- 선택 처방: {formula['처방명']}
- 전통 변증: {formula['전통 변증']}
- 처방 방향: {formula['처방 방향']}
- 처방 방향 6축: {', '.join(formula['처방 방향축'])}

5. 한약 처방 검토안
- 구성 약재: {formula['구성 약재']}
- 잘 맞는 환자상: {formula['잘 맞는 환자상']}
- 주의 환자상: {formula['주의 환자상']}
- 감별 처방: {formula['감별 처방']}
- 가감·조정: {formula['가감']}

6. 침구 치료 방향 및 검토 가능한 혈위군
- 기본 방향: {formula['침구 방향']}
{point_lines}
- 주의: 위 혈위군은 자동 침 처방이 아니라 후보군입니다. 실제 혈위, 자침 깊이, 유침 시간, 자극 강도, 보사법은 한의사가 결정합니다.

7. 뜸 치료 방향
- 기본 방향: {formula['뜸 방향']}
- 뜸은 허한·냉감·피부상태·감각저하·당뇨성 말초신경병증·실열·상열 여부를 확인 후 제한적으로 검토합니다.

8. 정합 소견
{chr(10).join(['- ' + m for m in matches]) if matches else '- 입력 정보 부족'}

9. 주의 및 재검토 소견
{chr(10).join(['- ' + c for c in cautions]) if cautions else '- 현재 입력상 큰 주의 소견 없음'}

10. 차트용 요약문
상기 환자는 '{inputs['symptom'] or '미입력'}'을 주호소로 하며, 한의사 종합소견상 '{inputs['assessment'] or '미입력'}'로 기록됨. 황제내경 관점에서는 {', '.join(neijing_df['황제내경 해당 개념'].tolist())} 개념을 참고할 수 있고, 동의보감 관점에서는 {', '.join(dongui_df['동의보감 해당 편제'].tolist())} 편제와 병증 해석을 참고할 수 있음. 현재 {formula['처방명']}은/는 {formula['처방 방향']} 방향에서 검토 가능하나, {formula['주의 환자상']}에 해당하는 소견이 있으면 재검토가 필요함. 침구는 처방 방향과 충돌하지 않도록 후보 혈위군을 검토하고, 뜸은 허한·냉감·피부상태 확인 후 제한적으로 검토함.

※ 본 문서는 자동 확정 처방이 아니라 한의사의 최종 판단을 돕는 임상 초안입니다.
"""
    return note.strip()

# ============================================================
# 7. 사이드바 입력
# ============================================================
st.sidebar.header("📝 환자 임상 정보 입력")
selected_formula = st.sidebar.selectbox("분석할 한의학 처방", FORMULA_DF["처방명"].tolist())
symptom = st.sidebar.text_input("주증상 및 진단명", placeholder="예: 만성피로, 안색창백, 어지럼, 식욕저하")
assessment = st.sidebar.text_area("한의사 종합검진 소견", height=160, placeholder="예: 맥 허약, 설 담백, 치흔. 기혈양허와 비위기허 경향. 소화력이 약함.")
goal = st.sidebar.text_input("치료 목표", placeholder="예: 피로 회복, 소화 안정, 수면 개선")

st.sidebar.subheader("🧪 검사값 및 복용약")
ast_alt = st.sidebar.text_input("AST/ALT")
creatinine = st.sidebar.text_input("Creatinine/eGFR")
bp = st.sidebar.text_input("혈압")
meds = st.sidebar.text_area("현재 복용약 상세", height=90)

st.sidebar.subheader("🚨 안전성 체크")
anti_coag = st.sidebar.checkbox("항응고제/항혈소판제/NSAIDs")
bp_med = st.sidebar.checkbox("혈압약")
diabetes_med = st.sidebar.checkbox("당뇨약/인슐린")
sedative = st.sidebar.checkbox("수면제/진정제/항우울제")
pregnant = st.sidebar.checkbox("임신/수유")
liver_kidney = st.sidebar.checkbox("간·신장 질환")
surgery = st.sidebar.checkbox("수술/시술 예정")
neuro = st.sidebar.checkbox("피부 감각저하/당뇨성 말초신경병증")

show_research = st.sidebar.checkbox("🔬 연구자용 용어 보기", value=False)

inputs = {
    "symptom": symptom,
    "assessment": assessment,
    "goal": goal,
    "bp": bp,
    "meds": meds,
    "anti_coag": anti_coag,
    "bp_med": bp_med,
    "diabetes_med": diabetes_med,
    "sedative": sedative,
    "pregnant": pregnant,
    "liver_kidney": liver_kidney,
    "surgery": surgery,
    "neuro": neuro,
}

formula = FORMULA_DF[FORMULA_DF["처방명"] == selected_formula].iloc[0].to_dict()
neijing_df = infer_neijing(formula, symptom, assessment)
dongui_df = infer_dongui(formula, symptom, assessment)
match_list, caution_list = build_matches_and_cautions(formula, inputs)
cand_df = acupoint_candidates(formula, symptom, assessment)

# 안전 체크 추가
if anti_coag:
    caution_list.append("항응고제/항혈소판제/NSAIDs 체크 → 활혈 혈위·약재, 출혈 경향, 수술 예정 여부 확인")
if bp_med or bp:
    caution_list.append("혈압 관련 정보 체크 → 승양·온보 자극 과잉 및 혈압 변화 확인")
if diabetes_med:
    caution_list.append("당뇨약/인슐린 체크 → 혈당 변화와 저혈당 증상 확인")
if sedative:
    caution_list.append("수면제/진정제/항우울제 체크 → 안신 처방·혈위 사용 시 주간 졸림 확인")
if pregnant:
    caution_list.append("임신/수유 체크 → 처방·침구·뜸 모두 전문가 확인, 임신 주의 혈위 필터 확인")
if liver_kidney:
    caution_list.append("간·신장 질환 체크 → 장기 복용 전 검사값 확인")
if surgery:
    caution_list.append("수술/시술 예정 체크 → 출혈 관련 약재·혈위와 복용 중단 여부 확인")
if neuro:
    caution_list.append("피부 감각저하/당뇨성 말초신경병증 체크 → 뜸 화상 위험 주의")

# ============================================================
# 8. 탭 구성
# ============================================================
tab_names = [
    "1. 통합 요약",
    "2. 소견서·치료계획",
    "3. 황제내경·동의보감",
    "4. 361 경혈 DB",
    "5. 경혈 인체 시각화",
    "6. 침구·혈위 후보",
    "7. 뜸 가능·주의",
    "8. 처방 방향 6축",
    "9. 안전성 확인",
    "10. 환자 설명문",
]
if show_research:
    tab_names.append("11. 연구자용 부록")

tabs = st.tabs(tab_names)
tab = dict(zip(tab_names, tabs))

with tab["1. 통합 요약"]:
    st.header(f"🧑‍⚕️ {selected_formula} 통합 요약")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("361 경혈 DB", f"{len(ACUPOINT_DF)}개")
    c2.metric("후보 혈위", f"{len(cand_df)}개")
    c3.metric("정합 소견", f"{len(match_list)}개")
    c4.metric("주의 소견", f"{len(caution_list)}개")

    st.success(f"**처방 방향:** {formula['처방 방향']}")
    st.info(f"**한의사용 6축:** {', '.join(formula['처방 방향축'])}")

    st.subheader("한의사 종합소견")
    st.write(assessment or "미입력")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("황제내경 연결")
        st.dataframe(neijing_df, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("동의보감 연결")
        st.dataframe(dongui_df, use_container_width=True, hide_index=True)

    st.subheader("상위 후보 혈위")
    st.dataframe(cand_df[["code", "경혈명", "경락", "처방 방향축", "임상 방향", "금기·주의", "뜸 가능 여부", "관련도"]].head(12), use_container_width=True, hide_index=True)

with tab["2. 소견서·치료계획"]:
    st.header("📝 소견서·치료계획 초안")
    st.warning("자동 확정 처방이 아니라 한의사가 검토·수정할 차트 초안입니다.")
    note = build_clinical_note(formula, inputs, cand_df, neijing_df, dongui_df, match_list, caution_list)
    st.text_area("차트용 소견서·치료계획 초안", note, height=760)
    st.download_button("소견서·치료계획 초안 다운로드", data=note, file_name=f"{selected_formula}_clinical_plan_361points.txt", mime="text/plain")

with tab["3. 황제내경·동의보감"]:
    st.header("📚 원전 해당 해석")
    st.warning("본 패널은 원전을 현대 생물학적으로 증명한다는 뜻이 아니라, 입력 소견을 전통 개념과 편제에 맞춰 정리하는 주석층입니다.")
    st.subheader("1. 황제내경 해당 개념")
    st.dataframe(neijing_df, use_container_width=True, hide_index=True)
    st.subheader("2. 동의보감 해당 편제")
    st.dataframe(dongui_df, use_container_width=True, hide_index=True)

with tab["4. 361 경혈 DB"]:
    st.header("🧾 361 표준 경혈 DB")
    st.info("코드·경락·처방 방향축·금기·주의·뜸 검토 여부를 포함한 앱용 구조화 DB입니다. 정확한 취혈 위치는 한의사가 WHO 표준 위치·체표 표지를 기준으로 확인해야 합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        meridian_filter = st.multiselect("경락 필터", sorted(ACUPOINT_DF["경락코드"].unique()), default=[])
    with col2:
        axis_filter = st.multiselect("처방 방향축 필터", ["보충축", "수렴·안정축", "승양·상승축", "배출·이수축", "소통·전환축", "완충·조화축"], default=[])
    with col3:
        search = st.text_input("경혈 검색", placeholder="예: ST36, 족삼리, 중완, Hegu")

    db_view = ACUPOINT_DF.copy()
    if meridian_filter:
        db_view = db_view[db_view["경락코드"].isin(meridian_filter)]
    if axis_filter:
        db_view = db_view[db_view["처방 방향축"].apply(lambda s: any(a in s for a in axis_filter))]
    if search:
        s = search.strip().lower()
        db_view = db_view[db_view.apply(lambda r: s in str(r["code"]).lower() or s in str(r["경혈명"]).lower() or s in str(r["standard_name"]).lower() or s in str(r["경락"]).lower(), axis=1)]

    st.dataframe(db_view[["code", "경혈명", "standard_name", "경락", "부위군", "처방 방향축", "임상 방향", "금기·주의", "뜸 가능 여부", "임신 주의"]], use_container_width=True, hide_index=True)
    st.download_button("361 경혈 DB CSV 다운로드", data=ACUPOINT_DF.to_csv(index=False).encode("utf-8-sig"), file_name="acupoint_361_db.csv", mime="text/csv")

with tab["5. 경혈 인체 시각화"]:
    st.header("🧍 경혈 인체 시각화")
    st.warning("이 그림은 실제 인체 사진 기반 자동 취혈이 아니라 교육·검토용 도식입니다. 정확한 위치는 체표 표지와 촌법으로 확인해야 합니다.")
    view_mode = st.radio("표시할 혈위", ["선택 처방 후보 혈위", "전체 361개", "검색/필터 결과"], horizontal=True)
    label_on = st.checkbox("라벨 표시", value=True)

    if view_mode == "전체 361개":
        plot_df = ACUPOINT_DF.copy()
        plot_df["관련도"] = 1
        label_on = False if len(plot_df) > 80 else label_on
    elif view_mode == "검색/필터 결과":
        plot_df = db_view.copy() if "db_view" in locals() else ACUPOINT_DF.head(60).copy()
        plot_df["관련도"] = plot_df.get("관련도", 1)
    else:
        plot_df = cand_df.head(35).copy()

    st.markdown(make_body_svg(plot_df, title=f"{selected_formula} 관련 경혈 표시", show_labels=label_on), unsafe_allow_html=True)

with tab["6. 침구·혈위 후보"]:
    st.header("📍 침구 치료 방향 및 혈위 후보")
    st.warning("후보 혈위군은 자동 침 처방이 아닙니다. 실제 혈위, 자침 깊이, 유침 시간, 보사법은 한의사가 결정합니다.")
    st.info(formula["침구 방향"])
    st.subheader("관련도 높은 후보 혈위")
    st.dataframe(cand_df[["code", "경혈명", "경락", "처방 방향축", "임상 방향", "금기·주의", "뜸 가능 여부", "관련도"]].head(30), use_container_width=True, hide_index=True)

with tab["7. 뜸 가능·주의"]:
    st.header("🔥 뜸 가능 여부 및 주의 조건")
    st.error("뜸은 화상, 감염, 피부 자극 위험이 있으므로 감각저하, 당뇨성 말초신경병증, 실열·상열, 임신, 피부질환을 반드시 확인해야 합니다.")
    st.info(formula["뜸 방향"])
    moxa_df = cand_df[["code", "경혈명", "경락", "뜸 가능 여부", "금기·주의", "임신 주의", "관련도"]].head(40)
    st.dataframe(moxa_df, use_container_width=True, hide_index=True)

with tab["8. 처방 방향 6축"]:
    st.header("🧭 처방 방향 6축")
    axis_rows = [
        {"축": "보충축", "뜻": "기·혈·음·양·정혈을 보태는 방향", "대표 소견": "피로, 무력, 안색창백, 식욕저하"},
        {"축": "수렴·안정축", "뜻": "흩어진 기운을 안으로 모으고 안정시키는 방향", "대표 소견": "불면, 심계, 도한, 불안, 진액 소모"},
        {"축": "승양·상승축", "뜻": "아래로 처진 기운을 위로 끌어올리는 방향", "대표 소견": "처짐, 중기하함, 무력감, 기단, 자한"},
        {"축": "배출·이수축", "뜻": "정체된 수분·습담·노폐를 밖으로 빼는 방향", "대표 소견": "부종, 소변불리, 몸무거움, 백니태"},
        {"축": "소통·전환축", "뜻": "막힌 기혈과 비위의 흐름을 돌리는 방향", "대표 소견": "흉협고만, 복부팽만, 식체, 통증"},
        {"축": "완충·조화축", "뜻": "치우친 보·사·한·열을 조절하는 방향", "대표 소견": "보하면 체하고 사하면 허해지는 중간형"},
    ]
    axis_df = pd.DataFrame(axis_rows)
    axis_df["현재 처방 관련성"] = axis_df["축"].apply(lambda x: "중심" if x in formula["처방 방향축"] else "보조 확인")
    st.dataframe(axis_df, use_container_width=True, hide_index=True)

with tab["9. 안전성 확인"]:
    st.header("🚨 안전성 확인")
    st.warning("아래 항목은 금지 판정이 아니라 추가 확인이 필요한 위험 신호입니다.")
    safety_rows = []
    for label, checked, note in [
        ("항응고제/항혈소판제/NSAIDs", anti_coag, "활혈 혈위·약재, 출혈 경향, 멍, 코피, 수술 예정 확인"),
        ("혈압약/고혈압", bp_med or bool(bp), "승양·온보 자극 과잉, 혈압 변화, 심계 확인"),
        ("당뇨약/인슐린", diabetes_med, "혈당 변화, 저혈당 증상, 감각저하 여부 확인"),
        ("수면제/진정제/항우울제", sedative, "안신 처방·혈위와 병용 시 주간 졸림 확인"),
        ("임신/수유", pregnant, "처방·침구·뜸 모두 전문가 확인, 임신 주의 혈위 필터 확인"),
        ("간·신장 질환", liver_kidney, "AST/ALT, Creatinine/eGFR 등 검사값 확인"),
        ("수술/시술 예정", surgery, "출혈 관련 약재·혈위와 복용 중단 여부 확인"),
        ("피부 감각저하/당뇨성 말초신경병증", neuro, "뜸 화상 위험 주의"),
    ]:
        if checked:
            safety_rows.append({"확인 항목": label, "우선순위": "높음", "확인 내용": note})
    if not safety_rows:
        safety_rows.append({"확인 항목": "특이 입력 없음", "우선순위": "일반주의", "확인 내용": "복용약, 병력, 알레르기, 검사값은 실제 진료에서 재확인"})
    st.dataframe(pd.DataFrame(safety_rows), use_container_width=True, hide_index=True)
    st.subheader("검사값 메모")
    st.dataframe(pd.DataFrame([
        {"항목": "AST/ALT", "입력값": ast_alt or "미입력"},
        {"항목": "Creatinine/eGFR", "입력값": creatinine or "미입력"},
        {"항목": "혈압", "입력값": bp or "미입력"},
        {"항목": "복용약", "입력값": meds or "미입력"},
    ]), use_container_width=True, hide_index=True)

with tab["10. 환자 설명문"]:
    st.header("💬 환자 설명문")
    patient_text = f"""
{selected_formula}은 전통 한의학에서 '{formula['전통 변증']}' 방향에서 검토되는 처방입니다.

쉽게 말하면, 환자의 몸 상태에서 부족한 부분, 막힌 부분, 열감이나 냉감, 소화 상태, 수면 상태 등을 함께 살펴 처방 방향을 정리하는 것입니다.

이 앱은 처방을 자동으로 정하거나 특정 효과를 보장하는 도구가 아닙니다. 담당 한의사가 환자의 증상, 맥과 설진, 복용약, 검사값, 안전성 확인 항목을 함께 보면서 처방 방향과 주의점을 정리하는 데 도움을 주기 위한 설명 도구입니다.

복용 전후에는 소화 상태, 대소변 변화, 피로감 변화, 열감이나 두근거림, 수면 변화, 기존 복용약과 관련된 변화를 관찰해 주세요.

불편감이 생기거나 기존 증상이 악화되면 임의로 계속 복용하지 말고 담당 한의사에게 알려야 합니다.
""".strip()
    st.text_area("환자 설명문", patient_text, height=360)
    st.download_button("환자 설명문 다운로드", data=patient_text, file_name=f"{selected_formula}_patient_explanation.txt", mime="text/plain")

if show_research:
    with tab["11. 연구자용 부록"]:
        st.header("🔬 연구자용 부록")
        st.markdown(
            """
            | 연구자용 표현 | 한의사용 번역 |
            |---|---|
            | 64큐브 / Q6 Core | 처방 방향 6축 |
            | H(3,4) Extension | 처방 주변 변화 가능성 |
            | Polyhedron Layer | 보사·승강출입 균형 |
            | 361 Acupoint DB | 처방 방향 6축과 경혈 후보군 연결 |
            | 좌표 표시 | 교육용 도식 표시, 실제 취혈 아님 |
            """
        )
        st.info("연구자용 구조는 처방 효과를 증명하거나 약재가 유전자를 조절한다는 뜻이 아닙니다. 전통 처방 방향을 정보 구조로 주석화하는 보조 구조입니다.")
        st.dataframe(ACUPOINT_DF, use_container_width=True, hide_index=True)
