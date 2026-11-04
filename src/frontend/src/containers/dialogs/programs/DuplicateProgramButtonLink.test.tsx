import { render, screen } from '@testing-library/react';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { mockViewportWidth } from 'src/responsive/testUtils';
import { DuplicateProgramButtonLink } from './DuplicateProgramButtonLink';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ baseUrl: 'afghanistan/programs/all' }),
}));

const program = { code: 'PRG1' } as ProgramDetail;

const renderButton = () =>
  render(
    <MemoryRouter>
      <DuplicateProgramButtonLink program={program} />
    </MemoryRouter>,
  );

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('DuplicateProgramButtonLink', () => {
  it('is an icon link on desktop', () => {
    mockViewportWidth(1440);
    renderButton();

    const link = screen.getByTestId('button-copy-program');
    expect(link.getAttribute('href')).toBe(
      '/afghanistan/programs/all/duplicate/PRG1',
    );
    expect(link.textContent).toBe('');
  });

  it('is a labelled link on mobile', () => {
    mockViewportWidth(375);
    renderButton();

    const link = screen.getByTestId('button-copy-program');
    expect(link.getAttribute('href')).toBe(
      '/afghanistan/programs/all/duplicate/PRG1',
    );
    expect(link.textContent).toBe('Duplicate Programme');
  });
});
