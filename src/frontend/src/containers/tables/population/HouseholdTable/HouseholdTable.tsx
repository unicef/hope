import { BlackLink } from '@components/core/BlackLink';
import { FlagTooltip } from '@components/core/FlagTooltip';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { WarningTooltip } from '@components/core/WarningTooltip';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HouseholdRdiMergeStatus } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TableCell } from '@mui/material';
import { Box } from '@mui/system';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import {
  adjustHeadCells,
  formatCurrencyWithSymbol,
  householdStatusToColor,
} from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { headCells } from './HouseholdTableHeadCells';
import { HouseholdList } from '@restgenerated/models/HouseholdList';
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';
import { CountResponse } from '@restgenerated/models/CountResponse';

interface HouseholdTableRestProps {
  filter;
  canViewDetails: boolean;
}

export const HouseholdTable = ({
  filter,
  canViewDetails,
}: HouseholdTableRestProps): ReactElement => {
  const { selectedProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
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
      admin1: filter.admin1,
      admin2: filter.admin2,
      residenceStatus: filter.residenceStatus,
      withdrawn: matchWithdrawnValue(),
      ordering: filter.orderBy,
      rdiMergeStatus: HouseholdRdiMergeStatus.Merged,
    };
  }, [
    businessArea,
    programId,
    filter.householdSizeMin,
    filter.householdSizeMax,
    filter.search,
    filter.documentType,
    filter.documentNumber,
    filter.admin1,
    filter.admin2,
    filter.residenceStatus,
    filter.withdrawn,
    filter.orderBy,
  ]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery<PaginatedHouseholdListList>({
    queryKey: ['businessAreasProgramsHouseholdsList', queryVariables],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList(queryVariables),
  });

  const { data: countData } = useQuery<CountResponse>({
    queryKey: ['businessAreasProgramsHouseholdsCount', programId, businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
  });

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

  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const renderRow = (household: HouseholdList): ReactElement => {
    if (!household) {
      return <></>;
    }
    const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;
    const handleClick = (): void => {
      navigate(householdDetailsPath);
    };
    return (
      <ClickableTableRow
        hover
        onClick={canViewDetails ? handleClick : undefined}
        role="checkbox"
        key={household.unicefId}
        data-cy="household-table-row"
      >
        <TableCell align="left">
          <>
            <Box mr={2}>
              {household.hasDuplicates && (
                <WarningTooltip
                  confirmed
                  message={t('Houesehold has Duplicates')}
                />
              )}
            </Box>
            <Box mr={2}>
              {household.sanctionListPossibleMatch && (
                <FlagTooltip message={t('Sanction List Possible Match')} />
              )}
            </Box>
            <Box mr={2}>
              {household.sanctionListConfirmedMatch && (
                <FlagTooltip
                  message={t('Sanction List Confirmed Match')}
                  confirmed
                />
              )}
            </Box>
          </>
        </TableCell>
        <TableCell align="left">
          <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
        </TableCell>
        <TableCell align="left">
          <StatusBox
            status={household.status}
            statusToColor={householdStatusToColor}
          />
        </TableCell>
        <AnonTableCell>{household.headOfHousehold}</AnonTableCell>
        <TableCell align="left">{household.size}</TableCell>
        <TableCell align="left">{household.admin2 || '-'}</TableCell>
        <TableCell align="left">{household.residenceStatus}</TableCell>
        <TableCell align="right">
          {formatCurrencyWithSymbol(
            Number(household.totalCashReceived),
            household.currency?.toString(),
          )}
        </TableCell>
        <TableCell align="right">
          <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
        </TableCell>
      </ClickableTableRow>
    );
  };

  return (
    <TableWrapper>
      <UniversalRestTable
        title={`${beneficiaryGroup?.groupLabelPlural}`}
        renderRow={renderRow}
        headCells={adjustedHeadCells}
        data={data}
        error={error}
        isLoading={isLoading}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={countData?.count}
      />
    </TableWrapper>
  );
};
