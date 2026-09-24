import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { MyTasksFilters } from './MyTasksFilters';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ isAllPrograms: false }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const choicesData = {
  grievanceTicketCategoryChoices: [
    { name: 'Data Change', value: 2 },
    { name: 'Sensitive Grievance', value: 3 },
    { name: 'Referral', value: 6 },
  ],
  grievanceTicketIssueTypeChoices: [
    {
      category: 2,
      label: 'Data Change',
      subCategories: { 13: 'Add Individual' },
    },
    {
      category: 3,
      label: 'Sensitive Grievance',
      subCategories: { 1: 'Data Breach', 5: 'Harassment' },
    },
  ],
  grievanceTicketPriorityChoices: [{ name: 'High', value: 1 }],
  grievanceTicketUrgencyChoices: [{ name: 'Very urgent', value: 1 }],
} as any;

const baseFilter = {
  search: '',
  category: '',
  issueType: '',
  priority: '',
  urgency: '',
  program: '',
  grievanceStatus: 'active',
  overdue: '',
  sensitive: '',
};

const setFilter = vi.fn();

const renderFilters = (props: Record<string, unknown> = {}) =>
  render(
    <MemoryRouter>
      <MyTasksFilters
        choicesData={choicesData}
        filter={baseFilter}
        setFilter={setFilter}
        initialFilter={baseFilter}
        appliedFilter={baseFilter}
        setAppliedFilter={vi.fn()}
        {...props}
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

/** MUI renders the options into a portal, so open the select first and read them from the body. */
const openOptions = (dataCy: string): HTMLElement[] => {
  fireEvent.mouseDown(within(screen.getByTestId(dataCy)).getByRole('combobox'));
  return screen.getAllByRole('option') as HTMLElement[];
};

describe('MyTasksFilters', () => {
  beforeEach(() => vi.clearAllMocks());

  it('labels the defaults of the selects that default to an empty value', () => {
    renderFilters();

    // Without displayEmpty MUI renders a blank box here, so the user cannot tell what the list
    // is currently showing.
    expect(screen.getByTestId('filters-overdue').textContent).toContain(
      'All Tickets',
    );
    expect(screen.getByTestId('filters-sensitive').textContent).toContain(
      'All Categories',
    );
  });

  it('drops Sensitive Grievance from the categories when filtering to other', () => {
    renderFilters({ filter: { ...baseFilter, sensitive: 'false' } });

    const options = openOptions('filters-category').map((o) => o.textContent);
    expect(options).toEqual(['Data Change', 'Referral']);
  });

  it('replaces the category select with the sensitive issue types', () => {
    renderFilters({ filter: { ...baseFilter, sensitive: 'true' } });

    // The category is already settled by the sensitivity choice, so the select would only offer
    // the one value it already has.
    expect(screen.queryByTestId('filters-category')).toBeNull();
    const options = openOptions('filters-issue-type').map((o) => o.textContent);
    expect(options).toEqual(['Data Breach', 'Harassment']);
  });

  it('normalises the boolean an email link is parsed into', () => {
    renderFilters({ filter: { ...baseFilter, sensitive: false } });

    // ?sensitive=false arrives as a boolean and must not collapse into the unset '' value.
    expect(screen.getByTestId('filters-sensitive').textContent).toContain(
      'Other',
    );
  });

  it('clears the category and issue type when sensitivity changes', () => {
    renderFilters({
      filter: { ...baseFilter, category: '2', issueType: '13' },
    });

    fireEvent.click(
      openOptions('filters-sensitive').find((o) => o.textContent === 'Other'),
    );

    expect(setFilter).toHaveBeenCalledWith(
      expect.objectContaining({
        sensitive: 'false',
        category: '',
        issueType: '',
      }),
    );
  });

  it('clears the issue type when the category changes', () => {
    renderFilters({
      filter: { ...baseFilter, category: '2', issueType: '13' },
    });

    fireEvent.click(
      openOptions('filters-category').find((o) => o.textContent === 'Referral'),
    );

    expect(setFilter).toHaveBeenCalledWith(
      expect.objectContaining({ category: '6', issueType: '' }),
    );
  });

  it('hides the ticket-status select when the page has no use for it', () => {
    renderFilters({ showStatusFilter: false });

    expect(screen.queryByTestId('filters-active-tickets')).toBeNull();
  });

  it('hides the sensitivity select when permissions already decide it', () => {
    renderFilters({ showSensitiveFilter: false });

    expect(screen.queryByTestId('filters-sensitive')).toBeNull();
  });
});
