'use client';

import { createContext, ReactNode, useContext, useState } from 'react';
import { redirect } from 'next/navigation';
import { createClient } from '../../utils/supabase/client';

interface AuthContextType {
  userEmail: string | null;
  setUserEmail: (userEmail: string | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userEmail, setUserEmail] = useState<string | null>(null);

  const logout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    setUserEmail(null); // Update state
    redirect('/');
  };

  return (
    <AuthContext.Provider value={{ userEmail, setUserEmail, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
