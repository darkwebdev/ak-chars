import { Meta, StoryFn } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { Sidebar } from '.';
import { Professions } from '../../const';

const meta: Meta<typeof Sidebar> = {
  title: 'Components/Sidebar',
  component: Sidebar,
  argTypes: {
    professions: { control: 'object' },
    current: { control: 'select', options: ['All', ...Professions] },
    onSelect: { action: 'selected' },
  },
};

export default meta;

const Template: StoryFn<typeof Sidebar> = (args) => <Sidebar {...args} />;

export const Default = Template.bind({});
Default.args = {
  professions: ['All', ...Professions],
  current: undefined,
  onSelect: action('selected'),
};
