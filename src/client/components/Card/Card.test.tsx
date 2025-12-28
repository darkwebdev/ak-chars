import { render, screen } from '@testing-library/react';
import { composeStories } from '@storybook/react';
import '@testing-library/jest-dom';
import * as stories from './Card.stories';

const { MultipleCards, WithToggle } = composeStories(stories);

describe('Card Stories', () => {
  test('renders MultipleCards story', () => {
    const { container } = render(<MultipleCards />);
    const cards = container.querySelectorAll('.card');
    expect(cards.length).toBe(6);
  });

  test('MultipleCards story shows owned and not owned states', () => {
    const { container } = render(<MultipleCards />);
    const ownedCards = container.querySelectorAll('.card.owned');
    // According to the story, 3 cards should be owned (orchid, texas, wisadel)
    expect(ownedCards.length).toBe(3);
  });

  test('MultipleCards story shows various tiers', () => {
    const { container } = render(<MultipleCards />);
    const tierBadges = container.querySelectorAll('.tierBadge');
    // 5 cards have tier badges (all except lancet)
    expect(tierBadges.length).toBe(5);
  });

  test('renders WithToggle story', () => {
    render(<WithToggle />);
    const card = document.querySelector('.card');
    expect(card).toBeInTheDocument();
  });

  test('WithToggle story shows character name', () => {
    render(<WithToggle />);
    const name = screen.getByText('Exusiai');
    expect(name).toBeInTheDocument();
  });
});
