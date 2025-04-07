import TableCell from '@mui/material/TableCell';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { WarningTooltip } from '@components/core/WarningTooltip';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface ImportedHouseholdTableRowProps {
  household;
  //TODO: add types
  // household: HouseholdDetail;
  rdi;
}

export function ImportedHouseholdTableRow({
  household,
  rdi,
}: ImportedHouseholdTableRowProps): ReactElement {
  const { baseUrl, businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;

  const handleClick = (): void => {
    navigate(householdDetailsPath, {
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
        {household.has_duplicates && (
          <WarningTooltip confirmed message={t('Household has Duplicates')} />
        )}
      </TableCell>
      <TableCell align="left">
        <StyledLink onClick={() => handleClick()}>
          {household.unicefId}
        </StyledLink>
      </TableCell>
      <AnonTableCell>{household?.headOfHousehold}</AnonTableCell>
      <TableCell align="right">{household.size}</TableCell>
      <TableCell align="left">{household?.admin2}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{household.first_registration_date}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
