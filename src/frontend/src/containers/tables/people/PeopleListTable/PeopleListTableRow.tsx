import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { RelationshipEnum } from '@restgenerated/models/RelationshipEnum';
import { individualStatusToColor, sexToCapitalize } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

interface IndividualsListTableRowProps {
  individual: IndividualList;
  canViewDetails: boolean;
}

export const PeopleListTableRow = ({
  individual,
  canViewDetails,
}: IndividualsListTableRowProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();

  const individualDetailsPath = `/${baseUrl}/population/people/${individual.id}`;
  const handleClick = (): void => {
    navigate(individualDetailsPath);
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={individual.id}
      data-cy="individual-table-row"
    >
      <TableCell align="left">
        {/*<IndividualFlags individual={individual} /> TODO REST refactor*/}
      </TableCell>
      <TableCell align="left">
        <BlackLink to={individualDetailsPath}>{individual.unicefId}</BlackLink>
      </TableCell>
      <AnonTableCell>{individual.fullName}</AnonTableCell>
      <TableCell align="left">
        <StatusBox
          status={individual.status}
          statusToColor={individualStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {individual.relationship === RelationshipEnum.HEAD
          ? t('Beneficiary')
          : t('Non-beneficiary')}
      </TableCell>
      <TableCell align="right">{individual.age}</TableCell>
      <TableCell align="left">{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align="left">{individual.household?.admin2?.name}</TableCell>
    </ClickableTableRow>
  );
};
