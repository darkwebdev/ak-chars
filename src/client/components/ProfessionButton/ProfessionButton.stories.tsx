import React from 'react';
import { Meta, StoryFn } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { ProfessionButton } from '.';

const professions = [
  '',
  'pioneer',
  'warrior',
  'tank',
  'sniper',
  'caster',
  'medic',
  'support',
  'special',
];

const meta: Meta<typeof ProfessionButton> = {
  title: 'Components/ProfessionButton',
  component: ProfessionButton,
  argTypes: {
    profession: {
      control: { type: 'select' },
      options: professions,
      description: 'Profession key (empty = all)',
    },
    active: { control: 'boolean' },
    onClick: { action: 'clicked' },
  },
};

export default meta;

const Template: StoryFn<typeof ProfessionButton> = (args) => (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  <ProfessionButton {...(args as any)} />
);

export const Default = Template.bind({});
Default.args = {
  profession: '',
  active: false,
  onClick: action('clicked'),
};

export const Active = Template.bind({});
Active.args = {
  ...Default.args,
  active: true,
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  ...Default.args,
  profession: 'pioneer',
};

export const WithActiveIcon = Template.bind({});
WithActiveIcon.args = {
  ...WithIcon.args,
  active: true,
};
