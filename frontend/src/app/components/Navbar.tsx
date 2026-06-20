"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

interface LoggedUser {
  phone_number: string;
  prenom: string | null;
  nom: string | null;
}

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<LoggedUser | null>(null);

  useEffect(() => {
    const checkUserSession = () => {
      if (typeof window !== "undefined") {
        const stored = localStorage.getItem("sportmeet_user");
        if (stored) {
          try {
            setCurrentUser(JSON.parse(stored));
          } catch (e) {
            console.error(e);
          }
        } else {
          setCurrentUser(null);
        }
      }
    };

    checkUserSession();
    
    // Listen for storage events in case session updates in other tabs
    window.addEventListener("storage", checkUserSession);
    return () => window.removeEventListener("storage", checkUserSession);
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem("sportmeet_user");
    setCurrentUser(null);
    router.push("/login");
    setTimeout(() => {
      window.location.reload();
    }, 100);
  };

  return (
    <header className="bg-brand-page shadow-sm sticky top-0 z-50 border-b border-brand-border/40">
      <nav className="flex justify-between items-center w-full px-4 md:px-[80px] max-w-[1280px] mx-auto h-16">
        <Link href="/" className="font-headline text-headline-md text-primary font-bold tracking-tight">
          Wasportly
        </Link>
        
        {/* Navigation Links */}
        <div className="hidden md:flex gap-8 items-center h-full">
          <Link
            href="/"
            className={`font-body-md text-body-md transition-all h-full flex items-center border-b-2 ${
              pathname === "/"
                ? "text-primary border-primary font-semibold"
                : "text-on-surface-variant hover:text-primary border-transparent"
            }`}
          >
            Discover
          </Link>
          <Link
            href="/activities"
            className={`font-body-md text-body-md transition-all h-full flex items-center border-b-2 ${
              pathname === "/activities"
                ? "text-primary border-primary font-semibold"
                : "text-on-surface-variant hover:text-primary border-transparent"
            }`}
          >
            Activities
          </Link>
          <Link
            href="#"
            className={`font-body-md text-body-md transition-all h-full flex items-center border-b-2 ${
              pathname === "/messages"
                ? "text-primary border-primary font-semibold"
                : "text-on-surface-variant hover:text-primary border-transparent"
            }`}
          >
            Messages
          </Link>
          {currentUser && (
            <Link
              href={`/profile?phone=${currentUser.phone_number}`}
              className={`font-body-md text-body-md transition-all h-full flex items-center border-b-2 ${
                pathname === "/profile"
                  ? "text-primary border-primary font-semibold"
                  : "text-on-surface-variant hover:text-primary border-transparent"
              }`}
            >
              Profile
            </Link>
          )}
        </div>

        {/* Profile Action Link or Login button */}
        <div className="flex items-center gap-4">
          {currentUser ? (
            <div className="flex items-center gap-4">
              <Link 
                href={`/profile?phone=${currentUser.phone_number}`}
                className={`flex items-center gap-2 font-body-md text-body-md text-primary font-bold hover:opacity-85 transition-all py-1 ${
                  pathname === "/profile" ? "border-b-2 border-primary" : ""
                }`}
              >
                <span className="material-symbols-outlined">person</span>
                <span className="hidden sm:inline">{currentUser.prenom || "Profil"}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 font-body-md text-body-md text-red-600 hover:text-red-700 font-bold transition-all py-1 outline-none"
                title="Déconnexion"
              >
                <span className="material-symbols-outlined text-[20px]">logout</span>
                <span className="hidden sm:inline">Déconnexion</span>
              </button>
            </div>
          ) : (
            <Link 
              href="/login"
              className={`flex items-center gap-2 font-body-md text-body-md text-primary font-bold hover:opacity-85 transition-all py-1 border border-primary/20 px-3.5 py-1.5 rounded-lg bg-primary/5 ${
                pathname === "/login" ? "bg-primary text-white border-primary" : ""
              }`}
            >
              <span className="material-symbols-outlined">login</span>
              <span>Connexion</span>
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
