"use client";

import React, { useState } from "react";

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
}

interface PlayerCardProps {
  user: User;
}

export default function PlayerCard({ user }: PlayerCardProps) {
  const [tiltStyle, setTiltStyle] = useState<React.CSSProperties>({});

  // 1. Determine level and card rarity
  const lvl = (user.niveau || "").toLowerCase();
  let rarity = "bronze"; // default
  let overall = 68;
  if (lvl.includes("avancé") || lvl.includes("expert")) {
    rarity = "gold";
    overall = 88;
  } else if (lvl.includes("intermédiaire")) {
    rarity = "silver";
    overall = 79;
  }

  // 2. Generate stats deterministically based on phone number
  const seedNum = parseInt(user.phone_number.slice(-3)) || 42;
  const generateStat = (base: number, maxAdd: number) => {
    return Math.min(99, Math.max(40, base + (seedNum % maxAdd)));
  };

  const spd = rarity === "gold" ? generateStat(80, 20) : rarity === "silver" ? generateStat(70, 15) : generateStat(55, 15);
  const sho = rarity === "gold" ? generateStat(75, 20) : rarity === "silver" ? generateStat(65, 15) : generateStat(50, 15);
  const pas = rarity === "gold" ? generateStat(82, 18) : rarity === "silver" ? generateStat(72, 12) : generateStat(58, 12);
  const dri = rarity === "gold" ? generateStat(84, 15) : rarity === "silver" ? generateStat(74, 12) : generateStat(60, 12);
  const def = rarity === "gold" ? generateStat(68, 25) : rarity === "silver" ? generateStat(58, 20) : generateStat(48, 15);
  const phy = rarity === "gold" ? generateStat(78, 22) : rarity === "silver" ? generateStat(68, 18) : generateStat(55, 15);

  // 3. Map sport to material symbol
  let sportIcon = "sports_soccer";
  const sport = (user.sport_prefere || "").toLowerCase();
  if (sport.includes("tennis")) sportIcon = "sports_tennis";
  else if (sport.includes("basket")) sportIcon = "sports_basketball";
  else if (sport.includes("hand")) sportIcon = "sports_handball";
  else if (sport.includes("rugby")) sportIcon = "sports_rugby";

  // 4. Handle 3D Tilt Effect
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateY = ((x - centerX) / centerX) * 15;
    const rotateX = ((centerY - y) / centerY) * 15;
    
    setTiltStyle({
      transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`,
      transition: "transform 0.1s ease",
    });
  };

  const handleMouseLeave = () => {
    setTiltStyle({
      transform: "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)",
      transition: "transform 0.5s ease",
    });
  };

  // 5. Choose background gradient based on rarity
  let cardBgClass = "bg-gradient-to-br from-[#78350f] via-[#b45309] to-[#451a03] text-orange-100"; // bronze
  if (rarity === "gold") {
    cardBgClass = "bg-gradient-to-br from-[#d97706] via-[#eab308] to-[#78350f] text-yellow-100";
  } else if (rarity === "silver") {
    cardBgClass = "bg-gradient-to-br from-[#475569] via-[#94a3b8] to-[#334155] text-slate-100";
  }

  return (
    <div className="flex justify-center p-2">
      <article
        className={`relative w-[320px] h-[480px] overflow-hidden flex flex-col p-6 shadow-2xl transition-all duration-300 ${cardBgClass}`}
        style={{
          clipPath: "polygon(50% 0%, 100% 12%, 100% 88%, 50% 100%, 0% 88%, 0% 12%)",
          ...tiltStyle,
        }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        {/* Card Shine Overlay */}
        <div className="absolute inset-0 bg-gradient-to-tr from-white/10 to-transparent pointer-events-none"></div>

        {/* Top: Stats & Avatar */}
        <div className="relative flex justify-between items-start mt-10">
          {/* Identity Columns */}
          <div className="flex flex-col items-center gap-2 ml-4">
            <div className="font-bold text-5xl tracking-tighter leading-none">{overall}</div>
            <div className="w-8 h-5 bg-white/20 rounded-sm flex items-center justify-center overflow-hidden border border-white/10">
              <img
                alt="CI"
                className="w-full h-full object-cover"
                src="https://flagcdn.com/w80/ci.png"
              />
            </div>
            <span className="material-symbols-outlined text-3xl opacity-90">{sportIcon}</span>
          </div>
          
          {/* Player Avatar */}
          <div className="w-36 h-36 -mr-2 bg-gradient-to-b from-white/10 to-transparent rounded-full flex items-center justify-center overflow-hidden border border-white/5 shadow-inner">
            <span className="material-symbols-outlined text-6xl opacity-40">person</span>
          </div>
        </div>

        {/* Name Bar */}
        <div className="text-center mt-6 border-t border-b border-white/20 py-2.5 mx-4">
          <h2 className="font-extrabold text-xl uppercase tracking-widest truncate leading-tight">
            {user.prenom || "Sporty"} {user.nom || "Player"}
          </h2>
          <p className="text-[10px] tracking-widest text-white/60 uppercase font-semibold mt-0.5">
            {user.categorie || "SENIOR"}
          </p>
        </div>

        {/* Attributes Grid */}
        <div className="grid grid-cols-2 gap-x-8 gap-y-1.5 mt-6 px-8 relative text-sm font-semibold">
          <div className="absolute left-1/2 top-1 bottom-1 w-[1px] bg-white/20"></div>
          <div className="flex flex-col gap-1">
            <div className="flex justify-between">
              <span className="opacity-80">SPD</span>
              <span>{spd}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-80">SHO</span>
              <span>{sho}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-80">PAS</span>
              <span>{pas}</span>
            </div>
          </div>
          <div className="flex flex-col gap-1">
            <div className="flex justify-between">
              <span className="opacity-80">DRI</span>
              <span>{dri}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-80">DEF</span>
              <span>{def}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-80">PHY</span>
              <span>{phy}</span>
            </div>
          </div>
        </div>

        {/* Footer info: location */}
        <div className="mt-auto mb-10 text-center text-[11px] font-bold tracking-wider text-white/70 uppercase">
          📍 {user.quartier || "Abidjan"}
        </div>
      </article>
    </div>
  );
}
