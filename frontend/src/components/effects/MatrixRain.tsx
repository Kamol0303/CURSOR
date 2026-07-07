"use client";

import { useEffect, useRef } from "react";

const MATRIX_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*+-/~{[|`]}";

type MatrixRainProps = {
  color?: string;
  opacity?: number;
};

export function MatrixRain({ color = "#1b4d3e", opacity = 0.12 }: MatrixRainProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) return;

    let animationId = 0;
    let intervalId: ReturnType<typeof setInterval> | null = null;
    const fontSize = 10;
    let drops: number[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const columns = Math.ceil(canvas.width / fontSize);
      drops = Array.from({ length: columns }, () => Math.floor(Math.random() * -20));
    };

    const draw = () => {
      ctx.fillStyle = "rgba(0, 0, 0, 0.04)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = color;
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const text = MATRIX_CHARS[Math.floor(Math.random() * MATRIX_CHARS.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }
    };

    resize();
    intervalId = setInterval(draw, 35);
    window.addEventListener("resize", resize);

    return () => {
      if (intervalId) clearInterval(intervalId);
      cancelAnimationFrame(animationId);
      window.removeEventListener("resize", resize);
    };
  }, [color]);

  return (
    <canvas
      ref={canvasRef}
      className="cyber-matrix-rain"
      style={{ opacity }}
      aria-hidden
    />
  );
}
