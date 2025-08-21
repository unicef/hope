import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@core/BlackLink';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { sexToCapitalize } from '@utils/utils';
import { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';

interface LookUpIndividualTableRowProps {
  individual: IndividualList;
  radioChangeHandler: (individual: IndividualList) => void;
  selectedIndividual: IndividualList;
}

export function LookUpIndividualTableRow({
  individual,
  radioChangeHandler,
  selectedIndividual,
}: LookUpIndividualTableRowProps): ReactElement {
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();

  return (
    <ClickableTableRow
      onClick={() => {
        radioChangeHandler(individual);
      }}
      hover
      role="checkbox"
      key={individual.id}
      data-cy="individual-table-row"
    >
      <TableCell padding="checkbox">
        <Radio
          color="primary"
          checked={selectedIndividual?.id === individual.id}
          onChange={() => {
            radioChangeHandler(individual);
          }}
          value={individual.id}
          name="radio-button-household"
          slotProps={{ input: { 'aria-label': individual.id } }}
        />
      </TableCell>
      <TableCell align="left">
        {!isAllPrograms ? (
          <BlackLink to={`/${baseUrl}/population/individuals/${individual.id}`}>
            {individual.unicefId}
          </BlackLink>
        ) : (
          <span>{individual.unicefId || '-'}</span>
        )}
      </TableCell>
      <TableCell align="left">{individual.fullName}</TableCell>
      {!isSocialDctType && (
        <TableCell align="left">
          {individual.household ? individual.household.unicefId : '-'}
        </TableCell>
      )}
      <TableCell align="right">{individual.age}</TableCell>
      <TableCell align="left">{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align="left">
        {individual.household?.admin2?.id || '-'}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{individual.lastRegistrationDate}</UniversalMoment>
      </TableCell>
      {isAllPrograms && (
        <TableCell align="left">
          {individual.program ? (
            <BlackLink to={`/${baseUrl}/details/${individual.program.id}`}>
              {individual.program.name}
            </BlackLink>
          ) : (
            '-'
          )}
        </TableCell>
      )}
    </ClickableTableRow>
  );
}
