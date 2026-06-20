"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface User {
  phone_number: string;
  nom: string | null;
  prenom: string | null;
  age: number | null;
  niveau: string | null;
  ville: string | null;
  quartier: string | null;
  taille: number | null;
  categorie: string | null;
  sport_prefere: string | null;
  is_registered: boolean;
}

interface Venue {
  id: string;
  name: string;
  address: string;
  city: string;
  neighborhood: string;
  google_maps_url?: string;
}

interface MatchParticipant {
  match_id: string;
  user_id: string;
  status: string;
  user: User;
}

interface Match {
  id: string;
  sport: string;
  match_time: string;
  venue_id: string;
  max_players: number;
  status: string;
  venue?: Venue;
  participants?: MatchParticipant[];
  is_paid?: boolean;
  price?: number;
}

export default function Discover() {
  const router = useRouter();
  const [sportSearch, setSportSearch] = useState("");
  const [locationSearch, setLocationSearch] = useState("");
  const [players, setPlayers] = useState<User[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  // Set page-discover class on body
  useEffect(() => {
    document.body.classList.add("page-discover");
    document.body.classList.remove("page-profile", "page-activities");
    return () => {
      document.body.classList.remove("page-discover");
    };
  }, []);

  // Fetch real data from backend
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch matches
        const mRes = await fetch(`${API_URL}/matches`);
        if (mRes.ok) {
          const mData = await mRes.json();
          const matchesWithParts = await Promise.all(
            mData.map(async (m: Match) => {
              const pRes = await fetch(`${API_URL}/matches/${m.id}/participants`);
              if (pRes.ok) {
                m.participants = await pRes.json();
              }
              return m;
            })
          );
          setMatches(matchesWithParts);
        }

        // Fetch users
        const uRes = await fetch(`${API_URL}/users`);
        if (uRes.ok) {
          const uData = await uRes.json();
          setPlayers(uData.filter((u: User) => u.is_registered));
        }
      } catch (e) {
        console.error("Error fetching discover data:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter lists based on search terms
  const filteredMatches = matches.filter((m) => {
    const matchesSport = !sportSearch || m.sport.toLowerCase().includes(sportSearch.toLowerCase());
    const matchesLoc = !locationSearch || 
      (m.venue?.neighborhood.toLowerCase().includes(locationSearch.toLowerCase())) ||
      (m.venue?.city.toLowerCase().includes(locationSearch.toLowerCase()));
    return matchesSport && matchesLoc;
  });

  const filteredPlayers = players.filter((p) => {
    const matchesSport = !sportSearch || (p.sport_prefere && p.sport_prefere.toLowerCase().includes(sportSearch.toLowerCase()));
    const matchesLoc = !locationSearch || 
      (p.quartier && p.quartier.toLowerCase().includes(locationSearch.toLowerCase())) ||
      (p.ville && p.ville.toLowerCase().includes(locationSearch.toLowerCase()));
    return matchesSport && matchesLoc;
  });

  // Mock static data to serve as high-quality fallbacks matching the layout
  const mockActivities = [
    {
      id: "mock-1",
      sport: "Tennis",
      title: "Match amical 1v1",
      location: "Central Park Court 4, 18:00",
      bgImage: "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?auto=format&fit=crop&w=500&q=80",
      avatars: [
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK"
      ]
    },
    {
      id: "mock-2",
      sport: "Running",
      title: "Footing 10km Chill",
      location: "Bords de Seine, 19:30",
      bgImage: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=500&q=80",
      avatars: [
        "https://lh3.googleusercontent.com/aida-public/AB6AXuDpwCSBiNaFvWF_WGe1Vc3SHEOI9Kt0eFdzAQcA4SY9cxaw5B8SMXyCwxS6nGMbPRcFa36bE9ejpblEjfiMJYUcPHeBRgnSfkDbRn-5IVS2L6eBkmS1kgGEvD4hy6CR0WTpGtGk_4v-1ceYDhq3URMdFNsb7G28FBZ7O1vIn1-tBpT_f0A76vP_onn1nTYOKPvY3NGK2gxVJkrdF1-AkvGYxJy_PJyx_liFTK7HEK6uGyD9ZKmX6c8FCrftu8K9ElN90HfPy1b9yi6t",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK"
      ]
    },
    {
      id: "mock-3",
      sport: "Padel",
      title: "Padel Intermédiaire",
      location: "Urban Sports Center, 12:00",
      bgImage: "https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=500&q=80",
      avatars: [
        "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK",
        "https://lh3.googleusercontent.com/aida-public/AB6AXuDpwCSBiNaFvWF_WGe1Vc3SHEOI9Kt0eFdzAQcA4SY9cxaw5B8SMXyCwxS6nGMbPRcFa36bE9ejpblEjfiMJYUcPHeBRgnSfkDbRn-5IVS2L6eBkmS1kgGEvD4hy6CR0WTpGtGk_4v-1ceYDhq3URMdFNsb7G28FBZ7O1vIn1-tBpT_f0A76vP_onn1nTYOKPvY3NGK2gxVJkrdF1-AkvGYxJy_PJyx_liFTK7HEK6uGyD9ZKmX6c8FCrftu8K9ElN90HfPy1b9yi6t"
      ]
    }
  ];

  const mockPartners = [
    {
      name: "Léa",
      age: 26,
      city: "Paris, FR",
      sports: ["YOGA", "RUNNING"],
      level: "INTERMÉDIAIRE",
      phone: "33600000001",
      avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB"
    },
    {
      name: "Thomas",
      age: 32,
      city: "Boulogne, FR",
      sports: ["TENNIS", "BASKET"],
      level: "AVANCÉ",
      phone: "33600000002",
      avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuDpwCSBiNaFvWF_WGe1Vc3SHEOI9Kt0eFdzAQcA4SY9cxaw5B8SMXyCwxS6nGMbPRcFa36bE9ejpblEjfiMJYUcPHeBRgnSfkDbRn-5IVS2L6eBkmS1kgGEvD4hy6CR0WTpGtGk_4v-1ceYDhq3URMdFNsb7G28FBZ7O1vIn1-tBpT_f0A76vP_onn1nTYOKPvY3NGK2gxVJkrdF1-AkvGYxJy_PJyx_liFTK7HEK6uGyD9ZKmX6c8FCrftu8K9ElN90HfPy1b9yi6t"
    },
    {
      name: "Marc",
      age: 29,
      city: "Neuilly, FR",
      sports: ["PADEL", "FITNESS"],
      level: "DÉBUTANT",
      phone: "33600000003",
      avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK"
    },
    {
      name: "Sophie",
      age: 24,
      city: "Paris, FR",
      sports: ["NATATION"],
      level: "AVANCÉ",
      phone: "33600000004",
      avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB"
    }
  ];

  // Helper to resolve cover image by sport
  const getSportImageUrl = (sportName: string) => {
    const s = sportName.toLowerCase();
    if (s.includes("football") || s.includes("foot")) {
      return "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=500&q=80";
    }
    if (s.includes("basket")) {
      return "https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=500&q=80";
    }
    if (s.includes("tennis")) {
      return "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?auto=format&fit=crop&w=500&q=80";
    }
    return "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=500&q=80";
  };

  // Helper to map sport to avatar on card
  const getPlayerAvatarUrl = (player: User) => {
    const nameCombined = ((player.prenom || "") + " " + (player.nom || "")).toLowerCase();
    if (nameCombined.includes("marie") || nameCombined.includes("sarah") || nameCombined.includes("diallo") || nameCombined.includes("kone") || nameCombined.includes("lea") || nameCombined.includes("sophie")) {
      return "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB";
    }
    if (nameCombined.includes("thomas") || nameCombined.includes("tiemtore") || nameCombined.includes("fahim") || nameCombined.includes("marc")) {
      return "https://lh3.googleusercontent.com/aida-public/AB6AXuDpwCSBiNaFvWF_WGe1Vc3SHEOI9Kt0eFdzAQcA4SY9cxaw5B8SMXyCwxS6nGMbPRcFa36bE9ejpblEjfiMJYUcPHeBRgnSfkDbRn-5IVS2L6eBkmS1kgGEvD4hy6CR0WTpGtGk_4v-1ceYDhq3URMdFNsb7G28FBZ7O1vIn1-tBpT_f0A76vP_onn1nTYOKPvY3NGK2gxVJkrdF1-AkvGYxJy_PJyx_liFTK7HEK6uGyD9ZKmX6c8FCrftu8K9ElN90HfPy1b9yi6t";
    }
    return "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK";
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Redirect to activities with filters or update local state
    if (sportSearch || locationSearch) {
      router.push(`/activities?sport=${sportSearch}&location=${locationSearch}`);
    }
  };

  return (
    <main className="w-full flex-grow flex flex-col bg-brand-page text-brand-primary">
      {/* 1. Hero Section */}
      <section 
        className="relative w-full h-[580px] bg-cover bg-center flex flex-col justify-center items-center px-4"
        style={{
          backgroundImage: `url("https://images.unsplash.com/photo-1593787406536-3676a152d9cb?auto=format&fit=crop&w=1600&q=80")`
        }}
      >
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-black/40"></div>

        {/* Hero Content */}
        <div className="relative z-10 text-center max-w-3xl mb-12">
          <h1 className="font-headline text-3xl md:text-5xl font-extrabold text-white leading-tight mb-8">
            Trouvez votre partenaire de<br />sport idéal
          </h1>
          
          {/* Search bar card */}
          <form 
            onSubmit={handleSearchSubmit}
            className="w-full max-w-3xl bg-white p-3 rounded-2xl md:rounded-full shadow-2xl flex flex-col md:flex-row items-center gap-2"
          >
            <div className="flex items-center gap-2 px-4 py-2 w-full md:w-1/2 border-b md:border-b-0 md:border-r border-gray-200">
              <span className="material-symbols-outlined text-gray-400">person</span>
              <input
                type="text"
                placeholder="Quel sport ?"
                className="w-full bg-transparent border-none text-brand-primary font-semibold placeholder-gray-400 text-sm focus:outline-none focus:ring-0"
                value={sportSearch}
                onChange={(e) => setSportSearch(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2 px-4 py-2 w-full md:w-1/2">
              <span className="material-symbols-outlined text-gray-400">location_on</span>
              <input
                type="text"
                placeholder="Ville ou Code Postal"
                className="w-full bg-transparent border-none text-brand-primary font-semibold placeholder-gray-400 text-sm focus:outline-none focus:ring-0"
                value={locationSearch}
                onChange={(e) => setLocationSearch(e.target.value)}
              />
            </div>
            <button 
              type="submit"
              className="bg-[#00113a] text-white hover:bg-[#002366] transition-all px-8 py-3.5 rounded-full font-bold text-sm w-full md:w-auto shrink-0 flex items-center justify-center gap-2"
            >
              <span className="material-symbols-outlined text-sm">search</span>
              Rechercher
            </button>
          </form>
        </div>

        {/* Floating statistics badges */}
        <div className="absolute bottom-0 translate-y-1/2 z-20 flex gap-4 md:gap-6 flex-wrap justify-center px-4">
          <div className="bg-[#2D6A4D] text-white px-5 py-3 rounded-full flex items-center gap-2 shadow-lg text-sm font-bold tracking-tight">
            <span className="material-symbols-outlined">groups</span>
            12,450 Sportifs actifs
          </div>
          <div className="bg-white text-[#00113a] border border-brand-border px-5 py-3 rounded-full flex items-center gap-2 shadow-lg text-sm font-bold tracking-tight">
            <span className="material-symbols-outlined">sync</span>
            842 Matchs aujourd'hui
          </div>
        </div>
      </section>

      {/* Spacer to handle the overlapping pills */}
      <div className="h-10 md:h-12 w-full"></div>

      {/* 2. Sports populaires Section */}
      <section className="bg-bg-section-gray w-full py-16 px-4 md:px-[80px]">
        <div className="max-w-[1280px] mx-auto">
          <h2 className="font-headline text-headline-md font-bold text-brand-primary mb-8 text-center md:text-left">
            Sports populaires
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-6 justify-center">
            {[
              { label: "Tennis", icon: "sports_tennis" },
              { label: "Padel", icon: "sports_tennis" },
              { label: "Running", icon: "directions_run" },
              { label: "Yoga", icon: "self_improvement" },
              { label: "Basket", icon: "sports_basketball" },
              { label: "Natation", icon: "pool" },
            ].map((sportItem) => (
              <div 
                key={sportItem.label}
                onClick={() => {
                  setSportSearch(sportItem.label);
                  router.push(`/activities?sport=${sportItem.label}`);
                }}
                className="bg-white rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer shadow-sm hover:-translate-y-1.5 hover:shadow-md transition-all duration-300 border border-brand-border/40 group"
              >
                <div className="w-14 h-14 bg-brand-page rounded-full flex items-center justify-center mb-3 group-hover:bg-[#2D6A4D]/10 transition-colors">
                  <span className="material-symbols-outlined text-[#00113a] text-2xl group-hover:text-[#2D6A4D] transition-colors">{sportItem.icon}</span>
                </div>
                <span className="font-bold text-sm text-brand-primary">{sportItem.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. Activités à proximité Section */}
      <section className="w-full py-16 px-4 md:px-[80px] bg-brand-page">
        <div className="max-w-[1280px] mx-auto">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="font-headline text-headline-md font-bold text-brand-primary">
                Activités à proximité
              </h2>
              <p className="text-sm text-brand-secondary mt-1">Rejoignez une session près de chez vous</p>
            </div>
            <Link href="/activities" className="text-sm font-bold text-[#00113a] hover:underline flex items-center gap-1">
              Tout voir
              <span className="material-symbols-outlined text-sm">chevron_right</span>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {filteredMatches.length > 0 ? (
              filteredMatches.slice(0, 3).map((match) => {
                const partsCount = match.participants?.filter(p => p.status === "confirmed").length || 1;
                const org = match.participants?.[0]?.user;
                const orgAvatar = org ? getPlayerAvatarUrl(org) : "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK";
                
                return (
                  <div key={match.id} className="bg-brand-card rounded-2xl overflow-hidden border border-brand-border/40 shadow-sm flex flex-col group hover:-translate-y-1 hover:shadow-md transition-all duration-300">
                    <div className="relative h-44 w-full overflow-hidden">
                      <img 
                        src={getSportImageUrl(match.sport)} 
                        alt={match.sport} 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <span className="absolute top-4 left-4 bg-[#2D6A4D] text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">
                        {match.sport}
                      </span>
                    </div>
                    <div className="p-5 flex-grow flex flex-col justify-between">
                      <div>
                        <div className="flex justify-between items-center mb-1 gap-2">
                          <h3 className="font-bold text-base text-brand-primary truncate">Match de {match.sport}</h3>
                          <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border uppercase tracking-wider shrink-0 ${
                            match.is_paid 
                              ? "bg-amber-500/10 text-amber-600 border-amber-550/20" 
                              : "bg-[#2D6A4D]/10 text-[#2D6A4D] border-[#2D6A4D]/20"
                          }`}>
                            {match.is_paid ? `${match.price} FCFA` : "Gratuit"}
                          </span>
                        </div>
                        <p className="text-xs text-brand-secondary flex items-center gap-1 mb-4 truncate">
                          <span className="material-symbols-outlined text-sm">location_on</span>
                          {match.venue?.name || "Terrain de jeu"}, {match.venue?.neighborhood || "Abidjan"}
                        </p>
                      </div>
                      
                      <div className="flex justify-between items-center pt-4 border-t border-brand-border/30 mt-4">
                        <div className="flex -space-x-2">
                          <img src={orgAvatar} alt="user" className="w-8 h-8 rounded-full border-2 border-white object-cover" />
                          <div className="w-8 h-8 rounded-full bg-brand-page border-2 border-white flex items-center justify-center text-[10px] font-bold text-brand-secondary">
                            +{partsCount}
                          </div>
                        </div>
                        <Link 
                          href="/activities"
                          className="border border-[#2D6A4D] text-[#2D6A4D] hover:bg-[#2D6A4D] hover:text-white transition-all px-4 py-1.5 rounded-lg text-xs font-bold"
                        >
                          Rejoindre
                        </Link>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              // Fallback templates from mockup
              mockActivities.map((act) => (
                <div key={act.id} className="bg-brand-card rounded-2xl overflow-hidden border border-brand-border/40 shadow-sm flex flex-col group hover:-translate-y-1 hover:shadow-md transition-all duration-300">
                  <div className="relative h-44 w-full overflow-hidden">
                    <img 
                      src={act.bgImage} 
                      alt={act.title} 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <span className="absolute top-4 left-4 bg-[#2D6A4D] text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">
                      {act.sport}
                    </span>
                  </div>
                  <div className="p-5 flex-grow flex flex-col justify-between">
                    <div>
                      <h3 className="font-bold text-base text-brand-primary mb-1">{act.title}</h3>
                      <p className="text-xs text-brand-secondary flex items-center gap-1 mb-4">
                        <span className="material-symbols-outlined text-sm">location_on</span>
                        {act.location}
                      </p>
                    </div>
                    
                    <div className="flex justify-between items-center pt-4 border-t border-brand-border/30 mt-4">
                      <div className="flex -space-x-2">
                        {act.avatars.map((av, idx) => (
                          <img key={idx} src={av} alt="user" className="w-8 h-8 rounded-full border-2 border-white object-cover" />
                        ))}
                      </div>
                      <Link 
                        href="/activities"
                        className="border border-[#2D6A4D] text-[#2D6A4D] hover:bg-[#2D6A4D] hover:text-white transition-all px-4 py-1.5 rounded-lg text-xs font-bold"
                      >
                        Rejoindre
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* 4. Partenaires à proximité Section */}
      <section className="bg-bg-section-gray w-full py-16 px-4 md:px-[80px]">
        <div className="max-w-[1280px] mx-auto">
          <h2 className="font-headline text-headline-md font-bold text-brand-primary mb-8 text-center md:text-left">
            Partenaires à proximité
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {filteredPlayers.length > 0 ? (
              filteredPlayers.slice(0, 4).map((player) => {
                const sports = player.sport_prefere ? [player.sport_prefere.toUpperCase()] : ["FITNESS"];
                const level = player.niveau ? player.niveau.toUpperCase() : "INTERMÉDIAIRE";
                
                return (
                  <div key={player.phone_number} className="bg-brand-card rounded-2xl p-6 border border-brand-border/40 shadow-sm flex flex-col items-center text-center hover:-translate-y-1 hover:shadow-md transition-all duration-300">
                    <div className="relative w-20 h-20 rounded-full border-2 border-[#2D6A4D] p-0.5 mb-4 bg-brand-page overflow-hidden">
                      <img 
                        src={getPlayerAvatarUrl(player)} 
                        alt="partner" 
                        className="w-full h-full object-cover rounded-full"
                      />
                      <span className="absolute bottom-1 right-1 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-white"></span>
                    </div>
                    <h3 className="font-bold text-base text-brand-primary mb-0.5">{player.prenom} {player.nom ? player.nom[0] + "." : ""}</h3>
                    <p className="text-xs text-brand-secondary mb-4">{player.quartier || "Abidjan"}, {player.ville || "CI"}</p>
                    
                    <div className="flex gap-1.5 flex-wrap justify-center mb-5">
                      {sports.map((sp) => (
                        <span key={sp} className="bg-brand-page text-[#00113a] text-[10px] font-bold px-3 py-1 rounded-full uppercase">
                          {sp}
                        </span>
                      ))}
                    </div>

                    <span className="bg-[#2D6A4D]/10 text-[#2D6A4D] text-[10px] font-extrabold px-4 py-1.5 rounded-full mb-6 border border-[#2D6A4D]/25 uppercase tracking-wide">
                      {level}
                    </span>

                    <Link 
                      href={`/profile?phone=${player.phone_number}`}
                      className="w-full bg-[#00113a] hover:bg-[#002366] text-white py-2.5 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-1.5"
                    >
                      <span className="material-symbols-outlined text-[16px]">chat_bubble</span>
                      Message
                    </Link>
                  </div>
                );
              })
            ) : (
              // Fallback templates from mockup
              mockPartners.map((partner) => (
                <div key={partner.phone} className="bg-brand-card rounded-2xl p-6 border border-brand-border/40 shadow-sm flex flex-col items-center text-center hover:-translate-y-1 hover:shadow-md transition-all duration-300">
                  <div className="relative w-20 h-20 rounded-full border-2 border-[#2D6A4D] p-0.5 mb-4 bg-brand-page overflow-hidden">
                    <img 
                      src={partner.avatar} 
                      alt={partner.name} 
                      className="w-full h-full object-cover rounded-full"
                    />
                    <span className="absolute bottom-1 right-1 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-white"></span>
                  </div>
                  <h3 className="font-bold text-base text-brand-primary mb-0.5">{partner.name}, {partner.age}</h3>
                  <p className="text-xs text-brand-secondary mb-4">{partner.city}</p>
                  
                  <div className="flex gap-1.5 flex-wrap justify-center mb-5">
                    {partner.sports.map((sp) => (
                      <span key={sp} className="bg-brand-page text-[#00113a] text-[10px] font-bold px-3 py-1 rounded-full uppercase">
                        {sp}
                      </span>
                    ))}
                  </div>

                  <span className="bg-[#2D6A4D]/10 text-[#2D6A4D] text-[10px] font-extrabold px-4 py-1.5 rounded-full mb-6 border border-[#2D6A4D]/25 uppercase tracking-wide">
                    {partner.level}
                  </span>

                  <Link 
                    href="/login"
                    className="w-full bg-[#00113a] hover:bg-[#002366] text-white py-2.5 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-[16px]">chat_bubble</span>
                    Message
                  </Link>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* 5. CTA Section: Prêt à bouger ? */}
      <section className="bg-[#0D1730] w-full py-20 px-4 text-center text-white relative overflow-hidden">
        {/* Soft background shape/decoration */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent"></div>

        <div className="relative z-10 max-w-2xl mx-auto space-y-6">
          <h2 className="font-headline text-3xl md:text-4xl font-extrabold tracking-tight">Prêt à bouger ?</h2>
          <p className="text-gray-300 text-sm md:text-base leading-relaxed">
            Rejoignez des milliers de sportifs et ne vous entraînez plus jamais seul.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 pt-4">
            <Link 
              href="/login" 
              className="bg-[#2D6A4D] text-white hover:bg-[#2D6A4D]/90 transition-all px-8 py-3.5 rounded-lg text-sm font-bold w-full sm:w-auto shadow-md"
            >
              S'inscrire gratuitement
            </Link>
            <Link 
              href="/activities" 
              className="border border-white/35 text-white hover:bg-white/10 transition-all px-8 py-3.5 rounded-lg text-sm font-bold w-full sm:w-auto"
            >
              En savoir plus
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
