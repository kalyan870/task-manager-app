import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ClerkProvider } from '@clerk/react';
import App from './App';
import './index.css';

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(publishableKey ? (
  <React.StrictMode>
    <ClerkProvider publishableKey={publishableKey} signInFallbackRedirectUrl="/" signUpFallbackRedirectUrl="/">
      <BrowserRouter><App /></BrowserRouter>
    </ClerkProvider>
  </React.StrictMode>
) : (
  <main role="alert" style={{ fontFamily: 'system-ui', maxWidth: 680, margin: '12vh auto', padding: 24 }}>
    <h1>TaskManager setup needed</h1>
    <p>Add <code>VITE_CLERK_PUBLISHABLE_KEY</code> to the client environment, then configure the server Clerk and Neon variables.</p>
  </main>
));
