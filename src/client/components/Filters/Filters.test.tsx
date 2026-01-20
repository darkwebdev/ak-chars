import { render, screen } from '@testing-library/react';
import { composeStories } from '@storybook/react';
import * as stories from './Filters.stories';

const { Default } = composeStories(stories);

describe('Filters Stories', () => {
  test('renders Default story', () => {
    const { container } = render(<Default />);
    const filters = container.querySelector('.filters');
    expect(filters).toBeInTheDocument();
  });

  test('Default story renders rarity select', () => {
    render(<Default />);
    const raritySelects = screen.getAllByRole('combobox');
    expect(raritySelects.length).toBeGreaterThan(0);
  });

  test('Default story renders checkbox for grouping', () => {
    render(<Default />);
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).toBeChecked();
  });
});
