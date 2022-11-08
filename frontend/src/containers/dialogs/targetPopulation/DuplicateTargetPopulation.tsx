import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { handleValidationErrors } from '../../../utils/utils';
import { useCopyTargetPopulationMutation } from '../../../__generated__/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

export interface FinalizeTargetPopulationPropTypes {
  open: boolean;
  setOpen: Function;
}

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
});

interface DuplicateTargetPopulationPropTypes {
  open: boolean;
  setOpen: Function;
  targetPopulationId: string;
}

export const DuplicateTargetPopulation = ({
  open,
  setOpen,
  targetPopulationId,
}: DuplicateTargetPopulationPropTypes): React.ReactElement => {
  const { t } = useTranslation();
  const [mutate, { loading }] = useCopyTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const initialValues = {
    name: '',
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
        validationSchema={validationSchema}
        initialValues={initialValues}
        onSubmit={async (values, { setFieldError }) => {
          try {
            const res = await mutate({
              variables: { input: { targetPopulationData: { ...values } } },
            });
            setOpen(false);
            showMessage(t('Target Population Duplicated'), {
              pathname: `/${businessArea}/target-population/${res.data.copyTargetPopulation.targetPopulation.id}`,
              historyMethod: 'push',
            });
          } catch (e) {
            const { nonValidationErrors } = handleValidationErrors(
              'copyTargetPopulation',
              e,
              setFieldError,
              showMessage,
            );
            if (nonValidationErrors.length > 0) {
              showMessage(
                t('Unexpected problem while creating Target Population'),
              );
            }
          }
        }}
      >
        {({ submitForm }) => (
          <>
            {open && <AutoSubmitFormOnEnter />}
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <Typography variant='h6'>
                  Duplicate Target Population?
                </Typography>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                {t(
                  'Please use a unique name for the copy of this Target Population.',
                )}
                <br /> <strong>{t('Note')}</strong>:{' '}
                {t(
                  'This duplicate will copy the Target Criteria of the Programme Population and update to the latest results from the system.',
                )}
              </DialogDescription>
              <Field
                name='name'
                fullWidth
                label={t('Name Copy of Target Population')}
                required
                variant='outlined'
                component={FormikTextField}
              />
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
                  data-cy='button-target-population-duplicate'
                >
                  {t('Save')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
};
