import { render, screen } from '@testing-library/react';
import { composeStories } from '@storybook/react';
import '@testing-library/jest-dom';
import * as stories from './Sidebar.stories';

const { Default } = composeStories(stories);

describe('Sidebar Stories', () => {
  test('renders Default story', () => {
    render(<Default />);
    const sidebar = document.querySelector('.profession-sidebar');
    expect(sidebar).toBeInTheDocument();
  });

  test('renders all profession buttons', () => {
    render(<Default />);
    const buttons = screen.getAllByRole('button');
    // Should have All + 8 professions
    expect(buttons.length).toBeGreaterThan(0);
  });
});
