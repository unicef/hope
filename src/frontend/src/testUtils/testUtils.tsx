import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { render, RenderOptions } from '@testing-library/react';
import { Formik } from 'formik';
import noop from 'lodash/noop';
import { TestProviders } from './testProviders';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { DataCollectingTypeTypeEnum } from '@restgenerated/models/DataCollectingTypeTypeEnum';

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'queries'>,
) =>
  render(
    <>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
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
    status: 'ACTIVE' as ProgramStatusEnum,
    pduFields: null,
    program_code: 'A123',
    dataCollectingType: {
      id: 1,
      householdFiltersAvailable: true,
      individualFiltersAvailable: true,
      label: 'data collecting type',
      code: '123',
      type: DataCollectingTypeTypeEnum.STANDARD,
      typeDisplay: 'Standard',
      children: null,
    },
    beneficiaryGroup: {
      id: '2',
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2023-01-01T00:00:00Z',
      name: 'Population',
      groupLabel: 'Household',
      groupLabelPlural: 'Households',
      memberLabel: 'Individual',
      memberLabelPlural: 'Individuals',
      masterDetail: true,
    },
  },
  setSelectedProgram: () => {},
  isActiveProgram: true,
  isSocialDctType: false,
  isStandardDctType: true,
  programHasPdu: false,
};
