import { createContext, useContext } from 'react';
import { useAuth as useClerkAuth, useUser } from '@clerk/react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { isLoaded, isSignedIn, getToken, signOut } = useClerkAuth();
  const { user: clerkUser } = useUser();
  const user = clerkUser ? {
    id: clerkUser.id,
    name: clerkUser.fullName || clerkUser.primaryEmailAddress?.emailAddress || 'Task manager user',
    email: clerkUser.primaryEmailAddress?.emailAddress || '',
  } : null;
  return (
    <AuthContext.Provider value={{ user: isSignedIn ? user : null, loading: !isLoaded, getToken, logout: signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
