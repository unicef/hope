import { Stack } from '@mui/material';
import type { StackProps } from '@mui/material';
import type { ReactElement } from 'react';
import { responsiveValue } from './breakpoints';

/** Lays children out in a row on desktop and stacks them on mobile. */
export const Row = (props: Omit<StackProps, 'direction'>): ReactElement => (
  <Stack
    direction={responsiveValue<'column' | 'row'>('column', 'row')}
    {...props}
  />
);
