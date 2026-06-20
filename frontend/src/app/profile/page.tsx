"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

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
}

function ProfileContent() {
  const searchParams = useSearchParams();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isOwnProfile, setIsOwnProfile] = useState(false);

  // Editing Profile Form States
  const [showEditModal, setShowEditModal] = useState(false);
  const [editPrenom, setEditPrenom] = useState("");
  const [editNom, setEditNom] = useState("");
  const [editAge, setEditAge] = useState<number | "">("");
  const [editTaille, setEditTaille] = useState<number | "">("");
  const [editNiveau, setEditNiveau] = useState("Débutant");
  const [editCategorie, setEditCategorie] = useState("Loisir");
  const [editQuartier, setEditQuartier] = useState("");
  const [editSport, setEditSport] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");

  useEffect(() => {
    document.body.classList.add("page-profile");
    document.body.classList.remove("page-discover", "page-activities");
    return () => {
      document.body.classList.remove("page-profile");
    };
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sportmeet_user");
      const phoneParam = searchParams.get("phone");
      
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (!phoneParam || phoneParam === parsed.phone_number) {
            setIsOwnProfile(true);
            loadProfile(parsed.phone_number);
          } else {
            setIsOwnProfile(false);
            loadProfile(phoneParam);
          }
        } catch (e) {
          console.error(e);
          const fallback = phoneParam || "2250707070707";
          setIsOwnProfile(false);
          loadProfile(fallback);
        }
      } else {
        if (phoneParam) {
          setIsOwnProfile(false);
          loadProfile(phoneParam);
        } else {
          // Redirect to login if not logged in and no query param
          window.location.href = "/login";
        }
      }
    }
  }, [searchParams]);

  const loadProfile = async (phone: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/users/${phone}`);
      if (res.ok) {
        setUser(await res.json());
      } else {
        console.error("User not found");
      }
    } catch (e) {
      console.error("Error loading profile:", e);
    } finally {
      setLoading(false);
    }
  };

  const defaultUser: User = {
    phone_number: "2250707070707",
    nom: "Tiemtore",
    prenom: "Fahim",
    age: 25,
    niveau: "Avancé",
    ville: "Abidjan",
    quartier: "Koumassi",
    taille: 182,
    categorie: "SENIOR",
    sport_prefere: "Basketball"
  };

  const activeUser = user || defaultUser;
  
  const activitiesCount = activeUser.age ? activeUser.age * 2 - 8 : 42;
  const partnersCount = activeUser.age ? Math.floor(activeUser.age * 0.8) : 18;
  const hoursCount = activitiesCount * 2 + 10;
  const reliability = "4.9";

  const sportName = activeUser.sport_prefere || "Football";

  // Match photo with player name
  const nameCombined = ((activeUser.prenom || "") + " " + (activeUser.nom || "")).toLowerCase();
  let portraitUrl = "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK"; // Julien L.
  if (nameCombined.includes("marie") || nameCombined.includes("sarah") || nameCombined.includes("diallo") || nameCombined.includes("kone")) {
    portraitUrl = "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB"; // Sophie L.
  } else if (nameCombined.includes("thomas") || nameCombined.includes("tiemtore") || nameCombined.includes("fahim")) {
    portraitUrl = "https://lh3.googleusercontent.com/aida-public/AB6AXuDpwCSBiNaFvWF_WGe1Vc3SHEOI9Kt0eFdzAQcA4SY9cxaw5B8SMXyCwxS6nGMbPRcFa36bE9ejpblEjfiMJYUcPHeBRgnSfkDbRn-5IVS2L6eBkmS1kgGEvD4hy6CR0WTpGtGk_4v-1ceYDhq3URMdFNsb7G28FBZ7O1vIn1-tBpT_f0A76vP_onn1nTYOKPvY3NGK2gxVJkrdF1-AkvGYxJy_PJyx_liFTK7HEK6uGyD9ZKmX6c8FCrftu8K9ElN90HfPy1b9yi6t"; // Thomas V.
  }

  const openEditModal = () => {
    setEditPrenom(activeUser.prenom || "");
    setEditNom(activeUser.nom || "");
    setEditAge(activeUser.age || "");
    setEditTaille(activeUser.taille || "");
    setEditNiveau(activeUser.niveau || "Débutant");
    setEditCategorie(activeUser.categorie || "Loisir");
    setEditQuartier(activeUser.quartier || "");
    setEditSport(activeUser.sport_prefere || "");
    setSaveError("");
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveError("");
    
    try {
      const payload = {
        prenom: editPrenom || null,
        nom: editNom || null,
        age: editAge ? Number(editAge) : null,
        taille: editTaille ? Number(editTaille) : null,
        niveau: editNiveau || null,
        categorie: editCategorie || null,
        quartier: editQuartier || null,
        sport_prefere: editSport || null,
        ville: activeUser.ville || "Abidjan"
      };

      const res = await fetch(`${API_URL}/users/${activeUser.phone_number}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const updated = await res.json();
        setUser(updated);
        
        if (isOwnProfile) {
          const stored = localStorage.getItem("sportmeet_user");
          if (stored) {
            try {
              const parsed = JSON.parse(stored);
              const merged = { ...parsed, prenom: updated.prenom, nom: updated.nom };
              localStorage.setItem("sportmeet_user", JSON.stringify(merged));
            } catch (err) {
              console.error(err);
            }
          }
        }
        
        setShowEditModal(false);
        window.dispatchEvent(new Event("storage"));
      } else {
        setSaveError("Impossible de mettre à jour le profil. Veuillez réessayer.");
      }
    } catch (err) {
      console.error(err);
      setSaveError("Erreur de connexion au serveur.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="flex-1 w-full max-w-[1280px] mx-auto px-4 md:px-[80px] py-10 space-y-10 bg-brand-page text-brand-primary">
      {/* Hero Banner Background */}
      <div className="w-full h-40 md:h-48 bg-bg-hero rounded-t-2xl relative overflow-hidden flex items-end px-6 md:px-10 pb-4">
        {/* Soft overlay inside banner */}
        <div className="absolute inset-0 bg-black/10"></div>
      </div>

      {/* Profile details overlay */}
      <section className="flex flex-col md:flex-row items-center md:items-end justify-between gap-6 pb-6 border-b border-brand-border px-6 md:px-10 -mt-20 md:-mt-24 relative z-10">
        <div className="flex flex-col md:flex-row items-center md:items-end gap-6 text-center md:text-left">
          <div className="relative">
            <div className="w-32 h-32 md:w-40 md:h-40 rounded-full border-4 border-brand-card shadow-lg overflow-hidden bg-brand-page flex items-center justify-center">
              <img
                className="w-full h-full object-cover"
                src={portraitUrl}
                alt={`${activeUser.prenom} ${activeUser.nom}`}
              />
            </div>
          </div>
          <div className="space-y-1 md:pb-2 text-left">
            <h1 className="font-headline-lg text-headline-lg text-brand-primary">
              {activeUser.prenom} {activeUser.nom}.
            </h1>
            <div className="flex items-center justify-start gap-1 text-brand-secondary">
              <span className="material-symbols-outlined text-[20px]">location_on</span>
              <span className="font-body-md text-body-md">{activeUser.quartier}, {activeUser.ville || "Abidjan"}</span>
            </div>
            <p className="font-body-md text-body-md text-brand-secondary max-w-md pt-2">
              Passionné de {sportName.toLowerCase()} de niveau {activeUser.niveau?.toLowerCase()}. Toujours partant pour un match collectif ou une session intense près de chez soi !
            </p>
          </div>
        </div>
        {isOwnProfile && (
          <button
            onClick={openEditModal}
            className="border-2 border-accent-navy text-accent-navy px-6 py-2.5 rounded-lg font-label-md text-label-md hover:bg-accent-navy hover:text-white transition-all duration-300 md:mb-2 shadow-sm"
          >
            Modifier le profil
          </button>
        )}
      </section>

      {/* Stats Grid */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-brand-card p-6 rounded-xl card-shadow border border-brand-border flex flex-col items-center justify-center text-center group hover:-translate-y-1 transition-transform duration-300">
          <span className="font-display-lg text-display-lg text-brand-primary group-hover:text-accent-green transition-colors">
            {activitiesCount}
          </span>
          <span className="font-label-md text-label-md text-brand-muted uppercase tracking-wider mt-1">
            Activités terminées
          </span>
        </div>
        <div className="bg-brand-card p-6 rounded-xl card-shadow border border-brand-border flex flex-col items-center justify-center text-center group hover:-translate-y-1 transition-transform duration-300">
          <span className="font-display-lg text-display-lg text-brand-primary group-hover:text-accent-green transition-colors">
            {partnersCount}
          </span>
          <span className="font-label-md text-label-md text-brand-muted uppercase tracking-wider mt-1">
            Partenaires rencontrés
          </span>
        </div>
        <div className="bg-brand-card p-6 rounded-xl card-shadow border border-brand-border flex flex-col items-center justify-center text-center group hover:-translate-y-1 transition-transform duration-300">
          <span className="font-display-lg text-display-lg text-brand-primary group-hover:text-accent-green transition-colors">
            {hoursCount}h
          </span>
          <span className="font-label-md text-label-md text-brand-muted uppercase tracking-wider mt-1">
            Heures de sport
          </span>
        </div>
        <div className="bg-brand-card p-6 rounded-xl card-shadow border border-brand-border flex flex-col items-center justify-center text-center group hover:-translate-y-1 transition-transform duration-300">
          <div className="flex items-center gap-1">
            <span className="font-display-lg text-display-lg text-accent-green">{reliability}</span>
            <span className="material-symbols-outlined text-accent-green text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
          </div>
          <span className="font-label-md text-label-md text-brand-muted uppercase tracking-wider mt-1">
            Score de fiabilité
          </span>
        </div>
      </section>

      {/* Main Content Area */}
      <div className="grid lg:grid-cols-12 gap-8 items-start">
        {/* Left: Recent Activities */}
        <div className="lg:col-span-8 space-y-4">
          <h2 className="font-headline-md text-headline-md text-brand-primary">
            Activités récentes
          </h2>
          <div className="bg-brand-card rounded-xl card-shadow overflow-hidden border border-brand-border">
            <div className="divide-y divide-brand-border">
              {/* Activity 1 */}
              <div className="p-6 flex items-center gap-6 bg-brand-card border-l-4 border-l-accent-green">
                <div className="w-12 h-12 bg-bg-green-light text-text-green rounded-lg flex items-center justify-center">
                  <span className="material-symbols-outlined text-[28px]">sports_soccer</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-label-md text-label-md text-brand-primary">{sportName} Match 5v5</h3>
                  <p className="text-caption text-brand-secondary">Samedi passé • Agora de Koumassi</p>
                </div>
                <div>
                  <span className="inline-block px-3 py-1 bg-bg-green-light text-text-green text-caption font-bold rounded-full uppercase tracking-tighter">
                    Terminé
                  </span>
                </div>
              </div>

              {/* Activity 2 */}
              <div className="p-6 flex items-center gap-6 bg-brand-card border-l-4 border-l-accent-green">
                <div className="w-12 h-12 bg-bg-green-light text-text-green rounded-lg flex items-center justify-center">
                  <span className="material-symbols-outlined text-[28px]">sports_basketball</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-label-md text-label-md text-brand-primary">Session Basketball 3v3</h3>
                  <p className="text-caption text-brand-secondary">Il y a 2 semaines • City Sport Cocody</p>
                </div>
                <div>
                  <span className="inline-block px-3 py-1 bg-bg-green-light text-text-green text-caption font-bold rounded-full uppercase tracking-tighter">
                    Terminé
                  </span>
                </div>
              </div>

              {/* Activity 3 */}
              <div className="p-6 flex items-center gap-6 bg-brand-card/50 opacity-90">
                <div className="w-12 h-12 bg-bg-badge-neutral text-brand-secondary rounded-lg flex items-center justify-center">
                  <span className="material-symbols-outlined text-[28px]">directions_run</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-label-md text-label-md text-brand-primary">Running Endurance 8km</h3>
                  <p className="text-caption text-brand-secondary">Il y a 3 semaines • Zone 4 Marcory</p>
                </div>
                <div>
                  <span className="inline-block px-3 py-1 bg-bg-badge-neutral text-brand-secondary text-caption font-bold rounded-full uppercase tracking-tighter">
                    Passé
                  </span>
                </div>
              </div>
            </div>
          </div>
          <button className="w-full py-3 text-brand-primary font-label-md hover:underline transition-all">
            Voir tout l'historique
          </button>
        </div>

        {/* Right: Favorites & Stats */}
        <div className="lg:col-span-4 space-y-6">
          {/* Sports Favoris */}
          <div className="space-y-3">
            <h2 className="font-headline-md text-headline-md text-brand-primary">Sports favoris</h2>
            <div className="bg-brand-card p-6 rounded-xl card-shadow border border-brand-border flex flex-wrap gap-2">
              <span className="px-4 py-2 bg-bg-green-light text-text-green font-label-md rounded-full border border-text-green/20 uppercase">
                {sportName}
              </span>
              <span className="px-4 py-2 bg-bg-green-light text-text-green font-label-md rounded-full border border-text-green/20 uppercase">
                Fitness
              </span>
              <span className="px-4 py-2 bg-bg-green-light text-text-green font-label-md rounded-full border border-text-green/20 uppercase">
                Running
              </span>
            </div>
          </div>

          {/* Statistiques par sport */}
          <div className="space-y-3">
            <h2 className="font-headline-md text-headline-md text-brand-primary">Statistiques</h2>
            <div className="bg-brand-card p-6 rounded-xl card-shadow border border-brand-border space-y-6">
              <div className="space-y-2">
                <div className="flex justify-between font-label-md text-brand-primary">
                  <span>{sportName}</span>
                  <span className="text-accent-green font-bold">78% Victoires</span>
                </div>
                <div className="h-2 w-full bg-progress-track rounded-full overflow-hidden">
                  <div className="h-full bg-progress-fill-navy rounded-full" style={{ width: "78%" }}></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between font-label-md text-brand-primary">
                  <span>Fitness</span>
                  <span className="text-accent-green font-bold">64% Victoires</span>
                </div>
                <div className="h-2 w-full bg-progress-track rounded-full overflow-hidden">
                  <div className="h-full bg-progress-fill-navy rounded-full" style={{ width: "64%" }}></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between font-label-md text-brand-primary">
                  <span>Running</span>
                  <span className="text-accent-green font-bold">92% Objectifs</span>
                </div>
                <div className="h-2 w-full bg-progress-track rounded-full overflow-hidden">
                  <div className="h-full bg-progress-fill-green rounded-full" style={{ width: "92%" }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* --- Modal EDIT PROFILE --- */}
      {showEditModal && (
        <div className="modal-overlay">
          <div className="modal-content relative max-w-[500px]">
            <button
              onClick={() => setShowEditModal(false)}
              className="absolute top-4 right-4 text-brand-secondary hover:text-brand-primary transition-colors font-bold text-lg"
            >
              ✕
            </button>
            <h3 className="font-headline-md text-headline-md text-brand-primary mb-4 pb-2 border-b border-brand-border">
              Modifier mes informations ⚙️
            </h3>
            
            <form onSubmit={handleEditSubmit} className="space-y-4">
              {saveError && <p className="text-red-600 text-xs font-semibold">⚠️ {saveError}</p>}
              
              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-brand-primary">Prénom</label>
                  <input
                    type="text"
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                    value={editPrenom}
                    onChange={(e) => setEditPrenom(e.target.value)}
                    required
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-brand-primary">Nom</label>
                  <input
                    type="text"
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                    value={editNom}
                    onChange={(e) => setEditNom(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-brand-primary">Âge</label>
                  <input
                    type="number"
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                    value={editAge}
                    onChange={(e) => setEditAge(e.target.value === "" ? "" : Number(e.target.value))}
                    required
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-brand-primary">Taille (cm)</label>
                  <input
                    type="number"
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                    value={editTaille}
                    onChange={(e) => setEditTaille(e.target.value === "" ? "" : Number(e.target.value))}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-brand-primary">Niveau</label>
                  <select
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                    value={editNiveau}
                    onChange={(e) => setEditNiveau(e.target.value)}
                    required
                  >
                    <option value="Débutant">Débutant</option>
                    <option value="Intermédiaire">Intermédiaire</option>
                    <option value="Avancé">Avancé</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-brand-primary">Catégorie</label>
                  <select
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                    value={editCategorie}
                    onChange={(e) => setEditCategorie(e.target.value)}
                    required
                  >
                    <option value="Senior">Senior</option>
                    <option value="Loisir">Loisir</option>
                    <option value="Compétition">Compétition</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-brand-primary">Quartier</label>
                <input
                  type="text"
                  className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                  value={editQuartier}
                  onChange={(e) => setEditQuartier(e.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-brand-primary">Sport Préféré</label>
                <input
                  type="text"
                  className="w-full bg-brand-page/50 border border-brand-border focus:border-accent-navy focus:ring-1 focus:ring-accent-navy rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                  value={editSport}
                  onChange={(e) => setEditSport(e.target.value)}
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-brand-border">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="bg-zinc-200 text-zinc-800 px-4 py-2.5 rounded-lg text-xs font-bold hover:bg-zinc-300 transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-accent-navy text-white px-5 py-2.5 rounded-lg text-xs font-bold hover:opacity-90 active:scale-95 transition-all"
                >
                  {saving ? "Enregistrement..." : "Enregistrer 💾"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

export default function Profile() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-on-surface-variant font-bold">Chargement du profil...</div>}>
      <ProfileContent />
    </Suspense>
  );
}
