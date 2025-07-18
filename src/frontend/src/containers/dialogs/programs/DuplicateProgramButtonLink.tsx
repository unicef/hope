import { IconButton } from '@mui/material';
import { FileCopy } from '@mui/icons-material';
import { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';

interface DuplicateProgramButtonLinkProps {
  program: ProgramDetail;
}

export function DuplicateProgramButtonLink({
  program,
}: DuplicateProgramButtonLinkProps): ReactElement {
  const { baseUrl } = useBaseUrl();

  return (
    <IconButton
      component={Link}
      to={`/${baseUrl}/duplicate/${program.slug}`}
      data-cy="button-copy-program"
    >
      <FileCopy />
    </IconButton>
  );
}
