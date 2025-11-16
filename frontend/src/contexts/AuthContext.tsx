import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { signup as apiSignup, signin as apiSignin } from '../services/api';
import type { SignupRequest, LoginRequest } from '../types';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if token exists on mount
    const token = localStorage.getItem('auth_token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  const login = async (data: LoginRequest) => {
    const response = await apiSignin(data);
    localStorage.setItem('auth_token', response.token);
    setIsAuthenticated(true);
  };

  const signup = async (data: SignupRequest) => {
    const response = await apiSignup(data);
    localStorage.setItem('auth_token', response.token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
