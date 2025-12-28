import { render, screen } from '@testing-library/react';
import { composeStories } from '@storybook/react';
import '@testing-library/jest-dom';
import * as stories from './ThemeToggle.stories';

const { Default, WithClass } = composeStories(stories);

describe('ThemeToggle Stories', () => {
  test('renders Default story', () => {
    render(<Default />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('theme-toggle');
  });

  test('renders WithClass story with custom class', () => {
    render(<WithClass />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('my-toggle');
  });
});
