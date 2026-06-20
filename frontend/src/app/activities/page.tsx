"use client";

import React, { useState, useEffect } from "react";
import { Plus, MapPin, Calendar, Users, Filter, X } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Venue {
  id: string;
  name: string;
  address: string;
  city: string;
  neighborhood: string;
  latitude?: number;
  longitude?: number;
}

interface User {
  id: string;
  phone_number: string;
  nom: string | null;
  prenom: string | null;
  age: number | null;
  niveau: string | null;
  ville: string | null;
  quartier: string | null;
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
}

export default function Activities() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [venues, setVenues] = useState<Venue[]>([]);
  
  // Filtering
  const [filterSport, setFilterSport] = useState("all");
  const [filterLevel, setFilterLevel] = useState("all");

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [selectedMatchToJoin, setSelectedMatchToJoin] = useState<Match | null>(null);
  const [joinPhone, setJoinPhone] = useState("");
  const [joinError, setJoinError] = useState("");
  const [joinSuccess, setJoinSuccess] = useState("");

  // Create form states
  const [createSport, setCreateSport] = useState("Football");
  const [createMatchTime, setCreateMatchTime] = useState("");
  const [createVenueId, setCreateVenueId] = useState("");
  const [createMaxPlayers, setCreateMaxPlayers] = useState(10);
  const [createCreatorPhone, setCreateCreatorPhone] = useState("");
  const [newVenueName, setNewVenueName] = useState("");
  const [newVenueAddress, setNewVenueAddress] = useState("");
  const [newVenueNeighborhood, setNewVenueNeighborhood] = useState("");
  const [newVenueLatitude, setNewVenueLatitude] = useState("");
  const [newVenueLongitude, setNewVenueLongitude] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Geocoding import states
  const [locationInput, setLocationInput] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");
  const [analyzeSuccess, setAnalyzeSuccess] = useState(false);

  // Inject body class for activities page styling
  useEffect(() => {
    document.body.classList.add("page-activities");
    document.body.classList.remove("page-profile", "page-discover");
    return () => {
      document.body.classList.remove("page-activities");
    };
  }, []);

  useEffect(() => {
    fetchInitialData();
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sportmeet_user");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed && parsed.phone_number) {
            setJoinPhone(parsed.phone_number);
            setCreateCreatorPhone(parsed.phone_number);
          }
        } catch (e) {
          console.error(e);
        }
      }
    }
  }, []);

  const fetchInitialData = async () => {
    try {
      // 1. Fetch venues
      const venuesRes = await fetch(`${API_URL}/venues`);
      if (venuesRes.ok) {
        const venuesData = await venuesRes.json();
        setVenues(venuesData);
        if (venuesData.length > 0) {
          setCreateVenueId(venuesData[0].id);
        }
      }

      // 2. Fetch matches
      const matchesRes = await fetch(`${API_URL}/matches`);
      if (matchesRes.ok) {
        const matchesData = await matchesRes.json();
        // Load participants for each match
        const matchesWithParts = await Promise.all(
          matchesData.map(async (m: Match) => {
            const partsRes = await fetch(`${API_URL}/matches/${m.id}/participants`);
            if (partsRes.ok) {
              m.participants = await partsRes.json();
            }
            return m;
          })
        );
        setMatches(matchesWithParts);
      }
    } catch (e) {
      console.error("Error loading activities data:", e);
    }
  };

  const handleAnalyzeLocation = async () => {
    setAnalyzeError("");
    setAnalyzeSuccess(false);
    if (!locationInput.trim()) {
      setAnalyzeError("Veuillez saisir un lien Google Maps ou des coordonnées GPS.");
      return;
    }
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_URL}/venues/parse-location`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url_or_coords: locationInput.trim() }),
      });
      const data = await res.json();
      if (res.ok) {
        setNewVenueName(data.name || "");
        setNewVenueAddress(data.address || "");
        setNewVenueNeighborhood(data.neighborhood || "");
        setNewVenueLatitude(data.latitude !== null ? String(data.latitude) : "");
        setNewVenueLongitude(data.longitude !== null ? String(data.longitude) : "");
        setAnalyzeSuccess(true);
      } else {
        setAnalyzeError(data.detail || "Échec de l'analyse de localisation.");
      }
    } catch (err) {
      console.error(err);
      setAnalyzeError("Erreur de connexion au service de géocodage.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleCreateMatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg("");

    try {
      if (!createCreatorPhone) {
        setErrorMsg("Veuillez entrer le numéro de l'organisateur.");
        setSubmitting(false);
        return;
      }

      // Find user creator
      const userRes = await fetch(`${API_URL}/users/${createCreatorPhone}`);
      if (!userRes.ok) {
        setErrorMsg("L'organisateur n'est pas enregistré sur SportMeet. Veuillez d'abord vous inscrire.");
        setSubmitting(false);
        return;
      }
      const creatorData = await userRes.json();
      const creatorId = creatorData.id;

      // Handle new venue
      let finalVenueId = createVenueId;
      if (createVenueId === "new") {
        if (!newVenueName || !newVenueAddress || !newVenueNeighborhood) {
          setErrorMsg("Veuillez remplir toutes les informations pour le nouveau terrain.");
          setSubmitting(false);
          return;
        }

        const venuePayload = {
          name: newVenueName,
          address: newVenueAddress,
          city: "Abidjan",
          neighborhood: newVenueNeighborhood,
          latitude: newVenueLatitude ? parseFloat(newVenueLatitude) : null,
          longitude: newVenueLongitude ? parseFloat(newVenueLongitude) : null
        };

        const venueRes = await fetch(`${API_URL}/venues`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(venuePayload)
        });

        if (!venueRes.ok) {
          setErrorMsg("Impossible de créer le terrain.");
          setSubmitting(false);
          return;
        }

        const newVenueData = await venueRes.json();
        finalVenueId = newVenueData.id;
      }

      if (!finalVenueId) {
        setErrorMsg("Sélectionnez ou créez un terrain.");
        setSubmitting(false);
        return;
      }

      // Create match
      const matchPayload = {
        sport: createSport,
        match_time: new Date(createMatchTime).toISOString(),
        venue_id: finalVenueId,
        max_players: createMaxPlayers,
        creator_id: creatorId
      };

      const matchRes = await fetch(`${API_URL}/matches`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(matchPayload)
      });

      if (!matchRes.ok) {
        setErrorMsg("Erreur lors de la création du match.");
        setSubmitting(false);
        return;
      }

      // Reset & Reload
      setShowCreateModal(false);
      setCreateMatchTime("");
      setNewVenueName("");
      setNewVenueAddress("");
      setNewVenueNeighborhood("");
      setNewVenueLatitude("");
      setNewVenueLongitude("");
      fetchInitialData();
    } catch (err) {
      console.error(err);
      setErrorMsg("Erreur réseau.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleJoinMatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setJoinError("");
    setJoinSuccess("");

    if (!selectedMatchToJoin) return;

    try {
      // Look up user by phone to ensure they are registered
      const userRes = await fetch(`${API_URL}/users/${joinPhone}`);
      if (!userRes.ok) {
        setJoinError("Votre numéro WhatsApp n'est pas encore enregistré. Veuillez d'abord vous inscrire.");
        return;
      }

      const userData = await userRes.json();

      // Simulate a Meta Cloud Webhook button payload response to trigger backend join, notifications, and waitlists
      const webhookPayload = {
        object: "whatsapp_business_account",
        entry: [
          {
            id: "mock_waba_id_000",
            changes: [
              {
                field: "messages",
                value: {
                  messaging_product: "whatsapp",
                  metadata: {
                    display_phone_number: "15555555555",
                    phone_number_id: "mock_phone_id"
                  },
                  contacts: [
                    {
                      profile: { name: `${userData.prenom} ${userData.nom}` },
                      wa_id: joinPhone
                    }
                  ],
                  messages: [
                    {
                      from: joinPhone,
                      id: `wamid.mock_web_join_${Date.now()}`,
                      timestamp: String(Math.floor(Date.now() / 1000)),
                      type: "interactive",
                      interactive: {
                        type: "button_reply",
                        button_reply: {
                          id: `match_join:${selectedMatchToJoin.id}`,
                          title: "Rejoindre"
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        ]
      };

      const res = await fetch(`${API_URL}/webhook`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(webhookPayload)
      });

      if (res.ok) {
        setJoinSuccess("Félicitations ! Votre demande de participation a été traitée sur WhatsApp.");
        setTimeout(() => {
          setShowJoinModal(false);
          setJoinPhone("");
          setJoinSuccess("");
          fetchInitialData();
        }, 2000);
      } else {
        setJoinError("Une erreur est survenue lors du traitement.");
      }
    } catch (err) {
      console.error(err);
      setJoinError("Erreur de connexion.");
    }
  };

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

  // Filter logic
  const filteredMatches = matches.filter((m) => {
    const matchesSport = filterSport === "all" || m.sport.toLowerCase().includes(filterSport.toLowerCase());
    const matchesLevel = filterLevel === "all" || (m.participants && m.participants.some(p => p.user.niveau && p.user.niveau.toLowerCase().includes(filterLevel.toLowerCase())));
    return matchesSport && matchesLevel;
  });

  return (
    <main className="flex-1 w-full max-w-[1280px] mx-auto px-4 md:px-[80px] py-10 bg-brand-page text-brand-primary">
      
      {/* Hero section */}
      <section className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="max-w-2xl">
          <h1 className="font-headline-lg text-headline-lg text-brand-primary mb-4">
            Trouvez votre prochaine session
          </h1>
          <p className="font-body-lg text-body-lg text-brand-secondary">
            Rejoignez des sportifs passionnés près de chez vous pour des entraînements collectifs ou des matchs amicaux.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="hidden md:flex items-center gap-2 bg-navy-primary text-white px-6 py-3 rounded-lg font-label-md text-label-md shadow-sm hover:bg-navy-dark transition-colors"
        >
          <span className="material-symbols-outlined">add</span>
          CRÉER UNE ACTIVITÉ
        </button>
      </section>

      {/* Filters Bar */}
      <section className="mb-8 border-b border-brand-border pb-4 overflow-x-auto hide-scrollbar">
        <div className="flex items-center gap-4 min-w-max pb-2">
          
          {/* Filter by sport */}
          <div className="flex items-center gap-2 bg-bg-tag-light border border-brand-border px-4 py-2 rounded-full text-brand-secondary font-label-md text-label-md cursor-pointer hover:border-brand-primary transition-all">
            <span className="material-symbols-outlined text-[16px] text-brand-primary">fitness_center</span>
            <select
              value={filterSport}
              onChange={(e) => setFilterSport(e.target.value)}
              className="bg-transparent border-none focus:ring-0 p-0 text-xs font-bold text-brand-secondary cursor-pointer outline-none"
            >
              <option value="all">Tous les Sports</option>
              <option value="football">Football</option>
              <option value="basketball">Basketball</option>
              <option value="tennis">Tennis</option>
            </select>
          </div>

          {/* Filter by level */}
          <div className="flex items-center gap-2 bg-bg-tag-light border border-brand-border px-4 py-2 rounded-full text-brand-secondary font-label-md text-label-md cursor-pointer hover:border-brand-primary transition-all">
            <span className="material-symbols-outlined text-[16px] text-brand-primary">leaderboard</span>
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="bg-transparent border-none focus:ring-0 p-0 text-xs font-bold text-brand-secondary cursor-pointer outline-none"
            >
              <option value="all">Tous Niveaux</option>
              <option value="débutant">Débutant</option>
              <option value="intermédiaire">Intermédiaire</option>
              <option value="avancé">Avancé</option>
            </select>
          </div>

          <div className="ml-auto text-caption font-caption text-brand-secondary self-center mr-2">
            {filteredMatches.length} activité(s) trouvée(s)
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMatches.map((match) => {
          const confirmedCount = match.participants?.filter(p => p.status === "confirmed").length || 0;
          const userLevel = match.participants?.[0]?.user?.niveau || "Tous niveaux";
          const organizer = match.participants?.[0]?.user;
          const organizerName = organizer ? `${organizer.prenom} ${organizer.nom ? organizer.nom[0] + "." : ""}` : "Sporty";
          
          return (
            <div key={match.id} className="kinetic-card rounded-lg overflow-hidden flex flex-col">
              {/* Card Photo placeholder */}
              <div className="relative h-48 overflow-hidden">
                <img
                  className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  alt={match.sport}
                  src={getSportImageUrl(match.sport)}
                />
                <div className="absolute top-4 right-4 bg-bg-tag-light/95 text-brand-primary px-3 py-1 rounded-full font-label-md text-[12px] backdrop-blur-sm">
                  {userLevel.toUpperCase()}
                </div>
              </div>

              {/* Card Details */}
              <div className="p-6 flex flex-col flex-grow bg-brand-card">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-headline-md text-headline-md text-brand-primary leading-tight">
                    Match de {match.sport}
                  </h3>
                  <span className="text-green-accent font-bold text-caption">
                    GRATUIT
                  </span>
                </div>

                <div className="flex items-center gap-2 text-brand-secondary mb-4">
                  <span className="material-symbols-outlined text-[18px]">calendar_today</span>
                  <span className="font-body-md text-body-md">
                    {new Date(match.match_time).toLocaleString("fr-FR", {
                      weekday: "long",
                      day: "numeric",
                      month: "short",
                      hour: "2-digit",
                      minute: "2-digit"
                    })}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-brand-secondary mb-6">
                  <span className="material-symbols-outlined text-[18px]">location_on</span>
                  <span className="font-body-md text-body-md truncate">
                    {match.venue?.name || "Terrain inconnu"} ({match.venue?.neighborhood || "Abidjan"})
                  </span>
                </div>

                {/* Card Footer: Host avatar, capacity list & join action */}
                <div className="mt-auto flex items-center justify-between pt-4 border-t border-brand-border">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full overflow-hidden border border-brand-border bg-brand-page flex items-center justify-center">
                      <img
                        className="w-full h-full object-cover"
                        src={organizerName.toLowerCase().includes("marie") || organizerName.toLowerCase().includes("sarah")
                          ? "https://lh3.googleusercontent.com/aida-public/AB6AXuCXxBPtr9Tc5MUhFSeFUH2kh4MZ_mnLP4e2w-10f26QbvWA4tblOLsoaZvwpm7HJm5KTePKdN9GGMEFXVbfsEmG_CW04rTVecA1mss2XKPPhGIjb6ImQBMLDzq_MctkZxM1WnwTDDDQrnuweyiIauR0SWSaT5llNbqXHyPnZj_F-u3S0YIv0Y_ZIRs_tmOnxsElOrtxjZk43BBS5-DfARGIQzG8uzaMB4EXe4oI2GMZ60rYS1w8tLYrgOZ3ie-EvB1jJ7uyGZPtWbxB"
                          : "https://lh3.googleusercontent.com/aida-public/AB6AXuAZ-dMbue0MXa4JvaaK1VinpTQsXjxXSx5H1CiS6SYRNCNZkpSSzYkhtopczGI46ek_1f2vdQZdPuLMSQTXoKGnSxCALdccbjQhMuggiYu2orQqrj8PcexyzlfHeJD4EuHph1ix5vcJv2465G-d3zigB8IGoQH8j2aEnoJ3l6-kcHWvkeaFntdxZCgNubvrtPEC3mHNKN_A5z2G4jrD6wP78O8dNZurslZabRIwjmwKoeePCRGF-9TGPB_VHIPv5Kz-7c_VnVr0NMQK"
                        }
                        alt="Organizer"
                      />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-caption font-caption font-bold text-brand-primary">
                        {organizerName}
                      </span>
                      <span className="text-[11px] text-green-accent font-bold uppercase">
                        {confirmedCount} / {match.max_players} PLACES
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedMatchToJoin(match);
                      setShowJoinModal(true);
                    }}
                    className="bg-navy-primary text-white px-6 py-2 rounded-lg font-label-md text-label-md hover:bg-navy-dark transition-colors shadow-sm"
                  >
                    REJOINDRE
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {filteredMatches.length === 0 && (
          <div className="col-span-full text-center py-16 text-brand-secondary italic bg-bg-tag-light border border-brand-border rounded-xl">
            Aucun match trouvé pour ces filtres. Créez-en un à la volée ! ⚽
          </div>
        )}
      </div>

      {/* --- Modal CREATE ACTIVITY --- */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content relative max-w-lg">
            <button
              onClick={() => setShowCreateModal(false)}
              className="absolute top-4 right-4 text-brand-secondary hover:text-brand-primary transition-colors"
            >
              <X size={20} />
            </button>
            <h3 className="font-headline text-headline-md font-bold text-brand-primary mb-4 pb-2 border-b border-brand-border">
              Organiser un match ⚽
            </h3>
            
            <form onSubmit={handleCreateMatchSubmit} className="space-y-4">
              {errorMsg && (
                <div className="p-3 bg-red-100 border-l-4 border-red-500 text-red-700 text-xs font-semibold rounded-r">
                  ⚠️ {errorMsg}
                </div>
              )}
              
              <div className="flex flex-col gap-1.5">
                <label className="text-caption font-bold text-brand-primary uppercase tracking-wider">Sport</label>
                <select
                  value={createSport}
                  onChange={(e) => setCreateSport(e.target.value)}
                  className="w-full bg-brand-page/50 border border-brand-border focus:border-navy-primary focus:ring-1 focus:ring-navy-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all text-brand-primary font-semibold"
                >
                  <option value="Football">⚽ Football</option>
                  <option value="Basketball">🏀 Basketball</option>
                  <option value="Tennis">🎾 Tennis</option>
                  <option value="Handball">🤾 Handball</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-caption font-bold text-brand-primary uppercase tracking-wider">Date & Heure</label>
                  <input
                    type="datetime-local"
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-navy-primary focus:ring-1 focus:ring-navy-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all text-brand-primary font-semibold"
                    value={createMatchTime}
                    onChange={(e) => setCreateMatchTime(e.target.value)}
                    required
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-caption font-bold text-brand-primary uppercase tracking-wider">Max Joueurs</label>
                  <input
                    type="number"
                    className="w-full bg-brand-page/50 border border-brand-border focus:border-navy-primary focus:ring-1 focus:ring-navy-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all text-brand-primary font-semibold"
                    min={2}
                    max={100}
                    value={createMaxPlayers}
                    onChange={(e) => setCreateMaxPlayers(parseInt(e.target.value))}
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-caption font-bold text-brand-primary uppercase tracking-wider">WhatsApp Organisateur</label>
                <input
                  type="text"
                  placeholder="Ex: 2250707070707"
                  className="w-full bg-brand-page/50 border border-brand-border focus:border-navy-primary focus:ring-1 focus:ring-navy-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all text-brand-primary font-semibold"
                  value={createCreatorPhone}
                  onChange={(e) => setCreateCreatorPhone(e.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-caption font-bold text-brand-primary uppercase tracking-wider">Terrain</label>
                <select
                  value={createVenueId}
                  onChange={(e) => setCreateVenueId(e.target.value)}
                  className="w-full bg-brand-page/50 border border-brand-border focus:border-navy-primary focus:ring-1 focus:ring-navy-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all text-brand-primary font-semibold"
                  required
                >
                  {venues.map((v) => (
                    <option key={v.id} value={v.id}>
                      🏟️ {v.name} ({v.neighborhood})
                    </option>
                  ))}
                  <option value="new">➕ Créer un nouveau terrain / Position GPS...</option>
                </select>
              </div>

              {createVenueId === "new" && (
                <div className="border border-brand-border rounded-xl p-4 bg-brand-page/35 space-y-4">
                  <h4 className="text-caption font-extrabold uppercase tracking-wider text-brand-primary border-b border-brand-border pb-1">Nouveau terrain</h4>
                  
                  {/* Google Maps link import input */}
                  <div className="flex flex-col gap-1.5 p-3 bg-brand-page/70 rounded-lg border border-brand-border">
                    <label className="text-[10px] font-extrabold text-navy-primary uppercase tracking-wider">
                      📍 Analyse Automatique (Lien Google Maps ou GPS Coords)
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Coller lien Maps ou ex: 5.3434, -4.0123"
                        className="flex-1 bg-white border border-brand-border focus:border-navy-primary rounded-lg px-3 py-1.5 text-xs font-semibold text-brand-primary outline-none"
                        value={locationInput}
                        onChange={(e) => setLocationInput(e.target.value)}
                      />
                      <button
                        type="button"
                        onClick={handleAnalyzeLocation}
                        disabled={analyzing}
                        className="bg-green-accent hover:bg-green-accent/95 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-1 shrink-0"
                      >
                        {analyzing ? "Analyse..." : "Analyser ⚡"}
                      </button>
                    </div>
                    {analyzeError && <p className="text-red-600 text-[10px] font-bold">⚠️ {analyzeError}</p>}
                    {analyzeSuccess && <p className="text-green-accent text-[10px] font-bold">✓ Localisation analysée avec succès !</p>}
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">Nom du terrain</label>
                    <input
                      type="text"
                      placeholder="Ex: Complexe Agora Koumassi"
                      className="w-full bg-white border border-brand-border focus:border-navy-primary rounded-lg px-3 py-2 text-xs font-semibold text-brand-primary outline-none transition-all"
                      value={newVenueName}
                      onChange={(e) => setNewVenueName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">Adresse</label>
                    <input
                      type="text"
                      placeholder="Ex: Boulevard du 7 Décembre"
                      className="w-full bg-white border border-brand-border focus:border-navy-primary rounded-lg px-3 py-2 text-xs font-semibold text-brand-primary outline-none transition-all"
                      value={newVenueAddress}
                      onChange={(e) => setNewVenueAddress(e.target.value)}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">Quartier</label>
                      <input
                        type="text"
                        placeholder="Ex: Koumassi"
                        className="w-full bg-white border border-brand-border focus:border-navy-primary rounded-lg px-3 py-2 text-xs font-semibold text-brand-primary outline-none transition-all"
                        value={newVenueNeighborhood}
                        onChange={(e) => setNewVenueNeighborhood(e.target.value)}
                        required
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">Ville</label>
                      <input
                        type="text"
                        value="Abidjan"
                        disabled
                        className="w-full bg-white/40 border border-brand-border/40 text-brand-secondary/60 rounded-lg px-3 py-2 text-xs font-semibold cursor-not-allowed outline-none"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">Latitude</label>
                      <input
                        type="number"
                        step="any"
                        placeholder="Ex: 5.3056"
                        className="w-full bg-white border border-brand-border focus:border-navy-primary rounded-lg px-3 py-2 text-xs font-semibold text-brand-primary outline-none transition-all"
                        value={newVenueLatitude}
                        onChange={(e) => setNewVenueLatitude(e.target.value)}
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">Longitude</label>
                      <input
                        type="number"
                        step="any"
                        placeholder="Ex: -3.9876"
                        className="w-full bg-white border border-brand-border focus:border-navy-primary rounded-lg px-3 py-2 text-xs font-semibold text-brand-primary outline-none transition-all"
                        value={newVenueLongitude}
                        onChange={(e) => setNewVenueLongitude(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-brand-border">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="bg-zinc-200 text-zinc-800 px-5 py-2.5 rounded-lg text-xs font-bold hover:bg-zinc-300 transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-navy-primary text-white px-6 py-2.5 rounded-lg text-xs font-bold hover:bg-navy-dark active:scale-95 transition-all"
                >
                  {submitting ? "Création..." : "CRÉER LE MATCH 🚀"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- Modal JOIN MATCH (WhatsApp simulation) --- */}
      {showJoinModal && selectedMatchToJoin && (
        <div className="modal-overlay">
          <div className="modal-content relative">
            <button
              onClick={() => setShowJoinModal(false)}
              className="absolute top-4 right-4 text-brand-secondary hover:text-brand-primary transition-colors"
            >
              <X size={20} />
            </button>
            <h3 className="font-headline text-lg font-bold text-brand-primary mb-4 pb-2 border-b border-brand-border">
              Rejoindre le match de {selectedMatchToJoin.sport} ⚽
            </h3>
            
            <form onSubmit={handleJoinMatchSubmit} className="space-y-4">
              <p className="text-xs text-brand-secondary leading-relaxed">
                Afin de confirmer votre participation et de vous inscrire, veuillez renseigner le numéro WhatsApp lié à votre Carte Joueur SportMeet.
              </p>
              
              {joinError && <p className="text-red-600 text-xs font-semibold">⚠️ {joinError}</p>}
              {joinSuccess && <p className="text-green-accent text-xs font-bold">🎉 {joinSuccess}</p>}
              
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-brand-primary uppercase tracking-wider">Numéro WhatsApp</label>
                <input
                  type="text"
                  placeholder="Ex: 2250707070707"
                  className="w-full bg-brand-page/50 border border-brand-border focus:border-navy-primary focus:ring-1 focus:ring-navy-primary rounded-lg px-4 py-2.5 text-sm font-semibold outline-none transition-all text-brand-primary"
                  value={joinPhone}
                  onChange={(e) => setJoinPhone(e.target.value)}
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-brand-border">
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  className="bg-zinc-200 text-zinc-800 px-4 py-2.5 rounded-lg text-xs font-bold hover:bg-zinc-300 transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="bg-navy-primary text-white px-5 py-2.5 rounded-lg text-xs font-bold hover:bg-navy-dark active:scale-95 transition-all"
                >
                  Valider l'Inscription 🟢
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
