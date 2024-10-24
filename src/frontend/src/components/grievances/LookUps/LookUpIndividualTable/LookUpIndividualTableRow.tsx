import { Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { AllIndividualsForPopulationTableQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { sexToCapitalize } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';

interface LookUpIndividualTableRowProps {
  individual: AllIndividualsForPopulationTableQuery['allIndividuals']['edges'][number]['node'];
  radioChangeHandler: (
    individual: AllIndividualsForPopulationTableQuery['allIndividuals']['edges'][number]['node'],
  ) => void;
  selectedIndividual: AllIndividualsForPopulationTableQuery['allIndividuals']['edges'][number]['node'];
}

export function LookUpIndividualTableRow({
  individual,
  radioChangeHandler,
  selectedIndividual,
}: LookUpIndividualTableRowProps): React.ReactElement {
  const { baseUrl, isAllPrograms } = useBaseUrl();

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
          inputProps={{ 'aria-label': individual.id }}
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
      <TableCell align="left">
        {individual.household ? individual.household.unicefId : '-'}
      </TableCell>
      <TableCell align="right">{individual.age}</TableCell>
      <TableCell align="left">{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align="left">
        {individual?.household?.admin2?.name || '-'}
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
