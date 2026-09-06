import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api.js";

const Ctx = createContext({ user: null, token: null, login: async () => {}, logout: () => {} });
const KEY = "mplads.session";

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    try {
      const raw = localStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    try {
      if (session) localStorage.setItem(KEY, JSON.stringify(session));
      else localStorage.removeItem(KEY);
    } catch {
      /* private mode — the session simply won't survive a reload */
    }
    // Every later request carries the token, so a scoped officer sees only their own works.
    api.setToken(session?.token || null);
  }, [session]);

  // The API is the authority on whether a token still works. When it rejects one, the
  // session chip must stop claiming the officer is signed in — otherwise the header says
  // "Bihar State Nodal Officer" while every scoped request is being refused.
  useEffect(() => {
    const onExpired = () => setSession(null);
    window.addEventListener("mplads:session-expired", onExpired);
    return () => window.removeEventListener("mplads:session-expired", onExpired);
  }, []);

  const value = {
    user: session?.user || null,
    token: session?.token || null,
    async login(username, password) {
      const res = await api.login(username, password);
      setSession({ token: res.token, user: res.user });
      return res.user;
    },
    logout() {
      setSession(null);
    },
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useAuth = () => useContext(Ctx);
