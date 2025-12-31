import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import { motion, AnimatePresence, useScroll, useTransform } from "framer-motion";
import { MapPin, Calendar, Users, Star, ArrowRight, X, Wifi, Coffee, Flame, Wind, ChevronRight } from "lucide-react";

// --- Mock Data ---
interface Campsite {
  id: string;
  name: string;
  region: string;
  location: string;
  price: number;
  rating: number;
  description: string;
  image: string;
  gallery: string[];
  amenities: string[];
  tags: string[];
}

const mockCampsites: Campsite[] = [
  {
    id: "1",
    name: "Moonlight Valley",
    region: "강원",
    location: "강원도 평창군 대관령면",
    price: 350000,
    rating: 4.9,
    description: "쏟아지는 별빛 아래, 최고급 에어스트림에서의 하룻밤. 프라이빗한 계곡과 숲이 어우러진 공간에서 진정한 휴식을 경험하세요.",
    image: "/images/curated/curated_1_gapyeong_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_1_gapyeong_dusk_1600x1200.png",
      "/images/curated/curated_1_gapyeong_dawn_1600x1200.png"
    ],
    amenities: ["wifi", "coffee", "fire", "ac"],
    tags: ["Luxury", "Stargazing", "Couple"]
  },
  {
    id: "2",
    name: "Ocean Cliff Edge",
    region: "제주",
    location: "제주특별자치도 서귀포시",
    price: 420000,
    rating: 4.8,
    description: "제주 남쪽 바다의 파도 소리를 들으며 잠드는 곳. 절벽 위 프라이빗 데크에서 바라보는 일몰은 잊지 못할 추억을 선사합니다.",
    image: "/images/curated/curated_2_yangpyeong_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_2_yangpyeong_dusk_1600x1200.png",
      "/images/curated/curated_2_yangpyeong_dawn_1600x1200.png"
    ],
    amenities: ["wifi", "coffee", "wind"],
    tags: ["Ocean View", "Healing", "Premium"]
  },
  {
    id: "3",
    name: "Forest Sanctuary",
    region: "경기",
    location: "경기도 가평군 북면",
    price: 280000,
    rating: 4.7,
    description: "서울에서 1시간, 울창한 잣나무 숲속의 비밀 요새. 빈티지 카라반의 감성과 호텔급 어메니티의 완벽한 조화.",
    image: "/images/curated/curated_3_jeju_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_3_jeju_dusk_1600x1200.png",
      "/images/curated/curated_3_jeju_dawn_1600x1200.png"
    ],
    amenities: ["fire", "coffee", "ac"],
    tags: ["Forest", "Vintage", "BBQ"]
  },
  {
    id: "4",
    name: "Sunset Lake",
    region: "충청",
    location: "충청북도 충주시",
    price: 310000,
    rating: 4.8,
    description: "잔잔한 호수 위로 비치는 노을을 감상하며 즐기는 카라반 캠핑. 수상 레저와 함께 역동적인 낮과 고요한 밤을 모두 즐기세요.",
    image: "/images/curated/curated_4_pocheon_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_4_pocheon_dusk_1600x1200.png",
      "/images/curated/curated_4_pocheon_dawn_1600x1200.png"
    ],
    amenities: ["wifi", "fire"],
    tags: ["Lake", "Activity", "Family"]
  },
  {
    id: "5",
    name: "Nomad's Desert",
    region: "경상",
    location: "경상북도 경주시",
    price: 380000,
    rating: 4.9,
    description: "이국적인 사막 분위기의 글램핑 사이트. 밤이 되면 쏟아지는 별과 함께 모닥불을 피우며 낭만적인 시간을 보내세요.",
    image: "/images/curated/curated_5_taean_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_5_taean_dusk_1600x1200.png",
      "/images/curated/curated_5_taean_dawn_1600x1200.png"
    ],
    amenities: ["fire", "coffee", "wind", "ac"],
    tags: ["Exotic", "Photo", "Glamping"]
  },
  {
    id: "6",
    name: "Cloud 9 High",
    region: "강원",
    location: "강원도 정선군",
    price: 450000,
    rating: 5.0,
    description: "해발 800m 고지대에서 구름을 내려다보는 환상적인 뷰. 최고급 모터홈이 제공하는 럭셔리한 편안함.",
    image: "/images/curated/curated_6_gangneung_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_6_gangneung_dusk_1600x1200.png",
      "/images/curated/curated_6_gangneung_dawn_1600x1200.png"
    ],
    amenities: ["wifi", "coffee", "ac", "fire"],
    tags: ["Mountain", "Luxury", "Silence"]
  }
];

const curatedLocalById: Record<string, { image: string; gallery: string[] }> = {
  "1": {
    image: "/images/curated/curated_1_gapyeong_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_1_gapyeong_dusk_1600x1200.png",
      "/images/curated/curated_1_gapyeong_dawn_1600x1200.png",
    ],
  },
  "2": {
    image: "/images/curated/curated_2_yangpyeong_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_2_yangpyeong_dusk_1600x1200.png",
      "/images/curated/curated_2_yangpyeong_dawn_1600x1200.png",
    ],
  },
  "3": {
    image: "/images/curated/curated_3_jeju_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_3_jeju_dusk_1600x1200.png",
      "/images/curated/curated_3_jeju_dawn_1600x1200.png",
    ],
  },
  "4": {
    image: "/images/curated/curated_4_pocheon_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_4_pocheon_dusk_1600x1200.png",
      "/images/curated/curated_4_pocheon_dawn_1600x1200.png",
    ],
  },
  "5": {
    image: "/images/curated/curated_5_taean_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_5_taean_dusk_1600x1200.png",
      "/images/curated/curated_5_taean_dawn_1600x1200.png",
    ],
  },
  "6": {
    image: "/images/curated/curated_6_gangneung_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_6_gangneung_dusk_1600x1200.png",
      "/images/curated/curated_6_gangneung_dawn_1600x1200.png",
    ],
  },
  "7": {
    image: "/images/curated/curated_7_sokcho_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_7_sokcho_dusk_1600x1200.png",
      "/images/curated/curated_7_sokcho_dawn_1600x1200.png",
    ],
  },
  "8": {
    image: "/images/curated/curated_8_yeosu_dusk_1600x1200.png",
    gallery: [
      "/images/curated/curated_8_yeosu_dusk_1600x1200.png",
      "/images/curated/curated_8_yeosu_dawn_1600x1200.png",
    ],
  },
};

const patchToLocalImages = (site: Campsite): Campsite => {
  const curated = curatedLocalById[site.id];
  if (!curated) return site;

  const currentImage = (site.image || "").trim();
  const shouldReplaceImage = currentImage === "" || /^https?:\/\//i.test(currentImage);

  const gallery = Array.isArray(site.gallery) ? site.gallery : [];
  const shouldReplaceGallery =
    gallery.length === 0 || gallery.some((g) => /^https?:\/\//i.test((g || "").trim()));

  return {
    ...site,
    image: shouldReplaceImage ? curated.image : site.image,
    gallery: shouldReplaceGallery ? curated.gallery : gallery,
  };
};

const regions = ["전체", "경기", "강원", "충청", "경상", "전라", "제주"];

// --- Icons Helper ---
const getAmenityIcon = (name: string) => {
  switch (name) {
    case "wifi": return <Wifi className="w-4 h-4" />;
    case "coffee": return <Coffee className="w-4 h-4" />;
    case "fire": return <Flame className="w-4 h-4" />;
    case "wind": return <Wind className="w-4 h-4" />;
    case "ac": return <span className="text-xs font-bold">AC</span>;
    default: return <Star className="w-4 h-4" />;
  }
};

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('ko-KR').format(price);
};

// --- Components ---

const Navbar = ({ isScrolled }: { isScrolled: boolean }) => (
  <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${isScrolled ? 'bg-black/80 backdrop-blur-md py-4 border-b border-white/10' : 'bg-transparent py-6'}`}>
    <div className="container mx-auto px-6 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-white text-black flex items-center justify-center font-serif font-bold text-xl rounded-sm">T</div>
        <span className="text-2xl font-serif tracking-widest font-bold text-white">TIMEBANK</span>
      </div>
      <div className="hidden md:flex gap-8 text-sm tracking-widest font-light text-gray-300">
        <a href="#" className="hover:text-white transition-colors">DESTINATIONS</a>
        <a href="#" className="hover:text-white transition-colors">EXPERIENCES</a>
        <a href="#" className="hover:text-white transition-colors">OUR FLEET</a>
        <a href="#" className="hover:text-white transition-colors">JOURNAL</a>
      </div>
      <button className="px-6 py-2 border border-white/30 hover:bg-white hover:text-black transition-all duration-300 text-xs tracking-widest uppercase rounded-sm">
        Login
      </button>
    </div>
  </nav>
);

const Hero = () => {
  const videoSources = [
    "/videos/danyang_sunrise.mp4",
    "/videos/gapyeong_foggy_river.mp4",
    "/videos/sanjeong_walking.mp4",
  ];
  const [videoIndex, setVideoIndex] = useState(0);

  return (
    <div className="relative h-screen w-full overflow-hidden">
      {/* Video Background */}
      <div className="absolute inset-0">
        <video
          autoPlay
          muted
          loop={false}
          playsInline
          className="w-full h-full object-cover opacity-60"
          key={videoSources[videoIndex]}
          onEnded={() => setVideoIndex((prev) => (prev + 1) % videoSources.length)}
        >
          <source src={videoSources[videoIndex]} type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-[#0f1110]"></div>
      </div>

      <div className="relative z-10 h-full flex flex-col justify-center items-center text-center px-4">
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="text-gold-400 text-sm md:text-base tracking-[0.3em] uppercase mb-6 text-[#d4af37]"
        >
          Premium Camping Experience
        </motion.p>
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="text-5xl md:text-7xl lg:text-9xl font-serif text-white mb-8 leading-tight"
        >
          Discover <br /> The Wild
        </motion.h1>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="w-full max-w-4xl glass rounded-full p-2 flex flex-col md:flex-row items-center justify-between gap-2 mt-8 shadow-2xl"
        >
          <div className="flex-1 w-full px-6 py-3 border-r border-white/10 flex flex-col items-start hover:bg-white/5 transition-colors rounded-full cursor-pointer group">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Location</span>
            <div className="flex items-center gap-2 text-white group-hover:text-[#d4af37] transition-colors">
              <MapPin className="w-4 h-4" />
              <span className="font-light">어디로 떠나시나요?</span>
            </div>
          </div>
          <div className="flex-1 w-full px-6 py-3 border-r border-white/10 flex flex-col items-start hover:bg-white/5 transition-colors rounded-full cursor-pointer group">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Check In - Out</span>
            <div className="flex items-center gap-2 text-white group-hover:text-[#d4af37] transition-colors">
              <Calendar className="w-4 h-4" />
              <span className="font-light">날짜 선택</span>
            </div>
          </div>
          <div className="flex-1 w-full px-6 py-3 flex flex-col items-start hover:bg-white/5 transition-colors rounded-full cursor-pointer group">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Guests</span>
            <div className="flex items-center gap-2 text-white group-hover:text-[#d4af37] transition-colors">
              <Users className="w-4 h-4" />
              <span className="font-light">성인 2, 아동 0</span>
            </div>
          </div>
          <button className="bg-[#d4af37] hover:bg-[#b5952f] text-black font-semibold rounded-full w-full md:w-auto md:aspect-square md:h-14 md:px-0 px-8 py-4 flex items-center justify-center transition-all duration-300 hover:scale-105">
             <ArrowRight className="w-6 h-6" />
          </button>
        </motion.div>
      </div>
    </div>
  );
};

const ImageMarquee = () => {
  const images = [
    "/images/moments/gapyeong_campsite_1_20251231_125909.png",
    "/images/moments/jeju_campsite_3_20251231_125954.png",
    "/images/moments/pocheon_campsite_4_20251231_130014.png",
    "/images/moments/gangneung_campsite_7_20251231_130111.png",
    "/images/moments/yeosu_campsite_8_20251231_130132.png"
  ];

  return (
    <div className="w-full py-10 bg-[#0f1110] overflow-hidden flex flex-col gap-4">
       <div className="container mx-auto px-6 mb-2">
         <h3 className="text-gray-500 text-xs tracking-[0.2em] uppercase">Moments in Nature</h3>
       </div>
       <div className="flex w-[200%]">
          <motion.div 
            className="flex gap-4"
            animate={{ x: [0, -1000] }}
            transition={{ repeat: Infinity, duration: 40, ease: "linear" }}
          >
            {[...images, ...images, ...images].map((src, i) => (
              <div key={i} className="relative w-64 h-40 md:w-80 md:h-52 rounded-sm overflow-hidden flex-shrink-0 group cursor-pointer grayscale hover:grayscale-0 transition-all duration-700">
                <img src={src} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" alt="camping mood" />
                <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors"></div>
              </div>
            ))}
          </motion.div>
       </div>
    </div>
  );
};

const CampsiteModal = ({ site, onClose }: { site: Campsite | null, onClose: () => void }) => {
  if (!site) return null;

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8"
      >
        <div className="absolute inset-0 bg-black/90 backdrop-blur-sm" onClick={onClose}></div>
        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          className="relative w-full max-w-5xl h-[90vh] bg-[#1a1a1a] rounded-lg overflow-hidden flex flex-col md:flex-row shadow-2xl border border-white/10"
        >
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 z-20 p-2 bg-black/50 hover:bg-white hover:text-black rounded-full transition-all text-white"
          >
            <X className="w-6 h-6" />
          </button>

          {/* Left: Image Gallery */}
          <div className="w-full md:w-1/2 h-48 md:h-full relative group">
             <img src={site.image} alt={site.name} className="w-full h-full object-cover" />
             <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-8">
                <div className="flex gap-2 mb-2">
                  {site.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-white/10 backdrop-blur-md text-[10px] uppercase tracking-wider text-white border border-white/20">
                      {tag}
                    </span>
                  ))}
                </div>
                <h2 className="text-4xl font-serif text-white mb-1">{site.name}</h2>
                <p className="text-gray-300 flex items-center gap-1 text-sm"><MapPin className="w-3 h-3" /> {site.location}</p>
             </div>
          </div>

          {/* Right: Details */}
          <div className="w-full md:w-1/2 h-full overflow-y-auto p-8 bg-[#1a1a1a] text-gray-200">
             <div className="flex justify-between items-start mb-8">
               <div>
                  <h3 className="text-sm text-[#d4af37] uppercase tracking-widest mb-2">Overview</h3>
                  <div className="flex items-center gap-1 text-yellow-500">
                    <Star className="w-4 h-4 fill-current" />
                    <span className="text-lg font-medium text-white">{site.rating}</span>
                    <span className="text-gray-500 text-sm">/ 5.0 (124 reviews)</span>
                  </div>
               </div>
               <div className="text-right">
                 <p className="text-sm text-gray-400">1박 요금</p>
                 <p className="text-3xl font-serif text-white">₩{formatPrice(site.price)}</p>
               </div>
             </div>

             <div className="mb-8">
               <h4 className="text-xl font-serif text-white mb-4">About this place</h4>
               <p className="font-light leading-relaxed text-gray-400">
                 {site.description} <br/><br/>
                 자연 그대로의 모습을 간직한 {site.name}에서 특별한 하루를 보내세요.
                 현대적인 편리함과 아날로그 감성이 공존하는 공간입니다.
               </p>
             </div>

             <div className="mb-8">
                <h4 className="text-xl font-serif text-white mb-4">Amenities</h4>
                <div className="grid grid-cols-2 gap-4">
                  {site.amenities.map(item => (
                    <div key={item} className="flex items-center gap-3 p-3 rounded bg-white/5 border border-white/5">
                      <span className="text-gray-300">{getAmenityIcon(item)}</span>
                      <span className="text-sm capitalize">{item}</span>
                    </div>
                  ))}
                </div>
             </div>

             <div className="mt-auto border-t border-white/10 pt-8">
               <button className="w-full py-4 bg-[#d4af37] text-black font-bold uppercase tracking-widest hover:bg-[#b5952f] transition-colors flex items-center justify-center gap-2">
                 Reserve Now <ChevronRight className="w-4 h-4" />
               </button>
               <p className="text-center text-xs text-gray-500 mt-4">예약 확정 시 안내 문자가 발송됩니다.</p>
             </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const App = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState("전체");
  const [selectedSite, setSelectedSite] = useState<Campsite | null>(null);
  const [campsites, setCampsites] = useState<Campsite[]>(mockCampsites.map(patchToLocalImages));

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/uwuseon_campsites.json", { cache: "no-store" });
        if (!res.ok) return;
        const json = (await res.json()) as Campsite[];
        if (Array.isArray(json) && json.length > 0) {
          setCampsites(json.map(patchToLocalImages));
        }
      } catch {
        // keep local mockCampsites
      }
    };
    load();
  }, []);

  const filteredCampsites = selectedRegion === "전체" 
    ? campsites 
    : campsites.filter(site => site.region === selectedRegion);

  return (
    <div className="min-h-screen bg-[#0f1110] text-gray-200 selection:bg-[#d4af37] selection:text-black">
      <Navbar isScrolled={isScrolled} />
      
      <Hero />
      
      <ImageMarquee />

      <main className="container mx-auto px-6 py-20">
        <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
          <div>
            <h2 className="text-4xl md:text-5xl font-serif text-white mb-4">
              Curated <span className="text-[#d4af37] italic">Sanctuaries</span>
            </h2>
            <p className="text-gray-400 font-light max-w-lg">
              엄선된 프리미엄 캠핑 스팟. 자연 속에서의 완벽한 고립을 경험하세요.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {regions.map(region => (
              <button
                key={region}
                onClick={() => setSelectedRegion(region)}
                className={`px-4 py-2 text-sm transition-all duration-300 border rounded-full ${
                  selectedRegion === region 
                    ? "border-[#d4af37] text-[#d4af37] bg-[#d4af37]/10" 
                    : "border-white/10 text-gray-500 hover:border-white/30 hover:text-gray-300"
                }`}
              >
                {region}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredCampsites.map((site, index) => (
            <motion.div
              key={site.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              onClick={() => setSelectedSite(site)}
              className="group cursor-pointer"
            >
              <div className="relative aspect-[4/3] overflow-hidden rounded-lg mb-4">
                <div className="absolute top-4 right-4 z-10 px-3 py-1 bg-black/40 backdrop-blur-md text-white text-xs font-medium border border-white/10 rounded-full flex items-center gap-1">
                  <Star className="w-3 h-3 fill-[#d4af37] text-[#d4af37]" /> {site.rating}
                </div>
                <img 
                  src={site.image} 
                  alt={site.name} 
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute bottom-6 left-6 right-6 flex justify-between items-end">
                    <span className="px-4 py-2 bg-white text-black text-sm font-bold uppercase tracking-wider flex items-center gap-2">
                       View Details <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-between items-start">
                <div>
                   <h3 className="text-xl font-serif text-white group-hover:text-[#d4af37] transition-colors">{site.name}</h3>
                   <p className="text-sm text-gray-500 mt-1">{site.location}</p>
                </div>
                <div className="text-right">
                   <p className="text-lg font-medium text-white">₩{formatPrice(site.price)}</p>
                   <p className="text-xs text-gray-500">per night</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredCampsites.length === 0 && (
          <div className="text-center py-20 text-gray-500 font-light">
            해당 지역에는 예약 가능한 캠핑장이 없습니다.
          </div>
        )}
      </main>

      <footer className="bg-[#0a0a0a] border-t border-white/5 py-20">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-start gap-12">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <div className="w-6 h-6 bg-white text-black flex items-center justify-center font-serif font-bold text-sm rounded-sm">T</div>
                <span className="text-xl font-serif tracking-widest font-bold text-white">TIMEBANK</span>
              </div>
              <p className="text-gray-500 text-sm max-w-xs leading-relaxed">
                자연과 가장 가까운 곳에서의 하룻밤.<br/>
                우리는 단순한 숙박이 아닌, 잊지 못할 경험을 제공합니다.
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-12 text-sm">
              <div>
                <h4 className="text-white font-serif mb-4">Company</h4>
                <ul className="space-y-2 text-gray-500">
                  <li><a href="#" className="hover:text-[#d4af37]">About Us</a></li>
                  <li><a href="#" className="hover:text-[#d4af37]">Careers</a></li>
                  <li><a href="#" className="hover:text-[#d4af37]">Press</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-serif mb-4">Support</h4>
                <ul className="space-y-2 text-gray-500">
                  <li><a href="#" className="hover:text-[#d4af37]">Contact</a></li>
                  <li><a href="#" className="hover:text-[#d4af37]">Terms</a></li>
                  <li><a href="#" className="hover:text-[#d4af37]">Privacy</a></li>
                </ul>
              </div>
            </div>
          </div>
          <div className="mt-20 pt-8 border-t border-white/5 text-center text-xs text-gray-600">
            &copy; 2024 TIMEBANK Inc. All rights reserved.
          </div>
        </div>
      </footer>

      {/* Modal Overlay */}
      <CampsiteModal site={selectedSite} onClose={() => setSelectedSite(null)} />
    </div>
  );
};

const root = createRoot(document.getElementById("root"));
root.render(<App />);