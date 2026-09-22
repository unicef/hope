import { describe, expect, it, vi } from 'vitest';
import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { BaseAutocompleteFilterRest } from './BaseAutocompleteFilterRest';

function renderFilter(props: {
  open: boolean;
  loadData: () => void;
  loading?: boolean;
}) {
  return renderWithProviders(
    <BaseAutocompleteFilterRest
      value=""
      label="Assignee"
      dataCy="assignee-autocomplete"
      loadData={props.loadData}
      loading={props.loading ?? false}
      options={[]}
      handleChange={vi.fn()}
      handleClose={vi.fn()}
      handleOptionSelected={() => false}
      handleOptionLabel={() => ''}
      handleOpen={vi.fn()}
      open={props.open}
      inputValue=""
      onInputTextChange={vi.fn()}
      debouncedInputText=""
    />,
  );
}

describe('BaseAutocompleteFilterRest', () => {
  it('renders the field before any data has loaded', () => {
    renderFilter({ open: false, loadData: vi.fn() });

    expect(screen.getByTestId('assignee-autocomplete')).toBeTruthy();
  });

  it('hides the field while a closed dropdown resolves its initial label', () => {
    renderFilter({ open: false, loadData: vi.fn(), loading: true });

    expect(screen.queryByTestId('assignee-autocomplete')).toBeNull();
  });

  it('keeps the field mounted while loading with the dropdown open', () => {
    renderFilter({ open: true, loadData: vi.fn(), loading: true });

    expect(screen.getByTestId('assignee-autocomplete')).toBeTruthy();
  });

  it('does not load data on mount', () => {
    const loadData = vi.fn();
    renderFilter({ open: false, loadData });

    expect(loadData).not.toHaveBeenCalled();
  });

  it('loads data once when the dropdown opens', () => {
    const loadData = vi.fn();
    const { rerender } = renderFilter({ open: false, loadData });

    rerender(
      <BaseAutocompleteFilterRest
        value=""
        label="Assignee"
        dataCy="assignee-autocomplete"
        loadData={loadData}
        loading={false}
        options={[]}
        handleChange={vi.fn()}
        handleClose={vi.fn()}
        handleOptionSelected={() => false}
        handleOptionLabel={() => ''}
        handleOpen={vi.fn()}
        open
        inputValue=""
        onInputTextChange={vi.fn()}
        debouncedInputText=""
      />,
    );

    expect(loadData).toHaveBeenCalledTimes(1);
  });
});
