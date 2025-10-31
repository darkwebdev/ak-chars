import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';
import jpegJs from 'jpeg-js';

export async function optimizeImage(
  file: string,
  readFromDir: string,
  writeToDir: string = path.resolve(process.cwd(), 'public', 'images'),
): Promise<boolean> {
  console.log('optimizeImage:', file);
  const ext = path.extname(file).toLowerCase();
  const base = path.basename(file, ext);
  const input = path.join(readFromDir, file);
  // Always write JPG output to public/images unless user specifically points there
  const output = path.join(writeToDir, `${base}.jpg`);
  if (ext === '.jpg' || ext === '.jpeg') return false;
  // If the public output already exists, nothing to do
  if (fs.existsSync(output)) return false;

  try {
    if (ext === '.png') {
      console.log('reading PNG', input);
      const inputBuf = fs.readFileSync(input);
      const png = PNG.sync.read(inputBuf) as { data: Buffer; width: number; height: number };
      console.log('png read OK', { width: png.width, height: png.height });
      const { data, width, height } = png;
      // jpeg-js expects RGB pixel data (no alpha). Strip alpha channel if present.
      const rgb = Buffer.allocUnsafe((data.length / 4) * 3);
      for (let i = 0, j = 0; i < data.length; i += 4, j += 3) {
        rgb[j] = data[i];
        rgb[j + 1] = data[i + 1];
        rgb[j + 2] = data[i + 2];
      }
      const encoded = jpegJs.encode({ data: rgb, width, height }, 80);
      // ensure public/images output dir exists and write there
      fs.mkdirSync(path.dirname(output), { recursive: true });
      fs.writeFileSync(output, encoded.data);
      console.log('wrote JPG', output);
      return true;
    }

    console.warn('unsupported format for conversion:', input);
    return false;
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error('Failed to convert', input, msg);
    return false;
  }
}

export default async function optimise(dirArg?: string) {
  const dirToUse = dirArg || process.argv[2];
  if (!dirToUse) {
    console.error('Usage: ts-node optimiseImages.ts <imagesDir>');
    return 0;
  }
  if (!fs.existsSync(dirToUse)) {
    console.error('Images directory not found:', dirToUse);
    return 0;
  }
  const files = fs.readdirSync(dirToUse);
  let convertedCount = 0;
  for (const f of files) {
    const ext = path.extname(f).toLowerCase();
    if (['.png', '.webp', '.gif', '.jpeg'].includes(ext)) {
      // eslint-disable-next-line no-await-in-loop
      const ok = await optimizeImage(f, dirToUse);
      if (ok) convertedCount += 1;
      else console.log('Skipped', f);
    }
  }
  console.log(`Optimiser: converted ${convertedCount} file(s) in ${dirToUse}`);
  return convertedCount;
}
