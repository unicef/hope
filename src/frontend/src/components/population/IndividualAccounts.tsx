import { DividerLine } from '@components/core/DividerLine';
import React, { FC } from 'react';
import { LabelizedField } from '@components/core/LabelizedField';
import { Title } from '@core/Title';
import { usePermissions } from '@hooks/usePermissions';
import { Grid, Paper, Theme, Typography } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { renderSomethingOrDash, splitCamelCase } from '@utils/utils';
import { t } from 'i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { useArrayToDict } from '@hooks/useArrayToDict';
import type { Account } from '@restgenerated/models/Account';

interface IndividualAccountsProps {
  individual: IndividualDetail;
  choicesData: IndividualChoices;
}

const Overview = styled(Paper)<{ theme?: Theme }>`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(4)};
`;
interface AccountItemProps {
  account: Account;
  lastItem?: boolean;
  accountFinancialInstitutionsDict:
    | {
        [p: string]: any;
      }
    | {
        [p: number]: any;
      };
}
const AccountItem: FC<AccountItemProps> = ({
  account,
  lastItem,
  accountFinancialInstitutionsDict,
}) => {
  const dataFields = account.dataFields;
  return (
    <Grid size={12} key={account.id}>
      <Typography variant="h6">{account.name}</Typography>
      <Grid container spacing={3}>
        <Grid size={3}>
          <LabelizedField label={t('Financial Institution')}>
            {renderSomethingOrDash(
              accountFinancialInstitutionsDict[account.financialInstitution],
            )}
          </LabelizedField>
        </Grid>

        <Grid size={3}>
          <LabelizedField label={t('Number')}>
            {renderSomethingOrDash(account.number)}
          </LabelizedField>
        </Grid>
        {dataFields.map((field, idx) => {
          return (
            <Grid key={idx} size={3}>
              <LabelizedField label={splitCamelCase(field.key)}>
                {renderSomethingOrDash(field.value)}
              </LabelizedField>
            </Grid>
          );
        })}
      </Grid>
      {!lastItem && <DividerLine />}
    </Grid>
  );
};

export const IndividualAccounts: FC<IndividualAccountsProps> = ({
  individual,
  choicesData,
}) => {
  const permissions = usePermissions();
  const canViewDeliveryMechanisms = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
    permissions,
  );
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const accountFinancialInstitutionsDict = useArrayToDict(
    choicesData.accountFinancialInstitutionChoices,
    'value',
    'name',
  );

  if (!individual?.accounts?.length || !canViewDeliveryMechanisms) {
    return null;
  }

  return (
    <Overview>
      <Title>
        <Typography variant="h6">
          {t(`${beneficiaryGroup?.memberLabel} Accounts`)}
        </Typography>
      </Title>
      <Grid container spacing={6}>
        {individual.accounts.map((account, index) => {
          return (
            <AccountItem
              account={account}
              key={account.id}
              lastItem={index + 1 === individual.accounts.length}
              accountFinancialInstitutionsDict={
                accountFinancialInstitutionsDict
              }
            />
          );
        })}
      </Grid>
    </Overview>
  );
};
