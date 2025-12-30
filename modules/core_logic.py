"""TimeBank 핵심 비즈니스 로직.

- 데이터 모델: Region > Campsite > Unit
- 예약 관리 및 ROI 계산
- 시스템 초기화 (Mock Data: 5대 랜드마크 포함)
- Viral Marketing Logic (공유 점장, 포인트 시스템) 포함
"""

import datetime
import uuid
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

# --- 데이터 모델 ---
@dataclass
class Unit:
    id: str
    name: str
    price: int
    max_guests: int
    rating: float
    image: str
    tags: List[str]

@dataclass
class Campsite:
    id: str
    region_id: str
    name: str
    description: str
    units: List[Unit]
    location_desc: str = ""
    features: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    base_price_weekday: int = 0  # ui/booking.py에서 참조하는 필드 추가
    review_count: int = 0        # ui/booking.py에서 참조하는 필드 추가
    rating: float = 0.0          # ui/booking.py에서 참조하는 필드 추가

@dataclass
class Region:
    id: str
    name: str
    description: str
    image: str # Representative image

@dataclass
class User:
    id: str
    name: str
    email: str
    is_member: bool = False
    points: int = 0
    invite_code: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    referral_count: int = 0
    total_earnings: int = 0 # 총 누적 수익 (포인트)

@dataclass
class Booking:
    id: str
    unit_id: str
    user_id: str
    check_in: datetime.date
    check_out: datetime.date
    guests: int
    original_price: int
    final_price: int
    used_points: int = 0
    earned_points: int = 0
    invite_code_used: Optional[str] = None
    status: str = "CONFIRMED"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

# --- 시스템 클래스 ---
class TimeBankSystem:
    def __init__(self):
        self._bookings: List[Booking] = []
        self._regions: List[Region] = []
        self._all_campsites: List[Campsite] = []
        self._users: Dict[str, User] = {} # Mock User Database
        self._init_data()
        self._init_mock_users()

    def _init_mock_users(self):
        """테스트용 사용자 초기화"""
        # 데모 유저 생성
        demo_user = User(id="demo_user", name="김타임", email="demo@timebank.com")
        self._users["demo_user"] = demo_user

    def _init_data(self):
        """5대 랜드마크 Mock Data 초기화"""
        
        # 1. Region 정의
        regions = {
            "r_pocheon": Region("r_pocheon", "포천", "비행 기지와 호수의 조화", "assets/img/KakaoTalk_20251220_140745850_08.jpg"),
            "r_gapyeong": Region("r_gapyeong", "가평", "깊은 숲속의 힐링", "assets/img/custom_20251229_072946.png"),
            "r_yangpyeong": Region("r_yangpyeong", "양평", "강변의 럭셔리", "assets/img/KakaoTalk_20251220_140745850_11.jpg"),
            "r_jeju": Region("r_jeju", "제주", "밤하늘과 우주선", "assets/img/KakaoTalk_20251220_140745850_06.jpg"),
            "r_taean": Region("r_taean", "태안", "바다 위 선셋 글램핑", "assets/img/KakaoTalk_20251220_140745850_07.jpg"),
        }
        self._regions = list(regions.values())

        # 2. Campsites & Units 정의

        # (1) 포천 산정호수 (The Base)
        units_pocheon = [
            Unit(id="u_pc_01", name="더 베이스 A동", price=350000, max_guests=4, rating=4.9, image="assets/img/KakaoTalk_20251220_140745850_08.jpg", tags=["호수뷰", "스파", "SF컨셉"]),
            Unit(id="u_pc_02", name="더 베이스 B동", price=280000, max_guests=2, rating=4.8, image="assets/img/caravan_interior.png", tags=["커플", "넷플릭스"])
        ]
        self._all_campsites.append(Campsite(
            id="c_pocheon", region_id="r_pocheon", name="포천 산정호수 (The Base)", 
            description="숲속 비행 기지 컨셉의 럭셔리 스테이", units=units_pocheon,
            location_desc="경기도 포천시 영북면 산정호수로", features=["수상레저", "비행기지컨셉"], images=["assets/img/KakaoTalk_20251220_140745850_08.jpg"],
            base_price_weekday=280000, review_count=128, rating=4.9
        ))

        # (2) 가평 아침고요 (Deep Forest)
        units_gapyeong = [
            Unit(id="u_gp_01", name="딥 포레스트 1호", price=420000, max_guests=6, rating=4.9, image="assets/img/custom_20251229_072946.png", tags=["숲속", "독채", "불멍"]),
        ]
        self._all_campsites.append(Campsite(
            id="c_gapyeong", region_id="r_gapyeong", name="가평 아침고요 (Deep Forest)", 
            description="착륙하는 우주선 컨셉의 프라이빗 빌라", units=units_gapyeong,
            location_desc="경기도 가평군 상면 수목원로", features=["수목원", "피톤치드"], images=["assets/img/custom_20251229_072946.png"],
            base_price_weekday=420000, review_count=85, rating=4.9
        ))

        # (3) 양평 리버사이드 (Water Front)
        units_yangpyeong = [
            Unit(id="u_yp_01", name="워터 프론트 스위트", price=380000, max_guests=4, rating=4.7, image="assets/img/KakaoTalk_20251220_140745850_11.jpg", tags=["리버뷰", "인피니티풀"]),
        ]
        self._all_campsites.append(Campsite(
            id="c_yangpyeong", region_id="r_yangpyeong", name="양평 리버사이드 (Water Front)", 
            description="강변에 정박한 우주선", units=units_yangpyeong,
            location_desc="경기도 양평군 서종면", features=["수상스키", "바베큐"], images=["assets/img/KakaoTalk_20251220_140745850_11.jpg"],
            base_price_weekday=380000, review_count=210, rating=4.7
        ))

        # (4) 제주 애월 스테이 (Night View)
        units_jeju = [
            Unit(id="u_jj_01", name="나이트 뷰 오션", price=550000, max_guests=4, rating=5.0, image="assets/img/KakaoTalk_20251220_140745850_06.jpg", tags=["오션뷰", "천문대"]),
        ]
        self._all_campsites.append(Campsite(
            id="c_jeju", region_id="r_jeju", name="제주 애월 스테이 (Night View)", 
            description="제주 밤바다와 우주선의 만남", units=units_jeju,
            location_desc="제주특별자치도 제주시 애월읍", features=["오션뷰", "별관측"], images=["assets/img/KakaoTalk_20251220_140745850_06.jpg"],
            base_price_weekday=550000, review_count=340, rating=5.0
        ))

        # (5) 태안 오션 글램핑 (Sunset)
        units_taean = [
            Unit(id="u_ta_01", name="선셋 글램핑 A", price=300000, max_guests=4, rating=4.8, image="assets/img/KakaoTalk_20251220_140745850_07.jpg", tags=["일몰", "갯벌체험"]),
        ]
        self._all_campsites.append(Campsite(
            id="c_taean", region_id="r_taean", name="태안 오션 글램핑 (Sunset)", 
            description="서해 낙조와 함께하는 감성 캠핑", units=units_taean,
            location_desc="충청남도 태안군 안면읍", features=["해수욕장", "낙조"], images=["assets/img/KakaoTalk_20251220_140745850_07.jpg"],
            base_price_weekday=300000, review_count=150, rating=4.8
        ))


    def get_regions(self) -> List[Region]:
        return self._regions

    def get_campsites_by_region(self, region_name: str) -> List[Campsite]:
        if region_name == "지도 전체":
            return self._all_campsites
        target_region = next((r for r in self._regions if r.name == region_name), None)
        if not target_region:
            return []
        return [c for c in self._all_campsites if c.region_id == target_region.id]
    
    def get_all_campsites(self) -> List[Campsite]:
        return self._all_campsites

    def get_all_units(self) -> List[Unit]:
        units = []
        for c in self._all_campsites:
            units.extend(c.units)
        return units
    
    def find_unit_by_id(self, unit_id: str) -> Optional[Unit]:
        for c in self._all_campsites:
            for u in c.units:
                if u.id == unit_id:
                    return u
        return None

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def join_membership(self, user_id: str, plan_price: int = 50000):
        """멤버십 가입 및 포인트 지급 로직"""
        user = self._users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.is_member:
            return # Already member
            
        # 1. 실제로는 여기서 PG 결제 로직 수행 (50,000원)
        
        # 2. 멤버십 활성화 및 포인트 지급 (즉시 페이백)
        user.is_member = True
        user.points += plan_price
        
    def find_user_by_invite_code(self, code: str) -> Optional[User]:
        for user in self._users.values():
            if user.invite_code == code:
                return user
        return None

    def calculate_price(self, campsite_or_unit, is_member: bool, membership_type: str, time_slot: str, is_weekend: bool) -> int:
        """가격 계산 로직 (기존 booking.py 로직 이관)"""
        # campsite_or_unit 처리
        base_price = 0
        if isinstance(campsite_or_unit, Campsite):
             base_price = campsite_or_unit.base_price_weekday
        elif isinstance(campsite_or_unit, Unit):
             base_price = campsite_or_unit.price
        
        # 주말 할증 (20%)
        if is_weekend:
            base_price = int(base_price * 1.2)
            
        # 시간대별 조정
        # time_slot: AM(0.5), PM(0.6), OVERNIGHT(1.0)
        multiplier = 1.0
        if time_slot == "AM":
            multiplier = 0.5
        elif time_slot == "PM":
            multiplier = 0.6
        elif time_slot == "OVERNIGHT":
            multiplier = 1.0
            
        final_price = int(base_price * multiplier)

        # 멤버십 할인 (100% 할인 = 0원)
        if is_member:
            final_price = 0
            
        return final_price

    def create_booking(self, unit_id: str, user_id: str, check_in: datetime.date, check_out: datetime.date, guests: int, 
                       used_points: int = 0, invite_code: str = None, 
                       # 하위 호환 및 booking.py 파라미터 맞춤
                       campsite_id: str = None, time_slot: str = None, is_member: bool = False, membership_type: str = None, payment_amount: int = None
                       ) -> Booking:
        
        user = self._users.get(user_id)
        # 데모 유저가 없으면 생성 (booking.py의 "current_user" 대응)
        if not user and user_id == "current_user":
             user = User(id="current_user", name="게스트", email="guest@timebank.com")
             self._users["current_user"] = user

        if not user:
             # Fallback
             user = self._users.get("demo_user")
             if not user:
                raise ValueError("User not found")
             user_id = user.id

        # Unit or Campsite ID resolution
        target_unit = None
        if unit_id:
            target_unit = self.find_unit_by_id(unit_id)
        
        # Campsite ID로 들어온 경우 첫 번째 Unit 선택 (간소화)
        if not target_unit and campsite_id:
            for c in self._all_campsites:
                if c.id == campsite_id:
                    if c.units:
                        target_unit = c.units[0]
                    break
        
        if not target_unit:
             # Mock Unit if needed or raise error
             # raise ValueError("Unit not found")
             pass 

        # 1. 가격 계산
        if payment_amount is not None:
            final_price = payment_amount
            original_price = payment_amount # 추정
        elif target_unit:
            original_price = target_unit.price
            final_price = original_price
        else:
            original_price = 0
            final_price = 0

        inviter_user = None
        
        # 2. 초대 코드 할인 적용 (5%)
        if invite_code:
            inviter_user = self.find_user_by_invite_code(invite_code)
            if inviter_user and inviter_user.id != user_id:
                discount = int(original_price * 0.05)
                final_price -= discount
            else:
                 invite_code = None

        # 3. 포인트 사용
        if used_points > 0:
            if user.points >= used_points:
                final_price -= used_points
                if final_price < 0:
                    used_points += final_price 
                    final_price = 0
                user.points -= used_points
            else:
                raise ValueError("Not enough points")
        
        # 4. 예약 생성
        booking = Booking(
            id=f"bk_{len(self._bookings)+1}",
            unit_id=unit_id if unit_id else (campsite_id if campsite_id else "unknown"),
            user_id=user_id,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            original_price=original_price,
            final_price=final_price,
            used_points=used_points,
            earned_points=0,
            invite_code_used=invite_code
        )
        
        # 5. 리워드 로직
        if final_price > 0:
            reward_points = int(final_price * 0.05)
            user.points += reward_points
            booking.earned_points = reward_points
            
            if inviter_user:
                referral_reward = int(final_price * 0.10)
                inviter_user.points += referral_reward
                inviter_user.referral_count += 1
                inviter_user.total_earnings += referral_reward

        self._bookings.append(booking)
        return booking

# 싱글톤 인스턴스
_system_instance = TimeBankSystem()

def get_system() -> TimeBankSystem:
    return _system_instance
