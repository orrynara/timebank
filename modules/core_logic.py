"""TimeBank 핵심 비즈니스 로직.

- ROI 계산
- 예약 데이터 관리 (In-memory Mock)
- 시스템 데이터 초기화 (Tujia 모델 기반)
"""

import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import random

# --- 데이터 모델 ---
@dataclass
class Region:
    id: str
    name: str
    description: str
    image_prompt: str

@dataclass
class Campsite:
    id: str
    region_id: str
    name: str
    location_desc: str
    features: List[str]
    type: str  # 'Z5', 'Capsule' 등
    
    # 신규 추가 속성 (Airbnb 스타일)
    rating: float = 0.0
    review_count: int = 0
    images: List[str] = field(default_factory=list)
    base_price_weekday: int = 50000  # 평일 기본가
    base_price_weekend: int = 150000 # 주말 기본가

    # 기존 로직 호환성 유지 (Deprecated 예정)
    price_half_day: int = 50000    # 오전/오후 4시간
    price_overnight: int = 150000  # 1박 2일

@dataclass
class MembershipProduct:
    id: str
    name: str
    price_monthly: int
    benefits: str

@dataclass
class Booking:
    id: str
    user_id: str
    campsite_id: str
    date: datetime.date
    time_slot: str  # 'AM', 'PM', 'OVERNIGHT'
    status: str     # 'CONFIRMED', 'CANCELLED'
    is_member: bool
    membership_type: str # 'NONE', 'SMART', 'ROYAL'
    payment_amount: int
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

# --- 시스템 클래스 ---
class TimeBankSystem:
    def __init__(self):
        self._regions = self._init_regions()
        self._campsites = self._init_campsites()
        self._memberships = self._init_memberships()
        self._bookings: List[Booking] = []
        self._init_dummy_bookings()
        
    def _init_regions(self) -> List[Region]:
        return [
            Region(
                id="R001", 
                name="경기 양평", 
                description="서울 근교, 숲속의 힐링 요새",
                image_prompt="Futuristic glamping site in Yangpyeong forest, morning sunlight, nature retreat, sci-fi caravan Z5"
            ),
            Region(
                id="R002", 
                name="강원 춘천", 
                description="호반의 도시, 물안개와 함께하는 아침",
                image_prompt="Futuristic glamping site near Chuncheon lake, fog, serene water reflection, house type caravan"
            ),
            Region(
                id="R003", 
                name="제주 애월", 
                description="에메랄드빛 바다와 현무암의 조화",
                image_prompt="Futuristic glamping site in Jeju Aewol, ocean cliff, basalt rocks, capsule caravan, sunset"
            ),
            Region(
                id="R004", 
                name="충남 태안", 
                description="서해 낙조와 갯벌 체험이 있는 곳",
                image_prompt="Futuristic glamping site in Taean beach, sunset, mudflat activities, mobile caravan"
            ),
        ]
        
    def _init_campsites(self) -> List[Campsite]:
        # 이미지 소스 (로컬 파일 및 외부 URL 혼합)
        # 팁: 로컬 이미지가 없으면 외부 URL을 fallback으로 사용하도록 UI에서 처리하거나 여기서 유효한 경로를 설정
        
        return [
            # 1. 양평 1호점 (Z5 우주선)
            Campsite(
                id="C001", 
                region_id="R001", 
                name="양평 1호점 (Z5 우주선)", 
                location_desc="경기 양평군 서종면 깊은 숲속, 자연과 기술의 조화", 
                features=["숲속 뷰", "프라이빗 데크", "AI 컨시어지", "Z5 모델"], 
                type="Z5 우주선",
                rating=4.98,
                review_count=128,
                images=[
                    "assets/img/caravan_side.png", # 로컬
                    "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=800&q=80", # 숲속 캠핑
                    "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=800&q=80"  # 밤하늘
                ],
                base_price_weekday=50000,
                base_price_weekend=150000
            ),
            # 2. 춘천 레이크뷰 (하우스형)
            Campsite(
                id="C002", 
                region_id="R002", 
                name="춘천 레이크뷰 (하우스형)", 
                location_desc="강원 춘천시 남산면 북한강변, 물안개 피어오르는 호수", 
                features=["리버 뷰", "수상 레저", "넓은 거실", "하우스형"], 
                type="하우스형",
                rating=4.85,
                review_count=85,
                images=[
                    "assets/img/caravan_exterior.png", # 로컬
                    "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=800&q=80", # 호수 캠핑
                    "https://images.unsplash.com/photo-1496080174650-637e3f22fa03?auto=format&fit=crop&w=800&q=80"  # 아침 안개
                ],
                base_price_weekday=50000,
                base_price_weekend=150000
            ),
            # 3. 제주 애월 스테이 (캡슐형)
            Campsite(
                id="C003", 
                region_id="R003", 
                name="제주 애월 스테이 (캡슐형)", 
                location_desc="제주 제주시 애월읍 해안도로, 바다 바로 앞", 
                features=["오션 뷰", "올레길 인접", "미니멀 라이프", "캡슐형"], 
                type="캡슐형",
                rating=4.92,
                review_count=210,
                images=[
                    "assets/img/caravan_interior.png", # 로컬 (내부)
                    "https://images.unsplash.com/photo-1510312305653-8ed496efae75?auto=format&fit=crop&w=800&q=80", # 제주 바다
                    "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=800&q=80"  # 리조트 느낌
                ],
                base_price_weekday=50000,
                base_price_weekend=150000
            ),
            # 4. 태안 오션 글램핑 (이동식)
            Campsite(
                id="C004", 
                region_id="R004", 
                name="태안 오션 글램핑 (이동식)", 
                location_desc="충남 태안군 안면읍 꽃지해수욕장, 황금빛 석양", 
                features=["낙조 전망", "갯벌 체험", "모빌리티", "이동식"], 
                type="이동식",
                rating=4.75,
                review_count=50,
                images=[
                    "assets/img/caravan_main.jpg", # 로컬
                    "https://images.unsplash.com/photo-1495954484750-af469f2f9be5?auto=format&fit=crop&w=800&q=80", # 석양
                    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80"  # 해변 리조트
                ],
                base_price_weekday=50000,
                base_price_weekend=150000
            ),
        ]

    def _init_memberships(self) -> List[MembershipProduct]:
        return [
            MembershipProduct(
                id="M_ROYAL",
                name="리조트 로얄",
                price_monthly=100000,
                benefits="연 60박 무료, 성수기 우선 예약"
            ),
            MembershipProduct(
                id="M_SMART",
                name="투지아 스마트",
                price_monthly=20000,
                benefits="평일 유휴시간(4h) 무료, 주말 3만원 정액"
            )
        ]

    def _init_dummy_bookings(self):
        """초기 데모용 예약 데이터 생성."""
        today = datetime.date.today()
        # 예약 1: 양평 1호점
        self.create_booking(
            user_id="demo_user",
            campsite_id="C001",
            date=today,
            time_slot="OVERNIGHT",
            is_member=True,
            membership_type="M_ROYAL",
            payment_amount=0
        )
        # 예약 2: 춘천 레이크뷰
        self.create_booking(
            user_id="demo_user",
            campsite_id="C002",
            date=today + datetime.timedelta(days=1),
            time_slot="PM",
            is_member=False,
            membership_type="NONE",
            payment_amount=50000
        )

    def get_regions(self) -> List[Region]:
        return self._regions
        
    def get_campsites_by_region(self, region_id: str) -> List[Campsite]:
        return [c for c in self._campsites if c.region_id == region_id]

    def get_all_campsites(self) -> List[Campsite]:
        """모든 캠핑장 목록 반환 (전체 검색용)"""
        return self._campsites

    def get_memberships(self) -> List[MembershipProduct]:
        return self._memberships

    def calculate_price(self, campsite: Campsite, is_member: bool, membership_type: str, time_slot: str, is_weekend: bool) -> int:
        """동적 가격 계산 로직 (Tujia 모델 반영)."""
        
        # 기본 가격 결정 (평일/주말)
        base_price = campsite.base_price_weekend if is_weekend else campsite.base_price_weekday
        
        # 1. 일반 회원 (비회원)
        if not is_member or membership_type == "NONE":
            if time_slot == "OVERNIGHT":
                return base_price
            else: # AM, PM (4시간 이용) - 단순화하여 박 가격의 1/3 수준 또는 고정값
                return 50000 # 시간당 요금제 또는 4시간 패키지 요금
        
        # 2. 멤버십 회원
        if membership_type == "M_ROYAL":
            # 로얄: 무료 (연 60박 차감 로직은 별도)
            return 0
            
        elif membership_type == "M_SMART":
            # 스마트: 
            # - 평일 4시간(AM/PM): 무료
            # - 주말 4시간(AM/PM) or 숙박: 30,000원 정액
            
            if is_weekend or time_slot == "OVERNIGHT":
                return 30000
            else:
                return 0 # 평일 시간제 무료
                
        return base_price # Fallback

    def calculate_roi(self, loan_amount: int, monthly_revenue: int) -> Dict[str, float]:
        """투자 수익률 계산."""
        interest_rate = 0.10
        operating_cost_ratio = 0.30
        
        monthly_interest = (loan_amount * interest_rate) / 12
        monthly_operating_cost = monthly_revenue * operating_cost_ratio
        
        net_profit = monthly_revenue - monthly_operating_cost - monthly_interest
        
        annual_profit = net_profit * 12
        roi_percent = (annual_profit / loan_amount) * 100 if loan_amount > 0 else 0
        
        return {
            "revenue": int(monthly_revenue),
            "operating_cost": int(monthly_operating_cost),
            "interest": int(monthly_interest),
            "net_profit": int(net_profit),
            "roi_percent": round(roi_percent, 1)
        }

    def create_booking(self, user_id: str, campsite_id: str, date: datetime.date, time_slot: str, 
                      is_member: bool, membership_type: str, payment_amount: int) -> Optional[Booking]:
        """예약 생성."""
        # 중복 체크
        for b in self._bookings:
            if b.campsite_id == campsite_id and b.date == date and b.time_slot == time_slot and b.status == "CONFIRMED":
                return None 
        
        new_booking = Booking(
            id=f"B{len(self._bookings)+1:04d}",
            user_id=user_id,
            campsite_id=campsite_id,
            date=date,
            time_slot=time_slot,
            status="CONFIRMED",
            is_member=is_member,
            membership_type=membership_type,
            payment_amount=payment_amount
        )
        self._bookings.append(new_booking)
        return new_booking

# 싱글톤 인스턴스
_system_instance = TimeBankSystem()

def get_system() -> TimeBankSystem:
    return _system_instance
