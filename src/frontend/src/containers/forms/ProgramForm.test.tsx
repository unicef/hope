import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react';
import { Formik } from 'formik';
import noop from 'lodash/noop';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import ProgramForm from './ProgramForm';

const location = vi.hoisted(() => ({ pathname: '/afghanistan/create' }));

vi.mock('react-router-dom', () => ({
  useLocation: () => location,
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ businessArea: 'afghanistan' }),
}));

vi.mock('@shared/autocompletes/rest/PaymentPlanPurposesAutocomplete', () => ({
  PaymentPlanPurposesAutocomplete: () => null,
}));

// restQueryKey keys queries by function name, so each mock needs its own.
vi.mock('@restgenerated/services/RestService', () => {
  const named = (name: string) =>
    Object.defineProperty(vi.fn(), 'name', { value: name });
  return {
    RestService: Object.fromEntries(
      [
        'restChoicesProgramsRetrieve',
        'restBusinessAreasDataCollectingTypesChoicesList',
        'restBusinessAreasPayeeTypesChoicesList',
        'restBeneficiaryGroupsList',
      ].map((name) => [name, named(name)]),
    ),
  };
});

const HOUSEHOLD = 'payee-household';
const INCENTIVE = 'payee-incentive';

const payeeTypes = [
  {
    id: HOUSEHOLD,
    name: 'Household',
    glCode: '7700410',
    defaultDataCollectingType: 'full_collection',
  },
  {
    id: INCENTIVE,
    name: 'Incentive Payee',
    glCode: '7700430',
    defaultDataCollectingType: null,
  },
];

const dataCollectingTypes = [
  { name: 'Full', value: 'full_collection', payeeType: HOUSEHOLD },
  { name: 'Partial', value: 'partial_collection', payeeType: HOUSEHOLD },
  { name: 'Frontline', value: 'frontline', payeeType: INCENTIVE },
];

const label = (id: string, overrides = {}) => ({
  id,
  name: id,
  groupLabel: 'Household',
  groupLabelPlural: 'Households',
  memberLabel: 'Individual',
  memberLabelPlural: 'Individuals',
  payeeType: HOUSEHOLD,
  dataCollectingTypes: [],
  active: true,
  ...overrides,
});

const payeeLabels = [
  label('Any DCT'),
  label('Partial only', { dataCollectingTypes: ['partial_collection'] }),
  label('Inactive', { active: false }),
  label('Workers', { payeeType: INCENTIVE }),
];

const renderForm = (
  initialValues: Record<string, unknown>,
  program?: ProgramDetail,
  validationSchema?: ReturnType<typeof programValidationSchema>,
) =>
  render(
    <Formik
      initialValues={initialValues}
      onSubmit={noop}
      validationSchema={validationSchema}
    >
      {({ values }) => (
        <ProgramForm values={values} errors={{}} program={program} />
      )}
    </Formik>,
    { wrapper: TestProviders },
  );

const emptyValues = {
  payeeType: '',
  dataCollectingTypeCode: '',
  beneficiaryGroup: '',
};

const openSelect = async (name: string): Promise<string[]> => {
  fireEvent.mouseDown(await screen.findByTestId(`select-${name}`));
  const listbox = await screen.findByRole('listbox');
  return within(listbox)
    .getAllByRole('option')
    .map((option) => option.textContent ?? '');
};

const choose = async (option: string): Promise<void> => {
  fireEvent.click(screen.getByTestId(`select-option-${option}`));
  await waitFor(() => expect(screen.queryByRole('listbox')).toBeNull());
};

const pickOption = async (name: string, option: string): Promise<void> => {
  await openSelect(name);
  await choose(option);
};

const inputOf = (name: string): HTMLInputElement =>
  document.querySelector(`input[name="${name}"]`) as HTMLInputElement;

const glCodeInput = (): HTMLInputElement =>
  within(screen.getByTestId('input-gl-code')).getByRole('textbox');

describe('ProgramForm payee type fields', () => {
  beforeEach(() => {
    location.pathname = '/afghanistan/create';
    vi.mocked(RestService.restChoicesProgramsRetrieve).mockResolvedValue({
      sectorChoices: [],
      frequencyOfPaymentsChoices: [],
    } as any);
    vi.mocked(
      RestService.restBusinessAreasDataCollectingTypesChoicesList,
    ).mockResolvedValue(dataCollectingTypes as any);
    vi.mocked(
      RestService.restBusinessAreasPayeeTypesChoicesList,
    ).mockResolvedValue(payeeTypes);
    vi.mocked(RestService.restBeneficiaryGroupsList).mockResolvedValue({
      results: payeeLabels,
    });
  });

  it('requests only active payee labels', async () => {
    renderForm(emptyValues);
    await screen.findAllByTestId('input-payee-type');
    expect(RestService.restBeneficiaryGroupsList).toHaveBeenCalledWith({
      active: true,
    });
  });

  it('disables DCT and Payee Label until a payee type is chosen', async () => {
    renderForm(emptyValues);
    await screen.findAllByTestId('input-payee-type');
    expect(inputOf('dataCollectingTypeCode').disabled).toBe(true);
    expect(inputOf('beneficiaryGroup').disabled).toBe(true);
    expect(screen.getAllByLabelText('Select Payee Type first')).toHaveLength(2);
  });

  it('fills GL code and default DCT, and filters DCTs and labels', async () => {
    renderForm(emptyValues);
    await pickOption('payeeType', 'Household');

    const glCode = glCodeInput();
    expect(glCode.value).toBe('7700410');
    expect(glCode.disabled).toBe(true);
    expect(inputOf('dataCollectingTypeCode').value).toBe('full_collection');
    expect(await openSelect('dataCollectingTypeCode')).toEqual([
      'Full',
      'Partial',
    ]);
    await choose('Full');

    expect(await openSelect('beneficiaryGroup')).toEqual(['Any DCT']);
    await choose('Any DCT');

    await pickOption('dataCollectingTypeCode', 'Partial');
    expect(await openSelect('beneficiaryGroup')).toEqual([
      'Any DCT',
      'Partial only',
    ]);
  });

  it('validates payee type, DCT and label together after a payee type is picked', async () => {
    renderForm(
      emptyValues,
      undefined,
      programValidationSchema(((key: string) => key) as any),
    );
    await pickOption('payeeType', 'Household');

    expect(await screen.findByText('Payee Label is required')).toBeTruthy();
    expect(screen.queryByText('Payee Type is required')).toBeNull();
    expect(screen.queryByText('Data Collecting Type is required')).toBeNull();
  });

  it('resets DCT and clears the label when the payee type changes', async () => {
    renderForm({
      payeeType: HOUSEHOLD,
      dataCollectingTypeCode: 'full_collection',
      beneficiaryGroup: 'Any DCT',
    });
    await pickOption('payeeType', 'Incentive Payee');

    expect(glCodeInput().value).toBe('7700430');
    expect(inputOf('dataCollectingTypeCode').value).toBe('');
    expect(inputOf('beneficiaryGroup').value).toBe('');
    expect(await openSelect('dataCollectingTypeCode')).toEqual(['Frontline']);
  });

  it('keeps the current DCT and deactivated label of an edited program', async () => {
    location.pathname = '/afghanistan/edit/1';
    const program = {
      payeeType: { id: HOUSEHOLD, name: 'Household', glCode: '7700410' },
      dataCollectingType: { code: 'legacy', label: 'Legacy DCT' },
      beneficiaryGroup: { id: 'deactivated', name: 'Old Label' },
    } as unknown as ProgramDetail;
    renderForm(
      {
        payeeType: HOUSEHOLD,
        dataCollectingTypeCode: 'legacy',
        beneficiaryGroup: 'deactivated',
      },
      program,
    );

    expect(await openSelect('dataCollectingTypeCode')).toEqual([
      'Full',
      'Partial',
      'Legacy DCT',
    ]);
    await choose('Legacy DCT');
    expect(await openSelect('beneficiaryGroup')).toEqual([
      'Any DCT',
      'Old Label',
    ]);
  });

  it('keeps the payee type and GL code of an edited program missing from the choices', async () => {
    location.pathname = '/afghanistan/edit/1';
    const program = {
      payeeType: { id: 'payee-legacy', name: 'Legacy', glCode: '7700999' },
      dataCollectingType: { code: 'legacy', label: 'Legacy DCT' },
      beneficiaryGroup: { id: 'Any DCT', name: 'Any DCT' },
    } as unknown as ProgramDetail;
    renderForm(
      {
        payeeType: 'payee-legacy',
        dataCollectingTypeCode: 'legacy',
        beneficiaryGroup: 'Any DCT',
      },
      program,
    );

    expect(await openSelect('payeeType')).toEqual([
      'Household',
      'Incentive Payee',
      'Legacy',
    ]);
    await choose('Legacy');
    expect(glCodeInput().value).toBe('7700999');
  });

  it('locks payee type, DCT and label on the copy page', async () => {
    location.pathname = '/afghanistan/duplicate/1';
    const program = {
      payeeType: { id: HOUSEHOLD, name: 'Household', glCode: '7700410' },
      dataCollectingType: { code: 'full_collection', label: 'Full' },
      beneficiaryGroup: { id: 'Any DCT', name: 'Any DCT' },
    } as unknown as ProgramDetail;
    renderForm(
      {
        payeeType: HOUSEHOLD,
        dataCollectingTypeCode: 'full_collection',
        beneficiaryGroup: 'Any DCT',
      },
      program,
    );
    await screen.findAllByTestId('input-payee-type');

    expect(inputOf('payeeType').disabled).toBe(true);
    expect(inputOf('dataCollectingTypeCode').disabled).toBe(true);
    expect(inputOf('beneficiaryGroup').disabled).toBe(true);
    expect(
      screen.getByLabelText('Payee Type is fixed when copying programs'),
    ).toBeTruthy();
  });
});
