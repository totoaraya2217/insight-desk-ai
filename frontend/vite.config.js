import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El navegador solo llama a /api; Vite lo reenvía al backend. Gemini nunca se invoca desde aquí.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": process.env.API_TARGET || "http://127.0.0.1:8000" },
  },
  build: {
    rollupOptions: {
      output: {
        // Dependencias separadas por librería: el código de la app queda liviano y cada parte se cachea aparte.
        manualChunks(id) {
          if (!id.includes("node_modules")) return;
          if (/[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/.test(id)) return "react";
          if (/[\\/]node_modules[\\/](d3-[^\\/]+|internmap|victory-vendor)[\\/]/.test(id)) return "d3";
          if (/[\\/]node_modules[\\/]lodash[\\/]/.test(id)) return "lodash";
          if (/[\\/]node_modules[\\/]recharts[\\/]/.test(id)) return "recharts";
          return "vendor";
        },
      },
    },
  },
});
