import {
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import AttachFileIcon from '@material-ui/icons/AttachFile';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PAYMENT_PLAN_QUERY } from '../../../../apollo/queries/paymentmodule/PaymentPlan';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  PaymentPlanQuery,
  useAllSteficonRulesQuery,
  useExportXlsxPpListMutation,
  useSetSteficonRuleOnPpListMutation,
} from '../../../../__generated__/graphql';

import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { LoadingButton } from '../../../core/LoadingButton';
import { LoadingComponent } from '../../../core/LoadingComponent';
import { Missing } from '../../../core/Missing';
import { Title } from '../../../core/Title';
import { UniversalMoment } from '../../../core/UniversalMoment';
import { BigValue } from '../../../rdi/details/RegistrationDetails/RegistrationDetails';
import { ImportXlsxPaymentPlanPaymentList } from '../ImportXlsxPaymentPlanPaymentList/ImportXlsxPaymentPlanPaymentList';

const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

const GreyTextSmall = styled.p`
  color: #9e9e9e;
  font-size: 14px;
`;

const OrDivider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 2px;
  width: 50%;
  margin-top: 20px;
`;

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 20px;
`;

const DividerLabel = styled.div`
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
  margin-top: 20px;
`;

const DownloadIcon = styled(GetApp)`
  color: #043f91;
`;

const SpinaczIconContainer = styled(Box)`
  position: relative;
  top: 4px;
  font-size: 16px;
  color: #666666;
`;

const BoxWithBorderRight = styled(Box)`
  border-right: 1px solid #b1b1b5;
`;

interface EntitlementProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const Entitlement = ({
  paymentPlan,
}: EntitlementProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [steficonRuleValue, setSteficonRuleValue] = useState<string>(
    paymentPlan?.steficonRule?.rule.id || '',
  );
  const options = {
    refetchQueries: () => [
      {
        query: PAYMENT_PLAN_QUERY,
        variables: {
          id: paymentPlan.id,
        },
      },
    ],
  };

  const [
    setSteficonRule,
    { loading: loadingSetSteficonRule },
  ] = useSetSteficonRuleOnPpListMutation(options);

  const { data: steficonData, loading } = useAllSteficonRulesQuery({
    variables: { enabled: true, deprecated: false, type: 'PAYMENT_PLAN' },
  });
  const [
    mutateExport,
    { loading: loadingExport },
  ] = useExportXlsxPpListMutation();

  if (!steficonData) {
    return null;
  }
  if (loading) {
    return <LoadingComponent />;
  }

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant='h6'>{t('Entitlement')}</Typography>
          </Title>
          <GreyText>{t('Select Entitlement Formula')}</GreyText>
          <Grid alignItems='center' container>
            <Grid item xs={6}>
              <FormControl variant='outlined' margin='dense' fullWidth>
                <InputLabel>{t('Entitlement Formula')}</InputLabel>
                <Select
                  value={steficonRuleValue}
                  labelWidth={180}
                  onChange={(event) =>
                    setSteficonRuleValue(event.target.value as string)
                  }
                >
                  {steficonData.allSteficonRules.edges.map((each) => (
                    <MenuItem key={each.node.id} value={each.node.id}>
                      {each.node.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item>
              <Box ml={2}>
                <Button
                  variant='contained'
                  color='primary'
                  disabled={loadingSetSteficonRule || !steficonRuleValue}
                  onClick={async () => {
                    try {
                      await setSteficonRule({
                        variables: {
                          paymentPlanId: paymentPlan.id,
                          steficonRuleId: steficonRuleValue,
                        },
                      });
                      showMessage(
                        t('Formula is executing, please wait until completed'),
                      );
                    } catch (e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
                  }}
                >
                  {t('Apply')}
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Box display='flex' alignItems='center'>
            <OrDivider />
            <DividerLabel>Or</DividerLabel>
            <OrDivider />
          </Box>
        </Box>
        <Box display='flex'>
          <Box width='50%'>
            <BoxWithBorderRight
              display='flex'
              justifyContent='center'
              alignItems='center'
              flexDirection='column'
            >
              {paymentPlan.hasPaymentListXlsxFile ? (
                <Button
                  color='primary'
                  startIcon={<DownloadIcon />}
                  component='a'
                  download
                  href={`/api/download-payment-plan-payment-list/${paymentPlan.id}`}
                >
                  {t('DOWNLOAD TEMPLATE')}
                </Button>
              ) : (
                <LoadingButton
                  loading={loadingExport}
                  disabled={loadingExport}
                  color='primary'
                  startIcon={<GetApp />}
                  onClick={async () => {
                    try {
                      await mutateExport({
                        variables: {
                          paymentPlanId: paymentPlan.id,
                        },
                      });
                      showMessage(
                        t('Exporting XLSX started. Please check your email.'),
                      );
                    } catch (e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
                  }}
                >
                  {t('Export Xlsx')}
                </LoadingButton>
              )}

              <GreyTextSmall>
                {t(
                  'Template contains payment list with all targeted households',
                )}
              </GreyTextSmall>
            </BoxWithBorderRight>
          </Box>
          <Box width='50%'>
            <Box
              display='flex'
              justifyContent='center'
              alignItems='center'
              flexDirection='column'
            >
              <Box>
                <ImportXlsxPaymentPlanPaymentList paymentPlan={paymentPlan} />
              </Box>
              {paymentPlan?.importedXlsxFileName && (
                <Box alignItems='center' display='flex'>
                  <SpinaczIconContainer>
                    <AttachFileIcon fontSize='inherit' />
                  </SpinaczIconContainer>
                  <Box mr={1}>
                    <GreyTextSmall>
                      {paymentPlan?.importedXlsxFileName}
                    </GreyTextSmall>
                  </Box>
                  <GreyTextSmall>
                    {paymentPlan?.xlsxFileImportedDate ? (
                      <UniversalMoment>
                        {paymentPlan?.xlsxFileImportedDate}
                      </UniversalMoment>
                    ) : null}
                  </GreyTextSmall>
                </Box>
              )}
            </Box>
          </Box>
        </Box>
        <Divider />
        <LabelizedField label={t('Total Cash Received')}>
          <BigValue>
            USD <Missing />
          </BigValue>
        </LabelizedField>
      </ContainerColumnWithBorder>
    </Box>
  );
};
