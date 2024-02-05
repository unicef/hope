import TableCell from '@mui/material/TableCell';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { AnonTableCell } from '../../../../components/core/Table/AnonTableCell';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { WarningTooltip } from '../../../../components/core/WarningTooltip';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface ImportedHouseholdTableRowProps {
  isMerged?: boolean;
  household;
  rdi;
}

export const ImportedHouseholdTableRow = ({
  isMerged,
  household,
  rdi,
}: ImportedHouseholdTableRowProps): React.ReactElement => {
  const { baseUrl, businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const history = useHistory();

  const importedHouseholdPath = `/${baseUrl}/registration-data-import/household/${household.id}`;
  const mergedHouseholdPath = `/${baseUrl}/population/household/${household.id}`;
  const url = isMerged ? mergedHouseholdPath : importedHouseholdPath;

  const handleClick = (): void => {
    history.push({
      pathname: url,
      state: {
        breadcrumbTitle: `Registration Data Import: ${rdi.name}`,
        breadcrumbUrl: `/${businessArea}/registration-data-import/${rdi.id}`,
      },
    });
  };

  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role="checkbox"
      key={household.id}
      data-cy="imported-households-row"
    >
      <TableCell align="left">
        {household.hasDuplicates && (
          <WarningTooltip confirmed message={t('Household has Duplicates')} />
        )}
      </TableCell>
      <TableCell align="left">
        <StyledLink onClick={() => handleClick()}>
          {isMerged ? household.unicefId : household.importId}
        </StyledLink>
      </TableCell>
      <AnonTableCell>{household?.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align="right">{household.size}</TableCell>
      <TableCell align="left">
        {isMerged ? household.admin2?.name : household.admin2Title}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{household.firstRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
