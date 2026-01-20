import { render, screen } from '@testing-library/react';
import { composeStories } from '@storybook/react';
import * as stories from './ProfessionButton.stories';

const { Default, Active, WithIcon, WithActiveIcon } = composeStories(stories);

describe('ProfessionButton Stories', () => {
  test('renders Default story', () => {
    render(<Default />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('profession-btn');
  });

  test('renders Active story with active class', () => {
    render(<Active />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('active');
  });

  test('renders WithIcon story', () => {
    render(<WithIcon />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  test('renders WithActiveIcon story', () => {
    render(<WithActiveIcon />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('active');
  });
});
