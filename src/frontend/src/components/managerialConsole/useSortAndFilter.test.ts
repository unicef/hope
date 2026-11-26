import { createElement, type ReactNode } from 'react';
import { TimezoneProvider } from 'src/timezoneContext';
import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { useSortAndFilter } from './useSortAndFilter';

const rows = [
  {
    id: 'a',
    unicefId: 'PP-A',
    program: 'Cash',
    lastApprovalProcessDate: '2026-01-05T12:00:00Z',
  },
  {
    id: 'b',
    unicefId: 'PP-B',
    program: 'Food',
    lastApprovalProcessDate: null,
  },
];
const columns = [
  { field: 'unicefId' },
  { field: 'program' },
  { field: 'lastApprovalProcessDate' },
];

const setup = () =>
  renderHook(() =>
    useSortAndFilter({ initialSortField: null, initialSortDirection: 'asc' }),
  ).result;

const visibleIds = (result: ReturnType<typeof setup>, searchText: string) =>
  result.current
    .filterRows(rows, 'lastApprovalProcessDate', searchText, columns)
    .map((row) => row.id);

describe('filterRows', () => {
  it.each([
    ['', ['a', 'b']],
    ['pp-b', ['b']],
    ['food', ['b']],
    ['5 Jan 2026', ['a']],
    ['5 jan', ['a']],
    ['invalid', []],
    ['missing', []],
  ])('filters by search text "%s"', (searchText, expected) => {
    expect(visibleIds(setup(), searchText)).toEqual(expected);
  });

  it('requires both the programme and the search text to match', () => {
    const result = setup();
    act(() => result.current.setSelectedProgram('Cash'));

    expect(visibleIds(result, '')).toEqual(['a']);
    expect(visibleIds(result, 'pp-a')).toEqual(['a']);
    expect(visibleIds(result, 'pp-b')).toEqual([]);
  });

  it('searches dates in the timezone the table displays', () => {
    const { result } = renderHook(
      () =>
        useSortAndFilter({
          initialSortField: null,
          initialSortDirection: 'asc',
        }),
      {
        wrapper: ({ children }: { children: ReactNode }) =>
          createElement(TimezoneProvider, {
            timezone: 'Pacific/Kiritimati',
            children,
          }),
      },
    );

    expect(visibleIds(result, '6 Jan 2026')).toEqual(['a']);
    expect(visibleIds(result, '5 Jan 2026')).toEqual([]);
  });
});
