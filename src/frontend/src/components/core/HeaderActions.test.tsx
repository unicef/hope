import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { HeaderActions } from './HeaderActions';

describe('HeaderActions', () => {
  it('renders every action', () => {
    render(
      <HeaderActions>
        <button type="button">Edit</button>
        <button type="button">Duplicate</button>
      </HeaderActions>,
    );

    expect(screen.getByTestId('header-actions').children).toHaveLength(2);
    expect(screen.getByRole('button', { name: 'Edit' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Duplicate' })).toBeTruthy();
  });
});
