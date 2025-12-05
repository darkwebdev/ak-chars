import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { ThemeToggle } from './index';
import { ThemeProvider } from '../../theme/ThemeProvider';

const meta: Meta<typeof ThemeToggle> = {
  title: 'Components/ThemeToggle',
  component: ThemeToggle,
  decorators: [(Story) => <ThemeProvider>{<Story />}</ThemeProvider>],
};

export default meta;

type Story = StoryObj<typeof ThemeToggle>;

export const Default: Story = {};

export const WithClass: Story = {
  args: {
    className: 'my-toggle',
  },
};
