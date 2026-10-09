import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    server: {
      port: 3000,
      open: false,
      proxy: mode === 'development' ? {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        }
      } : undefined
    },
    build: {
      outDir: 'dist',
    }
  };
});
