import { jwtDecode } from "jwt-decode";

const AUTH_STORAGE_KEY = "qsai.auth_token";
const USER_EMAIL_KEY = "qsai.userEmail";
const USER_NAME_KEY = "qsai.userName";

interface GoogleTokenPayload {
  email: string;
  name: string;
  picture?: string;
}

export const getIsAuthenticated = (): boolean => {
  const token = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!token) return false;
  try {
    const decoded = jwtDecode<{ exp?: number }>(token);
    if (decoded.exp && decoded.exp < Date.now() / 1000) {
      clearAuthentication();
      return false;
    }
    return true;
  } catch {
    clearAuthentication();
    return false;
  }
};

export const setAuthenticationFromGoogle = (token: string): void => {
  try {
    const decoded = jwtDecode<GoogleTokenPayload>(token);
    localStorage.setItem(AUTH_STORAGE_KEY, token);
    localStorage.setItem(USER_EMAIL_KEY, decoded.email);
    localStorage.setItem(USER_NAME_KEY, decoded.name);
  } catch (error) {
    console.error("Failed to decode token", error);
    throw error;
  }
};

export const getUserEmail = (): string | null => {
  return localStorage.getItem(USER_EMAIL_KEY);
};

export const getUserName = (): string | null => {
  return localStorage.getItem(USER_NAME_KEY);
};

export const getAuthToken = (): string | null => {
  const stored = localStorage.getItem(AUTH_STORAGE_KEY);
  if (stored) return stored;
  
  // In development, return a dummy token to allow testing without Google OAuth
  if (import.meta.env.MODE === "development" || import.meta.env.DEV) {
    return "dev-token-for-testing";
  }
  
  return null;
};

export const clearAuthentication = (): void => {
  localStorage.removeItem(AUTH_STORAGE_KEY);
  localStorage.removeItem(USER_EMAIL_KEY);
  localStorage.removeItem(USER_NAME_KEY);
};

export { AUTH_STORAGE_KEY };
