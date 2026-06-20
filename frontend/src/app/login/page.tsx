"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Login() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");
  
  // Login States
  const [loginPhone, setLoginPhone] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  // Register States
  const [regPhone, setRegPhone] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regPrenom, setRegPrenom] = useState("");
  const [regNom, setRegNom] = useState("");
  const [regAge, setRegAge] = useState<number | "">("");
  const [regTaille, setRegTaille] = useState<number | "">("");
  const [regNiveau, setRegNiveau] = useState("Débutant");
  const [regCategorie, setRegCategorie] = useState("Loisir");
  const [regQuartier, setRegQuartier] = useState("Cocody");
  const [regSport, setRegSport] = useState("Football");
  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    if (!loginPhone || !loginPassword) {
      setLoginError("Veuillez remplir tous les champs.");
      return;
    }
    setLoginLoading(true);
    try {
      const res = await fetch(`${API_URL}/users/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: loginPhone.trim(),
          password: loginPassword,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        // Save user to localStorage
        localStorage.setItem("sportmeet_user", JSON.stringify(data));
        // Force refresh & redirect to profile
        router.push(`/profile?phone=${data.phone_number}`);
        setTimeout(() => {
          window.location.reload();
        }, 100);
      } else {
        setLoginError(data.detail || "Numéro de téléphone ou mot de passe incorrect.");
      }
    } catch (err) {
      console.error(err);
      setLoginError("Erreur de connexion au serveur.");
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError("");
    if (!regPhone || !regPassword || !regPrenom || !regNom) {
      setRegError("Le téléphone, mot de passe, prénom et nom sont obligatoires.");
      return;
    }
    setRegLoading(true);
    try {
      const res = await fetch(`${API_URL}/users/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: regPhone.trim(),
          password: regPassword,
          prenom: regPrenom.trim(),
          nom: regNom.trim(),
          age: regAge === "" ? null : Number(regAge),
          taille: regTaille === "" ? null : Number(regTaille),
          niveau: regNiveau,
          categorie: regCategorie,
          quartier: regQuartier,
          sport_prefere: regSport,
          ville: "Abidjan"
        }),
      });
      const data = await res.json();
      if (res.ok) {
        // Save user to localStorage
        localStorage.setItem("sportmeet_user", JSON.stringify(data));
        // Redirect to profile
        router.push(`/profile?phone=${data.phone_number}`);
        setTimeout(() => {
          window.location.reload();
        }, 100);
      } else {
        setRegError(data.detail || "L'inscription a échoué. Veuillez vérifier les informations.");
      }
    } catch (err) {
      console.error(err);
      setRegError("Erreur de connexion au serveur.");
    } finally {
      setRegLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-brand-cream flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-md bg-brand-offwhite rounded-xl shadow-lg border border-primary/5 overflow-hidden">
        {/* Tab Headers */}
        <div className="flex border-b border-primary/10">
          <button
            onClick={() => setActiveTab("login")}
            className={`flex-1 py-4 font-headline text-label-md uppercase tracking-wider transition-all border-b-2 font-bold ${
              activeTab === "login"
                ? "border-primary text-primary bg-primary/5"
                : "border-transparent text-on-surface-variant hover:text-primary"
            }`}
          >
            Se Connecter
          </button>
          <button
            onClick={() => setActiveTab("register")}
            className={`flex-1 py-4 font-headline text-label-md uppercase tracking-wider transition-all border-b-2 font-bold ${
              activeTab === "register"
                ? "border-primary text-primary bg-primary/5"
                : "border-transparent text-on-surface-variant hover:text-primary"
            }`}
          >
            Créer un compte
          </button>
        </div>

        {/* Tab Contents */}
        <div className="p-8">
          {activeTab === "login" ? (
            /* Login Form */
            <form onSubmit={handleLogin} className="space-y-5">
              <div className="space-y-1">
                <h1 className="font-headline text-headline-md text-primary font-bold">Connexion</h1>
                <p className="font-sans text-body-md text-on-surface-variant">Accédez à votre espace Wasportly.</p>
              </div>

              {loginError && (
                <div className="p-3 bg-red-100 border-l-4 border-red-500 text-red-700 text-sm font-semibold rounded-r">
                  ⚠️ {loginError}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label htmlFor="loginPhone" className="block text-caption font-bold text-primary uppercase tracking-wider mb-1">
                    Numéro de Téléphone (WhatsApp)
                  </label>
                  <input
                    id="loginPhone"
                    type="text"
                    placeholder="ex: 2250707070707"
                    value={loginPhone}
                    onChange={(e) => setLoginPhone(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="loginPass" className="block text-caption font-bold text-primary uppercase tracking-wider mb-1">
                    Mot de passe
                  </label>
                  <input
                    id="loginPass"
                    type="password"
                    placeholder="••••••••"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-4 py-2.5 text-body-md outline-none transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full bg-primary hover:bg-primary/95 text-white font-bold py-3 rounded-lg uppercase tracking-wider text-label-md transition-all active:scale-98 shadow-md flex items-center justify-center gap-2"
              >
                {loginLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Connexion en cours...
                  </>
                ) : (
                  "Se Connecter"
                )}
              </button>
            </form>
          ) : (
            /* Register Form */
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-1">
                <h1 className="font-headline text-headline-md text-primary font-bold">Inscription</h1>
                <p className="font-sans text-body-md text-on-surface-variant">Rejoignez la communauté sportive.</p>
              </div>

              {regError && (
                <div className="p-3 bg-red-100 border-l-4 border-red-500 text-red-700 text-sm font-semibold rounded-r">
                  ⚠️ {regError}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="regPhone" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Téléphone (WhatsApp) *
                  </label>
                  <input
                    id="regPhone"
                    type="text"
                    placeholder="2250..."
                    value={regPhone}
                    onChange={(e) => setRegPhone(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="regPass" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Mot de passe *
                  </label>
                  <input
                    id="regPass"
                    type="password"
                    placeholder="••••••••"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="regPrenom" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Prénom *
                  </label>
                  <input
                    id="regPrenom"
                    type="text"
                    placeholder="Julien"
                    value={regPrenom}
                    onChange={(e) => setRegPrenom(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="regNom" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Nom *
                  </label>
                  <input
                    id="regNom"
                    type="text"
                    placeholder="Lefebvre"
                    value={regNom}
                    onChange={(e) => setRegNom(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="regAge" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Âge
                  </label>
                  <input
                    id="regAge"
                    type="number"
                    placeholder="25"
                    value={regAge}
                    onChange={(e) => setRegAge(e.target.value === "" ? "" : Number(e.target.value))}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="regTaille" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Taille (cm)
                  </label>
                  <input
                    id="regTaille"
                    type="number"
                    placeholder="180"
                    value={regTaille}
                    onChange={(e) => setRegTaille(e.target.value === "" ? "" : Number(e.target.value))}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="regSport" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Sport Préféré
                  </label>
                  <select
                    id="regSport"
                    value={regSport}
                    onChange={(e) => setRegSport(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  >
                    <option value="Football">Football</option>
                    <option value="Basketball">Basketball</option>
                    <option value="Tennis">Tennis</option>
                    <option value="Handball">Handball</option>
                    <option value="Rugby">Rugby</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="regNiveau" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Niveau
                  </label>
                  <select
                    id="regNiveau"
                    value={regNiveau}
                    onChange={(e) => setRegNiveau(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  >
                    <option value="Débutant">Débutant</option>
                    <option value="Intermédiaire">Intermédiaire</option>
                    <option value="Avancé">Avancé</option>
                    <option value="Expert">Expert</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="regQuartier" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Quartier
                  </label>
                  <input
                    id="regQuartier"
                    type="text"
                    placeholder="ex: Cocody"
                    value={regQuartier}
                    onChange={(e) => setRegQuartier(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="regCat" className="block text-[11px] font-bold text-primary uppercase tracking-wider mb-1">
                    Catégorie
                  </label>
                  <select
                    id="regCat"
                    value={regCategorie}
                    onChange={(e) => setRegCategorie(e.target.value)}
                    className="w-full bg-brand-cream/40 border border-primary/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-body-md outline-none transition-all"
                  >
                    <option value="Loisir">Loisir</option>
                    <option value="Senior">Senior</option>
                    <option value="Junior">Junior</option>
                    <option value="Vétéran">Vétéran</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={regLoading}
                className="w-full bg-secondary hover:bg-secondary/95 text-white font-bold py-3 rounded-lg uppercase tracking-wider text-label-md transition-all active:scale-98 shadow-md flex items-center justify-center gap-2 mt-2"
              >
                {regLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Création du compte...
                  </>
                ) : (
                  "Créer mon compte"
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}
