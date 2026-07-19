import React, { useState } from 'react';
import { signIn } from '../api/client';
import { ShieldAlert, Lock, Mail, ArrowRight, CornerDownLeft, Activity } from 'lucide-react';

export default function Login({ onLoginSuccess, onViewSwitch }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const data = await signIn(email, password);
      if (data?.session) {
        onLoginSuccess(data.session);
      } else {
        setError('Login succeeded but session could not be established.');
      }
    } catch (err) {
      console.error('Login error:', err);
      // Friendly messages based on standard Supabase auth responses
      if (err.message?.includes('Invalid login credentials') || err.message?.includes('Invalid credentials')) {
        setError('Incorrect email or password. Please try again.');
      } else {
        setError(err.message || 'An error occurred during sign-in.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 relative overflow-hidden font-sans">
      {/* Decorative background grid and glowing circles */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-60"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-emerald-500/10 blur-[128px]"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-blue-500/10 blur-[128px]"></div>

      {/* Main Container */}
      <div className="w-full max-w-md z-10 transition-all duration-300">
        
        {/* Logo/Branding */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-4 border border-emerald-400/20 animate-pulse">
            <ShieldAlert className="w-8 h-8 text-slate-950" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-blue-400 bg-clip-text text-transparent">
            VayuSetu
          </h1>
          <p className="text-xs font-semibold text-emerald-400 uppercase tracking-widest mt-1 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 animate-bounce" /> Authority enforcement panel
          </p>
        </div>

        {/* Card */}
        <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 p-8 rounded-3xl shadow-2xl relative">
          
          <h2 className="text-xl font-bold text-slate-100 mb-2">Authority Portal Login</h2>
          <p className="text-xs text-slate-400 mb-6">
            Enter your environmental officer credentials to access protected enforcement actions.
          </p>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-xs p-3.5 rounded-xl flex items-start gap-2.5">
                <span className="font-bold text-red-500">Error:</span>
                <span>{error}</span>
              </div>
            )}

            {/* Email Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300" htmlFor="email">
                Official Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@cpcb.gov.in"
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition duration-200"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300" htmlFor="password">
                Security Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition duration-200"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 text-sm font-bold rounded-xl hover:opacity-90 active:scale-[0.98] transition-all duration-150 flex items-center justify-center gap-2 group disabled:opacity-50 disabled:pointer-events-none shadow-lg shadow-emerald-500/15"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                  <span>Verifying Session...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center my-6">
            <div className="flex-grow border-t border-slate-800/80"></div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-600 px-3">Public Access</span>
            <div className="flex-grow border-t border-slate-800/80"></div>
          </div>

          {/* Return button */}
          <button
            onClick={() => onViewSwitch('citizen')}
            className="w-full py-3 bg-slate-950/40 hover:bg-slate-950/80 border border-slate-800/50 hover:border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold rounded-xl transition duration-150 flex items-center justify-center gap-2"
          >
            <CornerDownLeft className="w-3.5 h-3.5" />
            <span>Return to Citizen Portal</span>
          </button>
        </div>

        {/* Info footer */}
        <p className="text-center text-[10px] text-slate-600 mt-6 max-w-sm mx-auto leading-relaxed">
          Access is monitored. Unauthorized attempts to modify environmental violation records are subject to prosecution under the IT Act.
        </p>

      </div>
    </div>
  );
}
