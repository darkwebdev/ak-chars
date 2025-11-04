import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';
import jpegJs from 'jpeg-js';
import * as iq from 'image-q';
import UPNG from 'upng-js';

export async function optimizeImage(
  filePath: string,
  writeToDir: string = path.resolve(process.cwd(), 'public', 'images'),
  outputFormat: 'jpg' | 'png' = 'png',
): Promise<boolean> {
  const ext = path.extname(filePath).toLowerCase();
  const base = path.basename(filePath, ext);
  const input = filePath;
  const outputExt = outputFormat === 'png' ? '.png' : '.jpg';
  const output = path.join(writeToDir, `${base}${outputExt}`);
  if (ext === '.jpg' || ext === '.jpeg') return false;

  try {
    // If the output already exists, remove it so we overwrite
    try {
      if (fs.existsSync(output)) fs.unlinkSync(output);
    } catch (_) {
      // ignore removal errors and proceed
    }
    if (ext === '.png') {
      const inputBuf = fs.readFileSync(input);
      const png = PNG.sync.read(inputBuf) as { data: Buffer; width: number; height: number };
      const { data, width, height } = png;

      if (outputFormat === 'png') {
        // Apply color quantization and convert to indexed PNG for maximum compression
        const pointContainer = iq.utils.PointContainer.fromUint8Array(data, width, height);

        // Use 256 colors for indexed PNG
        const palette = await iq.buildPalette([pointContainer], {
          colors: 256,
        });

        const outPointContainer = await iq.applyPalette(pointContainer, palette);
        const quantizedData = outPointContainer.toUint8Array();

        // Use UPNG to encode as indexed PNG with better compression
        // @ts-ignore - UPNG types are incomplete
        const encoded = UPNG.encode([quantizedData.buffer], width, height, 256);
        const buffer = Buffer.from(encoded);

        fs.mkdirSync(path.dirname(output), { recursive: true });
        fs.writeFileSync(output, buffer);

        const inputSize = inputBuf.length;
        const outputSize = buffer.length;
        const savingsPercent = (((inputSize - outputSize) / inputSize) * 100).toFixed(1);
        console.log(`Wrote PNG ${output} (${outputSize} bytes, ${savingsPercent}% savings)`);

        return true;
      }

      // Convert to JPG
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
