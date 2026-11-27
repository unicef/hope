interface SelectableRow {
  id: string;
  unicefId?: string | null;
}

/** Narrows a selection to the rows the table currently shows. */
export const getVisibleSelection = (
  visibleRows: SelectableRow[],
  selected: string[],
) => {
  const selectedRows = visibleRows.filter((row) => selected.includes(row.id));

  return {
    visibleIds: visibleRows.map((row) => row.id),
    visibleSelectedIds: selectedRows.map((row) => row.id),
    selectedPlansUnicefIds: selectedRows.map((row) => row.unicefId ?? ''),
    allSelected:
      visibleRows.length > 0 && selectedRows.length === visibleRows.length,
  };
};
