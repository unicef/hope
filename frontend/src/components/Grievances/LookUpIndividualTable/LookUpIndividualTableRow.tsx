import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { Radio } from '@material-ui/core';
import { AllIndividualsQuery } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { getAgeFromDob, sexToCapitalize } from '../../../utils/utils';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { Pointer } from '../../Pointer';
import { UniversalMoment } from '../../UniversalMoment';

interface LookUpIndividualTableRowProps {
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
  radioChangeHandler: (
    individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'],
  ) => void;
  selectedIndividual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
}

export function LookUpIndividualTableRow({
  individual,
  radioChangeHandler,
  selectedIndividual,
}: LookUpIndividualTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  let age: number | string = 'N/A';
  if (individual.birthDate) {
    age = getAgeFromDob(individual.birthDate);
  }
  const handleClick = (): void => {
    const path = `/${businessArea}/population/individuals/${individual.id}`;
    const win = window.open(path, '_blank rel=noopener');
    if (win != null) {
      win.focus();
    }
  };
  const renderPrograms = (): string => {
    const programNames = individual?.household?.programs?.edges?.map(
      (edge) => edge.node.name,
    );
    return programNames?.length ? programNames.join(', ') : '-';
  };
  const renderAdminLevel2 = (): string => {
    if (individual?.household?.adminArea?.adminAreaType?.adminLevel === 2) {
      return individual?.household?.adminArea?.title;
    }
    return '-';
  };
  return (
    <ClickableTableRow hover role='checkbox' key={individual.id}>
      <TableCell padding='checkbox'>
        <Radio
          color='primary'
          checked={selectedIndividual?.id === individual.id}
          onChange={() => {
            radioChangeHandler(individual);
          }}
          value={individual.id}
          name='radio-button-household'
          inputProps={{ 'aria-label': individual.id }}
        />
      </TableCell>
      <TableCell onClick={handleClick} align='left'>
        <Pointer>{individual.unicefId}</Pointer>
      </TableCell>
      <TableCell align='left'>{individual.fullName}</TableCell>
      <TableCell align='left'>
        {individual.household ? individual.household.unicefId : ''}
      </TableCell>
      <TableCell align='right'>{age}</TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align='left'>{renderAdminLevel2()}</TableCell>
      <TableCell align='left'>{renderPrograms()}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{individual.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
