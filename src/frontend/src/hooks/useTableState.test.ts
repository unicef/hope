import { describe, expect, it } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useEffect } from 'react';
import { useTableState } from './useTableState';

describe('useTableState', () => {
  it('derives pagination params from the defaults', () => {
    const { result } = renderHook(() => useTableState());

    expect(result.current.page).toBe(0);
    expect(result.current.rowsPerPage).toBe(5);
    expect(result.current.rowsPerPageOptions).toEqual([5, 10, 15]);
    expect(result.current.ordering).toBeUndefined();
    expect(result.current.paginationParams).toEqual({ limit: 5, offset: 0 });
  });

  it('derives ordering from defaultOrderBy/defaultOrderDirection', () => {
    const { result } = renderHook(() =>
      useTableState({
        rowsPerPageOptions: [10, 15, 20],
        defaultOrderBy: 'createdAt',
        defaultOrderDirection: 'desc',
      }),
    );

    expect(result.current.orderBy).toBe('createdAt');
    expect(result.current.orderDirection).toBe('desc');
    expect(result.current.paginationParams).toEqual({
      limit: 10,
      offset: 0,
      ordering: '-created_at',
    });
  });

  it('keeps compound ordering keys', () => {
    const { result } = renderHook(() =>
      useTableState({ defaultOrderBy: 'paymentPlanGroup__name,-createdAt' }),
    );

    expect(result.current.ordering).toBe(
      'payment_plan_group__name,-created_at',
    );
  });

  it('falls back to defaultOrdering until a column sort is requested', () => {
    const { result } = renderHook(() =>
      useTableState({ defaultOrdering: 'unicef_id' }),
    );

    expect(result.current.orderBy).toBeUndefined();
    expect(result.current.ordering).toBe('unicef_id');

    act(() => result.current.requestSort('status'));

    expect(result.current.ordering).toBe('status');
  });

  it('toggles sort direction on the same column and resets the page', () => {
    const { result } = renderHook(() =>
      useTableState({ defaultOrderBy: 'status' }),
    );

    act(() => result.current.setPage(2));
    expect(result.current.offset).toBe(10);

    act(() => result.current.requestSort('status'));
    expect(result.current.orderDirection).toBe('desc');
    expect(result.current.ordering).toBe('-status');
    expect(result.current.page).toBe(0);

    act(() => result.current.requestSort('status'));
    expect(result.current.orderDirection).toBe('asc');

    act(() => result.current.requestSort('name'));
    expect(result.current.orderBy).toBe('name');
    expect(result.current.orderDirection).toBe('asc');
  });

  it('resets the page when rows per page changes', () => {
    const { result } = renderHook(() =>
      useTableState({ initialRowsPerPage: 10 }),
    );

    act(() => result.current.setPage(3));
    expect(result.current.paginationParams).toEqual({ limit: 10, offset: 30 });

    act(() => result.current.setRowsPerPage(20));
    expect(result.current.paginationParams).toEqual({ limit: 20, offset: 0 });
  });

  it('resets the page when resetPageOn changes, without committing a stale offset', () => {
    // Records what a consumer's query would see: (filters, offset) per commit.
    const committed: Array<[string, number]> = [];
    const { result, rerender } = renderHook(
      ({ filters }) => {
        const table = useTableState({ resetPageOn: filters });
        useEffect(() => {
          committed.push([filters.search, table.offset]);
        }, [filters, table.offset]);
        return table;
      },
      { initialProps: { filters: { search: 'a' } } },
    );

    act(() => result.current.setPage(2));
    expect(result.current.offset).toBe(10);

    rerender({ filters: { search: 'b' } });

    expect(result.current.page).toBe(0);
    // Filters 'b' were never committed together with the old offset.
    expect(committed).toEqual([
      ['a', 0],
      ['a', 10],
      ['b', 0],
    ]);
  });

  it('memoizes paginationParams while nothing changes', () => {
    const { result, rerender } = renderHook(() => useTableState());
    const first = result.current.paginationParams;

    rerender();

    expect(result.current.paginationParams).toBe(first);
  });
});
