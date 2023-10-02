import { Box, Button, Grid } from '@material-ui/core';
import ListItem from '@material-ui/core/ListItem';
import React, { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useCachedImportedIndividualFieldsQuery } from '../../../hooks/useCachedImportedIndividualFields';
import {
  associatedWith,
  isNot,
  paymentInstructionStatusToColor,
} from '../../../utils/utils';
import { BaseSection } from '../../core/BaseSection';
import { DividerLine } from '../../core/DividerLine';
import { UniversalCriteriaPlainComponent } from '../../core/UniversalCriteriaComponent/UniversalCriteriaPlainComponent';
import { LabelizedField } from '../../core/LabelizedField';
import { ErrorButton } from '../../core/ErrorButton';
import { StatusBox } from '../../core/StatusBox';
import { AcceptanceProcess } from './AcceptanceProcess/AcceptanceProcess';

type Item = {
  id: string;
  unicefId: string;
  status: string;
  deliveryMechanism: string;
  fsp: string;
  criteria;
  approvalProcess;
};

const AvatarTitle = styled(Box)`
  color: #000 !important;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1.5px;
`;

const AvatarId = styled(Box)`
  color: #000 !important;
  font-size: 20px;
  font-weight: 500;
`;

const StatusWrapper = styled.div`
  width: 140px;
  margin-left: 30px;
`;

export type PaymentInstructionItemProps = {
  item: Item;
  actions;
};

export const PaymentInstructionItem = ({
  item,
  actions,
}: PaymentInstructionItemProps): ReactElement => {
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();

  const { data, loading } = useCachedImportedIndividualFieldsQuery(
    businessArea,
  );
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: data?.allFieldsAttributes
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: data?.allFieldsAttributes?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [data, loading]);

  const rejectButton = (
    <Grid item>
      <ErrorButton onClick={actions.handleReject}>{t('Reject')}</ErrorButton>
    </Grid>
  );

  const authorizeButton = (
    <Grid item>
      <Button
        onClick={actions.handleAuthorize}
        variant='contained'
        color='primary'
      >
        {t('Authorize')}
      </Button>
    </Grid>
  );

  const releaseButton = (
    <Grid item>
      <Button
        onClick={actions.handleRelease}
        variant='contained'
        color='primary'
      >
        {t('Release')}
      </Button>
    </Grid>
  );

  const buttons = (
    <>
      <Box display='flex' justifyContent='center' alignItems='center'>
        <Grid container>
          <Grid container item spacing={4}>
            {item.status === 'PENDING' && [rejectButton, authorizeButton]}
            {item.status === 'AUTHORIZED' && [rejectButton, releaseButton]}
            {item.status === 'REJECTED' && authorizeButton}
          </Grid>
        </Grid>
      </Box>
    </>
  );

  const title = (
    <Box display='flex' alignItems='center'>
      <Box display='flex' flexDirection='column'>
        <AvatarTitle>{t('Payment Instruction')}</AvatarTitle>
        <Box
          display='flex'
          flexDirection='row'
          justifyContent='center'
          alignItems='center'
        >
          <AvatarId data-cy='payment-instruction-id'>
            ID: {item.unicefId}
          </AvatarId>
          <StatusWrapper>
            <StatusBox
              status={item.status}
              statusToColor={paymentInstructionStatusToColor}
            />
          </StatusWrapper>
        </Box>
      </Box>
    </Box>
  );

  return (
    <ListItem>
      <BaseSection title={title} buttons={buttons}>
        <>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={4}>
                <Box mr={4}>
                  <LabelizedField label={t('Delivery Mechanism')}>
                    {item.deliveryMechanism}
                  </LabelizedField>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box mr={4}>
                  <LabelizedField label={t('Fsp')}>{item.fsp}</LabelizedField>
                </Box>
              </Grid>
            </Grid>
          </Box>
          <DividerLine />
          <Grid container>
            <Box mb={2}>
              <UniversalCriteriaPlainComponent
                rules={item.criteria}
                householdFieldsChoices={
                  householdData?.allFieldsAttributes || []
                }
                individualFieldsChoices={
                  individualData?.allFieldsAttributes || []
                }
              />
            </Box>
          </Grid>
          <DividerLine />
          <AcceptanceProcess records={item.approvalProcess.edges} />
        </>
      </BaseSection>
    </ListItem>
  );
};
