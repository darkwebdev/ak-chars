import fs from 'fs';
import path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  // for GitHub Pages
  base: '/ak-chars/',
  // Copy files from the repo-level `public` directory into `dist` during build
  publicDir: path.resolve(__dirname, 'public'),
  root: path.resolve(__dirname, 'src', 'client'),
  plugins: [
    react(),
    {
      name: 'serve-data-directory',
      configureServer(server) {
        server.middlewares.use('/avatars', (req, res, next) => {
          const filePath = path.join(__dirname, 'public', 'avatars', req.url || '');

          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath).toLowerCase();
            const mimeTypes: Record<string, string> = {
              '.json': 'application/json',
              '.jpg': 'image/jpeg',
              '.jpeg': 'image/jpeg',
              '.png': 'image/png',
              '.webp': 'image/webp',
            };

            res.setHeader('Content-Type', mimeTypes[ext] || 'application/octet-stream');
            fs.createReadStream(filePath).pipe(res);
            return;
          }

          res.statusCode = 404;
          res.end('Not Found');
        });
      },
    },
  ],
  server: {
    port: 5193,
    fs: {
      allow: ['..', '../..'],
    },
  },
  build: {
    outDir: path.resolve(__dirname, 'dist'),
  },
});
