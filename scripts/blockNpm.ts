#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import process from 'process';

if (process.env.npm_config_user_agent && process.env.npm_config_user_agent.startsWith('npm')) {
  const file = path.resolve(import.meta.dirname, 'amnesia-counter.txt');
  const count = fs.existsSync(file) ? parseInt(fs.readFileSync(file, 'utf8'), 10) : 0;
  fs.writeFileSync(file, String(count + 1), 'utf8');
  console.error(
    `This project uses Yarn. Running via npm is blocked. Agent fucked up count: ${count + 1}`,
  );
  process.exit(1);
}

process.exit(0);
