import createGlobe from "cobe"
import { useEffect, useRef, useState, useCallback } from "react"
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

const GLOBE_CONFIG = {
  devicePixelRatio: 2,
  phi: 0,
  theta: 0.3,
  dark: 1, 
  diffuse: 1.2,
  mapSamples: 16000,
  mapBrightness: 2.0, 
  baseColor: [0.3, 0.4, 0.6], 
  markerColor: [251 / 255, 100 / 255, 21 / 255], 
  glowColor: [0.4, 0.5, 0.8], 
  markers: [
    { location: [28.6139, 77.2090], size: 0.1 }, 
  ],
}

export function Globe({ className }) {
  const canvasRef = useRef(null)
  const pointerInteracting = useRef(null)
  const pointerInteractionMovement = useRef(0)
  const rRef = useRef(0)
  const phiRef = useRef(0)

  const updatePointerInteraction = (value) => {
    pointerInteracting.current = value
    if (canvasRef.current) {
      canvasRef.current.style.cursor = value ? "grabbing" : "grab"
    }
  }

  const updateMovement = (clientX) => {
    if (pointerInteracting.current !== null) {
      const delta = clientX - pointerInteracting.current
      pointerInteractionMovement.current = delta
      rRef.current = delta / 200
    }
  }

  useEffect(() => {
    let width = 600
    if (canvasRef.current) {
      width = canvasRef.current.offsetWidth || 600
    }

    const globe = createGlobe(canvasRef.current, {
      ...GLOBE_CONFIG,
      width: width * 2,
      height: width * 2,
      onRender: (state) => {
        if (!pointerInteracting.current) {
          phiRef.current += 0.003
        }
        state.phi = phiRef.current + rRef.current
        state.width = width * 2
        state.height = width * 2
      },
    })

    setTimeout(() => {
      if (canvasRef.current) {
        canvasRef.current.style.opacity = "1"
      }
    }, 100)

    return () => {
      globe.destroy()
    }
  }, [])

  return (
    <div className={cn("relative flex items-center justify-center w-full h-full", className)}>
      <canvas
        ref={canvasRef}
        style={{
          width: "100%",
          height: "100%",
          maxWidth: 600,
          maxHeight: 600,
          aspectRatio: 1,
          opacity: 0,
          transition: "opacity 1s ease",
        }}
        onPointerDown={(e) =>
          updatePointerInteraction(
            e.clientX - pointerInteractionMovement.current
          )
        }
        onPointerUp={() => updatePointerInteraction(null)}
        onPointerOut={() => updatePointerInteraction(null)}
        onMouseMove={(e) => updateMovement(e.clientX)}
        onTouchMove={(e) =>
          e.touches[0] && updateMovement(e.touches[0].clientX)
        }
      />
    </div>
  )
}
