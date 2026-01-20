import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

// Mock graphqlClient to avoid import.meta issues
jest.mock('../src/client/utils/graphqlClient');

import { App } from '../src/client/App';

beforeEach(() => {
  // clear localStorage between tests
  localStorage.clear();
});

test('clicking a card toggles owned and persists to localStorage', async () => {
  render(<App />);

  // Wait for at least one card to be rendered
  const cards = await screen.findAllByRole('button');
  // Find the first card that has aria-pressed attribute (character cards)
  const card = cards.find(button => button.hasAttribute('aria-pressed'));
  if (!card) throw new Error('No character card rendered');

  // Initially not owned
  expect(card.getAttribute('aria-pressed')).toBe('false');

  // Click to mark owned
  fireEvent.click(card);
  expect(card.getAttribute('aria-pressed')).toBe('true');

  // localStorage should contain the ownedChars array
  const raw = localStorage.getItem('ownedChars');
  expect(raw).toBeTruthy();
  const arr = JSON.parse(raw as string) as string[];
  expect(Array.isArray(arr)).toBe(true);
  expect(arr.length).toBeGreaterThanOrEqual(1);

  // Click again to unmark
  fireEvent.click(card);
  expect(card.getAttribute('aria-pressed')).toBe('false');

  const raw2 = localStorage.getItem('ownedChars');
  const arr2 = JSON.parse(raw2 as string) as string[];
  // allow empty array or array without that id
  expect(Array.isArray(arr2)).toBe(true);
});
