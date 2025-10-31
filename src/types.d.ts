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
