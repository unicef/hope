import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useDeleteTargetPopulationMutation } from '../../../__generated__/graphql';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export interface DeleteTargetPopulation {
  open: boolean;
  setOpen: Function;
}

export const DeleteTargetPopulation = ({
  open,
  setOpen,
  targetPopulationId,
}): React.ReactElement => {
  const { t } = useTranslation();
  const [mutate, { loading }] = useDeleteTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const initialValues = {
    id: targetPopulationId,
  };
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <Formik
        validationSchema={null}
        initialValues={initialValues}
        onSubmit={async () => {
          await mutate({
            variables: { input: { targetId: targetPopulationId } },
          });
          setOpen(false);
          showMessage('Target Population Deleted', {
            pathname: `/${baseUrl}/target-population/`,
            historyMethod: 'push',
          });
        }}
      >
        {({ submitForm }) => (
          <>
            {open && <AutoSubmitFormOnEnter />}
            <DialogTitleWrapper>
              <DialogTitle>{t('Delete Target Population')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                {t('Are you sure you want to delete this Target Population?')}
              </DialogDescription>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                <LoadingButton
                  loading={loading}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-delete'
                >
                  {t('Delete')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
};
