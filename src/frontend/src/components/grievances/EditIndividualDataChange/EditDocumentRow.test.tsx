import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { EditDocumentRow } from './EditDocumentRow';
import { EditIdentityRow } from './EditIdentityRow';
import type { IndividualIdentity } from '@restgenerated/models/IndividualIdentity';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

// The edit form itself is not under test; stub it so clicking edit only checks what gets pushed.
vi.mock('../DocumentField', () => ({ DocumentField: () => null }));
vi.mock('../AgencyField', () => ({ AgencyField: () => null }));

const wrap = (ui) =>
  render(<MemoryRouter>{ui}</MemoryRouter>, { wrapper: TestProviders });

// Tests query by data-cy, but MUI icons only carry data-testid.
const clickEdit = () =>
  fireEvent.click(
    document.querySelector('[data-testid="EditIcon"]').closest('button'),
  );

// Document.country and IndividualIdentity.country are nullable.
describe('edit rows without a country', () => {
  it('EditDocumentRow shows a dash and edits with an empty country', () => {
    const arrayHelpers = { push: vi.fn(), remove: vi.fn() };
    wrap(
      <EditDocumentRow
        id="0"
        setFieldValue={vi.fn()}
        values={{}}
        arrayHelpers={arrayHelpers}
        addIndividualFieldsData={{}}
        document={{
          id: 'doc-1',
          country: null,
          type: { label: 'National ID', key: 'national_id' },
          documentNumber: '123',
          photo: null,
        }}
      />,
    );
    expect(screen.getByText('-')).toBeTruthy();

    clickEdit();
    expect(arrayHelpers.push).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'doc-1', country: null }),
    );
  });

  it('EditIdentityRow shows a dash and edits with an empty country', () => {
    const arrayHelpers = { push: vi.fn(), remove: vi.fn() };
    wrap(
      <EditIdentityRow
        id={0}
        setFieldValue={vi.fn()}
        values={{}}
        arrayHelpers={arrayHelpers}
        addIndividualFieldsData={{
          countriesChoices: [],
          identityTypeChoices: [],
        }}
        // The generated type says country is always set; the model allows null.
        identity={
          {
            id: 1,
            country: null,
            partner: 2,
            number: '456',
          } as unknown as IndividualIdentity
        }
      />,
    );
    expect(screen.getByText('-')).toBeTruthy();

    clickEdit();
    expect(arrayHelpers.push).toHaveBeenCalledWith(
      expect.objectContaining({ id: 1, country: null }),
    );
  });
});
