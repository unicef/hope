import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HouseholdChoiceDataQuery } from '@generated/graphql';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { MouseEvent, ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells } from './LookUpHouseholdComunicationTableHeadCells';
import { LookUpHouseholdTableRowCommunication } from './LookUpHouseholdTableRowCommunication';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';

interface LookUpHouseholdTableCommunicationProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  setFieldValue;
  selectedHousehold?;
  setSelectedIndividual?;
  setSelectedHousehold?;
  noTableStyling?;
  householdMultiSelect?: boolean;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

function LookUpHouseholdTableCommunication({
  businessArea,
  filter,
  choicesData,
  setFieldValue,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  noTableStyling = false,
  householdMultiSelect,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: LookUpHouseholdTableCommunicationProps): ReactElement {
  const { programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const initialQueryVariables = useMemo(() => {
    const matchWithdrawnValue = (): boolean | undefined => {
      if (filter.withdrawn === 'true') {
        return true;
      }
      if (filter.withdrawn === 'false') {
        return false;
      }
      return undefined;
    };

    return {
      businessAreaSlug: businessArea,
      programSlug: programId,
      familySize: JSON.stringify({
        before: filter.householdSizeMin,
        after: filter.householdSizeMax,
      }),
      search: filter.search.trim(),
      documentType: filter.documentType,
      documentNumber: filter.documentNumber.trim(),
      admin2: filter.admin2,
      residenceStatus: filter.residenceStatus,
      withdrawn: matchWithdrawnValue(),
      orderBy: filter.orderBy,
      headOfHouseholdPhoneNoValid: true,
    };
  }, [businessArea, programId, filter]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasProgramsHouseholdsList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList({
        ...queryVariables,
      }),
    enabled: !!businessArea && !!programId,
  });

  const [selected, setSelected] = useState<string[]>(
    householdMultiSelect ? [...selectedHousehold] : [selectedHousehold],
  );

  const handleCheckboxClick = (
    _event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
    name: string,
  ): void => {
    const selectedIndex = selected.indexOf(name);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(name);
    } else {
      newSelected.splice(selectedIndex, 1);
    }

    if (setSelectedIndividual === undefined && householdMultiSelect) {
      setSelectedHousehold(newSelected);
    }
    setSelected(newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    event.preventDefault();
    let newSelecteds = [];
    if (!selected.length) {
      newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
    } else {
      setSelected([]);
    }
    if (setSelectedIndividual === undefined && householdMultiSelect) {
      setSelectedHousehold(newSelecteds);
    }
  };

  const handleRadioChange = (household): void => {
    setSelectedHousehold(household);
    setFieldValue('selectedHousehold', household);
    setFieldValue('selectedIndividual', null);
    if (setSelectedIndividual !== undefined) {
      setSelectedIndividual(null);
    }
    setFieldValue('identityVerified', false);
  };

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const renderTable = (): ReactElement => (
    <UniversalRestTable
      renderRow={(row) => (
        <LookUpHouseholdTableRowCommunication
          key={(row as any).id}
          household={row}
          radioChangeHandler={handleRadioChange}
          selectedHousehold={selectedHousehold}
          choicesData={choicesData}
          checkboxClickHandler={handleCheckboxClick}
          selected={selected}
          householdMultiSelect={householdMultiSelect}
          redirectedFromRelatedTicket={redirectedFromRelatedTicket}
          isFeedbackWithHouseholdOnly={isFeedbackWithHouseholdOnly}
        />
      )}
      headCells={
        householdMultiSelect ? adjustedHeadCells.slice(1) : adjustedHeadCells
      }
      allowSort={false}
      onSelectAllClick={householdMultiSelect && handleSelectAllCheckboxesClick}
      numSelected={householdMultiSelect && selected.length}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={data}
      isLoading={isLoading}
      error={error}
    />
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    <TableWrapper>{renderTable()}</TableWrapper>
  );
}

export default withErrorBoundary(
  LookUpHouseholdTableCommunication,
  'LookUpHouseholdTableCommunication',
);
