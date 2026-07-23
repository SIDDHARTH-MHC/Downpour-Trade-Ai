/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f1419",
        panel: "#1a2332",
        border: "#2d3748",
        long: "#22c55e",
        short: "#ef4444",
        muted: "#94a3b8",
      },
    },
  },
  plugins: [],
};
