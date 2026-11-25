import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RegistrationIndividualBioData } from './RegistrationIndividualBioData';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock('src/programContext', () => ({
  useProgramContext: () => ({ selectedProgram: null }),
}));
vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ baseUrl: 'afghanistan' }),
}));

// Document.country and IndividualIdentity.country are nullable.
describe('RegistrationIndividualBioData', () => {
  it('renders a document and an identity without a country', () => {
    const individual = {
      documents: [
        {
          id: 'doc-1',
          country: null,
          type: { label: 'National ID', key: 'national_id' },
          documentNumber: 'DOC-123',
          photo: null,
        },
      ],
      identities: [{ id: 1, country: null, partner: 'WFP', number: 'ID-456' }],
      linkedGrievances: [],
      rolesInHouseholds: [],
    } as unknown as IndividualDetail;

    render(
      <MemoryRouter>
        <RegistrationIndividualBioData
          individual={individual}
          choicesData={{} as IndividualChoices}
        />
      </MemoryRouter>,
      { wrapper: TestProviders },
    );

    expect(screen.getByText('DOC-123')).toBeTruthy();
    expect(screen.getByText('ID-456')).toBeTruthy();
    const issued = document.querySelectorAll('[data-cy="label-issued"]');
    expect([...issued].map((field) => field.textContent)).toEqual(['-', '-']);
  });
});
