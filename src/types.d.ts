export interface RawChar {
  name?: string;
  appellation?: string;
  rarity?: string | null;
  profession?: string;
  subProfessionId?: string;
  isNotObtainable?: boolean;
  position?: string;
  tagList?: string[];
  traitList?: string[];
  skillList?: unknown[];
  avatarId?: string;
  entityId?: string;
  displayNumber?: string;
  description?: string;
  releaseDate?: string;
  [k: string]: unknown;
}

export type Char = {
  id: string;
  name?: string | null;
  rarity?: string | null;
  profession?: string | null;
  subProfessionId?: string | null;
};

declare module '*.json' {
  const value: unknown;
  export default value;
}

export type Profession = (typeof Professions)[number];

export type Rarity = 'TIER_1' | 'TIER_2' | 'TIER_3' | 'TIER_4' | 'TIER_5' | 'TIER_6';

// Allow importing SVGs as React components (svgr / vite-plugin-svgr)
declare module '*.svg' {
  import type { FunctionComponent, SVGProps } from 'react';
  const SvgComponent: FunctionComponent<SVGProps<SVGSVGElement>>;
  export default SvgComponent;
  export { SvgComponent as ReactComponent };
}
