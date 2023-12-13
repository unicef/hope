import { IconButton } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { ProgramQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

interface DuplicateProgramButtonLinkProps {
  program: ProgramQuery['program'];
}

export const DuplicateProgramButtonLink = ({
  program,
}: DuplicateProgramButtonLinkProps): ReactElement => {
  const { baseUrl } = useBaseUrl();

  return (
    <IconButton
      component={Link}
      to={`/${baseUrl}/duplicate/${program.id}`}
      data-cy='button-copy-program'
    >
      <FileCopy />
    </IconButton>
  );
};
