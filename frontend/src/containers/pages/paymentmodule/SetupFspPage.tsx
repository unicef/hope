import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../components/core/LabelizedField';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { Title } from '../../../components/core/Title';
import { FspDisplay } from '../../../components/paymentmodule/SetUpFspPlan/FspDisplay/FspDisplay';
import { SetUpFspHeader } from '../../../components/paymentmodule/SetUpFspPlan/SetUpFspHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useCreateTpMutation } from '../../../__generated__/graphql';

export const SetUpFspPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    mobileMoney: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
    transfer: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
    cash: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
    wallet: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
  };
  const [mutate] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  return (
    <>
      <SetUpFspHeader businessArea={businessArea} permissions={permissions} />
      <Box m={5}>
        <ContainerColumnWithBorder>
          <Box mt={4}>
            <Title>
              <Typography variant='h6'>
                {t('Total Maximum Amount')}() {t('per FSP')}
              </Typography>
            </Title>
          </Box>
          <Grid container>
            {[
              { id: 1, name: 'CITIGROUP', maxAmount: 10000 },
              { id: 2, name: 'Bank of America', maxAmount: 2222 },
              { id: 3, name: 'Chase Bank', maxAmount: 4566 },
            ].map((fsp) => (
              <Grid key={fsp.id} item xs={3}>
                <LabelizedField label={fsp.name}>
                  {fsp.maxAmount}
                </LabelizedField>
              </Grid>
            ))}
          </Grid>
        </ContainerColumnWithBorder>
      </Box>
      <Box m={5}>
        <ContainerColumnWithBorder>
          {[
            {
              id: 1,
              name: 'Mobile Money',
              fsps: [
                { id: 1, name: 'Chase Bank', maxAmount: 10000 },
                { id: 2, name: 'Bank of Bullet', maxAmount: 2222 },
                { id: 3, name: 'BlaBla Bank', maxAmount: 4566 },
              ],
            },
            {
              id: 2,
              name: 'Transfer',
              fsps: [
                { id: 1, name: 'Chase Bank', maxAmount: 10000 },
                { id: 2, name: 'Bank of Bullet', maxAmount: 2222 },
                { id: 3, name: 'BlaBla Bank', maxAmount: 4566 },
              ],
            },
            {
              id: 3,
              name: 'Cash',
              fsps: [
                { id: 1, name: 'Chase Bank', maxAmount: 10000 },
                { id: 2, name: 'Bank of Bullet', maxAmount: 2222 },
                { id: 3, name: 'BlaBla Bank', maxAmount: 4566 },
              ],
            },
            {
              id: 4,
              name: 'Wallet',
              fsps: [
                { id: 1, name: 'Chase Bank', maxAmount: 10000 },
                { id: 2, name: 'Bank of Bullet', maxAmount: 2222 },
                { id: 3, name: 'BlaBla Bank', maxAmount: 4566 },
              ],
            },
          ].map((el) => (
            <FspDisplay key={el.id} fsp={el} />
          ))}
        </ContainerColumnWithBorder>
      </Box>
    </>
  );
};
