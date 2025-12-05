import React from 'react';
import { Meta } from '@storybook/react';
import themeRaw from '../theme/styles.css?raw';
import '../styles.css';
import './design-system.css';

function generateTokenList(): string[] {
  const cssText = typeof themeRaw === 'string' ? themeRaw : '';
  if (!cssText) {
    return [];
  }

  const regex = /(--[a-zA-Z0-9-_]+)\s*:/g;
  const found = new Set<string>();
  let m: RegExpExecArray | null;
  while ((m = regex.exec(cssText)) !== null) {
    found.add(m[1]);
  }

  return Array.from(found);
}

const TokenSwatch = ({ name }: { name: string }) => (
  <div className="ds-token-swatch-wrapper">
    <div aria-hidden className="ds-token-swatch" style={{ background: `var(${name})` }} />
    <code className="ds-token-code">{name}</code>
  </div>
);

const TokenGrid = () => (
  <div className="ds-token-grid">
    {generateTokenList().map((t) => (
      <div key={t} className="ds-token-item">
        <TokenSwatch name={t} />
      </div>
    ))}
  </div>
);

const DocsPage: React.FC = () => {
  return (
    <div className="ds-container">
      <section className="ds-typography">
        <h1 className="ds-heading-h1">Heading H1 — Arknights Operactors</h1>
        <h2 className="ds-heading-h2">Heading H2 — Component Title</h2>
        <h3 className="ds-heading-h3">Heading H3 — Subsection</h3>
        <p className="ds-body">
          This is body copy demonstrating the default paragraph style.{' '}
          <span className="muted">Muted text</span> shows a subdued color.
        </p>
      </section>
    </div>
  );
};

const meta: Meta = {
  title: 'Design System',
};

export const Typography = () => <DocsPage />;

export const Colors = () => <TokenGrid />;

export default meta;
