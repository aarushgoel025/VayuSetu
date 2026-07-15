import React from 'react';
import { motion } from 'framer-motion';
import { Globe } from './ui/globe';
import { Wind, Activity, Users, ShieldAlert, Cpu } from 'lucide-react';

export default function LandingSequence() {
  const fadeUp = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
  };

  return (
    <>
      {/* 1. Hero / Globe Section */}
      <section className="h-screen w-full snap-start relative flex items-center justify-center overflow-hidden bg-slate-950">
        {/* Globe takes up the background */}
        <div className="absolute inset-0 pointer-events-auto z-0 flex items-center justify-center">
          <Globe />
        </div>

        {/* Text floating on top */}
        <div className="z-10 text-center flex flex-col items-center pointer-events-none px-4">
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            className="bg-slate-950/40 border border-white/10 backdrop-blur-md p-8 md:p-12 rounded-3xl shadow-[0_0_50px_rgba(0,0,0,0.8)] max-w-xl"
          >
            <div className="flex items-center justify-center gap-3 mb-4">
              <Wind className="w-10 h-10 text-blue-400 animate-pulse" />
              <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-blue-400 via-indigo-400 to-indigo-500">
                VayuSetu
              </h1>
            </div>
            <p className="text-lg md:text-xl text-slate-300 font-light tracking-wide leading-relaxed">
              Bridging the gap between Clean Air and Policy Action
            </p>
          </motion.div>
        </div>
        
        {/* Scroll indicator */}
        <motion.div 
          className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center text-slate-400 z-10"
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <span className="text-xs tracking-widest uppercase mb-2">Scroll to explore</span>
          <div className="w-[1px] h-12 bg-gradient-to-b from-slate-400 to-transparent"></div>
        </motion.div>
      </section>

      {/* 2. Story Section */}
      <section className="h-screen w-full snap-start flex flex-col items-center justify-center bg-slate-900 relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-800/50 via-slate-900 to-slate-950 pointer-events-none"></div>
        <motion.div 
          className="max-w-4xl px-8 z-10 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: false, amount: 0.5 }}
          variants={fadeUp}
        >
          <h2 className="text-5xl font-bold mb-8 text-blue-400">Our Story</h2>
          <p className="text-2xl leading-relaxed text-slate-300 font-light">
            Delhi has battled toxic air for decades. Traditional monitoring relies on delayed, scattered data and reactive measures. 
            <br/><br/>
            <strong className="text-white font-medium">VayuSetu changes the paradigm.</strong> We built an integrated intelligence bridge that transforms raw pollution data into actionable forecasting and enforcement.
          </p>
        </motion.div>
      </section>

      {/* 3. Features Section */}
      <section className="h-screen w-full snap-start flex flex-col items-center justify-center bg-slate-950">
        <motion.div 
          className="max-w-6xl w-full px-8"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: false, amount: 0.4 }}
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.2 } }
          }}
        >
          <motion.h2 variants={fadeUp} className="text-5xl font-bold mb-16 text-center text-indigo-400">
            Core Intelligence
          </motion.h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div variants={fadeUp} className="bg-slate-900/50 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
              <Cpu className="w-12 h-12 text-blue-500 mb-6" />
              <h3 className="text-2xl font-semibold mb-4 text-white">Predictive AI</h3>
              <p className="text-slate-400 leading-relaxed">
                A custom-built Ensemble AI model that predicts AQI trends 24 hours in advance with near 90% accuracy, shifting the city from reactive to proactive.
              </p>
            </motion.div>
            
            <motion.div variants={fadeUp} className="bg-slate-900/50 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
              <Activity className="w-12 h-12 text-emerald-500 mb-6" />
              <h3 className="text-2xl font-semibold mb-4 text-white">Carbon Footprints</h3>
              <p className="text-slate-400 leading-relaxed">
                Real-time tracking of localized vehicular emissions based on fleet makeup, directly connecting traffic patterns to pollution metrics.
              </p>
            </motion.div>
            
            <motion.div variants={fadeUp} className="bg-slate-900/50 p-8 rounded-2xl border border-slate-800 backdrop-blur-sm">
              <ShieldAlert className="w-12 h-12 text-rose-500 mb-6" />
              <h3 className="text-2xl font-semibold mb-4 text-white">Legal Advisory</h3>
              <p className="text-slate-400 leading-relaxed">
                Automated legal notice generation for industrial violators, instantly converting satellite hotspot detections into official compliance actions.
              </p>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* 4. Target Audience Section */}
      <section className="h-screen w-full snap-start flex flex-col items-center justify-center bg-slate-900 relative">
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent"></div>
        <motion.div 
          className="max-w-5xl px-8 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: false, amount: 0.5 }}
          variants={fadeUp}
        >
          <Users className="w-16 h-16 text-blue-400 mx-auto mb-8" />
          <h2 className="text-5xl font-bold mb-8 text-white">Who is this for?</h2>
          <div className="flex flex-col md:flex-row gap-12 text-left justify-center mt-12">
            <div className="flex-1">
              <h4 className="text-xl font-semibold text-blue-400 mb-3 border-b border-slate-700 pb-2">For Authorities</h4>
              <p className="text-slate-400 leading-relaxed">
                A unified command center to enforce GRAP regulations, monitor industrial hotspots, and direct municipal resources where they are needed most before an emergency strikes.
              </p>
            </div>
            <div className="flex-1">
              <h4 className="text-xl font-semibold text-emerald-400 mb-3 border-b border-slate-700 pb-2">For Citizens</h4>
              <p className="text-slate-400 leading-relaxed">
                A hyper-local dashboard tracking neighborhood air quality, vulnerable zones like hospitals, and actionable health advisories tailored to the immediate surroundings.
              </p>
            </div>
          </div>
        </motion.div>
      </section>
    </>
  );
}
