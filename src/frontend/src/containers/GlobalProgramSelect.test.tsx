import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ProgramProvider } from 'src/programContext';
import { TestProviders } from 'src/testUtils/testProviders';
import { GlobalProgramSelect } from './GlobalProgramSelect';

const programs = {
  A: { id: 'a', name: 'Programme A', code: 'A', status: 'ACTIVE' },
  B: { id: 'b', name: 'Programme B', code: 'B', status: 'ACTIVE' },
};

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsList: vi.fn(async () => ({
      results: Object.values(programs),
    })),
    restBusinessAreasProgramsRetrieve: vi.fn(async ({ code }) => programs[code]),
  },
}));

const Location = () => <div data-cy="location">{useLocation().pathname}</div>;

describe('GlobalProgramSelect', () => {
  beforeEach(() => {
    // setupTests stubs useGlobalProgram and useProgramContext; this test needs the real ones.
    vi.restoreAllMocks();
  });

  it('selects a programme on tap', async () => {
    render(
      <TestProviders>
        <ProgramProvider>
          <MemoryRouter initialEntries={['/afg/programs/A/details/A']}>
            <Routes>
              <Route
                path="/:businessArea/programs/:programId/*"
                element={
                  <>
                    <Location />
                    <GlobalProgramSelect />
                  </>
                }
              />
            </Routes>
          </MemoryRouter>
        </ProgramProvider>
      </TestProviders>,
    );

    fireEvent.click(await screen.findByTestId('global-program-filter'));
    const option = await screen.findByText('Programme B');

    // A tap fires touchend before the click.
    fireEvent.touchStart(option);
    fireEvent.touchEnd(option);
    fireEvent.mouseDown(option);
    fireEvent.click(option);
    await act(async () => {});

    expect(screen.getByTestId('location').textContent).toBe(
      '/afg/programs/B/details/B',
    );
  });
});
