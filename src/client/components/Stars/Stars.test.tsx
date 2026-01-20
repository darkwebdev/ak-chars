import { render } from '@testing-library/react';
import { composeStories } from '@storybook/react';
import * as stories from './Stars.stories';

const { OneStar, ThreeStar, SixStar } = composeStories(stories);

describe('Stars Stories', () => {
  test('renders OneStar story', () => {
    const { container } = render(<OneStar />);
    const stars = container.querySelectorAll('.stars');
    expect(stars.length).toBeGreaterThan(0);
  });

  test('renders ThreeStar story', () => {
    const { container } = render(<ThreeStar />);
    const stars = container.querySelectorAll('.stars');
    expect(stars.length).toBeGreaterThan(0);
  });

  test('renders SixStar story', () => {
    const { container } = render(<SixStar />);
    const stars = container.querySelectorAll('.stars');
    expect(stars.length).toBeGreaterThan(0);
  });
});
