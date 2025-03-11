import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { render, RenderOptions } from '@testing-library/react';
import { Formik } from 'formik';
import noop from 'lodash/noop';
import { TestProviders } from './testProviders';
import { Status791Enum } from '@restgenerated/models/Status791Enum';

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'queries'>,
) =>
  render(
    <>
      <BrowserRouter>
        <Formik initialValues={{}} onSubmit={noop}>
          {ui}
        </Formik>
      </BrowserRouter>
    </>,
    {
      wrapper: TestProviders,
      ...options,
    },
  );

export * from '@testing-library/react';
export { customRender as renderWithProviders };

let m_w = 123456789;
let m_z = 987654321;
const mask = 0xffffffff;

// Takes any integer
export const seed = (i) => {
  m_w = (123456789 + i) & mask;
  m_z = (987654321 - i) & mask;
};

// Returns number between 0 (inclusive) and 1.0 (exclusive),
// just like Math.random().
export const random = () => {
  m_z = (36969 * (m_z & 65535) + (m_z >> 16)) & mask;
  m_w = (18000 * (m_w & 65535) + (m_w >> 16)) & mask;
  let result = ((m_z << 16) + (m_w & 65535)) >>> 0;
  result /= 4294967296;
  return result;
};

export const fakeContextProgram = {
  selectedProgram: {
    id: '1',
    name: 'someName',
    programme_code: 'A123',
    status: 'ACTIVE' as Status791Enum,
    pdu_fields: null,
    program_code: 'A123',
    data_collecting_type: {
      id: 1,
      household_filters_available: true,
      individual_filters_available: true,
      label: 'data collecting type',
      code: '123',
      type: 'full',
      children: null,
    },
    beneficiaryGroup: {
      id: '2',
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
      name: 'Population',
      group_label: 'Household',
      group_label_plural: 'Households',
      member_label: 'Individual',
      member_label_plural: 'Individuals',
      master_detail: true,
    },
  },
  setSelectedProgram: () => {},
  isActiveProgram: true,
  isSocialDctType: false,
  isStandardDctType: true,
  programHasPdu: false,
};
