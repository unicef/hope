import { Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { PERMISSIONS } from 'src/config/permissions';

export const CreateTPMenu = (): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();

  return (
    <>
      {!isActiveProgram ? (
        <ButtonTooltip
          variant="contained"
          color="primary"
          title={t(
            'Program has to be active to create a new Target Population',
          )}
          component={Link}
          to={`/${baseUrl}/target-population/create`}
          dataCy="button-new-tp-disabled"
          dataPerm={PERMISSIONS.TARGETING_CREATE}
          disabled={!isActiveProgram}
        >
          {t('Create New')}
        </ButtonTooltip>
      ) : (
        <Button
          variant="contained"
          color="primary"
          component={Link}
          to={`/${baseUrl}/target-population/create`}
          data-cy="button-new-tp"
          data-perm={PERMISSIONS.TARGETING_CREATE}
        >
          {t('Create New')}
        </Button>
      )}
    </>
  );
};
