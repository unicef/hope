import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { ProgramCycleAutocompleteRest } from './ProgramCycleAutocompleteRest';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ businessArea: 'afghanistan', programId: 'prog-1' }),
}));

vi.mock('@restgenerated/services/RestService', () => {
  const methods = { restBusinessAreasProgramsCyclesList: vi.fn() };
  // restQueryKey derives the cache key root from `fn.name`.
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

const value = { value: 'cycle-1', name: 'Cycle One' };

describe('ProgramCycleAutocompleteRest', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(
      RestService.restBusinessAreasProgramsCyclesList,
    ).mockResolvedValue({ results: [], count: 0 } as any);
  });

  it('fetches cycles by default', async () => {
    render(<ProgramCycleAutocompleteRest value={value} onChange={vi.fn()} />, {
      wrapper: TestProviders,
    });
    await waitFor(() =>
      expect(
        RestService.restBusinessAreasProgramsCyclesList,
      ).toHaveBeenCalled(),
    );
  });

  it('does not fetch cycles when not enabled and shows the current cycle', async () => {
    render(
      <ProgramCycleAutocompleteRest
        value={value}
        onChange={vi.fn()}
        enabled={false}
        disabled
      />,
      { wrapper: TestProviders },
    );
    const input = screen.getByRole<HTMLInputElement>('combobox');
    expect(input.disabled).toBe(true);
    await waitFor(() => expect(input.value).toBe('Cycle One'));
    expect(
      RestService.restBusinessAreasProgramsCyclesList,
    ).not.toHaveBeenCalled();
  });
});
