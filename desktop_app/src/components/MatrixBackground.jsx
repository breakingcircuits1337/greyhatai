import React, { useRef, useEffect } from "react";

const CHARACTERS = "アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズヅブプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッンABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
const FONT_SIZE = 18;
const SPEED = 1.1;

export default function MatrixBackground() {
  const canvasRef = useRef();
  const animationId = useRef();
  const columns = useRef([]);
  const width = useRef(window.innerWidth);
  const height = useRef(window.innerHeight);

  // Resize handler
  function resizeCanvas() {
    const canvas = canvasRef.current;
    width.current = window.innerWidth;
    height.current = window.innerHeight;
    canvas.width = width.current;
    canvas.height = height.current;
    columns.current = Array.from({ length: Math.floor(width.current / FONT_SIZE) }, () => 1 + Math.random() * 10);
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    function draw() {
      ctx.fillStyle = "rgba(0,0,0,0.20)";
      ctx.fillRect(0, 0, width.current, height.current);

      ctx.font = `${FONT_SIZE}px 'Share Tech Mono', monospace`;
      ctx.fillStyle = "#00ff41";

      columns.current.forEach((y, idx) => {
        const char = CHARACTERS.charAt(Math.floor(Math.random() * CHARACTERS.length));
        const x = idx * FONT_SIZE;
        ctx.fillText(char, x, y * FONT_SIZE);

        if (y * FONT_SIZE > height.current && Math.random() > 0.975) {
          columns.current[idx] = 0;
        } else {
          columns.current[idx] += SPEED;
        }
      });

      animationId.current = requestAnimationFrame(draw);
    }

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    draw();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId.current);
    };
    // eslint-disable-next-line
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="matrix-animation"
      style={{
        position: "fixed",
        top: 0, left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: 0,
        pointerEvents: "none"
      }}
      width={window.innerWidth}
      height={window.innerHeight}
      aria-hidden="true"
    />
  );
}