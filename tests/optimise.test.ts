import fs from 'fs';
import os from 'os';
import path from 'path';
import { PNG } from 'pngjs';
import optimise from '../src/server/optimiseImages';

describe('optimiseImages', () => {
  it('converts PNG to JPG in a directory', async () => {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ak-chars-test-'));
    const avatarsDir = path.join(tmp, 'avatars');
    fs.mkdirSync(avatarsDir, { recursive: true });

    // create a small 2x2 RGBA PNG
    const png = new PNG({ width: 2, height: 2 });
    for (let i = 0; i < png.data.length; i += 4) {
      png.data[i] = 0xff; // R
      png.data[i + 1] = 0x00; // G
      png.data[i + 2] = 0x00; // B
      png.data[i + 3] = 0xff; // A
    }
    const buf = PNG.sync.write(png);
    const fname = path.join(avatarsDir, 'test.png');
    fs.writeFileSync(fname, buf);

    const publicJpg = path.join(process.cwd(), 'public', 'images', 'test.jpg');
    // ensure no leftover from previous runs
    try {
      if (fs.existsSync(publicJpg)) fs.unlinkSync(publicJpg);
    } catch (_) {}

    const converted = await optimise(avatarsDir);
    expect(converted).toBeGreaterThanOrEqual(1);

    const jpgPath = path.join(process.cwd(), 'public', 'images', 'test.jpg');
    expect(fs.existsSync(jpgPath)).toBe(true);

    // cleanup
    try {
      if (fs.existsSync(publicJpg)) fs.unlinkSync(publicJpg);
      fs.unlinkSync(fname);
      fs.rmdirSync(avatarsDir);
      fs.rmdirSync(tmp);
    } catch (_) {
      // ignore
    }
  }, 20000);
});
