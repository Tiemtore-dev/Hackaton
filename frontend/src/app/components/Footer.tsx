"use client";

import React from "react";

export default function Footer() {
  return (
    <footer className="bg-brand-page w-full mt-auto border-t border-brand-border/40 text-brand-primary">
      <div className="w-full py-12 px-4 md:px-20 max-w-[1280px] mx-auto flex flex-col md:flex-row justify-between items-center md:items-start gap-8">
        <div className="flex flex-col max-w-xs text-center md:text-left">
          <div className="font-sans text-2xl font-extrabold text-brand-primary mb-3">
            Wasportly<span className="text-secondary">.</span>
          </div>
          <p className="text-brand-secondary text-[14px] leading-relaxed">
            Le réseau social n°1 pour trouver vos futurs partenaires de sport et organiser vos sessions en un clic.
          </p>
        </div>
        
        <div className="grid grid-cols-3 gap-x-12 gap-y-4 text-left">
          <div className="flex flex-col gap-2">
            <span className="font-sans text-[13px] font-bold text-brand-primary uppercase tracking-wider">Plateforme</span>
            <a className="text-[13px] text-brand-secondary hover:underline hover:text-brand-primary transition-all" href="#">Community</a>
            <a className="text-[13px] text-brand-secondary hover:underline hover:text-brand-primary transition-all" href="#">Guidelines</a>
            <a className="text-[13px] text-brand-secondary hover:underline hover:text-brand-primary transition-all" href="#">Careers</a>
          </div>
          <div className="flex flex-col gap-2">
            <span className="font-sans text-[13px] font-bold text-brand-primary uppercase tracking-wider">Légal</span>
            <a className="text-[13px] text-brand-secondary hover:underline hover:text-brand-primary transition-all" href="#">Privacy</a>
            <a className="text-[13px] text-brand-secondary hover:underline hover:text-brand-primary transition-all" href="#">Terms</a>
            <a className="text-[13px] text-brand-secondary hover:underline hover:text-brand-primary transition-all" href="#">Support</a>
          </div>
          <div className="flex flex-col gap-2">
            <span className="font-sans text-[13px] font-bold text-brand-primary uppercase tracking-wider">Social</span>
            <div className="flex gap-2 items-center text-brand-secondary">
              <span className="material-symbols-outlined cursor-pointer hover:text-brand-primary transition-all text-[20px]">public</span>
              <span className="material-symbols-outlined cursor-pointer hover:text-brand-primary transition-all text-[20px]">share</span>
              <span className="material-symbols-outlined cursor-pointer hover:text-brand-primary transition-all text-[20px]">groups</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="w-full py-6 px-4 md:px-20 max-w-[1280px] mx-auto border-t border-brand-border/30 flex flex-col sm:flex-row justify-between items-center gap-4 relative">
        <span className="text-[12px] text-brand-secondary opacity-75">
          © {new Date().getFullYear()} Wasportly. All rights reserved.
        </span>
        <button 
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="absolute right-4 md:right-20 bottom-4 bg-[#0D1730] text-white w-10 h-10 rounded-full flex items-center justify-center hover:scale-105 active:scale-95 transition-all shadow-md outline-none"
          title="Retour en haut"
        >
          <span className="material-symbols-outlined text-[20px]">add</span>
        </button>
      </div>
    </footer>
  );
}
