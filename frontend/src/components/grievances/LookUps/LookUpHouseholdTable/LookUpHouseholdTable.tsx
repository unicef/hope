import React from 'react';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import {
  AllHouseholdsQuery,
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  useAllHouseholdsQuery,
} from '../../../../__generated__/graphql';
import { TableWrapper } from '../../../core/TableWrapper';
import { headCells } from './LookUpHouseholdTableHeadCells';
import { LookUpHouseholdTableRow } from './LookUpHouseholdTableRow';

interface LookUpHouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  setFieldValue;
  selectedHousehold?;
  setSelectedIndividual?;
  setSelectedHousehold?;
}

export const LookUpHouseholdTable = ({
  businessArea,
  filter,
  choicesData,
  setFieldValue,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
}: LookUpHouseholdTableProps): React.ReactElement => {
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    search: filter.search,
    programs: [filter.programs],
    lastRegistrationDate: JSON.stringify(filter.lastRegistrationDate),
    residenceStatus: filter.residenceStatus,
    admin2: filter?.admin2?.node?.id,
    familySize: JSON.stringify(filter.size),
  };
  if (filter.program) {
    initialVariables.programs = [filter.program];
  }

  const handleRadioChange = (
    household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'],
  ): void => {
    setSelectedHousehold(household);
    setFieldValue('selectedHousehold', household);
    setFieldValue('selectedIndividual', null);
    setSelectedIndividual(null);
    setFieldValue('identityVerified', false);
  };
  return (
    <TableWrapper>
      <UniversalTable<
        AllHouseholdsQuery['allHouseholds']['edges'][number]['node'],
        AllHouseholdsQueryVariables
      >
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllHouseholdsQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpHouseholdTableRow
            key={row.id}
            household={row}
            radioChangeHandler={handleRadioChange}
            selectedHousehold={selectedHousehold}
            choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
};
