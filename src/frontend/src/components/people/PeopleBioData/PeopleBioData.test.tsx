import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { PeopleBioData } from './PeopleBioData';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));
vi.mock('src/programContext', () => ({
  useProgramContext: () => ({ selectedProgram: null }),
}));

// Document.country and IndividualIdentity.country are nullable.
describe('PeopleBioData', () => {
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
        <PeopleBioData
          individual={individual}
          choicesData={{} as IndividualChoices}
          grievancesChoices={{} as GrievanceChoices}
          baseUrl="afghanistan"
          businessArea="afghanistan"
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
