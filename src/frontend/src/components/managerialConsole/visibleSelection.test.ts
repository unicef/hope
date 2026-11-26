import { describe, expect, it } from 'vitest';
import { getVisibleSelection } from './visibleSelection';

const rows = [
  { id: 'a', unicefId: 'PP-A' },
  { id: 'b', unicefId: 'PP-B' },
];

describe('getVisibleSelection', () => {
  it('leaves out selected plans that are not visible', () => {
    expect(getVisibleSelection(rows, ['hidden', 'b'])).toEqual({
      visibleIds: ['a', 'b'],
      visibleSelectedIds: ['b'],
      selectedPlansUnicefIds: ['PP-B'],
      allSelected: false,
    });
  });

  it('reports all selected when every visible row is selected', () => {
    expect(getVisibleSelection(rows, ['a', 'b']).allSelected).toBe(true);
  });

  it('reports nothing selected when only hidden plans are selected', () => {
    const selection = getVisibleSelection(rows, ['hidden']);
    expect(selection.visibleSelectedIds).toEqual([]);
    expect(selection.allSelected).toBe(false);
  });

  it('does not report all selected for an empty table', () => {
    expect(getVisibleSelection([], ['hidden']).allSelected).toBe(false);
  });
});
