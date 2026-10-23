import { Button, IconButton } from '@mui/material';
import { FileCopy } from '@mui/icons-material';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useIsMobile } from 'src/responsive';

interface DuplicateProgramButtonLinkProps {
  program: ProgramDetail;
}

export function DuplicateProgramButtonLink({
  program,
}: DuplicateProgramButtonLinkProps): ReactElement {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const isMobile = useIsMobile();
  const to = `/${baseUrl}/duplicate/${program.code}`;

  // A lone icon has no room for a hint on mobile, where header actions are full-width labelled buttons.
  if (isMobile) {
    return (
      <Button
        component={Link}
        to={to}
        variant="outlined"
        color="primary"
        startIcon={<FileCopy />}
        data-cy="button-copy-program"
      >
        {t('Duplicate Programme')}
      </Button>
    );
  }

  return (
    <IconButton component={Link} to={to} data-cy="button-copy-program">
      <FileCopy />
    </IconButton>
  );
}
