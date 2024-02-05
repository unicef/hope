import { Button } from '@mui/material';
import { Link } from 'react-router-dom';
import EditIcon from '@material-ui/icons/EditRounded';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

interface EditProgramButtonLinkProps {
  program: ProgramQuery['program'];
}

export const EditProgramButtonLink = ({
  program,
}: EditProgramButtonLinkProps): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  return (
    <Button
      data-cy="button-edit-program"
      variant="outlined"
      color="primary"
      startIcon={<EditIcon />}
      component={Link}
      to={`/${baseUrl}/edit/${program.id}`}
    >
      {t('EDIT PROGRAMME')}
    </Button>
  );
};
