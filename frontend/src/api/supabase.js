import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

let client;
try {
  if (supabaseUrl && supabaseAnonKey) {
    client = createClient(supabaseUrl, supabaseAnonKey);
  } else {
    throw new Error('Supabase URL and Anon Key are missing');
  }
} catch (e) {
  console.warn('Initializing fallback dummy Supabase client:', e.message);
  client = {
    auth: {
      getSession: async () => ({ data: { session: null } }),
      onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
      signInWithPassword: async () => ({ data: { user: null }, error: new Error('Supabase not configured') }),
      signOut: async () => ({ error: null }),
    }
  };
}

export const supabase = client;
